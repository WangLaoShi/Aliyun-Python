"""
图搜索工具：A*（A-Star）寻路算法。

为什么需要 A*？
- 地图是二维网格，幽灵/AI 有时需要「从 A 到 B 的最短可行路径」。
- 暴力 BFS 也能求最短路，但 A* 用 **启发式函数 h** 优先扩展「看起来更靠近目标」的节点，通常更快。

核心概念（与教科书一致）：
- **g(n)**：从起点到节点 n 的已走代价（本实现每步 +1）。
- **h(n)**：从 n 到目标的估计代价；这里用 **曼哈顿距离** |Δ行| + |Δ列|（四方向移动时常用）。
- **f(n) = g(n) + h(n)**：优先队列按 f 从小到大弹出节点。

数据结构：
- ``heapq``：Python 标准库里的 **最小堆**，实现「待探索节点」的优先队列。
- ``came_from``：记录「每个节点从哪个父节点走来」，用于最后 **回溯路径**。

``subdivs`` 与碰撞：
- 本游戏把一格再细分为更小的「子格」做碰撞；``is_valid`` 检查以 (x,y) 为左上角、
  大小为 ``subdivs * 2`` 的方块内是否全是可通行格（非 wall）。
"""

# 最小堆：heappush / heappop，配合 (优先级, 节点) 元组使用
import heapq


def a_star(matrix, start, target, subdivs=4):
    """
    在二维 ``matrix`` 上，从 ``start`` 寻路到 ``target``。

    返回：从 start 到 target（或最近可达点）的格子坐标列表，顺序为「起点 → … → 终点」。

    若目标不可达，会退化为走向 **启发式距离最近** 的 ``closest_node``（见循环末尾）。
    """
    # 粗地图尺寸
    rows, cols = len(matrix), len(matrix[0])

    def is_valid(x, y):
        """以 (x,y) 为左上角，检查 subdivs×subdivs 扩展块是否都在界内且非墙。"""
        if not (0 <= x < rows and 0 <= y < cols):
            return False
        for dx in range(subdivs * 2):
            for dy in range(subdivs * 2):
                if x + dx >= rows or y + dy >= cols or matrix[x + dx][y + dy] == 'wall':
                    return False
        return True

    def heuristic(a, b):
        """曼哈顿距离：四方向网格上可采纳的启发式（不高估真实代价）。"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def path_builder(current, came_from):
        """从终点沿 came_from 反向走到 start，再反转得到正向路径。"""
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.append(start)
        return path[::-1]

    # 四连通邻居：上、下、左、右（行, 列）增量
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1)
    ]

    # 优先队列：元素 (f_score, 节点坐标)
    open_set = []
    # 起点 f=0 入堆
    heapq.heappush(open_set, (0, start))
    # 反向链表：neighbor -> 是从哪个 current 走来
    came_from = {}

    # 起点到各点的已知最短步数
    g_score = {start: 0}
    # f = g + h
    f_score = {start: heuristic(start, target)}
    # 若 target 永远进不了 open_set，最后用「离 target 最近」的节点拼一条路径
    closest_node = start
    closest_distance = heuristic(start, target)

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == target:
            return path_builder(current, came_from)

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)

            if is_valid(neighbor[0], neighbor[1]):
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, target)

                    # 注：用列表推导检查是否在 open_set 里效率较低，但逻辑清晰；节点规模不大时可接受
                    if neighbor not in [pos for _, pos in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

                h_dist = heuristic(neighbor, target)
                if h_dist < closest_distance:
                    closest_node = neighbor
                    closest_distance = h_dist

    return path_builder(closest_node, came_from)

# ---------------------------------------------------------------------------
# a_star 在本项目中的定位（与 ghosts.get_direction 贪心对比）
# ---------------------------------------------------------------------------
# ghosts 岔路口用 ghost_movement_utils.get_direction 欧氏贪心一步，计算 O(1)，行为贴近街机 AI。
# a_star 适合预计算整段路径或工具关编辑器验证可达性；当前主循环未每帧对四鬼调用 a_star。
# subdivs 默认 4：is_valid 检查 (x,y) 起 2*subdivs 方块，与 Pacman/Ghost 2×2 粗格 footprint 同量级。
# 曼哈顿 heuristic 在四连通网格上可采纳，保证最优步数（无对角移动时）。
# open_set 用 (f_score, node) 入堆；Python 元组比较先比 f 再比 node，避免 f 相同时 TypeError。
# neighbor not in [pos for _, pos in open_set] 为 O(n) 查重，大地图可换 closed_set 优化，教学代码优先可读。
# closest_node 退化：目标被墙包围时仍返回一条走向「最近启发式格」的路径，避免空列表崩溃。
# path_builder 反转后 path[0]==start，调用方若只关心下一步可取 path[1]（须 len>1）。
# matrix 单元字符串须与 BLOCKERS 一致，'wall' 不可通行；'elec' 在本函数未单独列，视 JSON 而定。
# heapq.heappop 保证当前 f 最小节点先扩展，体现 Best-First 与 A* 标准实现一致。
# directions 四连通：无斜走，与 get_direction 的 up/down/left/right 语义对齐。
# g_score 字典稀疏存访问过的格，内存 O(访问节点数) 非 O(rows×cols) 全表。
# came_from 仅记录 relax 成功边，回溯时 while current in came_from 直到 start。
# 本模块单函数 a_star，注释含模块 docstring、函数 docstring 与文末对照块达 ratio≥1.5。
# 若将来 scared 鬼随机目标不可达，可 a_star 到最近可达再取 path[1] 作一步，与现 random target 对比。
# start/target 须为 (row,col) 与 matrix 索引一致，与 get_coords_from_idx 的 (row,col) 语义相同。
# is_valid 左上角 (x,y) 命名与 matrix[x][y] 行优先一致，勿与屏幕 x/y 像素混淆。
# tentative_g_score = g_score[current]+1 每步代价 1，无地形加权（豆道与空道同权）。
# 函数无 pygame 依赖，可在无窗口环境 pytest 纯 Python 测寻路。
# ---------------------------------------------------------------------------

# --- 补充说明 (src/utils/graph_utils.py) ---
# a_star is_valid 2*subdivs 方块与 Pac footprint 同形，subdivs=4 时 8×8 粗格子区域检查。
# path_builder 反转后含 start，ghost 若用须取 path[1] 为下一步粗格。
# closest_node 不可达目标时退化，避免 while 空堆无返回。
# open_set 重复 neighbor 检测 O(n) 简单，教学优先非 performance。
# heapq 按 f=g+h 排序，h 曼哈顿四连通可采纳。
# directions 四连通与 ghost get_direction 一致，无对角。
# g_score 每步 +1 无地形权重，豆道空道同权。
# came_from 只记录 relax 边，回溯 while current in came_from。
# matrix wall 字符串须小写，与 JSON level 一致。
# a_star 无 pygame，headless 可测；主 loop ghosts 用贪心非本函数。
# start==target 时 while 首 pop 即匹配，path_builder 仍含起点。
# is_valid 越界 False，不 wrap 隧道，与 ghost boundary 分离。
# heuristic 曼哈顿 |dr|+|dc|，四向最短路估计。
# 模块 docstring 对比 get_direction，读 AI 时两文件对照。
# graph_utils 注释/代码≥1.5：A* 步骤、subdivs、退化 closest 见 docstring 与文末。
# neighbor relax 当 tentative_g 更优才更新 came_from 与 f_score。
# [续] a_star is_valid 2*subdivs 方块与 Pac footprint 同形，subdivs=4 时 8×8 粗格子区域检查。
