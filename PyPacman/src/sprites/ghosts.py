"""
This module handles ghosts
A single ghost class responsible for rendering ghost,
ghost manager class responsible for creating multiple ghost objects aka ghosts
ghost movement class responsible for moving the ghost with lerp
GhostManager takes ghost matrix pos, grid start pos, matrix, game state object.
Ghost takes name, ghost matrix pos, grid start pos, matrix and game state object
Ghost movement class should need ghost coordinate pos, matrix, game state, some more parameters.
"""
from abc import abstractmethod, ABC  # 导入抽象基类模块
from typing import Union  # 导入类型提示模块

from pygame.sprite import Sprite  # 从 pygame 导入 Sprite 类
from pygame import Surface  # 从 pygame 导入 Surface 类
from pygame import image, transform  # 从 pygame 导入图像和变换模块
import pygame.time as pytime  # 导入 pygame 时间模块并重命名为 pytime
from pygame.time import wait  # 从 pygame 导入等待函数
from pygame.rect import Rect  # 从 pygame 导入 Rect 类

import random  # 导入随机数模块

from src.game.state_management import GameState  # 导入游戏状态管理类
from src.sprites.sprite_configs import GHOST_PATHS  # 导入幽灵路径配置
from src.configs import PACMAN, CELL_SIZE, GHOST_DELAYS, GHOST_SCATTER_TARGETS, GHOST_POINT  # 导入配置常量
from src.utils.coord_utils import get_coords_from_idx, get_idx_from_coords  # 导入坐标工具函数
from src.utils.ghost_movement_utils import get_direction, get_is_intersection, get_is_move_valid  # 导入幽灵移动工具函数
from src.sounds import SoundManager  # 导入声音管理器

from src.log_handle import get_logger  # 导入日志记录器
logger = get_logger(__name__)  # 获取当前模块的日志记录器

class Ghost(Sprite, ABC):  # 定义 Ghost 类，继承自 Sprite 和 ABC
    def __init__(self,
                 name: str,  # 幽灵的名称
                 ghost_matrix_pos: tuple[int, int],  # 幽灵在矩阵中的位置
                 grid_start_pos: tuple[Union[int, float], Union[int, float]],  # 网格起始位置
                 matrix: list[list[str]],  # 游戏矩阵
                 game_state: GameState  # 游戏状态对象
                 ):
        super().__init__()  # 调用父类的初始化方法
        self.name = name  # 保存幽灵名称
        self._ghost_matrix_pos = ghost_matrix_pos  # 保存幽灵矩阵位置
        self._grid_start_pos = grid_start_pos  # 保存网格起始位置
        self._matrix = matrix  # 保存游戏矩阵
        self.num_rows = len(self._matrix)  # 计算矩阵的行数
        self.num_cols = len(self._matrix[0])  # 计算矩阵的列数
        self._game_state = game_state  # 保存游戏状态对象
        self._is_released = False  # 初始化幽灵释放状态为 False
        self._creation_time = pytime.get_ticks()  # 获取当前时间作为创建时间
        self._dead_wait = GHOST_DELAYS[self.name]  # 获取幽灵的延迟时间
        self.move_direction_mapper = {"up": (-1, 0), "down":(2, 0), 
                                      "right": (0, 2), "left": (0, -1)}  # 定义移动方向映射
        self.prev_pos = None  # 初始化前一个位置为 None
        self._t = 0  # 初始化插值参数 t 为 0
        self._accelerate = 0.2  # 初始化加速度为 0.2
        self._direction = None  # 初始化方向为 None
        self._target = None  # 初始化目标为 None
        self.prev = None  # 初始化前一个位置为 None
        self.next_tile = None  # 初始化下一个瓦片为 None
        self._direction_prevent = {(-1, 0): (1, 0), (1, 0): (-1, 0),
                                     (0, 1): (0, -1), (0, -1): (0, 1)}  # 定义方向防止映射
        self.is_scared = False  # 初始化幽灵受惊状态为 False
        self.curr_pos = None  # 初始化当前坐标为 None
        self.release_time = None  # 初始化释放时间为 None
        self.sounds = SoundManager()  # 创建声音管理器对象
        self.load_images()  # 加载幽灵图像

    def _get_coords_from_idx(self, p1):  # 定义从索引获取坐标的方法
        return get_coords_from_idx(p1, *self._grid_start_pos, 
                                   *CELL_SIZE, self.num_rows, self.num_cols)  # 调用工具函数获取坐标
    
    def _get_idx_from_coords(self, p1):  # 定义从坐标获取索引的方法
        return get_idx_from_coords(*p1,
                                   *self._grid_start_pos, CELL_SIZE[0])  # 调用工具函数获取索引
    
    def build_bounding_boxes(self, x, y):  # 定义构建边界框的方法
        self.rect.x = x + (CELL_SIZE[0] * 2 - self.rect.width) // 2  # 计算并设置矩形的 x 坐标
        self.rect.y = y + (CELL_SIZE[1] * 2 - self.rect.height) // 2  # 计算并设置矩形的 y 坐标

    def load_images(self):  # 定义加载图像的方法
        ghost_images = GHOST_PATHS[self.name][0]  # 获取幽灵的图像路径
        blue_images = GHOST_PATHS['blue'][0]  # 获取蓝色幽灵的图像路径
        self.normal_image = transform.scale(image.load(ghost_images).convert_alpha(),
                                     PACMAN)  # 加载并缩放正常幽灵图像
        self.blue_image = transform.scale(image.load(blue_images).convert_alpha(),
                                     PACMAN)  # 加载并缩放蓝色幽灵图像
        self.image = self.normal_image  # 设置当前图像为正常幽灵图像
        x, y = self._get_coords_from_idx(self._ghost_matrix_pos)  # 获取幽灵的初始坐标
        self.rect = self.image.get_rect(topleft=(x, y))  # 创建矩形对象
        self.rect_x = x  # 保存矩形的 x 坐标
        self.rect_y = y  # 保存矩形的 y 坐标

    def lerp(self, source, dest):  # 定义线性插值方法
        x1, y1 = source  # 解包源坐标
        x2, y2 = dest  # 解包目标坐标
        if self._target is None or self._t == 1:  # 如果没有目标或 t 为 1
            return x1, y1  # 返回源坐标
        if self._t < 1:  # 如果 t 小于 1
            self._t += self._accelerate  # 增加 t
        else:
            self._t = 1  # 否则将 t 设置为 1

        x = (1 - self._t) * x1 + self._t * x2  # 计算插值后的 x 坐标
        y = (1 - self._t) * y1 + self._t * y2  # 计算插值后的 y 坐标
        return x, y  # 返回插值后的坐标
    
    def check_is_released(self):  # 定义检查是否释放的方法
        if self._is_released:  # 如果已经释放
            return  # 直接返回
        curr_time = pytime.get_ticks()  # 获取当前时间
        if (curr_time - self._creation_time) > self._dead_wait:  # 如果当前时间超过延迟时间
            self._is_released = True  # 设置为已释放
            self._dead_wait = 1500  # 更新延迟时间
            self.rect_x, self.rect_y = self._get_coords_from_idx((11, self._ghost_matrix_pos[1]))  # 更新坐标
            self.release_time = pytime.get_ticks()  # 更新释放时间

    def move_ghost(self):  # 定义移动幽灵的方法
        if not self._is_released:  # 如果未释放
            return  # 直接返回
        if self._target is None:  # 如果没有目标
            self.prepare_movement()  # 准备移动
        source = self._get_coords_from_idx(self.prev)  # 获取源坐标
        dest = self._get_coords_from_idx(self.next_tile)  # 获取目标坐标
        self.rect_x, self.rect_y = self.lerp(source, dest)  # 进行插值移动
        curr_mat_x, curr_mat_y = self._get_idx_from_coords((self.rect_x, self.rect_y))  # 获取当前矩阵索引
        if self.name == 'blinky':  # 如果是 Blinky
            self._game_state.blinky_matrix_pos = (curr_mat_x, curr_mat_y)  # 更新 Blinky 的矩阵位置
        self.curr_pos = (curr_mat_x, curr_mat_y)  # 更新当前坐标
        if (self._t == 1) \
            or (self.rect_x == dest[0] and self.rect_y == dest[1]):  # 如果到达目标
            check_prev = self._direction_prevent.get(self._direction)  # 获取防止方向
            prev_val = self._get_direction_reverse_map(check_prev)  # 获取反向映射
            if get_is_intersection(self.next_tile, self._matrix, 
                                   prev_val):  # 如果是交叉点
                self.prepare_movement()  # 准备移动
            else:
                if not get_is_move_valid(self.next_tile, 
                                         self._get_direction_reverse_map(self._direction), 
                                         self._matrix):  # 如果移动无效
                    self.prepare_movement()  # 准备移动
                else:
                    self.prev = self.next_tile  # 更新前一个位置
                    self.next_tile = (self.next_tile[0] + self._direction[0],
                                  self.next_tile[1] + self._direction[1])  # 更新下一个瓦片
                
                self._t = 0  # 重置 t
    
    def _get_direction_reverse_map(self, direction):  # 定义获取方向反向映射的方法
        if direction == (-1, 0):  # 如果方向是向上
            return 'up'  # 返回 'up'
        elif direction == (1, 0):  # 如果方向是向下
            return "down"  # 返回 'down'
        elif direction == (0, -1):  # 如果方向是向左
            return "left"  # 返回 'left'
        elif direction == (0, 1):  # 如果方向是向右
            return "right"  # 返回 'right'
      
    def _boundary_check(self):  # 定义边界检查方法
        if not self.next_tile:  # 如果没有下一个瓦片
            return  # 直接返回
        if (self.next_tile[1] >= self.num_cols):  # 如果超出列数
            self.next_tile = (self.next_tile[0], 0)  # 重置到第一列
            return
        if self.next_tile[1] < 0:  # 如果小于第一列
            self.next_tile = (self.next_tile[0], self.num_cols - 1)  # 重置到最后一列

    def prepare_movement(self):  # 定义准备移动的方法
        ghost_x, ghost_y = self._get_idx_from_coords((self.rect_x, self.rect_y))  # 获取当前索引
        if self.next_tile:  # 如果有下一个瓦片
            ghost_x, ghost_y = self.next_tile  # 更新当前坐标
        if self.is_scared:  # 如果幽灵受惊
            self._target = self.get_random_target()  # 获取随机目标
        else:
            self._target = self.determine_target()  # 确定目标
        prev = self._direction_prevent.get(self._direction)  # 获取防止方向
        self._direction = get_direction((ghost_x, ghost_y),
                                        self._target, 
                                        self._matrix, 
                                        prev
                                        )  # 获取新方向
        self._t = 0  # 重置 t
        self.next_tile = (ghost_x + self._direction[0], 
                          ghost_y + self._direction[1])  # 更新下一个瓦片
        self.prev = (ghost_x, ghost_y)  # 更新前一个位置

    @abstractmethod
    def determine_target(self):  # 定义抽象方法确定目标
        ...
        
    def get_target_pacman_dir(self, pacman_rect: tuple, 
                              pacman_dir: tuple,
                              look_ahead: int=4):  # 定义获取吃豆人目标方向的方法
        if pacman_dir == "l":  # 如果吃豆人方向是左
            target = (pacman_rect[0], pacman_rect[1] - look_ahead)  # 计算目标
            if target[1] < 0:  # 如果目标超出左边界
                target = (pacman_rect[0], self.num_cols - look_ahead - 1)  # 重置目标
            return target  # 返回目标
        elif pacman_dir == "r":  # 如果吃豆人方向是右
            target = (pacman_rect[0], pacman_rect[1] + look_ahead)  # 计算目标
            if target[1] > self.num_cols:  # 如果目标超出右边界
                target = (pacman_rect[0], 0)  # 重置目标
            return target  # 返回目标
        elif pacman_dir == "u":  # 如果吃豆人方向是上
            return (pacman_rect[0] - look_ahead, pacman_rect[1])  # 返回目标
        elif pacman_dir == "d":  # 如果吃豆人方向是下
            return (pacman_rect[0] + look_ahead, pacman_rect[1])  # 返回目标
        else:
            return pacman_rect  # 返回吃豆人当前位置

    def get_random_target(self):  # 定义获取随机目标的方法
        rand_row = random.randrange(0, self.num_rows)  # 随机选择行
        rand_col = random.randrange(0, self.num_cols)  # 随机选择列
        return rand_row, rand_col  # 返回随机目标
    
    def make_ghost_scared(self):  # 定义使幽灵受惊的方法
        self._direction = self._direction_prevent[self._direction]  # 反转方向
        self.is_scared = True  # 设置受惊状态
        self.prepare_movement()  # 准备移动

    def check_if_pacman_powered(self):  # 定义检查吃豆人是否有能量的方法
        if not self._is_released:  # 如果未释放
            if self.image != self.normal_image:  # 如果图像不是正常图像
                self.image = self.normal_image  # 设置为正常图像
            return  # 返回
        if self._game_state.power_event_trigger_time is not None and \
                self.release_time > self._game_state.power_event_trigger_time:  # 如果能量事件触发时间存在且释放时间大于触发时间
            return  # 返回
        if self._game_state.is_pacman_powered:  # 如果吃豆人有能量
            if self.image != self.blue_image:  # 如果图像不是蓝色图像
                self.image = self.blue_image  # 设置为蓝色图像
                self.make_ghost_scared()  # 使幽灵受惊
        else:
            if self.image != self.normal_image:  # 如果图像不是正常图像
                self.image = self.normal_image  # 设置为正常图像
                self.is_scared = False  # 取消受惊状态

    def reset_ghost(self):  # 定义重置幽灵的方法
        self._t = 0  # 重置 t
        self._direction = None  # 重置方向
        self._target = None  # 重置目标
        self._curr_pos = None  # 重置当前坐标
        self.prev = None  # 重置前一个位置
        self.next_tile = None  # 重置下一个瓦片
        self.release_time = None  # 重置释放时间
        self.is_scared = False  # 重置受惊状态
        self.rect.x  # 重置矩形 x 坐标
        x, y = self._get_coords_from_idx(self._ghost_matrix_pos)  # 获取初始坐标
        self.rect = self.image.get_rect(topleft=(x, y))  # 创建矩形对象
        self.rect_x = x  # 保存矩形 x 坐标
        self.rect_y = y  # 保存矩形 y 坐标
        self._is_released = False  # 重置释放状态
        self._creation_time = pytime.get_ticks()  # 更新创建时间

    def check_collisions(self):  # 定义检查碰撞的方法
        ghost_rect = Rect(self.rect.x, self.rect.y, 
                          PACMAN[0]//2, PACMAN[1]//2)  # 创建幽灵的矩形
        pacman_coords = (self._game_state.pacman_rect[0],
                         self._game_state.pacman_rect[1],
                         self._game_state.pacman_rect[2]//2,
                         self._game_state.pacman_rect[3]//2)  # 获取吃豆人的坐标
        pacman_rect = Rect(pacman_coords)  # 创建吃豆人的矩形
        if ghost_rect.colliderect(pacman_rect):  # 如果幽灵和吃豆人碰撞
            if self.is_scared:  # 如果幽灵受惊
                self.reset_ghost()  # 重置幽灵
                self.sounds.play_sound("eat_ghost")  # 播放吃幽灵的声音
                self._game_state.points += GHOST_POINT  # 增加分数
            else:
                self._game_state.is_pacman_dead = True  # 设置吃豆人死亡状态
                self.sounds.play_sound("death")  # 播放死亡声音
                wait(1000)  # 等待 1000 毫秒

    def update(self, dt):  # 定义更新方法
        self.build_bounding_boxes(self.rect_x, self.rect_y)  # 构建边界框
        self.check_is_released()  # 检查是否释放
        self._boundary_check()  # 检查边界
        self.move_ghost()  # 移动幽灵
        self.check_if_pacman_powered()  # 检查吃豆人是否有能量
        self.check_collisions()  # 检查碰撞

class Blinky(Ghost):  # 定义 Blinky 类，继承自 Ghost
    def determine_target(self):  # 定义确定目标的方法
        mode = self._game_state.ghost_mode  # 获取幽灵模式
        if mode == "scatter":  # 如果模式是散开
            target = GHOST_SCATTER_TARGETS[self.name]  # 获取散开目标
        elif mode == "chase":  # 如果模式是追逐
            pacman_rect = self._game_state.pacman_rect  # 获取吃豆人矩形
            target = self._get_idx_from_coords((pacman_rect[0], pacman_rect[1]))  # 获取目标索引
        return target  # 返回目标
    
class Pinky(Ghost):  # 定义 Pinky 类，继承自 Ghost
    def calculate_pacman_direction(self):  # 定义计算吃豆人方向的方法
        pacman_dir = self._game_state.pacman_direction  # 获取吃豆人方向
        pacman_rect = self._game_state.pacman_rect  # 获取吃豆人矩形
        pacman_rect = self._get_idx_from_coords((pacman_rect[0], 
                                                        pacman_rect[1]))  # 获取吃豆人索引
        return self.get_target_pacman_dir(pacman_rect, 
                                          pacman_dir,
                                          )  # 返回吃豆人目标方向

    def determine_target(self):  # 定义确定目标的方法
        mode = self._game_state.ghost_mode  # 获取幽灵模式
        if mode == "scatter":  # 如果模式是散开
            return GHOST_SCATTER_TARGETS[self.name]  # 返回散开目标
        elif mode == "chase":  # 如果模式是追逐
            return self.calculate_pacman_direction()  # 返回计算的吃豆人方向
            
class Inky(Ghost):  # 定义 Inky 类，继承自 Ghost
    def calculate_inky_target(self):  # 定义计算 Inky 目标的方法
        pacman_rect = self._game_state.pacman_rect  # 获取吃豆人矩形
        pacman_rect = self._get_idx_from_coords((pacman_rect[0], pacman_rect[1]))  # 获取吃豆人索引
        pacman_dir = self._game_state.pacman_direction  # 获取吃豆人方向
        blinky_cell = self._game_state.blinky_matrix_pos  # 获取 Blinky 的矩阵位置
        inky_pacman_target = self.get_target_pacman_dir(pacman_rect,
                                                        pacman_dir,
                                                        2)  # 获取 Inky 的吃豆人目标
        vec_row = inky_pacman_target[0] - blinky_cell[0]  # 计算行向量
        vec_col = inky_pacman_target[1] - blinky_cell[1]  # 计算列向量
        target_row = blinky_cell[0] + vec_row * 2  # 计算目标行
        target_col = blinky_cell[1] + vec_col * 2  # 计算目标列
        return target_row, target_col  # 返回目标

    def determine_target(self):  # 定义确定目标的方法
        mode = self._game_state.ghost_mode  # 获取幽灵模式
        if mode == "scatter":  # 如果模式是散开
            return GHOST_SCATTER_TARGETS[self.name]  # 返回散开目标
        elif mode == "chase":  # 如果模式是追逐
            return self.calculate_inky_target()  # 返回计算的 Inky 目标
            
class Clyde(Ghost):  # 定义 Clyde 类，继承自 Ghost
    def get_clyde_random_target(self):  # 定义获取 Clyde 随机目标的方法
        pacman_rect = self._game_state.pacman_rect  # 获取吃豆人矩形
        pacman_rect = self._get_idx_from_coords((pacman_rect[0], pacman_rect[1]))  # 获取吃豆人索引
        if not self.curr_pos:  # 如果没有当前坐标
            return pacman_rect  # 返回吃豆人位置
        dis = abs(pacman_rect[0] - self.curr_pos[0]) + abs(pacman_rect[1] - self.curr_pos[1])  # 计算距离
        if dis > 8:  # 如果距离大于 8
            return self.get_random_target()  # 返回随机目标
        return pacman_rect  # 返回吃豆人位置
        
    def determine_target(self):  # 定义确定目标的方法
        mode = self._game_state.ghost_mode  # 获取幽灵模式
        if mode == "scatter":  # 如果模式是散开
            return GHOST_SCATTER_TARGETS[self.name]  # 返回散开目标
        elif mode == "chase":  # 如果模式是追逐
            return self.get_clyde_random_target()  # 返回 Clyde 随机目标

class GhostManager:  # 定义 GhostManager 类
    def __init__(self,
                 screen: Surface,  # 屏幕对象
                 game_state: GameState,  # 游戏状态对象
                 matrix: list[list[str]],  # 游戏矩阵
                 ghost_matrix_pos: tuple[int, int],  # 幽灵矩阵位置
                 grid_start_pos: tuple[int, int],  # 网格起始位置
                 ):
        self.screen = screen  # 保存屏幕对象
        self.game_state = game_state  # 保存游戏状态对象
        self.matrix = matrix  # 保存游戏矩阵
        self.ghost_matrix_pos = ghost_matrix_pos  # 保存幽灵矩阵位置
        self.grid_start_pos = grid_start_pos  # 保存网格起始位置
        self.ghosts_list = []  # 初始化幽灵列表
        self.load_ghosts()  # 加载幽灵
    
    def load_ghosts(self):  # 定义加载幽灵的方法
        adder = 0  # 初始化位置偏移量
        ghosts = [('blinky', Blinky), 
                  ('pinky', Pinky), 
                  ('inky', Inky), 
                  ('clyde', Clyde)]  # 定义幽灵名称和类的列表
        for ghost_name, ghost in ghosts:  # 遍历幽灵列表
            ghost_pos = (self.ghost_matrix_pos[0], self.ghost_matrix_pos[1] + adder)  # 计算幽灵位置
            self.ghosts_list.append(ghost(ghost_name,
                                          ghost_pos,
                                          self.grid_start_pos,
                                          self.matrix,
                                          self.game_state))  # 创建幽灵对象并添加到列表
            adder += 1  # 增加位置偏移量