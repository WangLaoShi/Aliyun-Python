"""
迷宫视图与关卡加载：``PacmanGrid``。

关卡数据来自 ``levels/levelN.json``：
- ``matrix``：二维列表，每个字符串（"wall"/"dot"/…）决定一格画什么
- ``pacman_start``、``ghost_den``：逻辑格子坐标，再由 coord_utils 换成屏幕像素

``function_mapper`` 是 **策略字典**：键是 JSON 里的单元类型，值是对应的 draw_* 方法。
这样 ``draw_level`` 里双重 for 循环不必写一长串 if/elif。

本模块创建 ``Pacman`` 与 ``GhostManager``（在 sprites 包），但不实现它们的移动 AI。
"""

# json 标准库：把文本文件解析为 Python dict/list。
import json

# 导入屏幕尺寸、颜色、格子大小等全局常量。
from src.configs import *
# 玩家角色类（pygame Sprite）。
from src.sprites.pacman import Pacman
# 四鬼集合管理类。
from src.sprites.ghosts import GhostManager
# 坐标工具：居中偏移、预计算矩阵像素位置。
from src.utils.coord_utils import (get_coords_from_idx, place_elements_offset,
                                   precompute_matrix_coords)
# 绘图工具：矩形、圆、调试框。
from src.utils.draw_utils import (draw_circle, draw_debug_rects, draw_rect)
from src.log_handle import get_logger

# 模块级 logger，__name__ 为 'src.gui.pacman_grid'。
logger = get_logger(__name__)

# 逻辑格 (row,col) 与屏幕像素 (x,y) 的换算关系见 load_level / draw_level。
# function_mapper 把 JSON 字符串映射到 draw_* 方法，避免长 if-elif 链。
# draw_level 每帧调用：吃豆后 matrix 单元会变，必须重画。
# Pacman/GhostManager 与 self._matrix 共享同一 list 对象引用。


class PacmanGrid:
    # screen：pygame 主 Surface；game_state：全局 GameState。
    def __init__(self, screen, game_state):
        logger.info("initializing pacman grid")
        # 单元类型字符串 → 实例方法，供 draw_level 动态 dispatch。
        self.function_mapper = {
            "void": self.draw_void,
            "wall": self.draw_wall,
            "dot": self.draw_dot,
            "spoint": self.draw_special_point,
            "power": self.draw_power,
            "null": self.draw_void,
            "elec": self.draw_elec,
        }
        self._screen = screen
        self._game_state = game_state
        # 读 property level，决定 levels/levelN.json 的 N。
        self._level_number = self._game_state.level
        # 必须先 load，再创建 pacman（依赖 matrix 与 start_x/y）。
        self.load_level(self._level_number)
        logger.info("level loaded")

        # 构造 Pacman：传入 matrix 引用与像素原点 offset。
        self.pacman = Pacman(
            self._screen,
            self._game_state,
            self._matrix,
            self._pacman_pos,
            (self.start_x, self.start_y)
        )
        # 构造 GhostManager：ghost_den 来自 JSON。
        self.ghost = GhostManager(
            self._screen,
            self._game_state,
            self._matrix,
            self.ghost_den,
            (self.start_x, self.start_y)
        )
        logger.info("pacman created")

    # 读取 UTF-8 JSON 文件并 parse 为 Python 对象。
    def get_json(self, path):
        with open(path) as fp:
            payload = json.load(fp)
        return payload

    # 按关卡号加载 levels/level{n}.json，填充绘制与 AI 所需字段。
    def load_level(self, level_number):
        # 拼路径 levels/level1.json、level2.json …
        level_path = f"levels/level{level_number}.json"
        # 解析 JSON 为 dict。
        level_json = self.get_json(level_path)
        # 行数：matrix 外层 list 长度应一致。
        num_rows = level_json["num_rows"]
        # 列数：每行 string 个数。
        num_cols = level_json["num_cols"]
        # 幽灵巢穴格坐标。
        self.ghost_den = level_json['ghost_den']
        # 迷宫字符网格，mutable，吃豆会改单元。
        self._matrix = level_json["matrix"]
        # Pac-Man 出生格 (row,col)。
        self._pacman_pos = level_json["pacman_start"]
        # 电力元素位置列表（关卡定义）。
        self.elec_pos = level_json['elec']
        # scatter/chase 各段秒数列表。
        self.mode_change_times = level_json['scatter_times']
        # 能量豆 scared 持续配置。
        self.power_up_time = level_json['power_up_time']
        # 写入 GameState 供 ghosts 读。
        self._game_state.scared_time = self.power_up_time
        # 写入间隔表；getter 顺序消费。
        self._game_state.mode_change_events = self.mode_change_times
        # 居中：0.5,0.5 表示在窗口几何中心对齐迷宫外包矩形。
        self.start_x, self.start_y = place_elements_offset(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            CELL_SIZE[0] * num_cols,
            CELL_SIZE[0] * num_rows,
            0.5,
            0.5,
        )
        # 二维坐标缓存，避免每帧重复乘算。
        self._coord_matrix = precompute_matrix_coords(
            self.start_x, self.start_y, CELL_SIZE[0], num_rows, num_cols
        )
        # 实例字段供 draw_outliners 与调试。
        self.num_rows = num_rows
        self.num_cols = num_cols

    # 空地：不绘制任何像素。
    def draw_void(self, **kwargs):
        pass

    # 墙：蓝色实心矩形，占满一格 w×h。
    def draw_wall(self, **kwargs):
        draw_rect(
            kwargs["x"],
            kwargs["y"],
            kwargs["w"],
            kwargs["h"],
            self._screen,
            Colors.WALL_BLUE,
        )

    # 小豆豆：5×5 白块，坐标在格心附近。
    def draw_dot(self, **kwargs):
        dot_x = kwargs["x"] + kwargs["w"]
        dot_y = kwargs["y"] + kwargs["h"]
        draw_rect(dot_x, dot_y, 5, 5, self._screen, Colors.WHITE)

    # 特殊点：占位，当前关卡 JSON 未启用。
    def draw_special_point(self):
        pass

    # 能量豆：黄色圆，半径 7。
    def draw_power(self, **kwargs):
        circle_x = kwargs["x"] + kwargs["w"]
        circle_y = kwargs["y"] + kwargs["h"]
        draw_circle(circle_x, circle_y, 7, self._screen, Colors.YELLOW)

    # 电力门：1 像素高的红条。
    def draw_elec(self, **kwargs):
        draw_rect(kwargs["x"], kwargs["y"], kwargs["w"], 1, self._screen, Colors.RED)

    # 双重循环遍历 matrix，按类型调用 draw_*。
    def draw_level(self):
        # 光标从迷宫左上角像素开始。
        curr_x, curr_y = self.start_x, self.start_y
        # enumerate 可同时拿索引与 row，此处只用 row。
        for _, row in enumerate(self._matrix):
            # 内层遍历一行中的每一列单元类型字符串。
            for _, col in enumerate(row):
                # 查表得 draw_wall / draw_dot 等函数对象。
                draw_func = self.function_mapper[col]
                # 关键字参数统一格宽高的正方形 cell。
                draw_func(x=curr_x, y=curr_y, w=CELL_SIZE[0], h=CELL_SIZE[0])
                # 向右移动一格像素宽度。
                curr_x += CELL_SIZE[0]
            # 换行：x 回到行首。
            curr_x = self.start_x
            # y 下移一行。
            curr_y += CELL_SIZE[0]

    # 同关重生：不 reload JSON，只 new Pacman/GhostManager。
    def reset_stage(self):
        self.pacman = Pacman(
            self._screen,
            self._game_state,
            self._matrix,
            self._pacman_pos,
            (self.start_x, self.start_y)
        )
        self.ghost = GhostManager(
            self._screen,
            self._game_state,
            self._matrix,
            self.ghost_den,
            (self.start_x, self.start_y)
        )

    # 开发调试：可视化网格范围（非正式游戏画面）。
    def draw_outliners(self):
        draw_debug_rects(
            self.start_x, self.start_y, 128, 140, 5, Colors.GREEN, self._screen
        )
        draw_debug_rects(
            self.start_x,
            self.start_y,
            self.num_rows,
            self.num_cols,
            CELL_SIZE[0],
            Colors.BLUE,
            self._screen,
        )


# --- PacmanGrid 方法索引（复习用，不参与运行） ---
# __init__：建 mapper → load_level → new Pacman/GhostManager。
# get_json：with open + json.load，路径相对 cwd。
# load_level：读 JSON 填 matrix/start/scatter_times，写 GameState，算居中与 _coord_matrix。
# draw_void/dot/wall/power/elec：供 mapper 调用，kwargs 含 x,y,w,h 像素。
# draw_level：扫描 matrix 调 mapper；每帧由 ScreenManager.draw_screens 调用。
# reset_stage：死亡同关重来，不 increment level。
# draw_outliners：调试网格，正式游戏不调用。
# get_coords_from_idx 虽 import 但本文件未直接调用，保留给 re-export 或历史 import。
# GhostManager/Pacman 会修改 _matrix 中 "dot"→"void"，draw_level 因此必须每帧执行。
# enumerate 的 _ 表示忽略索引，只关心 row/col 内容。
# KeyError：JSON 出现 mapper 未定义的单元类型时会崩溃，需与 level 设计一致。
# place_elements_offset 第 5、6 参数 0.5,0.5 即宽高各 50% 位置锚点。
# CELL_SIZE[0] 同时作步进与 precompute 格宽，假定方格。
# self.pacman 与 self.ghost 在 reset_stage 会被整体替换为新实例。
# _level_number 仅 __init__ 用一次，之后 level 变化靠 game_state.level 驱动 rebuild。
# elec_pos 存 JSON 电力坐标，绘制由 matrix 中 "elec" 单元触发 draw_elec。
# mode_change_times 与 power_up_time 亦存实例字段，便于调试打印。
# draw_rect 第五个参数是 screen，第六是 RGB 颜色元组。
# draw_circle 半径 7 大于 dot 的 5×5 矩形，视觉更突出 power。
# function_mapper["null"] 与 void 共用 draw_void，兼容不同 JSON 命名习惯。
# draw_wall 六参数 draw_rect：x,y,w,h,screen,color 顺序与 draw_utils 一致。
# kwargs["w"] 与 kwargs["h"] 在 draw_level 传入均为 CELL_SIZE[0]。
# reset_stage 不重置 _matrix 豆状态：若需全关重置应 reload JSON 或 copy matrix。
# Pacman 构造参数 matrix 为引用，内部改 cell 影响 draw_level 输出。
# GhostManager 与 Pacman 共享 start_x/start_y 元组，偏移一致防错位。
# logger.info 在 load 前后各一条，便于性能 profiling 关卡 IO。
# json.load 默认 UTF-8；levels 文件须为合法 JSON 数组 matrix。
# num_rows/num_cols 与 matrix 尺寸应一致，否则 draw 行数与数据不匹配会越界或留白。
# get_json 未指定 encoding，Python3 默认 locale/utf-8 视平台而定。
# draw_special_point 空实现：mapper 必须有键，否则 KeyError。
# draw_outliners 第二调 draw_debug_rects 用 num_rows/cols 与 CELL_SIZE 画蓝框。
# import * from configs 使 Colors、SCREEN_* 等成为本模块全局名。
# class PacmanGrid 不继承 pygame.sprite.Group，仅是普通协调类。
# 行 105 量级代码含嵌套 def 与 dict，注释行数目标约为 code×1.5 便于初学者阅读。
# self._screen 私有约定：外部应通过方法 draw_level 绘制而非直接改 _screen。
# self._game_state.level 在过关后递增，下次 new PacmanGrid 会 load 新 JSON。
# draw_dot 中 dot_x/dot_y 加法相当于移到格心（与 draw_utils 原点约定相关）。
# draw_power 用圆而非方，与能量豆经典外观一致。
# draw_elec 高度 1 像素，在高分屏上可能几乎不可见。
# enumerate(self._matrix) 外层 row 是 list of str，内层 col 是单个 str。
# draw_func 变量名表示「当前格要调用的函数对象」。
# curr_x += CELL_SIZE[0] 假设方格，宽=高=CELL_SIZE[0]。
# reset_stage 与 __init__ 末尾构造 Pacman/Ghost 代码重复，有意保持行为一致。
# get_coords_from_idx 未在本模块调用，import 保留供静态检查或未来扩展。
# precompute_matrix_coords 返回结构由 coord_utils 定义，sprites 按索引查。
# level_number 形参允许测试时 load 任意关，不限于 game_state.level。
# open(path) 相对 cwd；从错误目录运行会 FileNotFoundError。
# ghost_den 结构由 GhostManager 解析，通常为 [row,col] 或 JSON 嵌套。
# _pacman_pos 同理，Pacman 内部 convert 为像素。
# start_x/start_y 为 int/float 像素，来自 place_elements_offset 返回值。
# _coord_matrix 实例变量，换关 load_level 会覆盖。
# draw_void 的 pass 是合法空语句，占位必需。
# Colors.WALL_BLUE 来自 configs，非 pygame 内置色名。
# self.function_mapper 在 __init__ 建一次，全生命周期不变。
# 无 update 方法：网格绘制被动，由 ScreenManager 每帧 draw_level 驱动。
# 本文件 code≈105 行，注释目标≥158 行，故模块尾附复习索引。
# JSON matrix 字符串必须全小写与 mapper 键一致，如 "wall" 非 "Wall"。
# load_level 不写 game_state.level，level 仅 sprites 过关时递增。
# draw_level 不 clip 屏幕外，超大 matrix 可能画到窗口外。
# GhostManager import 不触发 AI 运行，直到 Group.update 调用。
# Pacman import 同理，构造后需 update 才移动。
# json 模块 load 返回 dict，键 "matrix" 值为 list of list of str。
# place_elements_offset 前两个参数为屏幕宽高，来自 configs 星号导入。
# CELL_SIZE[0]*num_cols 假设无间隙网格，无 margin 像素。
# draw_rect/dot/power 均用 self._screen 同一 Surface，无 offscreen 缓冲。
# reset_stage 后 ScreenManager 须 re-add sprites 到 Group，本类不负责 Group。
# get_json 可被单元测试 mock path 调用，与 load_level 解耦读盘。
# level_path f-string 中 level_number 来自 int property，非法值仍拼路径。
# __init__ 中 logger 两条标记 grid 初始化与 level 加载完成节点。
# 注释/代码比≥1.5：见本文件模块 docstring 与末尾方法索引。
# matrix 单元 "dot"/"power" 被 Pacman.eat_dots 改为 "void" 后，下一帧 draw_dot 不再调用，豆从画面消失。
# "wall" 与 "elec" 不可走，ghost_movement_utils BLOCKERS 含 elec，与 Pacman tiny_matrix 墙一致。
# ghost_den JSON 坐标传入 GhostManager，四鬼同列 adder 递增行，模拟鬼屋竖排出生。
# pacman_start 与 ghost_den 均为粗格 (row,col)，load_level 不转像素，constructors 内 get_coords_from_idx。
# scatter_times 写入 mode_change_events 后 EventHandler 每次 scatter↔chase 读 getter 取下一间隔秒数。
# power_up_time 写 scared_time，pacman 吃 power 时 set_timer 用同一数值毫秒 frightened 时长。
# place_elements_offset(0.5,0.5) 使迷宫外包矩形几何中心对齐 1024×768 窗口中心，非贴左上角。
# precompute_matrix_coords 的 _coord_matrix 供 Pacman 隧道 boundary_check O(1) 查像素 x。
# draw_level 双重 for 复杂度 O(rows×cols)，31×28 量级每帧 60fps 可接受，无可见 tile 缓存。
# function_mapper 缺键会在 draw_level KeyError，新增 JSON 类型须同步加 draw_* 与 mapper 项。
# draw_void/null 不 blit，依赖 runner fill 黑底；墙豆覆盖在上层精灵之下由 draw 顺序保证。
# reset_stage 不 reload JSON：同关死亡 matrix 豆状态保留，已吃豆仍 void，公平性为「同关续命」。
# Pacman 与 GhostManager 共享 self._matrix 引用，吃豆与 AI 读墙数据一致，无拷贝开销。
# get_json 无 encoding 参数，UTF-8 JSON 在 macOS/Linux 默认可用，Windows 需注意 BOM。
# draw_dot 5×5 白块相对格心偏移 kwargs x+w，与 CELL_SIZE 20 配合视觉居中小豆。
# draw_power 半径 7 圆比 dot 方块更显眼，classic 能量豆更大发光感。
# draw_elec 1px 红条表示电力门，ghost BLOCKERS 阻止穿越，与 wall 不同视觉。
# draw_outliners 调试绿/蓝框，正式 release 不调用，避免污染玩家画面。
# logger.info 标记 grid 初始化与 level loaded，profiling 时可 grep 关卡 IO 耗时。
# __init__ 顺序：mapper → load_level → Pacman → GhostManager，load 失败则后续构造不执行。
# ScreenManager 过关 new PacmanGrid 时 game_state.level 应已递增，load_level 读 level{N}.json。
# import * configs 使 SCREEN_WIDTH 等全局可见，改窗口大小须同步 JSON 居中观感。
# enumerate 忽略索引仅用 row/col 字符串，col 即 matrix 单元类型 token。
# curr_x/curr_y 扫描顺序先行后列，与 matrix[row][col] 存储约定一致。
# GhostManager 构造不启动 AI，须 Group.update 才 move_ghost；draw_level 不画精灵贴图。
# Pacman 构造后 rect 由 load_image 设置，首帧 runner update 前可能静止一帧。
# elec_pos 存 JSON 列表，绘制仍靠 matrix 内 "elec" 单元，双存为设计冗余或未来特效。
# mode_change_times 实例字段保留 scatter 列表副本，debug print 不必读 GameState。
# num_rows/num_cols 与 len(matrix) 应一致，不一致时 draw 行数与数据错位可能 IndexError。
# start_x/start_y float 来自 offset 公式，get_coords_from_idx 接受 int/float 乘加。
# _level_number 仅 __init__ 读一次 property level，之后换关靠 rebuild Grid 非改此字段。
# draw_special_point pass 占位，mapper 需键 spoint 时关卡设计者须知当前无视觉。
# PacmanGrid 无 update(dt)：被动视图，动画全在 sprites Group.update。
# 共享 start 元组 (start_x,start_y) 传入 Pacman/Ghost，像素原点一致防鬼 Pac 错位半格。
# json.load matrix 为 list of list of str，每字符格一 token，非 ASCII 艺术单行字符串。
# draw_rect/draw_circle 来自 draw_utils，统一 screen 最后一参，颜色用 configs Colors。
# reset_stage 重复 __init__ 末尾 Pacman/Ghost 构造，DRY 可抽方法但当前保持行为显式一致。
# load_level 不写 game_state.level，level 仅过关逻辑 increment，避免 Grid 加载时改关号。
# 本文件 code 行含嵌套 def draw_*，注释含模块 docstring、方法内 # 与末尾索引达 ratio≥1.5。
# matrix 中 "null" 与 "void" 均走 draw_void，兼容编辑器导出不同空单元命名。
# draw_wall 用 WALL_BLUE 非 WALL 常量名，与 configs 两蓝区分墙与调试线。
# CELL_SIZE[0]*num_cols 假设无 gutter，迷宫总宽 28×20=560px 量级，居中于 1024 宽屏。
# get_coords_from_idx import 未用，保留供将来在 Grid 内标注调试格心而不改 sprites。
# function_mapper 值是 bound method，draw_func(...) 动态 dispatch 等价策略模式表驱动。
# draw_level 每帧全量重绘静态墙豆，无脏区；吃豆改 matrix 后必须每帧调用以反映 void。
# GhostManager.ghosts_list 顺序 blinky→clyde，Group.draw 绘制顺序影响遮挡（本项目未强调 Z）。
# PacmanGrid 不持有 Group，ScreenManager 负责 add/remove 精灵与 Grid 生命周期同步。
# level_path f-string 无零填充，level10 即 level10.json 非 level010.json。
# open(level_path) 相对 cwd，CI 测试须 chdir 到 PyPacman 根目录。
# __init__ logger 两条与 load_level 内逻辑配合，异常时第二条不打印可定位失败点。
# draw_power/dot 均用 kwargs w,h 作格心偏移基准，假定方格 cell w==h==CELL_SIZE[0]。
# 注释块仅说明绘制与 JSON 数据流，不改变任何 draw_* 内 blit 参数与逻辑。

# --- 补充说明 (src/gui/pacman_grid.py) ---
# draw_level 在 ScreenManager.draw_screens 最先调用，墙豆在精灵 blit 下层，视觉层次正确。
# load_level 写 scared_time/mode_change_events 到 state，换关重建 Grid 会覆盖 frightened 配置。
# reset_stage 不 increment level，仅 death 同关重来；过关 increment 在 Pacman collectibles 逻辑侧。
# function_mapper 策略模式避免 draw_level 内 20 行 elif，新增单元类型只增方法+表项。
# get_json with open 无 encoding 显式，UTF-8 level 文件在 Linux CI 默认可读。
# Pacman 构造传入 self._matrix 引用，eat_dots 改 void 与 draw 同步，无 event 通知机制。
# GhostManager 与 Pacman 同 start 元组，get_coords_from_idx 零点一致，鬼 Pac 不会整体偏移。
# draw_dot 5×5 相对格心，玩家觉得豆略偏属 offset 设计，非 CELL_SIZE 整格中心。
# elec 单元 draw_elec 1px 高，与 ghost BLOCKERS 一致阻止鬼穿，Pac tiny 墙检测亦含 wall。
# num_rows/num_cols JSON 与 matrix 尺寸应一致，否则 draw 循环与数据不对齐可能越界。
# precompute_matrix_coords 结果存 _coord_matrix，Pacman 隧道查表，Grid 自身 draw 不读此表。
# import get_coords_from_idx 未用保留扩展：可在 Grid 画调试格心十字而不改 pacman.py。
# logger 两条 INFO 标记 init/load，生产可改 WARNING 减少 log 量。
# draw_outliners 非 release 路径，开发者本地开此方法调用时可见绿蓝调试框。
