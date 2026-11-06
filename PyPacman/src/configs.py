"""
全局配置与常量（Configuration）。

本模块没有函数，只有「类属性」和「模块级变量」。在 Python 里，
多个文件 ``from src.configs import *`` 或 ``import src.configs as cfg``
就能共享同一套数字与颜色，避免在 gui、sprites 里重复写魔法数字。

初学者要点：
- **类**在这里只当「命名空间」用（Colors.WHITE），不必实例化 Colors()。
- **元组** ``(R, G, B)`` 表示 pygame 常用的 RGB 颜色。
- **字典** ``{键: 值}`` 用字符串名字（如 "inky"）查延迟、目标格坐标等。
"""

# ---------------------------------------------------------------------------
# 颜色：RGB 每个分量 0～255，(255,255,255) 为白，(0,0,0) 为黑。
# ---------------------------------------------------------------------------
# 仅作常量容器，不定义 __init__，符合「命名空间类」用法。
class Colors:
    # 高分 HUD、小豆子常用前景色。
    WHITE = (255, 255, 255)
    # runner.main 每帧 fill 清屏用。
    BLACK = (0, 0, 0)
    # 调试线、elec 元素等。
    RED = (255, 0, 0)
    # draw_outliners 调试框等。
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WALL = (112, 167, 255)
    # 能量豆 draw_power 填充色。
    YELLOW = (252, 186, 3)
    # 迷宫墙 draw_wall 主色。
    WALL_BLUE = (24, 24, 217)


# ---------------------------------------------------------------------------
# 窗口与网格：迷宫在逻辑上是 NUM_ROWS × NUM_COLS 的格子，每格 CELL_SIZE 像素。
# PACMAN / GHOSTS 是精灵贴图的目标尺寸（可与格子略大，由 sprites 缩放）。
# ---------------------------------------------------------------------------
# set_mode 宽；与 place_elements_offset 居中计算配合。
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
# 元组 (宽, 高)；draw_level 用 CELL_SIZE[0] 作步进。
CELL_SIZE = (20, 20)
# 与默认关卡 JSON 行数一致，可用于校验（关卡文件也可自带 num_rows）。
NUM_ROWS = 31
NUM_COLS = 28
# 精灵目标像素尺寸，load 后 scale 用。
PACMAN = (32, 32)
GHOSTS = (32, 32)

# 每帧移动的像素步长；数值越大角色越快（仍受主循环 fps 约束）。
PACMAN_SPEED = 4
GHOST_SPEED_FAST = 5
GHOST_SPEED_SLOW = 2
# 毫秒：幽灵从「散开 scatter」切到「追逐 chase」等模式的默认间隔量级。
GHOST_NORMAL_DELAY = 5000

# ---------------------------------------------------------------------------
# 得分规则：吃豆、能量豆、吃幽灵、过关的加分（与 state_management 里累加配合）。
# ---------------------------------------------------------------------------
DOT_POINT = 10
POWER_POINT = 15
GHOST_POINT = 25
LEVEL_COMP_POINT = 80

# 各幽灵离开「鬼屋」前的等待时间（毫秒），名字与关卡 JSON / sprites 一致。
GHOST_DELAYS = {
    "inky": 12000,
    "pinky": 8000,
    "blinky": 4000,
    "clyde": 16000,
    "blue": 0
}

# 追逐模式下，多久重新计算一次寻路目标（秒或帧相关逻辑在 ghosts 模块使用）。
GHOST_TARGET_CHANGE = {
    "inky": 10,
    "pinky": 8,
    "blinky": 6,
    "clyde": 7,
    "blue": 7
}

# scatter 模式下幽灵要赶往的「角落」格子坐标 (行, 列)，经典 Pac-Man AI 行为。
GHOST_SCATTER_TARGETS = {
    'blinky': (0, 30),
    "pinky": (0, 0),
    "inky": (31, 0),
    "clyde": (31, 30)
}

# 加载界面用的 GIF 路径（相对项目根目录，运行时应从 PyPacman 目录启动）。
loading_screen_gif = "assets/other/loading.gif"

# ---------------------------------------------------------------------------
# 常量与运行时模块的对应关系（改数字前先对照下列调用点）
# ---------------------------------------------------------------------------
# SCREEN_WIDTH/HEIGHT：runner.GameRun.__init__ 的 set_mode；HUD 的 place_elements_offset 也用宽。
# CELL_SIZE：PacmanGrid.draw_level 步进；get_coords_from_idx 把 (row,col) 换成像素时的乘数。
# NUM_ROWS/COLS：与 level1.json 一致时可作文档；实际以 JSON 内 num_rows/num_cols 为准。
# PACMAN/GHOSTS：sprites 里 transform.scale 的目标尺寸，影响碰撞 rect 与贴图清晰度。
# PACMAN_SPEED：pacman.move_pacman 每帧像素位移；tiny_matrix 的 subdiv = CELL_SIZE[0]//PACMAN_SPEED。
# GHOST_SPEED_*：若 ghosts 模块引用则影响 scared/normal；当前 lerp 用 _accelerate 为主。
# GHOST_NORMAL_DELAY：scatter/chase 默认定时量级参考，实际间隔来自关卡 scatter_times 列表。
# DOT/POWER/GHOST/LEVEL_COMP_POINT：pacman.eat_dots、ghosts.check_collisions、过关加分处累加。
# GHOST_DELAYS：Ghost.__init__ 读 name 键，决定鬼屋内等待毫秒数，blinky 最短、clyde 最长。
# GHOST_TARGET_CHANGE：预留各鬼重算追逐目标的周期（秒），与 EventHandler 模式切换配合阅读。
# GHOST_SCATTER_TARGETS：四鬼 scatter 角落 (row,col)，Blinky 右上、Pinky 左上、Inky 左下、Clyde 右下。
# Colors.WALL_BLUE：PacmanGrid.draw_wall 填充；BLACK 为 runner 每帧 fill 清屏色。
# loading_screen_gif：LoadingScreen 可选 GIF 路径，相对 PyPacman 根目录，需从该目录启动 python main.py。
# 星号 import（from configs import *）会把本模块所有公共名注入调用方全局，适合小项目但 IDE 补全较弱。
# 修改 RGB 元组后无需重启 Python 进程以外的逻辑，下一帧 draw 即生效。
# GHOST_DELAYS["blue"] 为 0：scared 贴图键名，非第四只鬼的出笼延迟。
# ---------------------------------------------------------------------------

# --- 补充说明 (src/configs.py) ---
# DOT_POINT 与 GameState._points 初值 -DOT_POINT 配合，HUD 第一次吃豆显示 0 分。
# GHOST_SCATTER_TARGETS 行 0/31 与 NUM_ROWS 31 对应，改关卡行数须同步改 scatter 角坐标。
# WALL 与 WALL_BLUE 分工：RED/GREEN 调试，YELLOW 能量豆，WHITE 小豆与 HUD 文字。
# PACMAN_SPEED 4 与 CELL_SIZE 20 得 subdiv 5，tiny 网格每粗格 5×5 子格，与 move_pacman ±1 配套。
# LEVEL_COMP_POINT 在过关流程加分处使用，与 collectibles==0 触发 level_complete 配合阅读 sprites/gui。
# loading_screen_gif 路径独立于 PACMAN_PATHS，LoadingScreen 可选播放，不影响主循环 Group。
# GHOST_TARGET_CHANGE 秒数表供扩展 periodic retarget，当前 ghosts 主循环以 prepare_movement 岔路口为主。
# SCREEN 1024×768 与 place_elements_offset 居中 28×20×20 迷宫，两侧留黑边属正常布局。
# configs 无 pygame import，纯常量可在 headless 测试 import，不初始化 display。
# 星号 import 后 runner/gui/sprites 直接用 Colors.BLACK，rename 常量须全局搜索替换调用点。
# [续] DOT_POINT 与 GameState._points 初值 -DOT_POINT 配合，HUD 第一次吃豆显示 0 分。
