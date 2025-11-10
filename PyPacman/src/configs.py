class Colors:  # 定义颜色类
    WHITE = (255, 255, 255)  # 白色的 RGB 值
    BLACK = (0, 0, 0)  # 黑色的 RGB 值
    RED = (255, 0, 0)  # 红色的 RGB 值
    GREEN = (0, 255, 0)  # 绿色的 RGB 值
    BLUE = (0, 0, 255)  # 蓝色的 RGB 值
    WALL = (112, 167, 255)  # 墙壁的 RGB 值
    YELLOW = (252, 186, 3)  # 黄色的 RGB 值
    WALL_BLUE = (24, 24, 217)  # 墙壁蓝色的 RGB 值


SCREEN_WIDTH = 1024  # 屏幕宽度
SCREEN_HEIGHT = 768  # 屏幕高度
CELL_SIZE = (20, 20)  # 单元格大小
NUM_ROWS = 31  # 行数
NUM_COLS = 28  # 列数
PACMAN = (32, 32)  # 吃豆人的大小
GHOSTS = (32, 32)  # 幽灵的大小
PACMAN_SPEED = 4  # 吃豆人的速度
GHOST_SPEED_FAST = 5  # 幽灵的快速速度
GHOST_SPEED_SLOW = 2  # 幽灵的慢速速度
GHOST_NORMAL_DELAY = 5000  # 幽灵的正常延迟时间

DOT_POINT = 10  # 吃小点的得分
POWER_POINT = 15  # 吃能量点的得分
GHOST_POINT = 25  # 吃幽灵的得分
LEVEL_COMP_POINT = 80  # 完成关卡的得分

GHOST_DELAYS = {  # 幽灵的延迟时间字典
    "inky": 12000,  # Inky 的延迟时间
    "pinky": 8000,  # Pinky 的延迟时间
    "blinky": 4000,  # Blinky 的延迟时间
    "clyde": 16000,  # Clyde 的延迟时间
    "blue": 0  # 蓝色幽灵的延迟时间
}

GHOST_TARGET_CHANGE = {  # 幽灵目标改变的时间字典
    "inky": 10,  # Inky 的目标改变时间
    "pinky": 8,  # Pinky 的目标改变时间
    "blinky": 6,  # Blinky 的目标改变时间
    "clyde": 7,  # Clyde 的目标改变时间
    "blue": 7  # 蓝色幽灵的目标改变时间
}

GHOST_SCATTER_TARGETS = {  # 幽灵散开模式的目标位置字典
    'blinky': (0, 30),  # Blinky 的目标位置
    "pinky": (0, 0),  # Pinky 的目标位置
    "inky": (31, 0),  # Inky 的目标位置
    "clyde": (31, 30)  # Clyde 的目标位置
}

loading_screen_gif = "assets/other/loading.gif"  # 加载屏幕的 GIF 文件路径