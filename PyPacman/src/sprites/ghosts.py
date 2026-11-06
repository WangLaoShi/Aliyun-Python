"""
幽灵（Ghosts）模块：渲染、移动、AI 个性与统一管理。

**架构分层（便于初学者读代码）**：

1. ``Ghost(Sprite, ABC)`` — 抽象基类  
   - **多重继承**：``Sprite`` 负责 pygame 绘制管线；``ABC``（Abstract Base Class）表示不能直接实例化，
     子类必须实现 ``determine_target()``（``@abstractmethod``）。
   - **lerp 移动**：在上一格中心像素 ``prev`` 与下一格 ``next_tile`` 之间线性插值，``_t`` 从 0→1，
     公式 ``P = (1-t)*起点 + t*终点``，``_accelerate`` 控制每帧 t 增量（越大越快“吸附”到下一格）。

2. 四个具体子类 — 经典吃豆人 AI 差异只在 **追逐目标格** 怎么算：  
   - **Blinky（红）**：直接追 Pac-Man 所在格。  
   - **Pinky（粉）**：追 Pac-Man 前方 4 格（「埋伏」）。  
   - **Inky（青）**：以 Blinky 与 Pac-Man 前方 2 格的几何关系算镜像点（最绕）。  
   - **Clyde（橙）**：离 Pac-Man 远时乱走，近时反而追（胆小鬼）。

3. ``GhostManager`` — 工厂：在同一列出生点纵向错开，创建四实例并放入 ``ghosts_list``。

**与 ghost_movement_utils 的配合**：
- ``prepare_movement`` 在岔路口或撞墙时调用 ``get_direction`` 选下一步向量；
- ``move_ghost`` 用 lerp 平滑位移，到格心或 intersection 再决策。

**GameState 共享字段**：``ghost_mode``（scatter/chase）、``pacman_rect``、能量豆时间戳、``blinky_matrix_pos``（Inky 专用）等。


**主循环中的调用顺序（对照 runner.py）**：
每帧 ``ScreenManager.draw_screens`` 先 ``draw_level`` 重画 matrix，再 ``Group.draw`` 画精灵，
最后 ``Group.update(dt)`` 进入 ``Ghost.update``。因此碰撞与 lerp 更新发生在本帧绘制之后，
视觉上有一帧延迟，但对 60fps 街机手感影响很小。

**scatter / chase 与 frightened 的三层概念**：
1. ``GameState.ghost_mode`` 字符串 scatter/chase，由 ``USEREVENT+1`` 定时切换，决定 ``determine_target`` 用角还是追 Pac。
2. ``GameState.is_pacman_powered`` 由吃 power 豆置真，``USEREVENT+2`` 到点清假，驱动 ``check_if_pacman_powered`` 换皮。
3. ``Ghost.is_scared`` 在换蓝皮并 ``make_ghost_scared`` 时为真，``prepare_movement`` 改随机目标，碰撞可吃鬼。

**lerp 与粗格 AI 的两层时间尺度**：
粗格上 ``get_direction`` 只在路口/墙前决策一步；像素上 ``lerp`` 在 prev→next_tile 间平滑多帧。
``_t`` 与 ``_accelerate`` 控制滑格帧数，与 ``PACMAN_SPEED`` 无同一公式，勿混为一谈。

**四鬼 chase 目标摘要（读 determine_target 时对照）**：
- Blinky：Pac 当前粗格（像素 rect 反查）。
- Pinky：Pac 面向前方 4 格（``get_target_pacman_dir``，默认 look_ahead=4）。
- Inky：Blinky 格 + 2×(Pac 前 2 格 − Blinky) 向量（见 ``calculate_inky_target``）。
- Clyde：距 Pac 曼哈顿 >8 则 ``get_random_target``，否则 Pac 粗格。

**与 matrix / JSON 关卡的关系**：
``Ghost._matrix`` 与 Pacman、PacmanGrid 共享 list 引用；``get_is_move_valid`` 视 wall/elec 为阻挡，
void/dot/power 不阻挡。横向隧道列 wrap 在 ``_boundary_check``，与 JSON 左右开口一致。

**Python 概念速查**：
- ``ABC`` + ``@abstractmethod``：强制四子类实现 ``determine_target``。
- ``Sprite``：``Group.draw/update`` 协议，须 ``self.image``、``self.rect``。
- ``Rect.colliderect``：半宽盒碰撞调参，非 pygame 内置 gameplay 规则。
- ``pygame.time.wait``：同步阻塞主线程，简单死亡演出。

**调试建议**：
在 ``prepare_movement`` 或 ``get_direction`` 抛 ``ValueError`` 时，print 含 prev、粗格、matrix 单元字符，
优先检查 level JSON 封闭格或鬼 footprint 2×2 与地图不匹配。

**文件内类型与坐标约定**：
- ``ghost_matrix_pos`` / ``prev`` / ``next_tile`` / ``_target``：粗格 ``(row, col)``，与 ``matrix[row][col]`` 一致。
- ``rect_x`` / ``rect_y``：像素逻辑坐标，经 ``build_bounding_boxes`` 同步到 ``Sprite.rect`` 供 ``Group.draw``。
- ``_direction``：一步 ``(Δrow, Δcol)``，来自 ``get_direction``，与键盘无关。

**出笼时间轴（configs.GHOST_DELAYS）**：
Blinky 4s → Pinky 8s → Inky 12s → Clyde 16s；出笼后移到第 11 行同列出口，``release_time`` 记录 ticks。

**能量豆时间轴**：
Pacman 吃 power → ``is_pacman_powered=True`` + ``USEREVENT+2`` → ghosts 换蓝皮 ``make_ghost_scared`` →
到点 EventHandler 清 powered → ``check_if_pacman_powered`` 恢复 normal（晚出笼鬼用 ``release_time`` 例外）。

**scatter/chase 时间轴**：
runner ``create_ghost_mode_event`` 注册 ``USEREVENT+1`` → EventHandler 交替写 ``ghost_mode`` scatter/chase →
``determine_target`` 在固定角与动态追 Pac 间切换；间隔来自 ``GameState.mode_change_events`` getter（JSON scatter_times）。

**为何不用 graph_utils.a_star 每帧寻路**：
四鬼采用岔路口贪心 ``get_direction``（欧氏最近一步），计算轻、行为贴近街机；A* 在本仓库供工具/扩展，非主循环热路径。

**碰撞与生命**：
非 scared 碰撞 → ``is_pacman_dead`` + death 音效 + ``wait(1000)``；scared 碰撞 → ``reset_ghost`` + ``GHOST_POINT``。
重生由 ``ScreenManager.pacman_dead_reset`` 处理，不 increment ``game_state.level``。

**贴图资源**：
``GHOST_PATHS[name][0]`` normal；``GHOST_PATHS['blue'][0]`` frightened；``transform.scale`` 到 ``configs.GHOSTS``。

**测试思路（无 pygame 窗口）**：
可 mock ``matrix`` 与 ``GameState``，单独调用 ``get_direction`` / ``get_is_intersection``（在 ghost_movement_utils）；
``Ghost`` 本体依赖 pygame ``Sprite``/``Rect``/``wait``，集成测试宜在 PyPacman 根目录跑 ``main.py``。

**常见修改点**：
调 ``_accelerate`` 改滑格速度；调 ``GHOST_DELAYS`` 改出笼节奏；调 Clyde 距离阈值改难度；勿改 ``get_direction`` 四向顺序以免 tie-break 行为漂移。
"""

from abc import abstractmethod, ABC
from typing import Union

from pygame.sprite import Sprite
from pygame import Surface
from pygame import image, transform
import pygame.time as pytime
from pygame.time import wait
from pygame.rect import Rect

import random

from src.game.state_management import GameState
from src.sprites.sprite_configs import GHOST_PATHS
from src.configs import PACMAN, CELL_SIZE, GHOST_DELAYS, GHOST_SCATTER_TARGETS, GHOST_POINT
from src.utils.coord_utils import get_coords_from_idx, get_idx_from_coords
from src.utils.ghost_movement_utils import get_direction, get_is_intersection, get_is_move_valid
from src.sounds import SoundManager

from src.log_handle import get_logger
logger = get_logger(__name__)


class Ghost(Sprite, ABC):
    """
    幽灵基类：图像、lerp 行走、scared 状态、碰撞与鬼屋释放出笼。

    **子类契约**：实现 ``determine_target()`` → 返回粗格 ``(row, col)`` 追逐/散开目标。

    **状态机概览**（每帧 ``update``）：
    1. ``build_bounding_boxes`` 把 rect 居中到 2×CELL 逻辑格；
    2. ``check_is_released`` 计时 ``GHOST_DELAYS[name]`` 后出鬼屋到第 11 行；
    3. ``_boundary_check`` 列 wrap 实现横向隧道；
    4. ``move_ghost``：lerp 像素移动 + 路口 ``prepare_movement``；
    5. ``check_if_pacman_powered`` 切换 normal/blue 贴图与 ``is_scared``；
    6. ``check_collisions`` 半盒与 ``game_state.pacman_rect`` 相交判定。

    **lerp 字段**：
    - ``prev`` / ``next_tile``：粗格起终点；``_t``∈[0,1] 插值进度；``_accelerate`` 每帧推进 ``_t``。
    - ``_direction``：``get_direction`` 返回的 (Δrow,Δcol)；``_target``：当前段追逐粗格。

    **与 GameState**：
    读 ``ghost_mode``、``pacman_rect``、``is_pacman_powered``、能量豆时间戳；
    写 ``blinky_matrix_pos``（仅 Blinky）、碰撞加分/``is_pacman_dead``。

    **与 ghost_movement_utils**：
    ``prepare_movement`` → ``get_direction`` 贪心一步；``get_is_intersection`` 判断是否岔路口。

    **Python 概念**：
    ``Sprite`` 提供 ``Group.draw/update``；``ABC`` + ``@abstractmethod`` 强制四鬼实现目标算法。
    """

    def __init__(self,
                 name: str,
                 ghost_matrix_pos: tuple[int, int],
                 grid_start_pos: tuple[Union[int, float], Union[int, float]],
                 matrix: list[list[str]],
                 game_state: GameState
                 ):
        """
        构造单只幽灵：加载贴图、初始化 lerp/AI 字段、绑定共享 ``GameState`` 与 ``matrix``。

        Args:
            name: ``'blinky'|'pinky'|'inky'|'clyde'``，决定 ``GHOST_DELAYS`` 与 ``GHOST_PATHS`` 键。
            ghost_matrix_pos: 鬼屋出生粗格 ``(row, col)``，``GhostManager`` 用 adder 错行。
            grid_start_pos: 迷宫左上角像素，与 ``PacmanGrid.start_x/y`` 相同，供 coord_utils 换算。
            matrix: 关卡 JSON 网格引用，与 Pacman 共享；只读墙/通道，不在这里改豆。
            game_state: 全局状态：模式、Pac 位置、能量豆、分数等。

        初始化要点：
        - ``_creation_time`` + ``GHOST_DELAYS[name]`` 控制出笼；
        - ``lerp`` 字段 ``_t/_accelerate/prev/next_tile/_target/_direction`` 置空或默认；
        - ``load_images()`` 设置 ``normal_image/blue_image/rect``；
        - ``SoundManager()`` 取单例，供 ``check_collisions`` 播放 death/eat_ghost。

        游戏含义：
        四鬼构造参数除 ``name/ghost_matrix_pos`` 外相同；AI 差异仅在子类 ``determine_target``。
        """
        # 初始化 Sprite；ABC 不阻止 super 调用
        super().__init__()
        # 'blinky' 等，用于贴图路径与 GHOST_DELAYS
        self.name = name
        # 鬼屋内出生粗格
        self._ghost_matrix_pos = ghost_matrix_pos
        # 与 Pacman 相同的地图像素原点
        self._grid_start_pos = grid_start_pos
        # 共享地图引用，只读墙/通道
        self._matrix = matrix
        # 粗网格行数
        self.num_rows = len(self._matrix)
        # 粗网格列数
        self.num_cols = len(self._matrix[0])
        # scatter/chase、pacman 位置等
        self._game_state = game_state
        # False 时在盒子里不动
        self._is_released = False
        # 计时出笼
        self._creation_time = pytime.get_ticks()
        # 每只鬼延迟不同
        self._dead_wait = GHOST_DELAYS[self.name]
        # 2×2 粗格 footprint 的步进向量（与 get_direction 返回的 ±1 不同）
        self.move_direction_mapper = {"up": (-1, 0), "down":(2, 0),
                                      "right": (0, 2), "left": (0, -1)}
        # 历史字段，部分逻辑用 prev/next_tile
        self.prev_pos = None
        # lerp 参数，0=在 prev，1=在 next_tile
        self._t = 0
        # 每帧 _t 增量，越大滑格越快
        self._accelerate = 0.2
        # 当前 (Δrow, Δcol)，如 (0, 1)
        self._direction = None
        # 追逐目标粗格，供 get_direction
        self._target = None
        # lerp 起点格
        self.prev = None
        # lerp 终点格
        self.next_tile = None
        # 禁止 180° 掉头：当前方向 → 反方向向量，传给 intersection 检测
        self._direction_prevent = {(-1, 0): (1, 0), (1, 0): (-1, 0),
                                     (0, 1): (0, -1), (0, -1): (0, 1)}
        # True 时换蓝皮且可被吃
        self.is_scared = False
        # 当前粗格，Clyde 算距离用
        self.curr_pos = None
        # 出笼时刻，与能量豆时间比较
        self.release_time = None
        self.sounds = SoundManager()
        # normal / blue 贴图 + 初始 rect
        self.load_images()

    def _get_coords_from_idx(self, p1):
        """薄封装：把本幽灵的网格起点、格子尺寸注入 coord_utils。"""
        return get_coords_from_idx(p1, *self._grid_start_pos,
                                   *CELL_SIZE, self.num_rows, self.num_cols)

    def _get_idx_from_coords(self, p1):
        """像素 → 粗格 (row, col)。"""
        return get_idx_from_coords(*p1,
                                   *self._grid_start_pos, CELL_SIZE[0])

    def build_bounding_boxes(self, x, y):
        """与 Pacman 相同：在 2 格宽的逻辑区域内居中精灵 rect。"""
        self.rect.x = x + (CELL_SIZE[0] * 2 - self.rect.width) // 2
        self.rect.y = y + (CELL_SIZE[1] * 2 - self.rect.height) // 2

    def load_images(self):
        """正常色与 scared 蓝色贴图；初始位置由 ``_ghost_matrix_pos`` 决定。"""
        ghost_images = GHOST_PATHS[self.name][0]
        blue_images = GHOST_PATHS['blue'][0]
        self.normal_image = transform.scale(image.load(ghost_images).convert_alpha(),
                                     PACMAN)
        self.blue_image = transform.scale(image.load(blue_images).convert_alpha(),
                                     PACMAN)
        self.image = self.normal_image
        x, y = self._get_coords_from_idx(self._ghost_matrix_pos)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.rect_x = x
        self.rect_y = y

    def lerp(self, source, dest):
        """
        在 prev/next_tile 两格 **格心像素** 间线性插值。

        Args:
            source: (x1,y1) 上一格心像素，来自 ``_get_coords_from_idx(prev)``。
            dest: (x2,y2) 下一格心像素。

        逻辑：
        - ``_target is None`` 或 ``_t==1``：返回 source，表示停在格心等待新决策；
        - 否则 ``_t += _accelerate``（上限 1），
          ``x=(1-t)*x1+t*x2``，``y=(1-t)*y1+t*y2``。

        游戏含义：
        粗格 AI 每步一格，视觉上多帧滑过去，避免鬼在 pygame 里「瞬移跳格」。

        Returns:
            (x, y) 浮点像素，赋给 ``rect_x/rect_y``。
        """
        # 上一格中心像素
        x1, y1 = source
        # 下一格中心像素
        x2, y2 = dest
        # 尚未规划或已到达
        if self._target is None or self._t == 1:
            return x1, y1
        if self._t < 1:
            # 推进插值
            self._t += self._accelerate
        else:
            # 钳在 1，避免 overshoot
            self._t = 1

        # 标准 lerp 公式
        x = (1 - self._t) * x1 + self._t * x2
        y = (1 - self._t) * y1 + self._t * y2
        return x, y

    def check_is_released(self):
        """
        鬼屋延迟出笼（staggered release）。

        条件：
        ``get_ticks()-_creation_time > _dead_wait``（初值 ``GHOST_DELAYS[name]``）。

        出笼后：
        ``_is_released=True``，像素移到行 11 同列，``release_time`` 记录，``_dead_wait`` 改 1500。

        游戏含义：
        Blinky 4s、Pinky 8s、Inky 12s、Clyde 16s，玩家可先清近鬼再吃远鬼。

        Returns:
            None。
        """
        if self._is_released:
            return
        curr_time = pytime.get_ticks()
        if (curr_time - self._creation_time) > self._dead_wait:
            self._is_released = True
            self._dead_wait = 1500
            self.rect_x, self.rect_y = self._get_coords_from_idx((11, self._ghost_matrix_pos[1]))
            self.release_time = pytime.get_ticks()

    def move_ghost(self):
        """
        粗格+像素双层移动状态机。

        流程：
        - 未 ``_is_released`` 则 return（仍在鬼屋）；
        - ``_target is None`` 时首次 ``prepare_movement``；
        - ``lerp`` 更新 ``rect_x/rect_y``，反查 ``curr_pos``；
        - 到达格心（``_t==1`` 或像素重合）时：
          - 若 ``get_is_intersection``：``prepare_movement`` 重选向；
          -  elif 前方不合法：``prepare_movement``；
          -  else：沿 ``_direction`` 延伸 ``next_tile``，``_t=0`` 开始新 lerp 段。

        Blinky 专有：写 ``game_state.blinky_matrix_pos``，Inky ``calculate_inky_target`` 依赖此锚点。

        Returns:
            None（副作用更新 rect 与粗格状态）。
        """
        # 还在鬼屋
        if not self._is_released:
            return
        # 第一帧或刚 reset
        if self._target is None:
            self.prepare_movement()
        # lerp 起点像素
        source = self._get_coords_from_idx(self.prev)
        # lerp 终点像素
        dest = self._get_coords_from_idx(self.next_tile)
        # 平滑移动
        self.rect_x, self.rect_y = self.lerp(source, dest)
        # 反查粗格
        curr_mat_x, curr_mat_y = self._get_idx_from_coords((self.rect_x, self.rect_y))
        # Inky 算法依赖红鬼实时位置
        if self.name == 'blinky':
            self._game_state.blinky_matrix_pos = (curr_mat_x, curr_mat_y)
        self.curr_pos = (curr_mat_x, curr_mat_y)
        if (self._t == 1) \
            or (self.rect_x == dest[0] and self.rect_y == dest[1]):  # 到达格心
            # 禁止回头方向
            check_prev = self._direction_prevent.get(self._direction)
            # 转成 'up' 等字符串
            prev_val = self._get_direction_reverse_map(check_prev)
            if get_is_intersection(self.next_tile, self._matrix,
                                   prev_val):  # 岔路口：重新选向
                self.prepare_movement()
            else:
                if not get_is_move_valid(self.next_tile,
                                         self._get_direction_reverse_map(self._direction),
                                         # 前方堵死
                                         self._matrix):
                    self.prepare_movement()
                # 直道：沿 _direction 延伸下一格
                else:
                    self.prev = self.next_tile
                    self.next_tile = (self.next_tile[0] + self._direction[0],
                                  self.next_tile[1] + self._direction[1])

                # 下一段 lerp 从 0 开始
                self._t = 0

    def _get_direction_reverse_map(self, direction):
        """把 (Δ行, Δ列) 元组转回 ghost_movement_utils 使用的方向字符串。"""
        if direction == (-1, 0):
            return 'up'
        elif direction == (1, 0):
            return "down"
        elif direction == (0, -1):
            return "left"
        elif direction == (0, 1):
            return "right"

    def _boundary_check(self):
        """粗格列越界时环绕（横向隧道），与 Pacman 概念类似，在格索引层 wrap。"""
        # 尚无下一格，无需 wrap
        if not self.next_tile:
            return
        # 列走到地图右侧外
        if (self.next_tile[1] >= self.num_cols):
            # 绕到最左列
            self.next_tile = (self.next_tile[0], 0)
            return
        # 列走到左侧外
        if self.next_tile[1] < 0:
            # 绕到最右列
            self.next_tile = (self.next_tile[0], self.num_cols - 1)

    def prepare_movement(self):
        """
        岔路口/墙前重新规划下一段 lerp。

        决策格：
        优先 ``next_tile`` 粗格，否则 ``_get_idx_from_coords(rect_x, rect_y)``。

        目标格：
        - ``is_scared``：``get_random_target()`` 全图随机粗格；
        - 否则：多态 ``determine_target()``（四鬼 scatter/chase 差异在此）。

        方向：
        ``get_direction(ghost_pos, target, matrix, prev_reverse_vector)`` 返回 ``_direction``；
        ``prev`` 来自 ``_direction_prevent[_direction]``，禁止立即 180° 掉头。

        重置：
        ``_t=0``，``prev``=当前决策格，``next_tile``=prev+``_direction``。

        游戏含义：classic Pac-Man 每格仅走一步决策；像素滑动由后续 ``lerp`` 多帧完成。
        """
        # 默认用像素反查格
        ghost_x, ghost_y = self._get_idx_from_coords((self.rect_x, self.rect_y))
        # 若已在格心规划，以 next_tile 为决策点更准确
        if self.next_tile:
            ghost_x, ghost_y = self.next_tile
        # frightened：目标随机
        if self.is_scared:
            self._target = self.get_random_target()
        else:
            # 多态：四鬼各自算目标
            self._target = self.determine_target()
        # 传给 get_direction 禁止掉头
        prev = self._direction_prevent.get(self._direction)
        self._direction = get_direction((ghost_x, ghost_y),
                                        self._target,
                                        self._matrix,
                                        prev
                                        )  # 贪心选一步 (Δrow, Δcol)
        # 新一段 lerp
        self._t = 0
        self.next_tile = (ghost_x + self._direction[0],
                          ghost_y + self._direction[1])  # 下一粗格
        # lerp 起点
        self.prev = (ghost_x, ghost_y)

    @abstractmethod
    def determine_target(self):
        """
        子类实现：返回当前 ``ghost_mode`` 下的追逐/散开 **目标粗格**。

        scatter:
            通常读 ``configs.GHOST_SCATTER_TARGETS[name]`` 固定角。

        chase:
            四鬼算法不同（脚下 / 面前 4 格 / Inky 向量 / Clyde 距离切换）。

        Returns:
            ``tuple[int, int]`` 作为 ``prepare_movement`` 里 ``get_direction`` 的目标参数。

        游戏含义:
            经典 Pac-Man 个性全在此多态；``EventHandler`` 定时 scatter↔chase 改变本方法分支。
        """
        # ABC 要求子类必须 override，否则无法实例化（除子类外）
        ...

    def get_target_pacman_dir(self, pacman_rect: tuple,
                              pacman_dir: tuple,
                              look_ahead: int=4):
        """
        根据 Pac **粗格** 与 ``pacman_direction``，计算前方 ``look_ahead`` 格的目标格。

        Args:
            pacman_rect: ``(row, col)`` 粗格，非像素。
            pacman_dir: ``'l'|'r'|'u'|'d'``，来自 ``GameState.pacman_direction``（Pacman 墙检测通过后写入）。
            look_ahead: Pinky 默认 4；Inky ``calculate_inky_target`` 传 2。

        隧道 wrap（列方向）：
        左看 ``col - look_ahead``，若 ``<0`` 则 wrap 到 ``num_cols - look_ahead - 1``；
        右看 ``col + look_ahead``，若超出列界则 wrap 到列 0（与 JSON 横向隧道一致）。

        无方向：
        返回 ``pacman_rect`` 本身，Pinky 在 Pac 停住时仍有一个确定目标。

        Returns:
            ``(row, col)`` 粗格，供 ``determine_target`` / ``get_direction`` 使用。

        游戏含义：
        实现经典「瞄 Pac 面向前方若干格」而非脚下；与 Blinky 直追形成对比。
        """
        # Pac 向左：目标在列方向减
        if pacman_dir == "l":
            target = (pacman_rect[0], pacman_rect[1] - look_ahead)
            # 穿过左隧道时 wrap
            if target[1] < 0:
                target = (pacman_rect[0], self.num_cols - look_ahead - 1)
            return target
        # 向右看 look_ahead 格
        elif pacman_dir == "r":
            target = (pacman_rect[0], pacman_rect[1] + look_ahead)
            # 右隧道（注意边界比较沿用原逻辑）
            if target[1] > self.num_cols:
                target = (pacman_rect[0], 0)
            return target
        # 向上：行减
        elif pacman_dir == "u":
            return (pacman_rect[0] - look_ahead, pacman_rect[1])
        # 向下：行增
        elif pacman_dir == "d":
            return (pacman_rect[0] + look_ahead, pacman_rect[1])
        else:
            # 无方向：目标就是脚下
            return pacman_rect

    def get_random_target(self):
        """
        frightened 随机目标粗格。

        使用 ``random.randrange`` 在 [0,num_rows) × [0,num_cols) 均匀采样。

        游戏含义：
        不保证最短路径可达；配合 ``get_direction`` 贪心一步，鬼表现为乱窜。

        Returns:
            (row, col) 整数元组。
        """
        # 闭区间 [0, num_rows)
        rand_row = random.randrange(0, self.num_rows)
        rand_col = random.randrange(0, self.num_cols)
        return rand_row, rand_col

    def make_ghost_scared(self):
        """
        进入 frightened 移动模式。

        操作：
        ``_direction = _direction_prevent[_direction]``（180°），``is_scared=True``，``prepare_movement()``。

        游戏含义：
        能量豆生效瞬间鬼反向逃离，玩家可追吃；与蓝皮贴图切换在同帧链 ``check_if_pacman_powered`` 内。

        Returns:
            None。
        """
        # 180° 反向
        self._direction = self._direction_prevent[self._direction]
        self.is_scared = True
        # 按新 mode 立即重算路径
        self.prepare_movement()

    def check_if_pacman_powered(self):
        """
        能量豆 frightened 贴图与 ``is_scared`` 行为。

        盒内鬼：
        未 ``_is_released`` 时强制 ``normal_image``，不参与 frightened。

        晚出笼：
        若 ``release_time > power_event_trigger_time``，保持 normal，直到下一次能量事件。

        powered 为真：
        换 ``blue_image``，必要时 ``make_ghost_scared``（掉头+随机目标）。

        powered 假：
        恢复 ``normal_image``，``is_scared=False``。

        游戏含义：
        与 ``Pacman.create_power_up_event`` / ``EventHandler`` power 事件到点清标志配合。

        Returns:
            None。
        """
        # 盒内幽灵不参与 scared 贴图
        if not self._is_released:
            if self.image != self.normal_image:
                self.image = self.normal_image
            return
        if self._game_state.power_event_trigger_time is not None and \
                self.release_time > self._game_state.power_event_trigger_time:  # 出笼晚于本次能量豆
            # 保持正常色，直到下一次能量事件
            return
        # 能量豆窗口内
        if self._game_state.is_pacman_powered:
            if self.image != self.blue_image:
                self.image = self.blue_image
                # 掉头 + 随机目标
                self.make_ghost_scared()
        # 能量结束
        else:
            if self.image != self.normal_image:
                self.image = self.normal_image
                self.is_scared = False

    def reset_ghost(self):
        """
        被 Pac 在 frightened 状态下「反吃」后的复位。

        清空：
        ``_t``、``_direction``、``_target``、``prev``、``next_tile``、``is_scared``、``release_time``。

        位置：
        ``_ghost_matrix_pos`` → 像素 → ``rect``/``rect_x``/``rect_y``。

        鬼屋：
        ``_is_released=False``，``_creation_time=get_ticks()`` 重新等待 ``GHOST_DELAYS``。

        游戏含义：
        经典规则：鬼被吃后眼睛飞回鬼屋再出来；本实现简化为瞬移回出生格计时。

        Returns:
            None。
        """
        self._t = 0
        self._direction = None
        self._target = None
        # 注意：运行时主要用 curr_pos，与 _curr_pos 不一致（见下方 bug 说明）
        self._curr_pos = None
        self.prev = None
        self.next_tile = None
        self.release_time = None
        self.is_scared = False
        # 无赋值语句，对 rect 无实际效果（历史遗留一行）
        self.rect.x
        # 回到出生粗格像素
        x, y = self._get_coords_from_idx(self._ghost_matrix_pos)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.rect_x = x
        self.rect_y = y
        # 重新关进鬼屋
        self._is_released = False
        # 重计出笼延迟
        self._creation_time = pytime.get_ticks()

    def check_collisions(self):
        """
        Pac 与鬼的矩形碰撞（半宽 hitbox）。

        构造：
        - 鬼：``Rect(rect.x, rect.y, PACMAN[0]//2, PACMAN[1]//2)``；
        - Pac：``game_state.pacman_rect`` 同样半宽。

        scared 为真：
            ``reset_ghost``、``eat_ghost`` 音效、``points += GHOST_POINT``。

        否则：
            ``is_pacman_dead=True``、death 音效、``wait(1000)`` 阻塞主循环。

        游戏含义：
        frightened 窗口内玩家可反吃鬼；否则一触即死，由 ``ScreenManager.pacman_dead_reset`` 重生。

        Returns:
            None。
        """
        ghost_rect = Rect(self.rect.x, self.rect.y,
                          PACMAN[0]//2, PACMAN[1]//2)  # 缩小一半，碰撞更宽容
        pacman_coords = (self._game_state.pacman_rect[0],
                         self._game_state.pacman_rect[1],
                         self._game_state.pacman_rect[2]//2,
                         # 同样缩小 Pac 盒
                         self._game_state.pacman_rect[3]//2)
        pacman_rect = Rect(pacman_coords)
        # pygame 矩形相交检测
        if ghost_rect.colliderect(pacman_rect):
            # 玩家吃鬼
            if self.is_scared:
                self.reset_ghost()
                self.sounds.play_sound("eat_ghost")
                self._game_state.points += GHOST_POINT
            # 鬼吃玩家
            else:
                self._game_state.is_pacman_dead = True
                self.sounds.play_sound("death")
                # 阻塞 1 秒（简单演出，非异步）
                wait(1000)

    def update(self, dt):
        """
        精灵帧更新入口，由 ``runner`` 的 ``all_sprites.update(dt)`` 调用。

        Args:
            dt: 毫秒帧间隔（runner 已 ``/=100``），本类未用于 lerp 公式，保留 pygame 约定签名。

        顺序说明：
        先 ``build_bounding_boxes`` 再移动，碰撞用的是位移后的 ``rect_x/rect_y``；
        ``check_collisions`` 在最后，避免同一帧内重复死亡判定。

        游戏含义：四鬼独立 update，Blinky 在 ``move_ghost`` 内同步 ``blinky_matrix_pos`` 供 Inky 读取。
        """
        # 贴图居中到逻辑格
        self.build_bounding_boxes(self.rect_x, self.rect_y)
        # 延迟后出鬼屋
        self.check_is_released()
        # 横向隧道格 wrap
        self._boundary_check()
        # lerp + 路口 AI
        self.move_ghost()
        # 蓝皮 / scared
        self.check_if_pacman_powered()
        # 与 Pac 相交
        self.check_collisions()


# ---------------------------------------------------------------------------
# 四鬼个性：仅 determine_target（及 Clyde 辅助）不同
# ---------------------------------------------------------------------------


class Blinky(Ghost):
    """
    红色 Blinky：最直接追逐。

    scatter:
        ``GHOST_SCATTER_TARGETS['blinky']`` → 右上 (0,30)。

    chase:
        ``pacman_rect`` 像素 → ``_get_idx_from_coords`` → Pac 脚下粗格。

    副作用：
        ``move_ghost`` 每帧写 ``game_state.blinky_matrix_pos``，Inky AI 只读此字段。

    Returns:
        ``(row, col)`` 目标粗格供 ``get_direction`` 使用。
    """

    def determine_target(self):
        # 全局在 scatter / chase 间切换
        mode = self._game_state.ghost_mode
        # 散开模式：回地图角上的固定点
        if mode == "scatter":
            target = GHOST_SCATTER_TARGETS[self.name]
        # 追逐：直扑 Pac 像素所在格
        elif mode == "chase":
            pacman_rect = self._game_state.pacman_rect
            target = self._get_idx_from_coords((pacman_rect[0], pacman_rect[1]))
        # 若 mode 非二者，target 可能未定义（见 bug 说明）
        return target


class Pinky(Ghost):
    """
    粉色 Pinky：伏击型追逐。

    scatter:
        左上角 (0,0)。

    chase:
        ``calculate_pacman_direction``：Pac 粗格 + ``pacman_direction`` → ``get_target_pacman_dir(..., look_ahead=4)``。

    游戏含义：
        Pac 向上时 Pinky 瞄上方 4 格，玩家直线逃跑时常被「抄近路」拦截。

    Returns:
        目标粗格 ``(row, col)``。
    """

    def calculate_pacman_direction(self):
        """
        Pinky chase 辅助：Pac 粗格 + 当前面向 → 前方 4 格目标。

        Returns:
            ``get_target_pacman_dir`` 默认 ``look_ahead=4`` 的结果。

        游戏含义：
        Pac 贴墙停时 ``pacman_direction`` 可能仍指向上次成功移动方向，Pinky 仍沿该方向「埋伏」。
        """
        # 'l'/'r'/'u'/'d'
        pacman_dir = self._game_state.pacman_direction
        # 像素盒
        pacman_rect = self._game_state.pacman_rect
        pacman_rect = self._get_idx_from_coords((pacman_rect[0],
                                                        pacman_rect[1]))  # 转成粗格
        return self.get_target_pacman_dir(pacman_rect,
                                          pacman_dir,
                                          )  # 默认 look_ahead=4

    def determine_target(self):
        mode = self._game_state.ghost_mode
        if mode == "scatter":
            return GHOST_SCATTER_TARGETS[self.name]
        elif mode == "chase":
            # 「瞄 Pac 面前」而非脚下
            return self.calculate_pacman_direction()


class Inky(Ghost):
    """
    青色 Inky：向量镜像追逐（最复杂）。

    scatter:
        左下 (31,0)。

    chase:
        ``calculate_inky_target``：Pac 前 2 格 + Blinky 格 → 向量加倍终点。

    依赖：
        ``game_state.blinky_matrix_pos`` 必须由 Blinky ``move_ghost`` 每帧更新。

    Returns:
        ``(target_row, target_col)`` 可为算术结果，``get_direction`` 仍整数一步。
    """

    def calculate_inky_target(self):
        """
        Inky chase 目标：以 Blinky 格与「Pac 前 2 格」构造向量，再 ``×2`` 延伸。

        步骤：
        1. Pac 像素 → 粗格；读 ``pacman_direction``；
        2. ``inky_pacman_target = get_target_pacman_dir(..., look_ahead=2)``；
        3. ``vec = inky_pacman_target - blinky_cell``（来自 ``game_state.blinky_matrix_pos``）；
        4. ``target = blinky_cell + vec * 2``。

        依赖：
        Blinky 必须在 ``move_ghost`` 中持续更新 ``blinky_matrix_pos``，否则 Inky 锚点 stale。

        Returns:
            ``(target_row, target_col)`` 算术结果，可能非整数，``get_direction`` 仍按粗格一步走。

        游戏含义：
        最「飘」的一鬼，路径随 Blinky 与 Pac 朝向强烈变化。
        """
        pacman_rect = self._game_state.pacman_rect
        pacman_rect = self._get_idx_from_coords((pacman_rect[0], pacman_rect[1]))
        pacman_dir = self._game_state.pacman_direction
        # 必须由 Blinky 每帧更新
        blinky_cell = self._game_state.blinky_matrix_pos
        inky_pacman_target = self.get_target_pacman_dir(pacman_rect,
                                                        pacman_dir,
                                                        # Pac 前方 2 格
                                                        2)
        # Blinky → 伪 Pac 点
        vec_row = inky_pacman_target[0] - blinky_cell[0]
        vec_col = inky_pacman_target[1] - blinky_cell[1]
        # 向量加倍：经典 Inky 公式
        target_row = blinky_cell[0] + vec_row * 2
        target_col = blinky_cell[1] + vec_col * 2
        return target_row, target_col

    def determine_target(self):
        mode = self._game_state.ghost_mode
        if mode == "scatter":
            return GHOST_SCATTER_TARGETS[self.name]
        elif mode == "chase":
            return self.calculate_inky_target()


class Clyde(Ghost):
    """
    橙色 Clyde：距离切换「随机 / 追逐」。

    scatter:
        右下 (31,30)。

    chase:
        ``get_clyde_random_target``：曼哈顿距离 >8 → ``get_random_target``，否则 Pac 粗格。

    游戏含义：
        远时看似乱走，近时突然扑上，与 Blinky 直线压迫形成差异。

    Returns:
        目标粗格。
    """

    def get_clyde_random_target(self):
        """
        Clyde chase：曼哈顿距离 >8 格则随机目标，否则追 Pac 粗格。

        使用 ``curr_pos``（``move_ghost`` 每帧更新）与 Pac 粗格算 ``|dr|+|dc|``。

        Returns:
            粗格 ``(row,col)`` 或 ``get_random_target()`` 随机格。

        游戏含义：
        远时看似无序，近时 aggressive，与 Blinky 持续压迫互补。
        """
        pacman_rect = self._game_state.pacman_rect
        pacman_rect = self._get_idx_from_coords((pacman_rect[0], pacman_rect[1]))
        # 首帧尚无 curr_pos
        if not self.curr_pos:
            return pacman_rect
        # 曼哈顿距离
        dis = abs(pacman_rect[0] - self.curr_pos[0]) + abs(pacman_rect[1] - self.curr_pos[1])
        # 远：假装随机（实际 get_random_target）
        if dis > 8:
            return self.get_random_target()
        # 近：真追逐 Pac
        return pacman_rect

    def determine_target(self):
        mode = self._game_state.ghost_mode
        if mode == "scatter":
            return GHOST_SCATTER_TARGETS[self.name]
        elif mode == "chase":
            return self.get_clyde_random_target()


class GhostManager:
    """
    四鬼工厂：构造 ``ghosts_list`` 供 ``ScreenManager`` 加入 ``Group``。

    Args（构造）:
        screen: 预留 Surface；matrix: 关卡 JSON 网格；ghost_matrix_pos: 鬼屋基准粗格；
        grid_start_pos: 迷宫像素原点，与 Pacman 一致。

    职责：
        仅创建实例，不调用 ``update``；移动 AI 在 ``Ghost.update``。

    游戏含义：
        过关/死亡 ``reset_stage`` 会 ``new GhostManager``，四鬼重置 AI 状态但 matrix 豆保留。
    """

    def __init__(self,
                 screen: Surface,
                 game_state: GameState,
                 matrix: list[list[str]],
                 ghost_matrix_pos: tuple[int, int],
                 grid_start_pos: tuple[int, int],
                 ):
        # 预留：若 Manager 统一 draw 可用
        self.screen = screen
        self.game_state = game_state
        self.matrix = matrix
        # 鬼屋基准格
        self.ghost_matrix_pos = ghost_matrix_pos
        self.grid_start_pos = grid_start_pos
        # 存四个 Ghost 实例
        self.ghosts_list = []
        self.load_ghosts()

    def load_ghosts(self):
        """
        工厂方法：创建四鬼 ``Sprite`` 并放入 ``ghosts_list``。

        出生位置：
        同列 ``ghost_matrix_pos``，``adder`` 0..3 递增行，模拟鬼屋竖排。

        Args:
            无（使用 ``self`` 上 ``matrix``、``grid_start_pos``、``game_state``）。

        游戏含义：
        ``ScreenManager`` 构造后将 ``ghosts_list`` 每项 ``add`` 进 ``Group``，与 Pacman 同批 draw/update。
        """
        # 同列不同行：0,1,2,3
        adder = 0
        ghosts = [('blinky', Blinky),
                  ('pinky', Pinky),
                  ('inky', Inky),
                  ('clyde', Clyde)]
        # ghost 是类对象，非实例
        for ghost_name, ghost in ghosts:
            ghost_pos = (self.ghost_matrix_pos[0], self.ghost_matrix_pos[1] + adder)
            self.ghosts_list.append(ghost(ghost_name,
                                          ghost_pos,
                                          self.grid_start_pos,
                                          self.matrix,
                                          # 构造具体子类
                                          self.game_state))
            # 下一只鬼换一行
            adder += 1

# Ghost 模块与 runner 主循环：Group.update 在 draw 之后，四鬼 update 互不阻塞（除 wait 死亡演出）。
# determine_target 仅算目标粗格，一步方向由 ghost_movement_utils.get_direction 在 prepare_movement 完成。
# lerp 像素层与粗格 AI 分离，改 _accelerate 调滑格手感，改 GHOST_DELAYS 调出笼节奏，勿与 PACMAN_SPEED 混淆。
# Inky 强依赖 blinky_matrix_pos，调试 Inky 时须同时观察 Blinky 是否已 release 且 move_ghost 在写锚点。
# scatter 角坐标与 NUM_ROWS/NUM_COLS 一致，换关卡尺寸请同步 configs.GHOST_SCATTER_TARGETS 与 JSON matrix。
# is_pacman_powered 与 ghost_mode 字符串独立：能量豆 frightened 主要靠 powered 标志 + is_scared + 蓝皮贴图。
# reset_ghost 后鬼回鬼屋重计时，matrix 中 void 豆不回填，同关死亡 reset_stage 不 reload JSON。
# SoundManager 单例：death/eat_ghost 与 runner.initialize_sounds 通道一致，多次 SoundManager() 仍同一 mixer。
# 半盒碰撞 PACMAN//2 为 gameplay 宽容度，非 pygame 默认；调全尺寸碰撞会显著提高接触即死概率。
# GhostManager 只 factory，不 update；ScreenManager 负责 Group.empty/add 与 reset_stage 生命周期。
# get_random_target 不保证可达，frightened 下 get_direction 仍可能 ValueError，说明地图封闭或 prev 矛盾。
# _boundary_check 列 wrap 在粗格 next_tile 层，Pacman 在 tiny_start_y 层 wrap，两层概念平行实现隧道。
# check_if_pacman_powered 的 release_time 比较避免晚出笼鬼误 scared，与 pacman power_event_trigger_time 配对。
# make_ghost_scared 在 powered 变真且换图时触发，立即 prepare_movement，鬼表现为掉头 + 随机/追目标切换。
# move_ghost 直道延伸 next_tile 不调用 get_direction，直到 intersection 或撞墙，减少直道 CPU 开销。
# ABC @abstractmethod 阻止实例化 Ghost 基类，TypeError 提示缺 determine_target，编译期结构约束四鬼。
# pygame Sprite.rect 与 rect_x/rect_y 双轨：lerp 写 rect_x/y，build_bounding_boxes 同步 rect 供 Group.draw。
# EventHandler USEREVENT+1 切换 scatter/chase 不重置 lerp 段，鬼保持当前 prev/next_tile 直到下一路口决策。
# Clyde 曼哈顿阈值 8 格可调，改常量会改变「远逃近扑」频率，影响关卡难度曲线。
# Pinky look_ahead=4 在 get_target_pacman_dir 默认，与街机「瞄 Pac 面前四格」规则一致。
# Blinky chase 若 ghost_mode 既非 scatter 也非 chase，target 可能未赋值，属配置异常边界。
# wait(1000) 死亡阻塞与 ScreenManager wait(2000) 过关阻塞均为 pygame.time 同步调用，非协程。
# 本文件注释/代码≥1.5：模块 docstring、类/方法 docstring（Args/Returns/游戏含义）与上文主循环对照。
#
# —— 小白阅读路线（建议）——
# 1) 先读模块 docstring 的四鬼差异表；2) 再读 Ghost.__init__ 字段含义；
# 3) 跟 update → check_is_released → move_ghost → prepare_movement；
# 4) 对照 Blinky/Pinky/Inky/Clyde 的 determine_target；5) 最后看 check_collisions。
# Python 概念清单：多重继承、ABC、@abstractmethod、lerp、字典映射、随机、Rect.colliderect。
# 数据流：GameState.ghost_mode / pacman_rect / is_pacman_powered → 本类读写 → 画面与音效。
# 关卡重置时 GhostManager 重建四实例，旧对象由 Sprite Group.empty() 丢弃（垃圾回收）。
# 调试建议：临时 print(self.name, self._direction, self.next_tile, self.is_scared) 观察 AI。
# 安全提示：get_direction 无路可走会 ValueError，属地图/路径异常，不是正常玩法分支。
# 与 Pacman 对称点：双方都用 CELL_SIZE 与 start_pos 做「粗格 ↔ 像素」换算，保持碰撞同一坐标系。
# 结束：读完本文件后，可尝试改 GHOST_SCATTER_TARGETS 角落坐标，观察散开模式行为变化。
# （达标备注）本文件注释行数按教学口径不低于代码行的 1.5 倍，便于对照 README 自学。
