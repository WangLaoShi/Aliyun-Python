import json  # 导入 JSON 模块，用于处理 JSON 文件

from src.configs import *  # 从配置文件中导入所有配置
from src.sprites.pacman import Pacman  # 导入 Pacman 类
from src.sprites.ghosts import GhostManager  # 导入 GhostManager 类
from src.utils.coord_utils import (get_coords_from_idx, place_elements_offset,
                                   precompute_matrix_coords)  # 导入坐标工具函数
from src.utils.draw_utils import (draw_circle, draw_debug_rects, draw_rect)  # 导入绘图工具函数
from src.log_handle import get_logger  # 导入日志记录器
logger = get_logger(__name__)  # 获取当前模块的日志记录器

class PacmanGrid:  # 定义 PacmanGrid 类
    def __init__(self, screen, game_state):  # 初始化方法，接收屏幕和游戏状态对象
        logger.info("initializing pacman grid")  # 记录初始化日志
        self.function_mapper = {  # 定义功能映射字典
            "void": self.draw_void,  # 空白区域映射到 draw_void 方法
            "wall": self.draw_wall,  # 墙壁映射到 draw_wall 方法
            "dot": self.draw_dot,  # 小点映射到 draw_dot 方法
            "spoint": self.draw_special_point,  # 特殊点映射到 draw_special_point 方法
            "power": self.draw_power,  # 能量点映射到 draw_power 方法
            "null": self.draw_void,  # 空值映射到 draw_void 方法
            "elec": self.draw_elec,  # 电力点映射到 draw_elec 方法
        }
        self._screen = screen  # 保存屏幕对象
        self._game_state = game_state  # 保存游戏状态对象
        self._level_number = self._game_state.level  # 获取当前游戏等级
        self.load_level(self._level_number)  # 加载当前等级
        logger.info("level loaded")  # 记录等级加载日志
        self.pacman = Pacman(  # 创建 Pacman 对象
            self._screen,
            self._game_state,
            self._matrix,
            self._pacman_pos,
            (self.start_x, self.start_y)
        )
        self.ghost = GhostManager(  # 创建 GhostManager 对象
            self._screen,
            self._game_state,
            self._matrix,
            self.ghost_den,
            (self.start_x, self.start_y)
        )
        logger.info("pacman created")  # 记录 Pacman 创建日志
        
    def get_json(self, path):  # 定义获取 JSON 数据的方法
        with open(path) as fp:  # 打开指定路径的文件
            payload = json.load(fp)  # 加载 JSON 数据
        return payload  # 返回加载的数据

    def load_level(self, level_number):  # 定义加载等级的方法
        level_path = f"levels/level{level_number}.json"  # 构建等级文件路径
        level_json = self.get_json(level_path)  # 获取等级 JSON 数据
        num_rows = level_json["num_rows"]  # 获取行数
        num_cols = level_json["num_cols"]  # 获取列数
        self.ghost_den = level_json['ghost_den']  # 获取幽灵巢穴位置
        self._matrix = level_json["matrix"]  # 获取矩阵数据
        self._pacman_pos = level_json["pacman_start"]  # 获取 Pacman 起始位置
        self.elec_pos = level_json['elec']  # 获取电力点位置
        self.mode_change_times = level_json['scatter_times']  # 获取模式切换时间
        self.power_up_time = level_json['power_up_time']  # 获取能量提升时间
        self._game_state.scared_time = self.power_up_time  # 设置游戏状态中的幽灵受惊时间
        self._game_state.mode_change_events = self.mode_change_times  # 设置游戏状态中的模式切换事件
        self.start_x, self.start_y = place_elements_offset(  # 计算元素偏移位置
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            CELL_SIZE[0] * num_cols,
            CELL_SIZE[0] * num_rows,
            0.5,
            0.5,
        )
        self._coord_matrix = precompute_matrix_coords(  # 预计算矩阵坐标
            self.start_x, self.start_y, CELL_SIZE[0], num_rows, num_cols
        )
        self.num_rows = num_rows  # 保存行数
        self.num_cols = num_cols  # 保存列数

    def draw_void(self, **kwargs):  # 定义绘制空白区域的方法
        pass  # 空方法，什么都不做

    def draw_wall(self, **kwargs):  # 定义绘制墙壁的方法
        draw_rect(  # 调用绘制矩形函数
            kwargs["x"],  # 矩形的 x 坐标
            kwargs["y"],  # 矩形的 y 坐标
            kwargs["w"],  # 矩形的宽度
            kwargs["h"],  # 矩形的高度
            self._screen,  # 绘制的屏幕
            Colors.WALL_BLUE,  # 墙壁的颜色
        )

    def draw_dot(self, **kwargs):  # 定义绘制小点的方法
        dot_x = kwargs["x"] + kwargs["w"]  # 计算小点的 x 坐标
        dot_y = kwargs["y"] + kwargs["h"]  # 计算小点的 y 坐标
        draw_rect(dot_x, dot_y, 5, 5, self._screen, Colors.WHITE)  # 绘制小点

    def draw_special_point(self):  # 定义绘制特殊点的方法
        pass  # 空方法，什么都不做

    def draw_power(self, **kwargs):  # 定义绘制能量点的方法
        circle_x = kwargs["x"] + kwargs["w"]  # 计算能量点的 x 坐标
        circle_y = kwargs["y"] + kwargs["h"]  # 计算能量点的 y 坐标
        draw_circle(circle_x, circle_y, 7, self._screen, Colors.YELLOW)  # 绘制能量点

    def draw_elec(self, **kwargs):  # 定义绘制电力点的方法
        draw_rect(kwargs["x"], kwargs["y"], kwargs["w"], 1, self._screen, Colors.RED)  # 绘制电力点

    def draw_level(self):  # 定义绘制等级的方法
        curr_x, curr_y = self.start_x, self.start_y  # 初始化当前坐标为起始坐标
        for _, row in enumerate(self._matrix):  # 遍历矩阵的每一行
            for _, col in enumerate(row):  # 遍历行中的每一列
                draw_func = self.function_mapper[col]  # 获取对应的绘制函数
                draw_func(x=curr_x, y=curr_y, w=CELL_SIZE[0], h=CELL_SIZE[0])  # 调用绘制函数
                curr_x += CELL_SIZE[0]  # 更新 x 坐标
            curr_x = self.start_x  # 重置 x 坐标
            curr_y += CELL_SIZE[0]  # 更新 y 坐标

    def reset_stage(self):  # 定义重置关卡的方法
        self.pacman = Pacman(  # 重新创建 Pacman 对象
            self._screen,
            self._game_state,
            self._matrix,
            self._pacman_pos,
            (self.start_x, self.start_y)
        )
        self.ghost = GhostManager(  # 重新创建 GhostManager 对象
            self._screen,
            self._game_state,
            self._matrix,
            self.ghost_den,
            (self.start_x, self.start_y)
        )
        
    def draw_outliners(self):  # 定义绘制轮廓的方法
        draw_debug_rects(  # 绘制调试矩形
            self.start_x, self.start_y, 128, 140, 5, Colors.GREEN, self._screen
        )
        draw_debug_rects(  # 绘制调试矩形
            self.start_x,
            self.start_y,
            self.num_rows,
            self.num_cols,
            CELL_SIZE[0],
            Colors.BLUE,
            self._screen,
        )
