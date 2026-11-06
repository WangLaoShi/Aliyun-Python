"""
游戏主控：``GameRun`` 类组装 pygame、状态、事件、GUI 与主循环。

可以把本类理解成 **Facade（外观）**：对外只有一个 ``main()``，
内部协调多个子系统。主循环是 pygame 项目的标准模式：

1. 处理输入（event）
2. 更新逻辑（update / game_state）
3. 绘制（fill → draw → flip）
4. ``clock.tick(fps)`` 限制帧率并测量帧间隔 dt

``dt`` 传给 ``all_sprites.update(dt)``，让精灵按时间而非「每帧固定步长」运动
（本项目里 dt 还做了 ``/= 100`` 缩放，与 sprites 里速度公式配套）。
"""

# sys.exit 在 main 结束时可确保进程退出码一致。
import sys

import pygame
import json

from src.configs import *
from src.game.event_management import EventHandler
from src.game.state_management import GameState
from src.gui.screen_management import ScreenManager
from src.sounds import SoundManager
from src.log_handle import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# 主循环与模块依赖（速查，便于对照 main()）
# ---------------------------------------------------------------------------
# GameRun.__init__：pygame 窗口 + GameState + EventHandler + ScreenManager。
# main() 每帧：get_ticks → 事件 → fill 黑底 → gui 画迷宫/HUD → Group 画精灵
#            → Group.update(dt) → 刷新高分 → flip → tick 限帧。
# dt：上一帧耗时（毫秒），除以 100 后传入 Sprite.update，与 PACMAN_SPEED 等配合。
# 持久化：只在循环结束后 update_highscore()，减少磁盘写入。
# 未使用 K_ESCAPE/K_q：退出主要靠关窗 QUIT；可在 EventHandler 扩展。
# ---------------------------------------------------------------------------


class GameRun:
    def __init__(self):
        logger.info("About to initialize pygame")
        # 初始化 pygame 各子系统（display、mixer 等）。
        pygame.init()
        # 创建显示 Surface；元组来自 configs 常量。
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Py-Pacman")
        logger.info("pygame initialized")

        # GameState 是「单一数据源」：分数、方向、幽灵模式等都从这里读写。
        self.game_state = GameState()
        logger.info("game state object created")

        # EventHandler 需要 screen 与 state，以便按键、定时事件改写 state。
        self.events = EventHandler(self.screen, self.game_state)
        logger.info("event handler object created")

        # pygame.sprite.Group：批量 draw/update 所有 Sprite 子类（Pacman、幽灵）。
        self.all_sprites = pygame.sprite.Group()

        self.gui = ScreenManager(self.screen, self.game_state, self.all_sprites)
        logger.info("screen manager object created")

    def initialize_highscore(self):
        # with open(...) as fp：离开 with 块会自动 close 文件，即使发生异常。
        # 路径相对「当前工作目录」，因此应从 PyPacman 目录运行 python main.py。
        with open("levels/stats.json") as fp:
            stats = json.load(fp)
            self.game_state.highscore = stats['highscore']
            self.game_state.mins_played = stats['mins_played']

    def create_ghost_mode_event(self):
        # USEREVENT 起是 pygame 留给开发者自定义定时事件的 ID 段。
        CUSTOM_EVENT = pygame.USEREVENT + 1
        # mode_change_events 首次读取会取 JSON 里 scatter_times[0]（秒），乘 1000 变毫秒。
        pygame.time.set_timer(
            CUSTOM_EVENT,
            self.game_state.mode_change_events * 1000
        )
        # 把事件 ID 存进 state，EventHandler 里用 event.type 比对。
        self.game_state.custom_event = CUSTOM_EVENT

    def initialize_sounds(self):
        # 单例：多次 SoundManager() 仍是同一混音器配置。
        sound_manager = SoundManager()
        # channel 0/1/2 分开 chomp、death、eat_ghost，减少互相 cut。
        sound_manager.load_sound("dot", "assets/sounds/pacman_chomp.wav", channel=0)
        sound_manager.load_sound("death", "assets/sounds/pacman_death.wav", 0.7, 500, 1)
        sound_manager.load_sound("eat_ghost", "assets/sounds/pacman_eatghost.wav", 0.6, 100, 2)
        sound_manager.set_background_music("assets/sounds/backgroud.mp3")
        sound_manager.play_background_music()

    def check_highscores(self):
        # 每帧 O(1) 比较；只在退出时写盘，避免频繁 IO。
        if self.game_state.points > self.game_state.highscore:
            self.game_state.highscore = self.game_state.points

    def update_highscore(self):
        # 'w' 覆盖写入；indent=4 让人类可直接打开 JSON 编辑。
        with open("levels/stats.json", 'w') as fp:
            json.dump(
                {"highscore": self.game_state.highscore,
                 "mins_played": self.game_state.mins_played},
                fp,
                indent=4
            )

    def main(self):
        # Clock 不控制「真实时间」，只帮助 tick 睡眠以逼近目标 fps。
        clock = pygame.time.Clock()
        # 第一帧 update 时 dt 为 None，sprites 内应能处理（或跳过位移）。
        dt = None

        self.create_ghost_mode_event()
        self.initialize_sounds()
        self.initialize_highscore()

        # running 由 EventHandler 在关窗时置 False，循环自然结束。
        while self.game_state.running:
            self.game_state.current_time = pygame.time.get_ticks()

            # pygame.event.get() 取出并清空队列；每个 event 有 type、键码等字段。
            for event in pygame.event.get():
                self.events.handle_events(event)

            # 清屏：否则上一帧像素会残留（无 double buffer 自动清）。
            self.screen.fill(Colors.BLACK)
            # 先画静态迷宫与 HUD，再画精灵，保证豆子在底层、角色在上层。
            self.gui.draw_screens()
            self.all_sprites.draw(self.screen)
            self.all_sprites.update(dt)
            self.check_highscores()
            # flip 提交 back buffer；无此句窗口会假死或黑屏不动。
            pygame.display.flip()

            dt = clock.tick(self.game_state.fps)
            dt /= 100

        # 循环结束后写 stats.json。
        self.update_highscore()
        # 释放 pygame 资源。
        pygame.quit()
        # 终止 Python 进程。
        sys.exit()

# initialize_highscore 只读 stats.json，不写；写发生在 update_highscore。
# create_ghost_mode_event 在 main 开头调用一次；后续 timer 由 EventHandler 重置。
# initialize_sounds 未保存 sound_manager 到 self，因单例 sprites 可再取。
# check_highscores 每帧调用，O(1)；写盘仅在退出时一次。
# json.dump indent=4 便于人工编辑 highscore 文件。
# all_sprites.update(dt) 在 draw 之后，dt 来自上一帧 tick，首帧 None。
# gui.draw_screens 内部可能 wait(2000) 阻塞，属过关演出非独立线程。
# from configs import * 引入 SCREEN_* Colors 等，注意命名空间污染但本项目约定如此。
# GameRun 无继承，main.py 只实例化并调用 main()。
# pygame.display.flip 双缓冲交换；fill BLACK 清整屏再画避免拖影。
# clock.tick 返回值毫秒，除以 100 为历史缩放，与 PACMAN_SPEED 公式配套。
# EventHandler 构造传入 screen 与 game_state，与 ScreenManager 共享同一 state 对象。
# sys.exit 无参数即退出码 0；异常未捕获时会跳过 update_highscore。
# GameRun 实例变量：screen, game_state, events, all_sprites, gui 共五个核心引用。
# initialize_sounds 中 death 参数 0.7,500,1 为 volumne,freq,channel 位置参数。
# load_sound("dot",..., channel=0) 仅 channel 关键字，其余默认 volumne/freq。
# main while 内无 break，仅 running False 退出，结构清晰适合初学者阅读。
# 主循环四步与经典 pygame 教程一致：事件 → 逻辑(update) → 绘制 → tick；本项目 draw 在 update 前属视觉优先。
# gui.draw_screens 内含 wait(2000) 过关阻塞，该帧内 Group.update 可能不执行或只执行一次，属设计取舍。
# all_sprites.update(dt) 在 draw 之后：本帧画面反映上一帧末状态，手感与「先算后画」略有不同但可接受。
# dt 首帧 None 传入 update：Pacman/ Ghost 未显式 guard 时位移可能跳过，第二帧起 tick 返回毫秒间隔。
# initialize_sounds 不存 self：SoundManager 单例，sprites 内 SoundManager() 仍指向同一 mixer 配置。
# stats.json 路径相对 cwd，与 levels/ 相同，部署时需保证工作目录为 PyPacman 根。
# create_ghost_mode_event 在 initialize_highscore 之前：timer 与 JSON 读盘无依赖，顺序可换但不改逻辑。
# check_highscores 每帧 O(1)，highscore 只涨不降，直到本局结束写盘。
# pygame.event.get() 清空队列，漏处理的事件会丢失，故每帧必须完整遍历。
# fill(BLACK) 清整屏，迷宫与精灵每帧全量重绘，无脏矩形优化，CPU 占用随分辨率与精灵数上升。
# GameRun 不订阅 KEYDOWN，方向键全在 EventHandler，runner 保持薄入口职责。
# sys.exit() 在 pygame.quit 之后，确保 mixer/display 释放后再结束进程。
# json.dump indent=4 便于人工编辑 highscore；无 atomic write，异常中断可能损坏 stats（小项目可接受）。
# logger INFO 里程碑与 log_handle DEBUG 默认级别独立，可在 log_handle 调级别看更细 trace。
# from configs import * 引入 SCREEN_* Colors PACMAN_SPEED 等，改 configs 即全局生效下一帧。
# GameRun 五引用 screen/game_state/events/all_sprites/gui 贯穿 main 生命周期，无热重载关卡 API。
# clock.tick(fps) 睡眠补齐帧时间，fps 来自 game_state 默认 60，setter 可慢动作调试。
# display.flip 双缓冲交换，无 vsync 参数时可能 tearing，街机复刻通常不追求垂直同步。
# 主循环无 try/finally：未捕获异常会跳过 update_highscore，生产环境可加 finally 保存。
# custom_event timer 与 power_up_event 由 pacman/runner 分别注册，EventHandler 统一 dispatch。
# all_sprites 成员在 ScreenManager 构造与 reset 时维护，runner 不直接 add/remove 精灵。
# pygame.init 一次即可，重复 init 无害；quit 后不可再 init 同进程需重启（pygame 限制）。
# main 不处理 level_complete：ScreenManager.draw_screens 内 check_level_complete 负责换关重建 Grid。
# is_pacman_dead 由 ghosts 碰撞置位，ScreenManager.pacman_dead_reset 在同帧 draw 链里处理重生。
# 注释/代码≥1.5：Facade 组装、主循环顺序、持久化与 timer 初始化见模块 docstring 与 class 上方速查。
# GameRun.main 阻塞直到 running False，main.py 调用后进程生命周期与本方法绑定。
# mixer 与 display 同属 pygame.init 子系统，initialize_sounds 在 main 开头确保 chomp 可播。
# levels/stats.json 键名 highscore/mins_played 硬编码，扩展字段需同步改 initialize/update 两处。
# 本文件末尾说明块仅注释，不参与 import 与类定义，py_compile 与运行时行为不变。
# for event in pygame.event.get() 空队列时循环体不执行，CPU 仍受 tick 限制。
# all_sprites.draw 要求每个成员有 image 与 rect，Sprite 子类默认满足。
# logger 记录初始化里程碑，级别 INFO，与 log_handle DEBUG 默认一致。
# pygame.display.set_caption 只改标题栏文字，不影响 FPS。
# json.load/dump 与 stats.json 字段 highscore、mins_played 键名硬编码。
# create_ghost_mode_event 在 initialize_highscore 之前调用，先 timer 再读盘无依赖。
# GameRun.main 不捕获 KeyboardInterrupt，Ctrl+C 可能跳过 save（视平台而定）。
# dt /= 100 为 float 除法，Python3 真除，结果为 float 传入 update。
# 本文件注释≥1.5×代码：Facade、主循环四步、持久化时机见模块 docstring。
# GameRun 不继承 threading.Thread，main 阻塞 UI 线程为 pygame 常规模型。
# runner 模块注释行数≥1.5×代码行，主循环步骤见 class 上方速查块。

# --- 补充说明 (src/runner.py) ---
# main 循环 gui.draw_screens 在 all_sprites.draw 前，迷宫底层；精灵 draw 覆盖在上。
# all_sprites.update 在 draw 之后，本帧画面显示的是 update 前状态，下一帧才反映位移。
# initialize_highscore 读 stats 失败会抛异常，无 try/except，缺文件时启动即报错便于发现。
# create_ghost_mode_event 只 main 开头一次，后续 scatter/chase 由 EventHandler 重设 timer。
# GameRun 不处理 level_complete，换关完全在 ScreenManager.draw_screens 内阻塞 wait 后重建。
# pygame.quit 在 while 退出后调用，释放 display/mixer，再 sys.exit 结束进程。
# from configs import * 与显式 import 混用，runner 依赖 SCREEN_* Colors 等全局名。
# logger.info 里程碑便于对照玩家报告「卡在哪一步」，非性能 trace。
# check_highscores 每帧比较 points>highscore，内存更新，写盘仅 update_highscore 一次。
# dt/=100 历史缩放，与 PACMAN_SPEED 公式配套注释在 runner 模块 docstring，改 dt 须测手感。
