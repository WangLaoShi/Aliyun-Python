from pygame import (K_DOWN, K_ESCAPE, K_LEFT, K_RIGHT, K_SPACE, K_UP, KEYDOWN,
                    QUIT, K_q)  # 从 pygame 导入需要的键盘事件常量
from pygame import USEREVENT  # 导入用户自定义事件常量
from pygame.time import set_timer  # 导入设置计时器的函数

class EventHandler:  # 定义事件处理类
    def __init__(self, screen, game_state):  # 初始化方法，接收屏幕和游戏状态对象
        self._screen = screen  # 保存屏幕对象
        self._game_screen = game_state  # 保存游戏状态对象

    def pygame_quit(self):  # 定义退出游戏的方法
        self._game_screen.running = False  # 设置游戏状态为不运行

    def key_bindings(self, key):  # 定义键盘绑定方法，接收按键参数
        if key == K_LEFT:  # 如果按下左键
            self._game_screen.direction = "l"  # 设置游戏方向为左
        elif key == K_RIGHT:  # 如果按下右键
            self._game_screen.direction = "r"  # 设置游戏方向为右
        elif key == K_UP:  # 如果按下上键
            self._game_screen.direction = "u"  # 设置游戏方向为上
        elif key == K_DOWN:  # 如果按下下键
            self._game_screen.direction = "d"  # 设置游戏方向为下

    def handle_events(self, event):  # 定义事件处理方法，接收事件参数
        if event.type == QUIT:  # 如果事件类型是退出
            self.pygame_quit()  # 调用退出游戏的方法

        if event.type == KEYDOWN:  # 如果事件类型是按键按下
            self.key_bindings(event.key)  # 调用键盘绑定方法
        
        if event.type == self._game_screen.custom_event:  # 如果事件类型是自定义事件
            curr_mode = self._game_screen.ghost_mode  # 获取当前幽灵模式
            if curr_mode == 'scatter':  # 如果当前模式是散开
                self._game_screen.ghost_mode = 'chase'  # 切换模式为追逐
            elif curr_mode == 'chase':  # 如果当前模式是追逐
                self._game_screen.ghost_mode = 'scatter'  # 切换模式为散开
            CUSTOM_EVENT = USEREVENT + 1  # 定义新的自定义事件
            set_timer(CUSTOM_EVENT, 
                                self._game_screen.mode_change_events * 1000)  # 设置计时器以触发新的自定义事件
            self._game_screen.custom_event = CUSTOM_EVENT  # 更新游戏状态中的自定义事件
        
        if event.type == self._game_screen.power_up_event:  # 如果事件类型是能量提升事件
            self._game_screen.is_pacman_powered = False  # 设置吃豆人不再有能量提升效果

