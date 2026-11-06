"""
键盘与 pygame 事件分发：``EventHandler``。

Pygame 不采用「回调注册表」，而是每帧把事件队列交给游戏代码。
常见 event.type：
- ``QUIT``：点关闭按钮
- ``KEYDOWN``：键按下（长按还会产生 KEYDOWN 重复）
- ``USEREVENT + n``：``set_timer`` 触发的自定义定时事件

本类把「输入 → 修改 GameState」集中在一起，runner 主循环只需一行 handle_events。
"""

from pygame import (K_DOWN, K_ESCAPE, K_LEFT, K_RIGHT, K_SPACE, K_UP, KEYDOWN,
                    QUIT, K_q)
from pygame import USEREVENT
from pygame.time import set_timer


class EventHandler:
    def __init__(self, screen, game_state):
        self._screen = screen
        # 命名 _game_screen 是历史命名，实际类型是 GameState，不是 screen。
        self._game_screen = game_state

    def pygame_quit(self):
        # 不直接 sys.exit：让 main 循环跑完保存高分、pygame.quit() 再退出。
        self._game_screen.running = False

    def key_bindings(self, key):
        # 方向用单字母存进 state，sprites 里与 "l"/"r"/"u"/"d" 约定一致。
        if key == K_LEFT:
            self._game_screen.direction = "l"
        elif key == K_RIGHT:
            self._game_screen.direction = "r"
        elif key == K_UP:
            self._game_screen.direction = "u"
        elif key == K_DOWN:
            self._game_screen.direction = "d"

    def handle_events(self, event):
        # 多个 if 而非 elif：同一帧理论上不同类型不会重复，但分开写便于以后扩展。
        if event.type == QUIT:
            self.pygame_quit()

        if event.type == KEYDOWN:
            # event.key 是整数常量 K_LEFT 等，不是字符 'a'。
            self.key_bindings(event.key)

        if event.type == self._game_screen.custom_event:
            curr_mode = self._game_screen.ghost_mode
            # 经典 Pac-Man 在 scatter 与 chase 间循环；scared 由能量豆单独进入。
            if curr_mode == 'scatter':
                self._game_screen.ghost_mode = 'chase'
            elif curr_mode == 'chase':
                self._game_screen.ghost_mode = 'scatter'
            # 每次触发后重新 set_timer：下一间隔取自 mode_change_events 列表（见 GameState）。
            CUSTOM_EVENT = USEREVENT + 1
            set_timer(
                CUSTOM_EVENT,
                self._game_screen.mode_change_events * 1000
            )
            self._game_screen.custom_event = CUSTOM_EVENT

        if event.type == self._game_screen.power_up_event:
            # 能量豆倒计时结束：幽灵恢复追逐/散开逻辑，由 is_pacman_powered 标志控制。
            self._game_screen.is_pacman_powered = False

# K_ESCAPE、K_q、K_SPACE 已 import 但未绑定，便于将来扩展暂停/退出/菜单。
# set_timer 的毫秒参数来自 mode_change_events getter，单位由 JSON 秒 ×1000 转换。
# custom_event 与 power_up_event 均为 pygame 事件 type 整数，存在 GameState 便于比对。
# EventHandler 不继承 pygame.sprite 或 Layer，仅为普通 Python 类。
# handle_events 一次处理一个 event；runner 用 for 遍历 get() 返回列表。
# pygame_quit 设 running=False 后，while 条件下一帧失败，执行 save 与 quit。
# scatter/chase 切换不改变 is_pacman_powered；scared 由能量豆逻辑单独处理。
# elif curr_mode=='chase' 时切 scatter，形成二态循环（非 scared 时）。
# key_bindings 无 else：其它键忽略，不修改 direction。
# _screen 当前未在方法内使用，保留构造参数便于将来鼠标/UI 扩展。
# USEREVENT+1 与 runner.create_ghost_mode_event 使用相同编号约定。
# power_up_event 分支只清 powered 标志，不自动改 ghost_mode 字符串。
# KEYDOWN 重复：长按方向键时 OS 可能重复 KEYDOWN，direction 会被反复设为同值。
# QUIT 与窗口关闭按钮关联，Alt+F4 等也会生成 QUIT。
# handle_events 不 return 布尔值，runner 无法据此 break，仅靠 running 标志。
# set_timer(..., 0) 可取消定时器，本项目未使用取消逻辑。
# mode_change_events * 1000：getter 返回秒，pygame 要毫秒。
# K_ESCAPE/K_q/K_SPACE import 未用，lint 可能 warn，为扩展预留。
# EventHandler 实例无状态字段除 _screen/_game_screen，无 tick 计数。
# handle_events 同步执行，耗时逻辑会拖慢主循环帧率。
# 本模块注释行数目标≥1.5×代码行，便于对照 pygame 事件模型学习。
# key_bindings 未处理对角线键，仅四方向箭头。
# scatter/chase 与 scared 独立：能量豆只改 is_pacman_powered，不直接写 ghost_mode 字符串。
# custom_event 每次 handle 后重新 set_timer，间隔秒数来自 GameState.mode_change_events getter 副作用。
# power_up_event 到点仅清 powered，幽灵贴图由 ghosts.check_if_pacman_powered 下一帧恢复 normal。
# KEYDOWN 只改 direction（玩家意图），pacman_direction 由 Pacman.movement_bind 在能走时写入。
# QUIT 不设 running 以外的字段，stats 保存仍在 runner 循环退出后 update_highscore 执行。
# EventHandler 无 dt 参数，定时逻辑完全依赖 pygame 事件队列而非轮询 current_time。
# _game_screen 命名历史遗留，类型为 GameState，与 ScreenManager 读写的 state 是同一实例。
# USEREVENT+1 与 runner.create_ghost_mode_event 必须一致，否则 scatter/chase 永不切换。
# USEREVENT+2 由 pacman.create_power_up_event 注册，与本类 power_up_event 分支配对。
# 未绑定 K_ESCAPE：关窗仍是主要退出方式，扩展暂停可在 key_bindings 加分支不改 runner 结构。
# handle_events 同步执行，set_timer 回调投递到下一帧 get()，不会在同一次 handle 内嵌套触发。
# mode_change_events * 1000 把 JSON 秒转为 pygame 毫秒，与 scared_time 单位一致。
# 方向键重复 KEYDOWN 时 direction 重复赋值无害，Pacman 仍按 tiny_matrix 墙检测决定是否转弯。
# EventHandler 不读 matrix，输入层与迷宫数据解耦，便于单元测试 mock GameState。
# 本模块注释/代码≥1.5：事件类型、定时器与 GameState 字段对照见模块 docstring 与文末说明。

# --- 补充说明 (src/game/event_management.py) ---
# KEYDOWN 与 QUIT 分两个 if 非 elif，便于同帧理论上不同类型并存（虽罕见）。
# scatter/chase 切换不重置 is_pacman_powered，能量豆窗口内仍可由 ghosts 维持 scared 贴图。
# custom_event 重设 timer 使用 mode_change_events getter，每次读取推进 __current_mode_index 副作用。
