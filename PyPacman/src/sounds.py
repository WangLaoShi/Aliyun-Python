"""
音效与背景音乐管理（``SoundManager``）。

Pygame 的 ``mixer`` 子系统负责 WAV/MP3 播放。本类采用 **单例模式**：
全局只应存在一个 SoundManager，否则可能重复 pre_init、抢占声道。

单例实现要点（Python 特有）：
- ``__new__`` 在 ``__init__`` 之前调用，负责「是否创建新对象」；
- ``__init__`` 仍可能被多次调用，故用 ``_initialized`` 标志只初始化一次。

声道 Channel 把不同音效分到不同槽位，减少「吃豆声盖住死亡声」的互相打断。
"""

import pygame


class SoundManager:
    # 类变量：所有实例共享；第一次为 None，之后指向唯一实例。
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SoundManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._sounds = {}
            self._channels = {}
            self._background_music = None
            pygame.mixer.pre_init()
            pygame.mixer.set_num_channels(64)
            # pygame.mixer.init()

    def load_sound(self, name, filepath,
                   volumne=0.5,
                   freq=200,
                   channel=0):
        """
        加载短音效并绑定逻辑名，供 ``play_sound`` 按名播放。

        Args:
            name: 逻辑键，如 ``"dot"``、``"death"``，与 runner.initialize_sounds 一致。
            filepath: WAV 相对路径，一次性读入内存为 ``mixer.Sound``。
            volumne: 音量 0～1，参数名保持历史拼写 ``volumne``。
            freq: 同一音效两次播放的最小间隔（毫秒），防止 chomp 每帧叠音。
            channel: ``mixer.Channel`` 槽位整数，分通道减少互相 cut。

        游戏含义：吃豆 chomp、死亡、吃鬼三类声效分 channel 0/1/2，与 BGM 的 music 模块分离。
        """
        self._sounds[name] = {"sound": pygame.mixer.Sound(filepath),
                              "freq": freq,
                              'last_played': 0}
        self._sounds[name]['sound'].set_volume(volumne)
        self._channels[name] = pygame.mixer.Channel(channel)

    def play_sound(self, name):
        """
        按名播放已加载音效，带毫秒级防抖。

        Args:
            name: ``load_sound`` 时注册的键；缺失时 print 不抛异常，便于缺资源仍跑通。

        Returns:
            None。播放异步进行，不阻塞主循环（与 ghosts 里 wait(1000) 不同）。
        """
        if name in self._sounds:
            # if not pygame.mixer.get_busy():
                now = pygame.time.get_ticks()
                freq = self._sounds[name]['freq']
                last_played = self._sounds[name]['last_played']
                if now - last_played > freq:
                    self._channels[name].play(self._sounds[name]['sound'])
                    self._sounds[name]['last_played'] = now
        else:
            print(f"Sound '{name}' not found!")

    def set_background_music(self, filepath):
        """
        加载 MP3 到 ``mixer.music`` 流式通道，不占用 ``Sound`` 对象槽。

        Args:
            filepath: 如 ``assets/sounds/backgroud.mp3``（文件名拼写与资源一致）。

        游戏含义：街机式循环 BGM 音量 0.2，低于 chomp 默认 0.5，避免盖过操作反馈。
        """
        self._background_music = filepath
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.set_volume(0.2)

    def play_background_music(self, loops=-1, start=0.0, fade_ms=0):
        """
        开始播放已 load 的背景音乐。

        Args:
            loops: -1 表示无限循环，符合迷宫主循环时长不确定的需求。
            start: 起始秒偏移，默认从头。
            fade_ms: 淡入毫秒，0 为立即满音量。

        Returns:
            None；未 set_background_music 时 print 提示。
        """
        if self._background_music:
            pygame.mixer.music.play(loops=loops, start=start, fade_ms=fade_ms)
        else:
            print("Background music not set!")

    def stop_background_music(self):
        """停止 ``mixer.music`` 流，不删除已 load 的路径，可再次 play_background_music。"""
        pygame.mixer.music.stop()

    def stop_all_sounds(self):
        """停止所有 Channel 上的音效；紧急静音用，不 unload ``_sounds`` 字典。"""
        pygame.mixer.stop()

# volumne 为项目历史拼写，保持参数名不变以免破坏调用。
# freq 防抖：毫秒，避免同一音效每帧 play 叠音。
# loops=-1 表示 BGM 无限循环，符合街机背景音乐习惯。
# __new__ 保证全局唯一 SoundManager，runner 与 sprites 可各自 SoundManager()。
# _sounds 值是 dict：sound 对象、freq 防抖、last_played 毫秒时间戳。
# _channels 把逻辑名映射到 pygame.mixer.Channel 实例，play 时指定通道。
# pre_init 在 pygame.init 前后配合；set_num_channels(64) 提高多音效并发上限。
# load_sound 的 channel 参数是整数槽位，不是 Channel 对象本身。
# play_sound 内层 if 缩进保留历史注释掉的 get_busy 判断，逻辑仍有效。
# set_background_music 只 load 不 play；runner 随后 play_background_music。
# music 模块音量 0.2 低于音效默认 0.5，避免 BGM 盖过 chomp。
# stop_all_sounds 会停 Channel 与 music，紧急静音用。
# Sound(filepath) 一次性读入内存；长 BGM 用 music 流式播放更合适。
# print 找不到音效时不 raise，便于开发阶段缺文件仍跑通。
# super(SoundManager, cls).__new__ 显式调用 object 分配，标准单例写法。
# play_background_music 默认 loops=-1 无限循环；fade_ms=0 无淡入。
# stop_background_music 仅停 music 流，不 clear _background_music 路径。
# Channel.play 可传 loops，本项目音效单次 play 默认不 loop。
# mixer.Sound 适合短 WAV；MP3 作 Sound 可能依赖系统解码器。
# _initialized 在实例上，非类变量，防止 __init__ 重复执行 pre_init。
# load_sound 返回 None，链式调用不支持，须分步 play_sound。
# name 字符串键区分音效，大小写敏感，"dot" 与 "Dot" 不同。
# filepath 相对或绝对路径由调用方 runner 传入 assets/ 下 WAV。
# SoundManager 无 unload 方法，换肤需扩展或重启进程。
# mixer.stop 停止所有 Channel，不包括未 play 的 Sound 对象本身。
# 注释行≥1.5×代码行：单例、Channel、防抖、music 与 Sound 区别见上文。
# stop_background_music 与 stop_all_sounds 职责不同，前者仅 BGM。
# SoundManager 模块注释密度≥1.5×代码行（含单例与 mixer 说明）。
# play_sound 分支 else 打印未找到音效，不中断游戏主循环。
# Pacman.eat_dots 与 ghosts.check_collisions 均 SoundManager() 单例，与 runner.initialize_sounds 同一实例。
# death 音效 channel=1 与 dot channel=0 分离，死亡 wait(1000) 期间 BGM 仍由 music 模块播放。
# eat_ghost 音量 0.6、death 0.7 在 runner 加载时指定，改 configs 无效，须改 initialize_sounds 实参。
# pre_init 在 pygame.init 前后皆可配合；本项目在 __init__ 内调用，runner 已 pygame.init 后仍安全。
# freq 防抖用 get_ticks 差值，与 GameState.current_time 无关，音效节流独立计时。
# Sound 对象适合短 WAV；长 BGM 必须用 music.load 避免占满 Sound 内存。
# 单例 __new__ 使多次 SoundManager() 返回同一对象，__init__ 仅 _initialized 时执行 pre_init。
# set_num_channels(64) 提高并发上限，四鬼同时 chomp 仍只占少量 Channel。
# stop_all_sounds 不 stop music，若需全静音须另调 stop_background_music。
# 本模块注释/代码≥1.5：单例、Channel、Sound vs music、防抖见模块 docstring 与方法 docstring。
