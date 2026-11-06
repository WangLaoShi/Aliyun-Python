"""
吃豆人精灵（Pacman）模块。

**继承关系**：
- ``Pacman`` 继承 ``pygame.sprite.Sprite``。Sprite 是 pygame 对「可更新、可绘制、可编组」游戏对象的基类；
  子类通常实现 ``update()``，并在 ``__init__`` 里设置 ``self.image`` 与 ``self.rect``。

**本类职责概览**：
1. 加载四方向动画帧，按 ``game_state.direction`` 切换朝向。
2. 在 **tiny_matrix**（细分子网格）上移动，用子格检测墙，实现比「整格一跳」更平滑的像素移动。
3. 吃豆 / 能量豆，更新分数与 ``collectibles``；能量豆触发 ``USEREVENT`` 定时 scared 模式。
4. 左右隧道 ``boundary_check``：出界后从对侧 ``coord_matrix`` 查表重置像素 x。

**与 GameState 的协作**：
- 读：玩家输入方向 ``direction``、 scared 时长等。
- 写：``pacman_direction``、``pacman_rect``、分数、``level_complete``、能量事件 id 等。

初学者提示：``dt`` 参数在 ``update`` / ``move_pacman`` 中传入，但当前移动步长固定为 ``PACMAN_SPEED``，
尚未做「帧率无关」的 dt 缩放——这是常见的后续优化点。


**主循环与 tiny 网格**：
``runner`` 在 ``Group.update(dt)`` 调用 ``Pacman.update``。移动顺序为
``movement_bind``（读 ``game_state.direction`` + 墙检测）→ ``move_pacman``（``PACMAN_SPEED`` 像素步）
→ ``boundary_check``（隧道 ``coord_matrix`` 查表）→ ``eat_dots``（粗格 matrix 改 void）。

**direction 与 move_direction 分离**：
EventHandler 只写 ``direction``（玩家意图）；``movement_bind`` 在 ``edges_helper``/``edge_helper_horizontal``
通过后才写 ``move_direction`` 与 ``pacman_direction``，实现墙前预输入、出弯再转。

**吃豆与 frightened 事件链**：
``eat_dots`` 吃 power 调用 ``create_power_up_event``（``USEREVENT+2``），
``GameState.is_pacman_powered=True``；ghosts 侧 ``check_if_pacman_powered`` 换蓝皮并 ``make_ghost_scared``。
EventHandler 在 power 事件到点清 ``is_pacman_powered``。

**过关与 collectibles**：
``count_dots_powers`` 初值过滤不可达豆；``collectibles==0`` 置 ``level_complete``，
``ScreenManager`` wait 后 ``new PacmanGrid`` 加载 ``game_state.level`` 对应 JSON。

**subdiv 与 PACMAN_SPEED 配套**：
``subdiv = CELL_SIZE[0] // PACMAN_SPEED``；``move_pacman`` 每帧 ±1 子格对应 ±PACMAN_SPEED 像素。
改 configs 须同时验证 ``get_tiny_matrix`` 尺寸与 ``edges_helper`` 探测线位置。

**dt 参数说明**：
``update(dt)``/``move_pacman(dt)`` 保留 ``dt`` 以兼容 ``Group.update`` 签名，当前未参与速度公式，
帧率稳定依赖 ``clock.tick(60)``；帧率无关移动是常见后续优化。

**edges_helper 与 tiny 索引对应关系**：
左移：探测 ``tiny_start_y - 1`` 竖条；右移：探测 ``tiny_start_y + subdiv*2`` 竖条；
上移：``tiny_start_x - 1`` 横条；下移：``tiny_start_x + subdiv*2`` 横条。与 ``move_pacman`` 增量一致。

**分数与 HUD**：
``DOT_POINT``/``POWER_POINT`` 来自 configs；``GameState.points`` 初值 ``-DOT_POINT``，首颗豆后 HUD 显示 0；
``runner.check_highscores`` 每帧刷新内存最高，退出写 ``stats.json``。

**与 ghosts 的数据接口**：
每帧 ``move_pacman`` 写 ``pacman_rect`` 四元组；``movement_bind`` 写 ``pacman_direction`` 供 Pinky/Inky；
吃 power 触发 frightened 事件链，ghosts 读 ``is_pacman_powered`` 与 ``power_event_trigger_time``。

**过关与换关**：
``collectibles==0`` → ``level_complete`` → ``ScreenManager.check_level_complete`` ``wait(2000)`` →
``new PacmanGrid(game_state.level)``；matrix 在新 JSON 重载，分数与 level 状态保留在 ``GameState``。

**资源与动画**：
``sprite_configs.PACMAN_PATHS`` 四向三帧；``frame_delay=5`` 降帧嘴型；``direction_mapper`` 键 ``l/r/u/d`` 对应键盘写入的 ``direction``。
"""

from math import ceil
from typing import Union

from pygame import image, transform
from pygame.sprite import Sprite
from pygame import Surface, USEREVENT
from pygame.time import set_timer, get_ticks

from src.configs import CELL_SIZE, PACMAN_SPEED, PACMAN, DOT_POINT, POWER_POINT
from src.game.state_management import GameState
from src.sprites.sprite_configs import *
from src.utils.coord_utils import (get_coords_from_idx,
                                   get_idx_from_coords,
                                   get_tiny_matrix,
                                   precompute_matrix_coords)
from src.sounds import SoundManager
from src.log_handle import get_logger

logger = get_logger(__name__)


class Pacman(Sprite):
    """
    玩家吃豆人：四向动画、tiny 网格移动、吃豆计分、能量豆 frightened、隧道穿屏。

    **update 流水线**（每帧 ``Group.update``）：
    ``frame_update`` → ``build_bounding_boxes`` → ``movement_bind`` → ``move_pacman``
    → ``boundary_check`` → ``eat_dots`` → ``frame_direction_update`` → 检查 ``collectibles``。

    **双方向模型**：
    - ``game_state.direction``：键盘意图（EventHandler）；
    - ``move_direction`` / ``pacman_direction``：墙检测通过后的实际朝向（供 Pinky 等 AI）。

    **tiny 网格**：
    ``subdiv = CELL_SIZE // PACMAN_SPEED``；移动 ±1 子格 ↔ ±PACMAN_SPEED 像素；
    ``edges_helper_*`` 在子格精度探测墙。

    **共享 matrix**：
    ``eat_dots`` 把 dot/power 改 void，``PacmanGrid.draw_level`` 下一帧不再画豆。

    **dt 说明**：
    签名保留 ``dt``，当前速度不乘 ``dt``，帧率靠 ``clock.tick(60)`` 稳定。
    """

    def __init__(self,
                 screen: Surface,
                 game_state: GameState,
                 matrix: list[list[str]],
                 pacman_pos: tuple,
                 start_pos: tuple):
        """
        构造 Pacman：加载动画、建立 tiny 网格与坐标查表、统计 ``collectibles``。

        Args:
            screen: 主 Surface 引用（可选 blit，主绘制仍靠 ``Group.draw``）。
            game_state: 读写 ``direction``、分数、``pacman_rect``、过关与能量豆标志。
            matrix: 与 ``PacmanGrid`` 共享的关卡网格，``eat_dots`` 会改 dot/power→void。
            pacman_pos: JSON ``pacman_start`` 粗格 ``(row,col)``。
            start_pos: 迷宫像素原点 ``(start_x,start_y)``。

        构造顺序：
        ``load_all_frames`` → ``calculate_pacman_coords`` → ``load_image`` →
        ``calculate_tiny_matrix`` → ``calculate_coord_matrix`` → ``count_dots_powers``。

        游戏含义：
        ``ScreenManager`` 构造/``reset_stage`` 会 ``new Pacman`` 同关重生；过关后 ``new PacmanGrid`` 重载 JSON。
        """
        # super() 调用 Sprite.__init__，注册 self.image/self.rect 等 pygame 约定属性
        super().__init__()
        # 绘制目标 Surface（本类也可被外部 blit，此处保留引用）
        self.screen = screen
        # 全局状态：分数、输入方向、能量豆、矩形同步
        self.game_state = game_state
        # 出生时在粗地图上的 (row, col)
        self.pacman_pos = pacman_pos
        # 可变的地图副本，吃豆会把 "dot" 改成 "void"
        self.matrix = matrix
        # 地图左上角像素 (start_x, start_y)
        self.start_pos = start_pos
        # 四方向 PNG 动画列表 + direction_mapper
        self.load_all_frames()
        # 粗格索引 → 初始像素坐标
        self.calculate_pacman_coords()
        # 设置 self.image 与 rect 到第一帧
        self.load_image()
        # 细碰撞网格 + subdiv + tiny_start_*
        self.calculate_tiny_matrix()
        # 隧道穿屏用的像素查表
        self.calculate_coord_matrix()
        # 动画降帧：每 5 个逻辑帧换一张嘴型图
        self.frame_delay = 5
        # 吃豆音效封装
        self.sound = SoundManager()
        # 剩余豆数，归零则过关
        self.collectibles = self.count_dots_powers()

    # ------------------------------------------------------------------
    # 关卡数据：统计剩余豆数（过关条件 collectibles == 0）
    # ------------------------------------------------------------------

    def count_dots_powers(self):
        """
        统计本关剩余可吃豆（过关条件 ``collectibles==0``）。

        规则：
        当前格为 dot/power，且 ``matrix[row+1][col]`` 不是 wall/elec/null 才计数。

        游戏含义：
        过滤「豆贴在墙顶」等编辑器异常，防止永远无法 ``level_complete``。

        Returns:
            int 剩余豆数，初值存 ``self.collectibles``。
        """
        # 累加器：还剩多少豆要吃完
        collectibles = 0
        # 外层：行索引
        for row in range(len(self.matrix)):
            # 内层：列索引
            for col in range(len(self.matrix[0])):
                # 防御：避免 row+1 越界写法误用列界
                if col + 1 >= len(self.matrix[0]):
                    # 跳过本列
                    continue
                # 当前格是豆，且正下方一格不是墙/电/空，才计入总数
                if self.matrix[row][col] in ['dot', 'power'] and \
                        self.matrix[row+1][col] not in ['wall', 'elec', 'null']:
                    # 找到一个有效豆
                    collectibles += 1
        # logger.info("total_collectibles: %s",collectibles)
        # 供 update 判断 level_complete
        return collectibles

    # ------------------------------------------------------------------
    # 显示：当前帧、碰撞矩形居中
    # ------------------------------------------------------------------

    def load_image(self):
        """把 ``self.frames[curr_frame_idx]`` 设为 ``self.image``，并同步 rect 左上角。"""
        # Sprite 绘制用位图
        self.image = self.frames[self.curr_frame_idx]
        # 逻辑移动用的 x（可与 rect.x 略有偏移）
        self.rect_x = self.pacman_x_coord
        # 逻辑移动用的 y
        self.rect_y = self.pacman_y_coord
        self.rect = self.image.get_rect(topleft=(self.pacman_x_coord,
                                                 self.pacman_y_coord))  # 碰撞/绘制矩形

    def build_bounding_boxes(self, x: Union[int, float], y: Union[int, float]):
        """
        精灵贴图可能比逻辑格小；在 (x,y) 格基础上 **居中** 放置 rect。

        ``CELL_SIZE[0] * 2`` 表示吃豆人在地图上占 2 格宽的逻辑区域。
        """
        self.rect.x = x + (CELL_SIZE[0] * 2 - self.rect.width) // 2
        self.rect.y = y + (CELL_SIZE[1] * 2 - self.rect.height) // 2

    def frame_update(self):
        """
        嘴型动画降帧。

        每帧 ``frame_delay -= 1``，到 0 则重置为 5 并 ``curr_frame_idx = (idx+1) % len(frames)``，
        更新 ``self.image``。

        游戏含义：
        三帧 PNG 循环模拟 Pac 张嘴；与 ``frame_direction_update`` 换向列表独立。

        Returns:
            None。
        """
        # 倒计时，未到 0 则保持同一帧
        self.frame_delay -= 1
        # 到点换帧
        if self.frame_delay <= 0:
            # 重新装载间隔
            self.frame_delay = 5
            # 循环索引
            self.curr_frame_idx = (self.curr_frame_idx + 1) % len(self.frames)
            # 刷新嘴型
            self.image = self.frames[self.curr_frame_idx]

    def frame_direction_update(self):
        """
        按 ``move_direction`` 切换 ``self.frames`` 列表。

        ``move_direction`` 非空时，``direction_mapper[l/r/u/d]`` → left/right/up/down 帧序列。

        游戏含义：
        贴图朝向与实际行走方向一致；停墙边时 ``move_direction`` 可仍保留上一方向。

        Returns:
            None。
        """
        if self.move_direction != "":
            self.frames = self.direction_mapper[self.move_direction]

    # ------------------------------------------------------------------
    # 坐标系：粗格像素起点、tiny 网格、预计算查表
    # ------------------------------------------------------------------

    def calculate_pacman_coords(self):
        """
        将 JSON ``pacman_start`` 粗格转为像素缓存。

        使用 ``get_coords_from_idx`` 与 ``start_pos``、``CELL_SIZE``、matrix 尺寸。

        游戏含义：
        ``load_image`` 用 ``pacman_x/y_coord`` 设首帧 ``rect``；移动后改 ``rect_x/y``。

        Returns:
            None。
        """
        x, y = get_coords_from_idx(
            self.pacman_pos,
            self.start_pos[0],
            self.start_pos[1],
            CELL_SIZE[0],
            CELL_SIZE[1],
            len(self.matrix),
            len(self.matrix[0])
        )
        # 缓存像素 x，移动时改 rect_x 再 build_bounding_boxes
        self.pacman_x_coord = x
        # 缓存像素 y
        self.pacman_y_coord = y

    def load_all_frames(self):
        """
        加载四向嘴型动画资源。

        内部 ``frame_helper(direction)`` 列表推导：
        ``PACMAN_PATHS[direction]`` 每路径 ``load→convert_alpha→scale(PACMAN)``。

        初始化 ``direction_mapper`` 键 l/r/u/d，默认 ``frames=right_frames``。

        游戏含义：
        资源路径集中在 ``sprite_configs``；换皮肤只改 PNG 不改逻辑。

        Returns:
            None。
        """

        def frame_helper(direction):
            width, height = PACMAN
            return [
                transform.scale(image.load(path).convert_alpha(), (width, height))
                for path in PACMAN_PATHS[direction]
            ]

        # 当前动画帧下标
        self.curr_frame_idx = 0
        # 键 "l" 使用的列表
        self.left_frames = frame_helper("left")
        self.right_frames = frame_helper("right")
        self.down_frames = frame_helper("down")
        self.up_frames = frame_helper("up")
        # 把单字母方向键映射到对应帧序列（与键盘 handler 约定一致）
        self.direction_mapper = {
            "l": self.left_frames,
            "r": self.right_frames,
            "u": self.up_frames,
            "d": self.down_frames,
        }
        # 默认朝向，直到玩家按键
        self.frames = self.right_frames
        # 实际在走的方向（可能被墙挡住）
        self.move_direction = self.game_state.direction

    def calculate_tiny_matrix(self):
        """
        初始化 tiny 碰撞网格与子格起点。

        调用 ``get_tiny_matrix(matrix, CELL_SIZE[0], PACMAN_SPEED)``：
        墙粗格复制为子格 wall，其余 null。

        ``subdiv = CELL_SIZE[0] // PACMAN_SPEED``；
        ``tiny_start_x/y = pacman_pos * subdiv`` 粗格转 subgrid 索引。

        游戏含义：
        移动与墙检测在子格精度，比粗格一格一跳更平滑。

        Returns:
            None（写入实例属性）。
        """
        self.tiny_matrix = get_tiny_matrix(self.matrix,
                                           CELL_SIZE[0],
                                           PACMAN_SPEED)
        self.subdiv = CELL_SIZE[0] // PACMAN_SPEED
        self.tiny_start_x = self.pacman_pos[0] * self.subdiv
        self.tiny_start_y = self.pacman_pos[1] * self.subdiv

    def calculate_coord_matrix(self):
        """为 tiny 网格每个子格预存像素坐标，供隧道瞬移时 O(1) 读取。"""
        self.coord_matrix = precompute_matrix_coords(*self.start_pos,
                                                     PACMAN_SPEED,
                                                     len(self.tiny_matrix),
                                                     len(self.tiny_matrix[0]))

    # ------------------------------------------------------------------
    # 碰撞：在 tiny_matrix 上探测 2×subdiv 宽的墙条
    # ------------------------------------------------------------------

    def edges_helper_vertical(self, row: int,
                              col: int,
                              additive: int):
        """横向移动前：沿列方向 ``additive`` 检查竖条子格是否全是非墙。"""
        # 吃豆人高度占 2*subdiv 条子格
        for r in range(self.subdiv * 2):
            if self.tiny_matrix[row + r][col + additive] == "wall":
                # 前方竖条任一子格是墙 → 不可横移
                return False
        # 整条探测带畅通
        return True

    def edge_helper_horizontal(self, row: int,
                               col: int,
                               additive: int):
        """纵向移动前：沿行方向 ``additive`` 检查横条子格是否全是非墙。"""
        # 宽度同样占 2*subdiv
        for c in range(self.subdiv * 2):
            if self.tiny_matrix[row + additive][col + c] == "wall":
                # 前方横条有墙
                return False
        return True

    def boundary_check(self):
        """
        子格列 wrap + ``coord_matrix`` 查表改 ``rect_x``。

        右出界：
        ``tiny_start_y + subdiv*2 >= len(tiny_matrix[0])-1`` → 列归 0，x 取 ``coord_matrix[tiny_start_x][0][0]``。

        左出界：
        ``tiny_start_y-1<0`` → 列跳到 ``len-(subdiv*3)``，x 取负偏移列像素。

        游戏含义：
        与 JSON 地图左右隧道一致；ghost 在粗格列 ``_boundary_check`` 层 wrap，实现平行。

        Returns:
            None。
        """
        # 从右侧出界
        if (self.tiny_start_y + self.subdiv * 2) >= len(self.tiny_matrix[0]) - 1:
            # 子格列回到最左
            self.tiny_start_y = 0
            # 查表取对应像素 x
            self.rect_x = self.coord_matrix[self.tiny_start_x][0][0]

        # 从左侧出界
        elif (self.tiny_start_y - 1) < 0:
            # 列跳到右侧隧道口
            self.tiny_start_y = len(self.tiny_matrix[0]) - (self.subdiv * 3)
            # 魔法列索引对齐美术
            self.rect_x = self.coord_matrix[self.tiny_start_x][-self.subdiv*2 - 4][0]

    # ------------------------------------------------------------------
    # 交互：能量豆定时事件、吃豆计分
    # ------------------------------------------------------------------

    def create_power_up_event(self):
        """
        吃 power 豆后注册 frightened 结束定时器。

        ``USEREVENT+2`` → ``game_state.power_up_event``；
        ``set_timer(..., scared_time)``；
        ``is_pacman_powered=True``，``power_event_trigger_time=get_ticks()``。

        游戏含义：
        EventHandler 到点清 ``is_pacman_powered``；ghosts ``check_if_pacman_powered`` 恢复 normal。

        Returns:
            None。
        """
        # pygame 保留 USEREVENT 以上给自定义事件
        CUSTOM_EVENT = USEREVENT + 2
        set_timer(CUSTOM_EVENT,
                self.game_state.scared_time)  # 到期后 pygame 投递 CUSTOM_EVENT 到队列
        # 主循环据此识别是哪一种定时器
        self.game_state.power_up_event = CUSTOM_EVENT
        # 幽灵 AI 读此标志变 scared
        self.game_state.is_pacman_powered = True
        # 毫秒时间戳，协调出笼幽灵
        self.game_state.power_event_trigger_time = get_ticks()

    def eat_dots(self):
        """
        粗格判豆与能量豆 frightened 触发。

        使用 ``get_idx_from_coords(rect.x, rect.y, start_pos, CELL_SIZE)`` 得 (row,col)。

        dot:
            matrix→void，chomp 音效，``DOT_POINT``，``collectibles-=1``。

        power:
            void + ``create_power_up_event``（``USEREVENT+2``）+ ``POWER_POINT``。

        游戏含义：
            与 ``PacmanGrid`` 共享 matrix，渲染层下一帧 ``draw_level`` 反映 void。

        Returns:
            None。
        """
        r, c = get_idx_from_coords(
            self.rect.x, self.rect.y, *self.start_pos, CELL_SIZE[0]
        )
        # 普通豆
        if self.matrix[r][c] == "dot":
            # 地图上移除，渲染层不再画豆
            self.matrix[r][c] = "void"
            self.sound.play_sound("dot")
            self.collectibles -= 1
            self.game_state.points += DOT_POINT
        # 能量豆：额外 frightened 模式
        elif self.matrix[r][c] == "power":
            self.matrix[r][c] = "void"
            # 启动定时 scared
            self.create_power_up_event()
            self.sound.play_sound("dot")
            self.collectibles -= 1
            self.game_state.points += POWER_POINT

    # ------------------------------------------------------------------
    # 移动：输入绑定 + 逐步像素位移
    # ------------------------------------------------------------------

    def movement_bind(self):
        """
        预输入转弯：意图方向 vs 实际 ``move_direction``。

        对每个 ``game_state.direction`` 分支调用 ``edges_helper_vertical`` 或 ``edge_helper_horizontal``；
        仅当探测带内子格均非 wall 时，更新 ``move_direction`` 与 ``game_state.pacman_direction``。

        游戏含义：
        墙前按住转向键，Pac 出弯后自动转向；Pinky 读 ``pacman_direction`` 瞄前方格。

        Returns:
            None。
        """
        # 玩家请求向左
        if self.game_state.direction == 'l':
            # 左侧无墙
            if self.edges_helper_vertical(self.tiny_start_x, self.tiny_start_y, -1):
                # 允许实际左移
                self.move_direction = "l"
                # 同步给 Pinky 等 AI
                self.game_state.pacman_direction = 'l'
        # 向右
        elif self.game_state.direction == 'r':
            if self.edges_helper_vertical(
                self.tiny_start_x, self.tiny_start_y, self.subdiv * 2
            ):  # 探测线在右侧
                self.move_direction = "r"
                self.game_state.pacman_direction = 'r'
        # 向上
        elif self.game_state.direction == 'u':
            if self.edge_helper_horizontal(self.tiny_start_x, self.tiny_start_y, -1):
                self.move_direction = "u"
                self.game_state.pacman_direction = 'u'
        # 向下
        elif self.game_state.direction == 'd':
            if self.edge_helper_horizontal(
                self.tiny_start_x, self.tiny_start_y, self.subdiv * 2
            ):
                self.move_direction = "d"
                self.game_state.pacman_direction = 'd'

    def move_pacman(self, dt: float):
        """
        像素步进 + 子格索引同步。

        Args:
            dt: 保留未用；步长 ``PACMAN_SPEED`` 来自 configs。

        左右：
        改 ``rect_x`` 与 ``tiny_start_y``（±1），探测线 ``edges_helper_vertical``。

        上下：
        改 ``rect_y`` 与 ``tiny_start_x``，探测 ``edge_helper_horizontal``。

        副作用：
        写 ``game_state.pacman_rect`` 四元组 (x,y,2*CELL,2*CELL) 供 ``ghosts.check_collisions``。

        Returns:
            None。
        """
        # 向左：像素 x 减，子格列减
        if self.move_direction == "l":
            if self.edges_helper_vertical(self.tiny_start_x, self.tiny_start_y, -1):
                self.rect_x -= PACMAN_SPEED
                self.tiny_start_y -= 1
        # 向右：探测线在右侧 subdiv*2 处
        elif self.move_direction == "r":
            if self.edges_helper_vertical(
                self.tiny_start_x, self.tiny_start_y, self.subdiv * 2
            ):
                self.rect_x += PACMAN_SPEED
                self.tiny_start_y += 1
        # 向上：像素 y 减，子格行减
        elif self.move_direction == "u":
            if self.edge_helper_horizontal(self.tiny_start_x, self.tiny_start_y, -1):
                self.rect_y -= PACMAN_SPEED
                self.tiny_start_x -= 1
        # 向下
        elif self.move_direction == "d":
            if self.edge_helper_horizontal(
                self.tiny_start_x, self.tiny_start_y, self.subdiv * 2
            ):
                self.rect_y += PACMAN_SPEED
                self.tiny_start_x += 1

        # 同步给幽灵 AI：粗碰撞盒 (x,y,w,h)，宽高为两格
        self.game_state.pacman_rect = (self.rect_x, self.rect_y,
                                       CELL_SIZE[0]*2, CELL_SIZE[0]*2)

    def update(self, dt: float):
        """
        ``pygame.sprite.Sprite`` 帧入口。

        Args:
            dt: 传给 ``move_pacman``，当前未参与速度公式。

        顺序：
        动画 → 居中 rect → 绑定方向 → 位移 → 隧道 → 吃豆 → 换向帧 → 过关旗。

        游戏含义：
        ``eat_dots`` 在移动之后，判格基于本帧 ``rect``；``pacman_rect`` 在 ``move_pacman`` 内写入供鬼碰撞。
        """
        # 嘴型动画
        self.frame_update()
        # rect 与贴图对齐
        self.build_bounding_boxes(self.rect_x, self.rect_y)
        # 读取玩家意图 → move_direction
        self.movement_bind()
        # 实际位移（dt 暂未参与速度公式）
        self.move_pacman(dt)
        # 横向隧道
        self.boundary_check()
        # 判格吃豆
        self.eat_dots()
        # 换朝向贴图
        self.frame_direction_update()
        # 全部有效豆已吃完
        if self.collectibles == 0:
            # 通知关卡系统（ScreenManager.check_level_complete 会重建迷宫）
            self.game_state.level_complete = True

# —— 小白阅读路线 ——
# 1) load_all_frames / direction_mapper：字典映射方向到动画列表；
# 2) tiny_matrix：把墙格放大，便于按 PACMAN_SPEED 像素步进判墙；
# 3) movement_bind + move_pacman：意图与真实移动分离（按键先缓存到 GameState.direction）；
# 4) eat_dots：改 matrix 字符串 + 加分 + 能量事件；collectibles==0 触发过关。
# Python：Sprite 继承、列表推导加载图、取模循环帧、坐标换算工具函数、单例 SoundManager。
