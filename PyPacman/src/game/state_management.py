from src.configs import DOT_POINT  # 从配置文件中导入 DOT_POINT 常量

class GameState:  # 定义游戏状态类
    def __init__(self):  # 初始化方法
        self.__level = 1  # 初始化游戏等级为 1
        self.__running = True  # 初始化游戏运行状态为 True
        self.__fps = 60  # 初始化帧率为 60
        self.__direction = ""  # 初始化方向为空字符串
        self.__current_time = None  # 初始化当前时间为 None
        self.__pacman_rect = None  # 初始化吃豆人的矩形位置为 None
        self.__ghost_pos = {}  # 初始化幽灵位置字典为空
        self.__is_loaded = False  # 初始化加载状态为 False
        self.__is_pacman_powered = False  # 初始化吃豆人能量状态为 False
        self._ghost_mode = 'scatter'  # 初始化幽灵模式为 'scatter'
        self._mode_change_events = None  # 初始化模式改变事件为 None
        self.__current_mode_index = 0  # 初始化当前模式索引为 0
        self._custom_event = None  # 初始化自定义事件为 None
        self._pacman_direction = None  # 初始化吃豆人方向为 None
        self._blinky_matrix_pos = None  # 初始化 Blinky 的矩阵位置为 None
        self._scared_time = None  # 初始化幽灵受惊时间为 None
        self._power_up_event = None  # 初始化能量提升事件为 None
        self._power_event_trigger_time = None  # 初始化能量事件触发时间为 None
        self._is_pacman_dead = False  # 初始化吃豆人死亡状态为 False
        self._highscore = 0  # 初始化最高分为 0
        self._mins_played = 0  # 初始化游戏时间为 0 分钟
        self._points = -DOT_POINT  # 初始化分数为负的 DOT_POINT
        self._level_complete = False  # 初始化关卡完成状态为 False

    @property
    def level_complete(self):  # 定义 level_complete 属性的 getter 方法
        return self._level_complete  # 返回关卡完成状态
    
    @level_complete.setter
    def level_complete(self, val):  # 定义 level_complete 属性的 setter 方法
        self._level_complete = val  # 设置关卡完成状态

    @property
    def points(self):  # 定义 points 属性的 getter 方法
        return self._points  # 返回当前分数
    
    @points.setter
    def points(self, val):  # 定义 points 属性的 setter 方法
        self._points = val  # 设置当前分数

    @property
    def highscore(self):  # 定义 highscore 属性的 getter 方法
        return self._highscore  # 返回最高分
    
    @highscore.setter
    def highscore(self, val):  # 定义 highscore 属性的 setter 方法
        self._highscore = val  # 设置最高分
    
    @property
    def mins_played(self):  # 定义 mins_played 属性的 getter 方法
        return self._mins_played  # 返回游戏时间（分钟）
    
    @mins_played.setter
    def mins_played(self, val):  # 定义 mins_played 属性的 setter 方法
        self._mins_played = val  # 设置游戏时间（分钟）

    @property
    def is_pacman_dead(self):  # 定义 is_pacman_dead 属性的 getter 方法
        return self._is_pacman_dead  # 返回吃豆人死亡状态
    
    @is_pacman_dead.setter
    def is_pacman_dead(self, val):  # 定义 is_pacman_dead 属性的 setter 方法
        self._is_pacman_dead = val  # 设置吃豆人死亡状态

    @property
    def power_event_trigger_time(self):  # 定义 power_event_trigger_time 属性的 getter 方法
        return self._power_event_trigger_time  # 返回能量事件触发时间
    
    @power_event_trigger_time.setter
    def power_event_trigger_time(self, val):  # 定义 power_event_trigger_time 属性的 setter 方法
        self._power_event_trigger_time = val  # 设置能量事件触发时间

    @property
    def power_up_event(self):  # 定义 power_up_event 属性的 getter 方法
        return self._power_up_event  # 返回能量提升事件
    
    @power_up_event.setter
    def power_up_event(self, val):  # 定义 power_up_event 属性的 setter 方法
        self._power_up_event = val  # 设置能量提升事件

    @property
    def scared_time(self):  # 定义 scared_time 属性的 getter 方法
        return self._scared_time  # 返回幽灵受惊时间
    
    @scared_time.setter
    def scared_time(self, val):  # 定义 scared_time 属性的 setter 方法
        self._scared_time = val  # 设置幽灵受惊时间

    @property
    def blinky_matrix_pos(self):  # 定义 blinky_matrix_pos 属性的 getter 方法
        return self._blinky_matrix_pos  # 返回 Blinky 的矩阵位置
    
    @blinky_matrix_pos.setter
    def blinky_matrix_pos(self, val):  # 定义 blinky_matrix_pos 属性的 setter 方法
        self._blinky_matrix_pos = val  # 设置 Blinky 的矩阵位置

    @property
    def pacman_direction(self):  # 定义 pacman_direction 属性的 getter 方法
        return self._pacman_direction  # 返回吃豆人方向
    
    @pacman_direction.setter
    def pacman_direction(self, val):  # 定义 pacman_direction 属性的 setter 方法
        self._pacman_direction = val  # 设置吃豆人方向

    @property
    def custom_event(self):  # 定义 custom_event 属性的 getter 方法
        return self._custom_event  # 返回自定义事件
    
    @custom_event.setter
    def custom_event(self, val):  # 定义 custom_event 属性的 setter 方法
        self._custom_event = val  # 设置自定义事件

    @property
    def mode_change_events(self):  # 定义 mode_change_events 属性的 getter 方法
        if self.__current_mode_index >= len(self._mode_change_events):  # 如果当前模式索引超出事件列表长度
            curr_event = self._mode_change_events[-1]  # 获取最后一个模式事件
        else:
            curr_event = self._mode_change_events[self.__current_mode_index]  # 获取当前索引的模式事件
            self.__current_mode_index += 1  # 增加当前模式索引
        return curr_event  # 返回当前模式事件

    @mode_change_events.setter
    def mode_change_events(self, val):  # 定义 mode_change_events 属性的 setter 方法
        self._mode_change_events = val  # 设置模式改变事件列表

    @property
    def ghost_mode(self):  # 定义 ghost_mode 属性的 getter 方法
        return self._ghost_mode  # 返回幽灵模式
    
    @ghost_mode.setter
    def ghost_mode(self, value):  # 定义 ghost_mode 属性的 setter 方法
        if value not in ['scatter', 'chase', 'scared']:  # 如果设置的模式不在允许的列表中
            raise ValueError("Only scatter, scared or chase modes are available")  # 抛出异常
        self._ghost_mode = value  # 设置幽灵模式

    @property
    def is_pacman_powered(self):  # 定义 is_pacman_powered 属性的 getter 方法
        return self.__is_pacman_powered  # 返回吃豆人能量状态
    
    @is_pacman_powered.setter
    def is_pacman_powered(self, val):  # 定义 is_pacman_powered 属性的 setter 方法
        self.__is_pacman_powered = val  # 设置吃豆人能量状态
        
    @property
    def is_loaded(self):  # 定义 is_loaded 属性的 getter 方法
        return self.__is_loaded  # 返回加载状态

    def get_ghost_pos(self, name):  # 定义获取幽灵位置的方法
        return self.__ghost_pos.get(name)  # 返回指定名称的幽灵位置
    
    def set_ghost_pos(self, name, val):  # 定义设置幽灵位置的方法
        self.__ghost_pos[name] = val  # 设置指定名称的幽灵位置

    @property
    def pacman_rect(self):  # 定义 pacman_rect 属性的 getter 方法
        return self.__pacman_rect  # 返回吃豆人的矩形位置
    
    @pacman_rect.setter
    def pacman_rect(self, rect):  # 定义 pacman_rect 属性的 setter 方法
        self.__pacman_rect = rect  # 设置吃豆人的矩形位置
    
    @property
    def current_time(self):  # 定义 current_time 属性的 getter 方法
        return self.__current_time  # 返回当前时间
    
    @current_time.setter
    def current_time(self, val):  # 定义 current_time 属性的 setter 方法
        self.__current_time = val  # 设置当前时间

    @property
    def direction(self):  # 定义 direction 属性的 getter 方法
        return self.__direction  # 返回当前方向

    @direction.setter
    def direction(self, value):  # 定义 direction 属性的 setter 方法
        if value not in ["r", "l", "u", "d", ""]:  # 如果设置的方向不在允许的列表中
            raise ValueError("Unknown direction")  # 抛出异常
        self.__direction = value  # 设置当前方向

    @property
    def level(self):  # 定义 level 属性的 getter 方法
        return self.__level  # 返回当前等级

    @level.setter
    def level(self, value):  # 定义 level 属性的 setter 方法
        self.__level = value  # 设置当前等级

    @property
    def running(self):  # 定义 running 属性的 getter 方法
        return self.__running  # 返回游戏运行状态

    @running.setter
    def running(self, value):  # 定义 running 属性的 setter 方法
        self.__running = value  # 设置游戏运行状态

    @property
    def fps(self):  # 定义 fps 属性的 getter 方法
        return self.__fps  # 返回帧率

    @fps.setter
    def fps(self, value):  # 定义 fps 属性的 setter 方法
        self.__fps = value  # 设置帧率
