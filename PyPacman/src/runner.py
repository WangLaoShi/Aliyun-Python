import sys  # 导入系统模块，用于系统退出

import pygame  # 导入 pygame 模块，用于游戏开发
import json  # 导入 JSON 模块，用于处理 JSON 文件

from src.configs import *  # 从配置文件中导入所有配置
from src.game.event_management import EventHandler  # 导入事件管理类
from src.game.state_management import GameState  # 导入游戏状态管理类
from src.gui.screen_management import ScreenManager  # 导入屏幕管理类
from src.sounds import SoundManager  # 导入声音管理类
from src.log_handle import get_logger  # 导入日志记录器
logger = get_logger(__name__)  # 获取当前模块的日志记录器

class GameRun:  # 定义游戏运行类
    def __init__(self):  # 初始化方法
        logger.info("About to initialize pygame")  # 记录初始化 pygame 的日志
        pygame.init()  # 初始化 pygame
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # 设置游戏窗口大小
        pygame.display.set_caption("Py-Pacman")  # 设置游戏窗口标题
        logger.info("pygame initialized")  # 记录 pygame 初始化完成的日志
        self.game_state = GameState()  # 创建游戏状态对象
        logger.info("game state object created")  # 记录游戏状态对象创建的日志
        self.events = EventHandler(self.screen, self.game_state)  # 创建事件处理对象
        logger.info("event handler object created")  # 记录事件处理对象创建的日志
        self.all_sprites = pygame.sprite.Group()  # 创建精灵组
        self.gui = ScreenManager(self.screen, self.game_state, self.all_sprites)  # 创建屏幕管理对象
        logger.info("screen manager object created")  # 记录屏幕管理对象创建的日志

    def initialize_highscore(self):  # 定义初始化最高分的方法
        with open("levels/stats.json") as fp:  # 打开存储最高分的 JSON 文件
            stats = json.load(fp)  # 加载 JSON 文件内容
            self.game_state.highscore = stats['highscore']  # 设置游戏状态中的最高分
            self.game_state.mins_played = stats['mins_played']  # 设置游戏状态中的已玩分钟数
    
    def create_ghost_mode_event(self):  # 定义创建幽灵模式事件的方法
        CUSTOM_EVENT = pygame.USEREVENT + 1  # 定义自定义事件
        pygame.time.set_timer(CUSTOM_EVENT, 
                              self.game_state.mode_change_events * 1000)  # 设置计时器以触发自定义事件
        self.game_state.custom_event = CUSTOM_EVENT  # 更新游戏状态中的自定义事件

    def initialize_sounds(self):  # 定义初始化声音的方法
        sound_manager = SoundManager()  # 创建声音管理器对象
        sound_manager.load_sound("dot", "assets/sounds/pacman_chomp.wav", channel=0)  # 加载吃小点的声音
        sound_manager.load_sound("death","assets/sounds/pacman_death.wav", 0.7, 500, 1)  # 加载死亡的声音
        sound_manager.load_sound("eat_ghost","assets/sounds/pacman_eatghost.wav", 0.6, 100, 2)  # 加载吃幽灵的声音
        sound_manager.set_background_music("assets/sounds/backgroud.mp3")  # 设置背景音乐
        sound_manager.play_background_music()  # 播放背景音乐

    def check_highscores(self):  # 定义检查最高分的方法
        if self.game_state.points > self.game_state.highscore:  # 如果当前分数大于最高分
            self.game_state.highscore = self.game_state.points  # 更新最高分

    def update_highscore(self):  # 定义更新最高分的方法
        with open("levels/stats.json", 'w') as fp:  # 打开存储最高分的 JSON 文件
            json.dump({"highscore":self.game_state.highscore,
                       "mins_played": self.game_state.mins_played}, fp, indent=4)  # 将最高分和已玩分钟数写入文件
            
    def main(self):  # 定义主循环方法
        clock = pygame.time.Clock()  # 创建时钟对象
        dt = None  # 初始化时间增量为 None
        self.create_ghost_mode_event()  # 创建幽灵模式事件
        self.initialize_sounds()  # 初始化声音
        self.initialize_highscore()  # 初始化最高分
        while self.game_state.running:  # 当游戏状态为运行时
            self.game_state.current_time = pygame.time.get_ticks()  # 获取当前时间
            for event in pygame.event.get():  # 遍历事件队列
                self.events.handle_events(event)  # 处理事件
            self.screen.fill(Colors.BLACK)  # 用黑色填充屏幕
            self.gui.draw_screens()  # 绘制屏幕
            self.all_sprites.draw(self.screen)  # 绘制所有精灵
            self.all_sprites.update(dt)  # 更新所有精灵
            self.check_highscores()  # 检查最高分
            pygame.display.flip()  # 更新屏幕显示
            dt = clock.tick(self.game_state.fps)  # 控制帧率并获取时间增量
            dt /= 100  # 将时间增量缩小 100 倍
        self.update_highscore()  # 更新最高分
        pygame.quit()  # 退出 pygame
        sys.exit()  # 退出系统
