from math import ceil  # 导入数学模块中的 ceil 函数，用于向上取整
from typing import Union  # 导入类型提示模块

from pygame import image, transform  # 从 pygame 导入图像和变换模块
from pygame.sprite import Sprite  # 从 pygame 导入 Sprite 类
from pygame import Surface, USEREVENT  # 从 pygame 导入 Surface 类和用户事件常量
from pygame.time import set_timer, get_ticks  # 从 pygame 导入设置计时器和获取时间的函数

from src.configs import CELL_SIZE, PACMAN_SPEED, PACMAN, DOT_POINT, POWER_POINT  # 导入配置常量
from src.game.state_management import GameState  # 导入游戏状态管理类
from src.sprites.sprite_configs import *  # 导入精灵配置
from src.utils.coord_utils import (get_coords_from_idx, 
                                   get_idx_from_coords, 
                                   get_tiny_matrix,
                                   precompute_matrix_coords)  # 导入坐标工具函数
from src.sounds import SoundManager  # 导入声音管理器
from src.log_handle import get_logger  # 导入日志记录器
logger = get_logger(__name__)  # 获取当前模块的日志记录器

class Pacman(Sprite):  # 定义 Pacman 类，继承自 Sprite
    def __init__(self, 
                 screen: Surface,  # 屏幕对象
                 game_state: GameState,  # 游戏状态对象
                 matrix: list[list[str]],  # 游戏矩阵
                 pacman_pos: tuple,  # 吃豆人位置
                 start_pos: tuple):  # 起始位置
        super().__init__()  # 调用父类的初始化方法
        self.screen = screen  # 保存屏幕对象
        self.game_state = game_state  # 保存游戏状态对象
        self.pacman_pos = pacman_pos  # 保存吃豆人位置
        self.matrix = matrix  # 保存游戏矩阵
        self.start_pos = start_pos  # 保存起始位置
        self.load_all_frames()  # 加载所有帧
        self.calculate_pacman_coords()  # 计算吃豆人坐标
        self.load_image()  # 加载图像
        self.calculate_tiny_matrix()  # 计算微型矩阵
        self.calculate_coord_matrix()  # 计算坐标矩阵
        self.frame_delay = 5  # 初始化帧延迟为 5
        self.sound = SoundManager()  # 创建声音管理器对象
        self.collectibles = self.count_dots_powers()  # 计算可收集物品数量

    def count_dots_powers(self):  # 定义计算小点和能量点数量的方法
        collectibles = 0  # 初始化可收集物品数量为 0
        for row in range(len(self.matrix)):  # 遍历矩阵的每一行
            for col in range(len(self.matrix[0])):  # 遍历行中的每一列
                if col + 1 >= len(self.matrix[0]):  # 如果列超出范围
                    continue  # 跳过
                if self.matrix[row][col] in ['dot', 'power'] and \
                        self.matrix[row+1][col] not in ['wall', 'elec', 'null']:  # 如果是小点或能量点且下方不是墙、电力或空
                    collectibles += 1  # 增加可收集物品数量
        # logger.info("total_collectibles: %s",collectibles)  # 记录总可收集物品数量
        return collectibles  # 返回可收集物品数量

    def load_image(self):  # 定义加载图像的方法
        self.image = self.frames[self.curr_frame_idx]  # 获取当前帧的图像
        self.rect_x = self.pacman_x_coord  # 设置矩形的 x 坐标
        self.rect_y = self.pacman_y_coord  # 设置矩形的 y 坐标
        self.rect = self.image.get_rect(topleft=(self.pacman_x_coord,
                                                 self.pacman_y_coord))  # 创建矩形对象
    
    def build_bounding_boxes(self, x: Union[int, float], y: Union[int, float]):  # 定义构建边界框的方法
        self.rect.x = x + (CELL_SIZE[0] * 2 - self.rect.width) // 2  # 计算并设置矩形的 x 坐标
        self.rect.y = y + (CELL_SIZE[1] * 2 - self.rect.height) // 2  # 计算并设置矩形的 y 坐标
        
    def frame_update(self):  # 定义帧更新的方法
        self.frame_delay -= 1  # 减少帧延迟
        if self.frame_delay <= 0:  # 如果帧延迟小于等于 0
            self.frame_delay = 5  # 重置帧延迟
            self.curr_frame_idx = (self.curr_frame_idx + 1) % len(self.frames)  # 更新当前帧索引
            self.image = self.frames[self.curr_frame_idx]  # 更新图像

    def frame_direction_update(self):  # 定义帧方向更新的方法
        if self.move_direction != "":  # 如果移动方向不为空
            self.frames = self.direction_mapper[self.move_direction]  # 更新帧列表

    def calculate_pacman_coords(self):  # 定义计算吃豆人坐标的方法
        x, y = get_coords_from_idx(
            self.pacman_pos,
            self.start_pos[0],
            self.start_pos[1],
            CELL_SIZE[0],
            CELL_SIZE[1],
            len(self.matrix),
            len(self.matrix[0])
        )  # 获取吃豆人坐标
        self.pacman_x_coord = x  # 保存吃豆人 x 坐标
        self.pacman_y_coord = y  # 保存吃豆人 y 坐标
    
    def load_all_frames(self):  # 定义加载所有帧的方法
        def frame_helper(direction):  # 定义帧助手函数
            width, height = PACMAN  # 获取吃豆人的宽度和高度
            return [
                transform.scale(image.load(path).convert_alpha(), (width, height))
                for path in PACMAN_PATHS[direction]
            ]  # 加载并缩放图像
        self.curr_frame_idx = 0  # 初始化当前帧索引为 0
        self.left_frames = frame_helper("left")  # 加载左方向帧
        self.right_frames = frame_helper("right")  # 加载右方向帧
        self.down_frames = frame_helper("down")  # 加载下方向帧
        self.up_frames = frame_helper("up")  # 加载上方向帧
        self.direction_mapper = {
            "l": self.left_frames,
            "r": self.right_frames,
            "u": self.up_frames,
            "d": self.down_frames,
        }  # 定义方向映射
        self.frames = self.right_frames  # 设置初始帧为右方向帧
        self.move_direction = self.game_state.direction  # 获取游戏状态中的移动方向

    def calculate_tiny_matrix(self):  # 定义计算微型矩阵的方法
        self.tiny_matrix = get_tiny_matrix(self.matrix,
                                           CELL_SIZE[0],
                                           PACMAN_SPEED)  # 获取微型矩阵
        self.subdiv = CELL_SIZE[0] // PACMAN_SPEED  # 计算子划分
        self.tiny_start_x = self.pacman_pos[0] * self.subdiv  # 计算微型起始 x 坐标
        self.tiny_start_y = self.pacman_pos[1] * self.subdiv  # 计算微型起始 y 坐标

    def calculate_coord_matrix(self):  # 定义计算坐标矩阵的方法
        self.coord_matrix = precompute_matrix_coords(*self.start_pos,
                                                     PACMAN_SPEED,
                                                     len(self.tiny_matrix),
                                                     len(self.tiny_matrix[0]))  # 预计算坐标矩阵

    def edges_helper_vertical(self, row: int, 
                              col: int, 
                              additive: int):  # 定义垂直边缘助手方法
        for r in range(self.subdiv * 2):  # 遍历子划分的两倍
            if self.tiny_matrix[row + r][col + additive] == "wall":  # 如果是墙
                return False  # 返回 False
        return True  # 返回 True

    def edge_helper_horizontal(self, row: int, 
                               col: int, 
                               additive: int):  # 定义水平边缘助手方法
        for c in range(self.subdiv * 2):  # 遍历子划分的两倍
            if self.tiny_matrix[row + additive][col + c] == "wall":  # 如果是墙
                return False  # 返回 False
        return True  # 返回 True

    def boundary_check(self):  # 定义边界检查方法
        if (self.tiny_start_y + self.subdiv * 2) >= len(self.tiny_matrix[0]) - 1:  # 如果超出右边界
            self.tiny_start_y = 0  # 重置到第一列
            self.rect_x = self.coord_matrix[self.tiny_start_x][0][0]  # 更新矩形 x 坐标

        elif (self.tiny_start_y - 1) < 0:  # 如果超出左边界
            self.tiny_start_y = len(self.tiny_matrix[0]) - (self.subdiv * 3)  # 重置到最后一列
            self.rect_x = self.coord_matrix[self.tiny_start_x][-self.subdiv*2 - 4][0]  # 更新矩形 x 坐标

    def create_power_up_event(self):  # 定义创建能量提升事件的方法
        CUSTOM_EVENT = USEREVENT + 2  # 定义自定义事件
        set_timer(CUSTOM_EVENT, 
                self.game_state.scared_time)  # 设置计时器以触发自定义事件
        self.game_state.power_up_event = CUSTOM_EVENT  # 更新游戏状态中的能量提升事件
        self.game_state.is_pacman_powered = True  # 设置吃豆人有能量
        self.game_state.power_event_trigger_time = get_ticks()  # 更新能量事件触发时间

    def eat_dots(self):  # 定义吃小点的方法
        r, c = get_idx_from_coords(
            self.rect.x, self.rect.y, *self.start_pos, CELL_SIZE[0]
        )  # 获取当前索引
        if self.matrix[r][c] == "dot":  # 如果是小点
            self.matrix[r][c] = "void"  # 设置为已吃
            self.sound.play_sound("dot")  # 播放吃小点的声音
            self.collectibles -= 1  # 减少可收集物品数量
            self.game_state.points += DOT_POINT  # 增加分数
        elif self.matrix[r][c] == "power":  # 如果是能量点
            self.matrix[r][c] = "void"  # 设置为已吃
            self.create_power_up_event()  # 创建能量提升事件
            self.sound.play_sound("dot")  # 播放吃小点的声音
            self.collectibles -= 1  # 减少可收集物品数量
            self.game_state.points += POWER_POINT  # 增加分数
                
    def movement_bind(self):  # 定义移动绑定的方法
        if self.game_state.direction == 'l':  # 如果方向是左
            if self.edges_helper_vertical(self.tiny_start_x, self.tiny_start_y, -1):  # 如果可以移动
                self.move_direction = "l"  # 设置移动方向为左
                self.game_state.pacman_direction = 'l'  # 更新游戏状态中的吃豆人方向
        elif self.game_state.direction == 'r':  # 如果方向是右
            if self.edges_helper_vertical(
                self.tiny_start_x, self.tiny_start_y, self.subdiv * 2
            ):  # 如果可以移动
                self.move_direction = "r"  # 设置移动方向为右
                self.game_state.pacman_direction = 'r'  # 更新游戏状态中的吃豆人方向
        elif self.game_state.direction == 'u':  # 如果方向是上
            if self.edge_helper_horizontal(self.tiny_start_x, self.tiny_start_y, -1):  # 如果可以移动
                self.move_direction = "u"  # 设置移动方向为上
                self.game_state.pacman_direction = 'u'  # 更新游戏状态中的吃豆人方向
        elif self.game_state.direction == 'd':  # 如果方向是下
            if self.edge_helper_horizontal(
                self.tiny_start_x, self.tiny_start_y, self.subdiv * 2
            ):  # 如果可以移动
                self.move_direction = "d"  # 设置移动方向为下
                self.game_state.pacman_direction = 'd'  # 更新游戏状态中的吃豆人方向
 
    def move_pacman(self, dt: float):  # 定义移动吃豆人的方法
        if self.move_direction == "l":  # 如果移动方向是左
            if self.edges_helper_vertical(self.tiny_start_x, self.tiny_start_y, -1):  # 如果可以移动
                self.rect_x -= PACMAN_SPEED  # 减少 x 坐标
                self.tiny_start_y -= 1  # 减少微型起始 y 坐标
        elif self.move_direction == "r":  # 如果移动方向是右
            if self.edges_helper_vertical(
                self.tiny_start_x, self.tiny_start_y, self.subdiv * 2
            ):  # 如果可以移动
                self.rect_x += PACMAN_SPEED  # 增加 x 坐标
                self.tiny_start_y += 1  # 增加微型起始 y 坐标
        elif self.move_direction == "u":  # 如果移动方向是上
            if self.edge_helper_horizontal(self.tiny_start_x, self.tiny_start_y, -1):  # 如果可以移动
                self.rect_y -= PACMAN_SPEED  # 减少 y 坐标
                self.tiny_start_x -= 1  # 减少微型起始 x 坐标
        elif self.move_direction == "d":  # 如果移动方向是下
            if self.edge_helper_horizontal(
                self.tiny_start_x, self.tiny_start_y, self.subdiv * 2
            ):  # 如果可以移动
                self.rect_y += PACMAN_SPEED  # 增加 y 坐标
                self.tiny_start_x += 1  # 增加微型起始 x 坐标

        self.game_state.pacman_rect = (self.rect_x, self.rect_y, 
                                       CELL_SIZE[0]*2, CELL_SIZE[0]*2)  # 更新游戏状态中的吃豆人矩形

    def update(self, dt: float):  # 定义更新方法
        self.frame_update()  # 更新帧
        self.build_bounding_boxes(self.rect_x, self.rect_y)  # 构建边界框
        self.movement_bind()  # 绑定移动
        self.move_pacman(dt)  # 移动吃豆人
        self.boundary_check()  # 检查边界
        self.eat_dots()  # 吃小点
        self.frame_direction_update()  # 更新帧方向
        if self.collectibles == 0:  # 如果没有可收集物品
            self.game_state.level_complete = True  # 设置关卡完成状态