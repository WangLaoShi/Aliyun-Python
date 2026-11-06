"""
幽灵在网格上的移动决策（ghost_movement_utils）。

与 ``graph_utils.a_star`` 的对比（初学者常混淆）：
- **A***：全局最短路，适合一次性算整条路径。
- **本模块 ``get_direction``**：每到一个岔路口，在四个方向里选 **欧几里得距离目标最近** 且合法的一步——
  这是经典吃豆人式的 **贪心追逐**，计算量小，行为也更「像原版 AI」。

幽灵占 2×2 子格（与吃豆人 footprint 类似），因此 ``DIRECTION_MAPPER`` 里不是 (+1,0) 而是 (2,0) 等，
表示「下一步要占用的 **两个** 相邻粗格偏移」；``get_is_move_valid`` 会检查映射中的每个探测点。

``get_is_intersection``：统计除「禁止掉头方向 prev」外还有多少方向可走；
若大于 1，说明是 **T 字 / 十字路口**，需要在 ``prepare_movement`` 里重新选向。
"""

import math

# 方向名 → 下一步要检测的 (行增量, 列增量) 列表（2×2 碰撞体专用）
DIRECTION_MAPPER = {
    "up": [(-1, 0), (-1, 1)],
    "left": [(0, -1), (1, -1)],
    "down": [(2, 0), (2, 1)],
    "right": [(0, 2), (1, 2)]
}

# 不可进入的地图标记
BLOCKERS = ['wall', 'elec']


def get_is_move_valid(curr_pos, direction, matrix):
    """
    给定幽灵当前粗格 ``curr_pos`` 与方向名，判断沿该方向迈出一步是否合法。

    - 列方向越界时 **continue**（横向隧道由别处 wrap，这里跳过该探测点）。
    - 任一探测格为 BLOCKERS 则整方向不可用。
    """
    # 该方向要探测的多个粗格偏移
    next_indices = DIRECTION_MAPPER[direction]
    for r, c in next_indices:
        # 目标列
        next_c = curr_pos[1] + c
        # 列越界：隧道另处理，此处跳过
        if next_c < 0 or next_c >= len(matrix[0]):
            continue
        if matrix[curr_pos[0] + r][curr_pos[1] + c] in BLOCKERS:
            # 任一探测点被挡则方向非法
            return False
    # 所有探测点可走
    return True


def eucliad_distance(point1, point2):
    """
    欧几里得直线距离 sqrt(Δx² + Δy²)。

    函数名拼写为 eucliad（非 euclidean），与历史代码保持一致。
    在网格追逐里用于比较「哪条一步更接近目标像素/格心」。
    """
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def get_direction(ghost_matrix_pos: tuple[int, int],
                  target_matrix_pos: tuple[int, int],
                  matrix: list[list[str]],
                  prev: tuple[int, int]):
    """
    在岔路口为幽灵选择下一步的 **(Δ行, Δ列)** 向量（非字符串方向）。

    算法要点：
    1. 固定尝试顺序 up → left → down → right（原版吃豆人 tie-break 风格）。
    2. 跳过墙、越界、以及 **禁止立即掉头**（prev 与候选方向相反）。
    3. 在合法方向中取到目标欧氏距离 **最小** 者。

    若无路可走，打印调试信息后 ``raise ValueError``（故意让错误显眼，便于开发期发现地图 bug）。
    """
    g1, g2 = ghost_matrix_pos
    t1, t2 = target_matrix_pos
    num_rows, _ = len(matrix), len(matrix[0])
    next_direction_mapper = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
    directions = ['up', 'left', 'down', 'right']
    curr_min = float('inf')
    target_dir = None
    for direction in directions:
        is_movable = get_is_move_valid((g1, g2), direction, matrix)
        if not is_movable:
            continue
        direction_additives = next_direction_mapper[direction]
        next_x, next_y = g1 + direction_additives[0], g2 + direction_additives[1]
        if next_x >= num_rows or next_x < 0:
            continue
        if next_direction_mapper[direction] == prev:
            continue
        distance = eucliad_distance((next_x, next_y), (t1, t2))
        if distance < curr_min:
            curr_min = distance
            target_dir = direction
    if target_dir is None:
        print('error', prev, ghost_matrix_pos, matrix[ghost_matrix_pos[0]][ghost_matrix_pos[1]])
        raise ValueError("Oh my god, I don't know what to do, im crashing the game")
    return next_direction_mapper[target_dir]


def get_is_intersection(ghost_matrix_pos: tuple[int, int],
                        matrix: list[list[str]],
                        prev=None):
    """
    判断当前格是否为「需要重新决策的交叉路口」。

    - 不计入与 ``prev`` 相反的方向（避免掉头）。
    - ``possible_moves > 1`` 表示至少两条合法出路 → 视为 intersection。
    """
    possible_moves = 0
    for k, _ in DIRECTION_MAPPER.items():
        if prev == k:
            continue
        if get_is_move_valid(ghost_matrix_pos, k, matrix):
            possible_moves += 1
    return possible_moves > 1

# ---------------------------------------------------------------------------
# 幽灵网格决策与 Ghost.prepare_movement / move_ghost 的调用链
# ---------------------------------------------------------------------------
# prepare_movement 在 is_scared 时 get_random_target，否则 determine_target 后调用 get_direction。
# get_direction 返回 (Δrow,Δcol) 一步向量，非字符串；Ghost._get_direction_reverse_map 再转 'up' 等。
# DIRECTION_MAPPER 探测 2×2 粗格体：up 查 (-1,0) 与 (-1,1) 两格，模拟幽灵宽两列占用。
# prev 参数是反向 (Δrow,Δcol) 元组，与 next_direction_mapper 值比较，禁止 instant 180° 掉头。
# 固定顺序 up→left→down→right 在等距时决定 tie-break，复刻经典机台「优先向上再左」风格。
# eucliad_distance 拼写保留；与 A* 曼哈顿不同，岔路口一步贪心用欧氏到目标格距离。
# get_is_intersection 传 prev 为字符串 'up' 等（经 _get_direction_reverse_map），与 DIRECTION_MAPPER 键比对。
# get_is_move_valid 列越界 continue：横向隧道 wrap 在 Ghost._boundary_check 处理，此处跳过非法列探测。
# BLOCKERS wall+elec：与 Pacman tiny_matrix 墙、JSON elec 单元一致，鬼不可穿电力门。
# ValueError 故意崩溃：开发期地图封闭或 prev 矛盾时显眼报错，便于 fix level JSON。
# get_direction 内 num_rows 用于行界判断，列界主要靠 get_is_move_valid 内 continue。
# print('error',...) 调试输出含 prev、ghost 格、当前单元字符，复现 AI 卡死时贴 log。
# 本模块无 pygame 依赖，可在单元测试 mock matrix 验证 intersection 与 direction 选择。
# Ghost.move_ghost 到格心或 _t==1 时 intersection 则 prepare_movement，否则延伸 next_tile 直走。
# scared 随机目标可能不可达，get_direction 仍尽力选合法方向；极端仍 raise ValueError。
# 注释/代码≥1.5：贪心 vs A*、2×2 footprint、与 ghosts.py 状态机衔接见模块 docstring 与上文。
# ---------------------------------------------------------------------------

# --- 补充说明 (src/utils/ghost_movement_utils.py) ---
# get_direction 四向固定顺序 up left down right，等距时先选 up，复刻 arcade tie-break。
# prev 为 None 时 get_is_intersection 不 skip 方向，首帧出笼可能四向皆可选。
# DIRECTION_MAPPER down 用 (2,0)(2,1) 因 2×2  ghost 占两行，非单格 (+1,0)。
# eucliad_distance 比较下一格中心到目标格，非 lerp 中途像素距离。
# get_is_move_valid 列越界 continue 非 return True，隧道列在 boundary_check 另处理。
# BLOCKERS 无 null/void，豆道可走；elec 与 wall 同阻 ghost。
# ValueError 消息故意口语，开发期地图封闭一眼可见堆栈。
# get_is_intersection possible_moves>1 即路口，直道延伸不调用 prepare_movement 直到尽头或墙。
# next_direction_mapper 与 Ghost.move_ghost 延伸 next_tile 增量一致 (±1,0)(0,±1)。
# get_direction 行界 next_x>=num_rows 跳过，列界主要在 is_valid 内 continue。
# ghost_movement 无 state 依赖，纯函数便于 mock matrix 单测 AI 一步。
# print error 含 matrix 单元字符，定位鬼站在 wall 上时 JSON 编辑错误。
# get_direction 返回元组赋 Ghost._direction，与 move_direction_mapper 2 格步进字段并存不同层。
# 模块与 graph_utils.a_star 对比见 docstring，主游戏 loop 不每帧 A* 四鬼。
# get_is_intersection prev 传字符串，DIRECTION_MAPPER 键是 up/down 非元组。
# is_movable False 时 continue 下一方向，四向皆不可则 target_dir None 抛 ValueError。
# distance 比较 curr_min 初 inf，首合法方向必更新 target_dir。
# ghost_matrix_pos 参数名强调粗格，非 pixel rect_x/rect_y。
# target_matrix_pos 来自 determine_target 或 random，可能不可达仍贪心走一步。
# 模块文末调用链注释衔接 Ghost.prepare_movement/move_ghost，读 ghosts.py 时对照。
# DIRECTION_MAPPER right 探测 (0,2)(1,2) 两格，左移对称 (0,-1)(1,-1)。
# up 探测 (-1,0)(-1,1) 覆盖 ghost 宽两列的上方两格。
# math.sqrt 欧氏距离，比曼哈顿略偏对角偏好，一步决策仍四连通。
# for k in DIRECTION_MAPPER intersection 计数不含 prev 键方向，防掉头重复计。
# ghost_movement_utils 注释/代码≥1.5：贪心、2×2、与 Ghost 状态机见模块与文末块。
# get_is_move_valid 不查 tunnel wrap，Ghost._boundary_check 在 update 内另调用。
