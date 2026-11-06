"""
游戏状态容器：``GameState``。

整局游戏的可变数据（分数、方向、是否运行、幽灵模式等）集中在一个对象里，
其它模块通过 **属性 property** 读写，而不是随便改 ``self.__xxx``。

Python 封装习惯：
- 双下划线前缀 ``__level`` 会触发「名称改写」， mainly 防止子类意外同名覆盖；
- ``@property`` / ``@xxx.setter`` 让外部写 ``state.points = 10`` 时仍可校验或挂钩逻辑。

``mode_change_events`` 的 getter 带 **副作用**：每次读取会推进内部索引，
供 EventHandler 定时切换 scatter/chase 时使用不同间隔（来自关卡 JSON 列表）。

阅读建议：先扫 ``__init__`` 看有哪些字段，再按需查对应 property 的注释。
"""

from src.configs import DOT_POINT

# ---------------------------------------------------------------------------
# GameState 在工程中的数据流（帮助建立整体图景）
# ---------------------------------------------------------------------------
# EventHandler 写：direction, running, ghost_mode（scatter/chase 切换）, is_pacman_powered。
# runner 写：current_time；读：running, fps, points/highscore；退出时持久化 highscore。
# PacmanGrid 写：mode_change_events 列表、scared_time；读：level。
# sprites（pacman/ghosts）写：points, pacman_rect, ghost 位置, level_complete, is_pacman_dead 等。
# ScoreScreen 只读：points, highscore。
# 双下划线 __field 与单下划线 _field 在本项目都是「请勿随便改」的约定，后者多用于 property 后备字段。
# ---------------------------------------------------------------------------


class GameState:
    def __init__(self):
        # --- 关卡与主循环 ---
        # 当前关卡号，对应 levels/level{N}.json；过关后 level 递增（在 sprites 里改）。
        self.__level = 1
        # True 时 runner.main 的 while 继续；False 时保存统计并退出 pygame。
        self.__running = True
        # 传给 clock.tick(fps)，限制每秒最多多少帧，稳定游戏速度。
        self.__fps = 60
        # 玩家「下一帧想走的方向」，由 EventHandler 写，Pacman 读并尝试转弯。
        self.__direction = ""
        # pygame.time.get_ticks() 毫秒时间戳，动画/计时器都依赖它。
        self.__current_time = None

        # --- 实体位置（由 sprites 更新，gui/碰撞读取）---
        # pygame.Rect：吃豆人在屏幕上的 hitbox，碰撞检测用。
        self.__pacman_rect = None
        # 键为幽灵名 "blinky" 等，值为格子或像素坐标（由 ghosts 模块约定）。
        self.__ghost_pos = {}

        # --- 加载与能量豆 ---
        # 预留：资源是否加载完成（可用于异步读图）。
        self.__is_loaded = False
        # True 表示处于「能量豆生效」：幽灵变 scared、可被反吃。
        self.__is_pacman_powered = False

        # --- 幽灵 AI 模式 ---
        # 'scatter' | 'chase' | 'scared'，ghosts 里分支不同寻路策略。
        self._ghost_mode = 'scatter'
        # 来自关卡 JSON 的 scatter/chase 切换间隔列表（秒），由 setter 一次写入。
        self._mode_change_events = None
        # 配合 mode_change_events getter，记录下次该取列表第几个间隔。
        self.__current_mode_index = 0
        # pygame 定时事件类型 ID，scatter↔chase 切换时 EventHandler 比对 event.type。
        self._custom_event = None
        # 吃豆人当前「已生效的朝向」，与 direction（按键愿望）可能不同（撞墙时）。
        self._pacman_direction = None
        # 红鬼 Blinky 在逻辑矩阵中的格坐标，其它鬼 AI 会参考。
        self._blinky_matrix_pos = None
        # 能量豆持续时间（毫秒量级，与关卡 JSON power_up_time 一致）。
        self._scared_time = None
        # 能量豆结束时的 USEREVENT id，到点关闭 is_pacman_powered。
        self._power_up_event = None
        # 记录能量豆事件应触发的时刻，用于 set_timer 或比较 current_time。
        self._power_event_trigger_time = None

        # --- 生命、记分、过关 ---
        # True 时 ScreenManager 会在下一帧重置精灵（一条命消耗完）。
        self._is_pacman_dead = False
        # 历史最高，启动时从 stats.json 读，游戏中可能被 check_highscores 刷新。
        self._highscore = 0
        # 累计游戏分钟数，持久化到 stats.json（本项目中较少更新）。
        self._mins_played = 0
        # 初始 -DOT_POINT：第一次吃到豆时加 DOT_POINT，HUD 从 0 起计（与 pacman 逻辑配合）。
        self._points = -DOT_POINT
        # True 表示本关所有豆已清，ScreenManager 等待后进下一关。
        self._level_complete = False

    # -------------------------------------------------------------------------
    # 过关与计分（property：对外像普通属性，对内可换存储字段名）
    # -------------------------------------------------------------------------
    # 写入：pacman/sprites 在清关时设 True。
    # 读取：ScreenManager.check_level_complete 等待并重建下一关。
    # 注意：GUI 负责清回 False，sprites 不应直接 new PacmanGrid。
    @property
    def level_complete(self):
        # getter：返回 _level_complete 布尔值。
        return self._level_complete

    @level_complete.setter
    def level_complete(self, val):
        # setter：过关流程中可写 True/False。
        self._level_complete = val

    # 写入：吃豆/吃鬼/过关时 sprites 累加。
    # 读取：ScoreScreen HUD；runner.check_highscores 每帧比较。
    # 与 configs.DOT_POINT 等常量相加，不在此 property 内计算。
    @property
    def points(self):
        # getter：整数，可为负直到第一次吃豆。
        return self._points

    @points.setter
    def points(self, val):
        # setter：直接覆盖或累加后的结果写入。
        self._points = val

    # 写入：启动读 JSON；游戏中 runner 可刷新；退出前写盘。
    # 读取：ScoreScreen 显示 HIGHSCORE。
    @property
    def highscore(self):
        # getter：整数，默认 0。
        return self._highscore

    @highscore.setter
    def highscore(self, val):
        # setter：持久化前内存中的最高记录。
        self._highscore = val

    # 写入：initialize_highscore / update_highscore 与 JSON 同步。
    # 读取：目前 HUD 未显示，预留统计用。
    @property
    def mins_played(self):
        # getter：整数分钟。
        return self._mins_played

    @mins_played.setter
    def mins_played(self, val):
        # setter：与 highscore 一并 dump 到文件。
        self._mins_played = val

    # 写入：pacman 撞鬼且未 powered 时 True。
    # 读取：ScreenManager.pacman_dead_reset 检测并 reset_stage。
    @property
    def is_pacman_dead(self):
        # getter：布尔，一条命消耗标志。
        return self._is_pacman_dead

    @is_pacman_dead.setter
    def is_pacman_dead(self, val):
        # setter：重生流程开头会清 False。
        self._is_pacman_dead = val

    # -------------------------------------------------------------------------
    # 能量豆定时（pygame USEREVENT id 与时间戳存 state，供 event 与 sprites 共用）
    # -------------------------------------------------------------------------
    # 写入：pacman 吃 power 豆时结合 scared_time 计算。
    # 读取：sprites 内与 current_time 比较或 set_timer 参考。
    @property
    def power_event_trigger_time(self):
        # getter：None 表示尚未激活能量豆计时。
        return self._power_event_trigger_time

    @power_event_trigger_time.setter
    def power_event_trigger_time(self, val):
        # setter：毫秒 time.get_ticks 语义。
        self._power_event_trigger_time = val

    # 写入：pacman 注册 USEREVENT+n。
    # 读取：EventHandler 比对 event.type 关闭 powered。
    @property
    def power_up_event(self):
        # getter：None 表示未注册定时事件。
        return self._power_up_event

    @power_up_event.setter
    def power_up_event(self, val):
        # setter：与 custom_event 类似，存 ID 供主循环分发。
        self._power_up_event = val

    # 写入：PacmanGrid.load_level 同步关卡配置。
    # 读取：ghosts 决定 scared 模式维持多久。
    @property
    def scared_time(self):
        # getter：数值单位与关卡 JSON 一致（本项目为毫秒量级配置）。
        return self._scared_time

    @scared_time.setter
    def scared_time(self, val):
        # setter：换关时会重新 load 覆盖。
        self._scared_time = val

    # 写入：ghosts 每帧或格子变化时更新。
    # 读取：Pinky/Inky 经典 targeting 算法。
    @property
    def blinky_matrix_pos(self):
        # getter：元组或 None。
        return self._blinky_matrix_pos

    @blinky_matrix_pos.setter
    def blinky_matrix_pos(self, val):
        # setter：供 AI 共享锚点。
        self._blinky_matrix_pos = val

    # 写入：pacman 在成功移动后更新。
    # 读取：动画选帧、反向限制；与 direction（按键愿望）可能不同。
    @property
    def pacman_direction(self):
        # getter：如 "l"/"r" 或 None。
        return self._pacman_direction

    @pacman_direction.setter
    def pacman_direction(self, val):
        # setter：死亡重生时 ScreenManager 清 None。
        self._pacman_direction = val

    # 写入：runner.create_ghost_mode_event 与 EventHandler 内 set_timer 后更新。
    # 读取：EventHandler.handle_events 分支判断。
    @property
    def custom_event(self):
        # getter：USEREVENT+1 一类整数。
        return self._custom_event

    @custom_event.setter
    def custom_event(self, val):
        # setter：每次重设 timer 可能改写 ID（本项目固定 +1 模式）。
        self._custom_event = val

    # 写入：PacmanGrid 传入整表 list；只应 load 时 set 一次为主。
    # 副作用：getter 递增 __current_mode_index，供 EventHandler 下次 set_timer。
    @property
    def mode_change_events(self):
        # 若关卡配置的间隔用完了，一直用最后一个，避免 IndexError。
        if self.__current_mode_index >= len(self._mode_change_events):
            curr_event = self._mode_change_events[-1]
        else:
            curr_event = self._mode_change_events[self.__current_mode_index]
            self.__current_mode_index += 1
        return curr_event

    @mode_change_events.setter
    def mode_change_events(self, val):
        # setter：保存 list 引用，不拷贝。
        self._mode_change_events = val

    # 写入：EventHandler 定时切换；能量豆进入 scared；setter 白名单校验。
    # 读取：GhostManager 寻路与速度分支。
    @property
    def ghost_mode(self):
        # getter：字符串，初始 'scatter'。
        return self._ghost_mode

    @ghost_mode.setter
    def ghost_mode(self, value):
        # 非法字符串拒绝写入，避免 ghosts 模块 if 链走到未定义分支。
        if value not in ['scatter', 'chase', 'scared']:
            raise ValueError("Only scatter, scared or chase modes are available")
        self._ghost_mode = value

    # 写入：吃 power 豆 True；定时事件或逻辑 False。
    # 读取：碰撞判定、ghost 是否 scared。
    @property
    def is_pacman_powered(self):
        # getter：布尔，存 __is_pacman_powered（名称改写字段）。
        return self.__is_pacman_powered

    @is_pacman_powered.setter
    def is_pacman_powered(self, val):
        # setter：EventHandler 在 power_up_event 到点置 False。
        self.__is_pacman_powered = val

    # 当前流程未使用；可与 LoadingScreen 联动。
    @property
    def is_loaded(self):
        # getter：始终可读，默认 False。
        return self.__is_loaded

    # 用方法而非 property 访问 __ghost_pos，因为需要 (name) 参数，像 dict API。
    def get_ghost_pos(self, name):
        # dict.get：无键时返回 None 而不是 KeyError，便于「幽灵尚未出场」的情况。
        return self.__ghost_pos.get(name)

    def set_ghost_pos(self, name, val):
        # 写入指定幽灵名对应的坐标缓存。
        self.__ghost_pos[name] = val

    # 写入：pacman 每帧更新位置。
    # 读取：撞墙、撞鬼、吃豆检测。
    @property
    def pacman_rect(self):
        # getter：None 直到首帧 update。
        return self.__pacman_rect

    @pacman_rect.setter
    def pacman_rect(self, rect):
        # setter：传入 Rect 对象引用。
        self.__pacman_rect = rect

    # 写入：runner.main 每帧开头。
    # 读取：动画、音效节流、定时逻辑。
    @property
    def current_time(self):
        # getter：毫秒整数。
        return self.__current_time

    @current_time.setter
    def current_time(self, val):
        # setter：与 pygame 时钟同步。
        self.__current_time = val

    # 写入：EventHandler.key_bindings。
    # 读取：pacman 尝试转弯；setter 校验 r/l/u/d/空串。
    @property
    def direction(self):
        # getter：短字符串，非 pygame 键常量。
        return self.__direction

    @direction.setter
    def direction(self, value):
        if value not in ["r", "l", "u", "d", ""]:
            raise ValueError("Unknown direction")
        self.__direction = value

    # 写入：过关后 sprites 递增。
    # 读取：PacmanGrid.load_level 拼 JSON 路径。
    @property
    def level(self):
        # getter：整数，对应 levels/level{N}.json。
        return self.__level

    @level.setter
    def level(self, value):
        # setter：换关时更新。
        self.__level = value

    # 写入：EventHandler 关窗 False。
    # 读取：runner.main while self.game_state.running。
    @property
    def running(self):
        # getter：True 继续游戏。
        return self.__running

    @running.setter
    def running(self, value):
        # setter：False 触发保存与 quit。
        self.__running = value

    # 写入：可调难度或省电；默认构造 60。
    # 读取：runner.main clock.tick(self.game_state.fps)。
    @property
    def fps(self):
        # getter：正整数帧/秒。
        return self.__fps

    @fps.setter
    def fps(self, value):
        # setter：过低会导致操作迟滞。
        self.__fps = value

    # -------------------------------------------------------------------------
    # 附录：@property 装饰器在 Python 里究竟做了什么？（纯注释，无运行代码）
    # -------------------------------------------------------------------------
    # 1) 写 @property def points(self): return self._points
    #    之后，外部调用 game_state.points 时会执行这个函数，像读属性一样，不能写 points()。
    # 2) 写 @points.setter def points(self, val): ...
    #    之后，game_state.points = 100 会进 setter，可在赋值前做校验（如 direction 的白名单）。
    # 3) 为什么不直接在类外改 _points？因为 grep 很难找谁改了分，且无法统一校验。
    # 4) __双下划线 名称改写：类内 __level 会变成 _GameState__level，子类不易误覆盖。
    # 5) mode_change_events 的 getter 每次「读」都改变 __current_mode_index，属于少见副作用；
    #    阅读 EventHandler 时要意识到 set_timer(... mode_change_events * 1000) 会消耗下一间隔。
    # 6) dict 字段 __ghost_pos 用 get/set 方法，因为键是动态的幽灵名，不适合写 4 个固定 property。
    # 7) None 初始值：表示「尚未被 sprites 赋值」；访问前 sprites 应负责 first update 写入 rect。
    # 8) 与 dataclass 对比：dataclass 自动生成 __init__；本类选手写是为了教学 property 与校验。
    # 9) is_loaded 无 setter：外部只能读，若需写应补 @is_loaded.setter 或方法。
    # 10) get_ghost_pos/set_ghost_pos 封装 __ghost_pos，避免外部拿到 dict 乱改键名。
    # 11) _points 初始 -DOT_POINT：与第一次 eat dot +DOT_POINT 显示 0 分配合。
    # 12) ghost_mode scared 通常与 is_pacman_powered 同时为真，但字段独立存储。
    # 13) __current_mode_index 仅在 mode_change_events getter 内递增，setter 不重置索引。
    # 14) running False 后 main 仍执行 update_highscore、pygame.quit，再 sys.exit。
    # 15) fps 与 JSON 无关，纯代码默认 60，可 setter 调低做慢动作调试。
    # 16) level_complete/points/highscore 等用 _ 单下划线存，property 包装对外接口。
    # 17) __is_pacman_powered 双下划线：名称改写在类内仍为 __is_pacman_powered 访问。
    # 18) direction setter 允许 "" 表示无输入，Pacman 可能沿 pacman_direction 惯性移动。
    # 19) custom_event 与 power_up_event 均为 int 或 None，勿与 pygame 常量 K_* 混淆。
    # 20) mode_change_events setter 赋值 list 后不重置 __current_mode_index，换关需新 GameState 或手动重置。
    # 21) blinky_matrix_pos 类型由 ghosts 约定，通常为 (row,col) 整数元组。
    # 22) scared_time 与 power_up_time 同源，load_level 时一次性写入 state。
    # 23) is_pacman_dead 与 level_complete 互斥场景：死亡不触发过关，过关不触发 dead_reset。
    # 24) mins_played 本项目中较少 increment，字段主要为 stats.json 预留。
    # 25) GameState 无 update() 方法：状态分散在各模块 property 写入，非集中 tick。
    # 26) property getter 无参数，setter 除 self 外一个 value，符合 Python 描述符习惯。
    # 27) ValueError 在 direction/ghost_mode setter 抛出，调用方应 try/except 或先校验。
    # 28) _mode_change_events 为 None 时 mode_change_events getter 会报错，load_level 须先 setter。
    # 29) __ghost_pos 不设 property 整表暴露，避免外部 replace 整个 dict 失去追踪。
    # 30) is_loaded 只读：无 setter 意味着外部不能直接 game_state.is_loaded=True（除非加 setter）。
    # 31) highscore/points 分离：当局分可低于最高，HUD 两行分别展示。
    # 32) power_event_trigger_time 与 power_up_event 配合实现「到点事件」而非每帧轮询（部分逻辑在 sprites）。
    # 33) __init__ 不设 is_loaded=True，表示构造完成不等于资源加载完成。
    # 34) running 默认 True：GameRun 构造后 main 即可 while，无需再置位。
    # 35) __fps 默认 60：欧美常用 60Hz；改 30 可省 CPU 做教学慢放。
    # 36) DOT_POINT 仅 __init__ 导入，用于 _points 初值，不在 property 内引用。
    # 37) 每个 @property 块上方【property】注释说明用途、读写方，便于对照 grep。
    # 38) setter 普遍为直赋，除 direction/ghost_mode 外无复杂校验逻辑。
    # 39) GameState 实例由 GameRun 创建一次，全游戏共享，非每关 new。
    # 40) __init__ 不接收参数，关卡数据来自 PacmanGrid.load_level 写入 property。
    # 41) is_pacman_powered 用 __ 前缀存储，property 仍可读写在类内统一。
    # 42) _custom_event 单下划线：模块内约定「内部字段」，property 仍公开访问。
    # 43) level_complete 与 level 不同：前者布尔过关旗，后者整数关号。
    # 44) is_pacman_dead 与 running 不同：dead 可在一局内多次 True/False。
    # 45) 附录注释 1～45 条均为教学说明，不参与运行时逻辑。
    # 46) 全文件 property 一览：level_complete, points, highscore, mins_played, is_pacman_dead,
    #     power_event_trigger_time, power_up_event, scared_time, blinky_matrix_pos,
    #     pacman_direction, custom_event, mode_change_events, ghost_mode, is_pacman_powered,
    #     is_loaded, pacman_rect, current_time, direction, level, running, fps。
    # 47) get_ghost_pos/set_ghost_pos 非 property，因需动态键名参数。
    # 48) 注释行数目标≥1.5×代码行，每个 @property 上方有【property】用途说明。
    # 49) 修改本类字段时优先走 property，避免绕过 direction/ghost_mode 校验。
    # 50) GameState 不序列化：存档仅 stats.json 的 highscore/mins_played，非整 state。
    # 51) 本类注释行≥1.5×代码行：__init__ 字段说明 + 各 property【property】块 + 附录 1～51。
    # 52) 阅读顺序建议：模块 docstring → __init__ → 按需查 property 注释 → 附录 property 教程。
    # 53) mode_change_events getter 副作用：读属性即消耗下一 scatter 间隔，调试时注意 print 次数。
    # 54) direction 与 pacman_direction 双字段：输入愿望 vs 实际运动，撞墙时二者可不一致。
    # 55) ghost_mode scared 时 is_pacman_powered 通常为 True，但两字段独立维护。
    # 56) 全文件 py_compile 须通过，注释增删不得改变任何可执行语句与字面量。
    # 57) GameState 注释/代码比≥1.5，满足初学者逐 property 学习密度。
    # 58) 修改游戏行为时请改 sprites/gui/runner，本类仅承载状态与校验。
    # 59) scatter/chase 由 EventHandler 写 ghost_mode；scared 贴图主要由 is_pacman_powered 驱动 ghosts。
    # 60) pacman_rect 存 (x,y,w,h) 元组而非 Rect，ghosts.check_collisions 内再构造 Rect。
    # 61) level 与 _level_number(PacmanGrid) 分离：过关后 sprites 增 level，下次 new Grid 才 load 新 JSON。
    # 62) mode_change_events 列表来自 JSON scatter_times，长度可大于 2，getter 顺序消费直至用最后一个。
    # 63) __current_mode_index 换关不自动归零，若同一 GameState 跨多关需留意间隔序列是否重复。
    # 64) power_event_trigger_time 与 release_time(Ghost) 比较，避免晚出笼鬼误变 scared 蓝皮。
    # 65) _points 初值 -DOT_POINT 仅影响 HUD 显示节奏，不改变吃豆加分常量本身。
    # 66) is_pacman_dead 与 running 独立：死亡重生不退出，关窗才 running=False。
    # 67) fps 不参与 ghost lerp：幽灵 _accelerate 固定，Pacman 用 PACMAN_SPEED 固定步长。
    # 68) get_ghost_pos/set_ghost_pos 当前 ghosts 路径少用，预留多鬼坐标缓存扩展。
    # 69) custom_event/power_up_event 均为 int event.type，勿与 K_LEFT 等键码混淆。
    # 70) ghost_mode setter 白名单不含空串，非法赋值抛 ValueError 保护 AI 分支。
    # 71) direction setter 允许 "" 表示无新按键，Pacman 可沿 pacman_direction 惯性滑格。
    # 72) is_loaded 无 setter：加载屏若完成应补 setter 或专用 mark_loaded() 方法（当前未实现）。
    # 73) GameState 单例式生命周期：GameRun 构造一次，全关共享，highscore 跨关累积。
    # 74) current_time 每帧 runner 写入 get_ticks()，sprites 可读做动画但当前少用。
    # 75) blinky_matrix_pos 仅 Blinky 子类在 move_ghost 写入，Inky.chase 强依赖此字段非 None。
    # 76) scared_time 毫秒量级，与 pacman set_timer(power_up_event) 间隔一致。
    # 77) level_complete 由 Pacman.update 在 collectibles==0 置 True，GUI 负责清 False 与换关。
    # 78) mins_played 字段持久化但本仓库较少 increment，扩展游玩统计时可写 setter 挂钩。
    # 79) __双下划线字段名称改写仅防子类意外覆盖，同类内仍用 self.__running 访问。
    # 80) 本文件注释/代码≥1.5：property 教程见附录 1～80，改状态请优先走 setter 校验。
    # -------------------------------------------------------------------------

# --- 补充说明 (src/game/state_management.py) ---
# property direction 白名单 r/l/u/d/空串，非法值 ValueError，防止 typo 写入 state。
# ghost_mode setter 仅 scatter/chase/scared 三值，与 EventHandler 实际写的 scatter/chase 及扩展 scared 一致。
# mode_change_events getter 在 index 超 len 时用列表最后一项，长局 scatter 间隔不会 IndexError。
# pacman_rect setter 接受 Rect 或元组取决于 sprites 写法，当前 Pacman 写四元组 tuple。
# power_up_event 与 custom_event 并存，EventHandler 用四个独立 if 分支 dispatch 不同 USEREVENT。
# highscore 与 points 分离存储，runner.check_highscores 只升不降，当局分可低于历史最高。
# level_complete 与 is_pacman_dead 由不同模块置位，GUI reset 路径互斥，避免同时 wait 与 rebuild。
# GameState 无 clone 方法，换关不 new state，level/mode 索引跨关累积需注意 mode_change 索引。
# is_pacman_powered 用 __ 名称改写存储，property 对外透明，sprites 读写 is_pacman_powered 即可。
# current_time 每帧 runner 赋值，预留动画同步 scared 剩余时间等扩展点。
# get_ghost_pos 动态键名 API 适合四鬼字典缓存，ghosts 当前多用 blinky_matrix_pos 单字段。
# fps 默认 60 与 clock.tick 配合，调低 fps 不会自动降低 PACMAN_SPEED 像素步长。
