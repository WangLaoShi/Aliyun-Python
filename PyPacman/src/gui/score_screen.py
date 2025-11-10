from pygame.surface import Surface  # 从 pygame 导入 Surface 类，用于创建屏幕表面
from pygame import font  # 从 pygame 导入字体模块

from src.game.state_management import GameState  # 导入游戏状态管理类
from src.configs import *  # 导入所有配置
from src.utils.coord_utils import place_elements_offset  # 导入坐标工具函数

class ScoreScreen:  # 定义 ScoreScreen 类
    def __init__(self,
                 screen: Surface,
                 game_state: GameState):  # 初始化方法，接收屏幕和游戏状态对象
        self._screen = screen  # 保存屏幕对象
        self._game_state = game_state  # 保存游戏状态对象
        self.start_x, self.start_y = place_elements_offset(  # 计算元素偏移位置
            SCREEN_WIDTH,  # 屏幕宽度
            SCREEN_HEIGHT,  # 屏幕高度
            200,  # 元素宽度
            200,  # 元素高度
            0.25,  # 水平偏移比例
            0.05  # 垂直偏移比例
        )
        font.init()  # 初始化字体模块
        self.font = font.Font(None, 36)  # 创建字体对象，使用默认字体和大小为 36

    def draw_scores(self):  # 定义绘制分数的方法
        score_text = "SCORE: " + str(self._game_state.points)  # 创建分数文本
        score_surface = self.font.render(score_text, True, Colors.WHITE)  # 渲染分数文本为图像
        self._screen.blit(score_surface, (self.start_x, self.start_y))  # 在屏幕上绘制分数图像

        highscore_text = "HIGHSCORE: " + str(self._game_state.highscore)  # 创建最高分文本
        hs_surface = self.font.render(highscore_text, True, Colors.WHITE)  # 渲染最高分文本为图像
        self._screen.blit(hs_surface, (self.start_x + 300, self.start_y))  # 在屏幕上绘制最高分图像
        