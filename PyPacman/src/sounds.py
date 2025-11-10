import pygame  # 导入 pygame 模块，用于处理声音


class SoundManager:  # 定义声音管理类
    _instance = None  # 初始化类变量 _instance 为 None，用于实现单例模式

    def __new__(cls, *args, **kwargs):  # 定义 __new__ 方法，用于控制实例的创建
        if not cls._instance:  # 如果 _instance 为空
            cls._instance = super(SoundManager, cls).__new__(cls, *args, **kwargs)  # 创建一个新的实例
        return cls._instance  # 返回实例

    def __init__(self):  # 初始化方法
        if not hasattr(self, "_initialized"):  # 如果实例没有 _initialized 属性
            self._initialized = True  # 设置 _initialized 属性为 True
            self._sounds = {}  # 初始化声音字典
            self._channels = {}  # 初始化声道字典
            self._background_music = None  # 初始化背景音乐为 None
            pygame.mixer.pre_init()  # 预初始化混音器
            pygame.mixer.set_num_channels(64)  # 设置混音器的声道数量
            # pygame.mixer.init()  # 初始化混音器（注释掉）
    
    def load_sound(self, name, filepath, 
                   volumne=0.5, 
                   freq=200,
                   channel=0):  # 定义加载声音的方法
        """Loads a sound effect and assigns it a name."""  # 加载一个声音效果并分配一个名称
        self._sounds[name] = {"sound": pygame.mixer.Sound(filepath),  # 创建声音对象并存储在字典中
                              "freq": freq,  # 存储播放频率
                              'last_played': 0}  # 存储上次播放时间
        self._sounds[name]['sound'].set_volume(volumne)  # 设置声音的音量
        self._channels[name] = pygame.mixer.Channel(channel)  # 创建声道对象并存储在字典中

    def play_sound(self, name):  # 定义播放声音的方法
        """Plays a specific sound effect."""  # 播放特定的声音效果
        if name in self._sounds:  # 如果声音名称在声音字典中
            # if not pygame.mixer.get_busy():
                now = pygame.time.get_ticks()  # 获取当前时间
                freq = self._sounds[name]['freq']  # 获取声音的播放频率
                last_played = self._sounds[name]['last_played']  # 获取声音的上次播放时间
                if now - last_played > freq:  # 如果当前时间与上次播放时间的差大于频率
                    self._channels[name].play(self._sounds[name]['sound'])  # 播放声音
                    self._sounds[name]['last_played'] = now  # 更新上次播放时间
        else:
            print(f"Sound '{name}' not found!")  # 打印声音未找到的错误信息

    def set_background_music(self, filepath):  # 定义设置背景音乐的方法
        """Loads and sets the background music."""  # 加载并设置背景音乐
        self._background_music = filepath  # 存储背景音乐的文件路径
        pygame.mixer.music.load(filepath)  # 加载背景音乐文件
        pygame.mixer.music.set_volume(0.2)  # 设置背景音乐的音量

    def play_background_music(self, loops=-1, start=0.0, fade_ms=0):  # 定义播放背景音乐的方法
        """Starts playing the background music."""  # 开始播放背景音乐
        if self._background_music:  # 如果背景音乐已设置
            pygame.mixer.music.play(loops=loops, start=start, fade_ms=fade_ms)  # 播放背景音乐
        else:
            print("Background music not set!")  # 打印背景音乐未设置的错误信息

    def stop_background_music(self):  # 定义停止背景音乐的方法
        """Stops the background music."""  # 停止背景音乐
        pygame.mixer.music.stop()  # 停止播放背景音乐

    def stop_all_sounds(self):  # 定义停止所有声音的方法
        """Stops all currently playing sounds."""  # 停止所有当前播放的声音
        pygame.mixer.stop()  # 停止所有声音
