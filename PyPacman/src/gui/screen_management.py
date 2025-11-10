from src.configs import *  # 从配置文件中导入所有配置
from src.gui.pacman_grid import *  # 从 GUI 模块中导入 PacmanGrid 类
from src.gui.loading_screen import LoadingScreen  # 导入 LoadingScreen 类
from src.gui.score_screen import ScoreScreen  # 导入 ScoreScreen 类
from src.log_handle import get_logger  # 导入日志记录器

from pygame.time import wait  # 从 pygame 导入等待函数

logger = get_logger(__name__)  # 获取当前模块的日志记录器

class ScreenManager:  # 定义 ScreenManager 类
    def __init__(self, screen, game_state, all_sprites):  # 初始化方法，接收屏幕、游戏状态和所有精灵组
        logger.info("screen manager initializing")  # 记录初始化日志
        self._screen = screen  # 保存屏幕对象
        self._game_state = game_state  # 保存游戏状态对象
        self.all_sprites = all_sprites  # 保存所有精灵组
        self.loading_screen = LoadingScreen(self._screen)  # 创建加载屏幕对象
        self.pacman = PacmanGrid(screen, game_state)  # 创建 PacmanGrid 对象
        self.score_screen = ScoreScreen(self._screen, self._game_state)  # 创建 ScoreScreen 对象
        logger.info("pacman grid created")  # 记录 PacmanGrid 创建日志
        self.all_sprites.add(self.pacman.pacman)  # 将 Pacman 添加到精灵组
        for ghost in self.pacman.ghost.ghosts_list:  # 遍历幽灵列表
            self.all_sprites.add(ghost)  # 将每个幽灵添加到精灵组

    def pacman_dead_reset(self):  # 定义吃豆人死亡重置的方法
        if self._game_state.is_pacman_dead:  # 如果吃豆人死亡状态为真
            self._game_state.is_pacman_dead = False  # 重置吃豆人死亡状态
            self._game_state.direction = ""  # 重置方向
            self._game_state.pacman_direction = None  # 重置吃豆人方向
            self.all_sprites.empty()  # 清空精灵组
            self.pacman.reset_stage()  # 重置关卡
            self.all_sprites.add(self.pacman.pacman)  # 将 Pacman 添加到精灵组
            for ghost in self.pacman.ghost.ghosts_list:  # 遍历幽灵列表
                self.all_sprites.add(ghost)  # 将每个幽灵添加到精灵组
    
    def check_level_complete(self):  # 定义检查关卡完成的方法
        if self._game_state.level_complete:  # 如果关卡完成状态为真
            wait(2000)  # 等待 2000 毫秒
            self.all_sprites.empty()  # 清空精灵组
            self.pacman = PacmanGrid(self._screen, self._game_state)  # 重新创建 PacmanGrid 对象
            self.score_screen = ScoreScreen(self._screen, self._game_state)  # 重新创建 ScoreScreen 对象
            logger.info("pacman grid created")  # 记录 PacmanGrid 创建日志
            self.all_sprites.add(self.pacman.pacman)  # 将 Pacman 添加到精灵组
            for ghost in self.pacman.ghost.ghosts_list:  # 遍历幽灵列表
                self.all_sprites.add(ghost)  # 将每个幽灵添加到精灵组
            self._game_state.level_complete = False  # 重置关卡完成状态

    def draw_screens(self):  # 定义绘制屏幕的方法
        self.pacman.draw_level()  # 绘制当前关卡
        self.pacman_dead_reset()  # 调用吃豆人死亡重置方法
        self.score_screen.draw_scores()  # 绘制分数
        self.check_level_complete()  # 检查关卡是否完成
