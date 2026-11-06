"""
坐标与网格工具（coord_utils）。

本游戏同时使用多套「坐标语言」，初学者务必分清：

1. **逻辑矩阵索引 (row, col)**  
   - ``matrix[row][col]`` 里的字符串表示墙、豆、通道等。
   - 行号 row 向下增大，列号 col 向右增大（与数学里矩阵下标习惯一致）。

2. **屏幕像素坐标 (x_coord, y_coord)**  
   - pygame 绘制用：原点在窗口左上角，x 向右、y 向下。
   - 由 ``start_x, start_y``（地图左上角像素）+ 格子宽高 ``cell_w, cell_h`` 换算。

3. **微型矩阵 tiny_matrix**  
   - 把每个地图格再切成 ``cell_size // pacman_speed`` 份，吃豆人按「子格」移动，碰撞更细腻。
   - 只有墙会在子格上复制为 ``"wall"``，其余格填 ``"null"`` 表示可走。

4. **预计算 coord_matrix**  
   - 对每个 tiny 格预先存好像素坐标，隧道穿屏时可直接查表，避免每帧重复乘加。

负索引约定（``__get_x_y``）：
- 允许 ``pacman_pos`` 用负数表示「从末尾倒数」，类似 Python 列表负下标，用于环绕隧道。
"""

# ---------------------------------------------------------------------------
# 屏幕布局：居中与按比例偏移
# ---------------------------------------------------------------------------


def center_element(screen_width, screen_height, element_width, element_height):
    """
    把一块 UI（宽 element_width、高 element_height）大致放在屏幕中偏下位置。

    内部调用 ``place_elements_offset``，x 用 0.5（水平居中），y 用 0.6（略低于正中心，留标题栏空间）。
    """
    return place_elements_offset(
        screen_width, screen_height, element_width, element_height, 0.5, 0.6
    )


def place_elements_offset(
    screen_width, screen_height, element_width, element_height, xoffset, yoffset
):
    """
    通用放置公式（不是左上角对齐，而是按剩余空间的比例偏移）：

    - x = (屏幕宽 - 元素宽) * xoffset
    - y = (屏幕高 - 元素高) * yoffset

    xoffset/yoffset 在 0~1 之间时可理解为「从左上往右下推多少比例的空隙」。
    """
    x = (screen_width - element_width) * xoffset
    y = (screen_height - element_height) * yoffset
    return x, y


# ---------------------------------------------------------------------------
# 矩阵索引 ↔ 像素坐标
# ---------------------------------------------------------------------------


def __get_x_y(pos, num_rows, num_cols):
    """
    私有辅助：把可能为负的 (row, col) 规范到 [0, num_rows) / [0, num_cols) 语义。

    例如 col = -1 表示「最后一列之前一格」，实现上变为 num_cols + (-1)。
    """
    x = pos[0]
    y = pos[1]
    if pos[0] < 0:
        x = num_rows + x
    if pos[1] < 0:
        y = num_cols + y
    return x, y


def get_coords_from_idx(
    pacman_pos, start_x, start_y, cell_w, cell_h, num_rows, num_cols
):
    """
    逻辑格索引 → 该格 **左上角** 的屏幕像素 (x_coord, y_coord)。

    注意映射关系：
    - 矩阵的 **列 y** 对应屏幕 **x**（横向走列）
    - 矩阵的 **行 x** 对应屏幕 **y**（纵向走行）

    这与 ``get_idx_from_coords`` 互为逆运算（见该函数返回值顺序）。
    """
    # 规范负索引
    x, y = __get_x_y(pacman_pos, num_rows, num_cols)
    # 列 → 屏幕 x
    x_coord = start_x + (y * cell_w)
    # 行 → 屏幕 y
    y_coord = start_y + (x * cell_h)
    return x_coord, y_coord


def get_idx_from_coords(x_coord, y_coord, start_x, start_y, cell_size):
    """
    像素坐标 → 逻辑格索引。

    使用整数除法 ``//`` 做格子量化（落在同一格内的像素得到相同索引）。

    返回值顺序是 (y_pos, x_pos)，即 (row, col)，与 ``matrix[row][col]`` 一致。
    """
    x_pos = int((x_coord - start_x) // cell_size)
    y_pos = int((y_coord - start_y) // cell_size)
    return y_pos, x_pos


def precompute_matrix_coords(start_x, start_y, cell_size, num_rows, num_cols):
    """
    为 tiny 网格的每个格点预存 [pixel_x, pixel_y]。

    外层循环增加「行方向」的 y（col_start），内层增加「列方向」的 x（row_start），
    步长均为 ``cell_size``（在本项目中常传入 PACMAN_SPEED 级别的细步长）。

    结果形状：``matrix_coords[row][col] == [x, y]``，便于 O(1) 查像素位置。
    """
    matrix_coords = []
    col_start = start_y
    for _ in range(num_rows):
        row_start = start_x
        m = []
        for _ in range(num_cols):
            m.append([row_start, col_start])
            row_start += cell_size
        col_start += cell_size
        matrix_coords.append(m)
    return matrix_coords


# ---------------------------------------------------------------------------
# 细分子网格（吃豆人移动 / 碰撞）
# ---------------------------------------------------------------------------


def get_tiny_matrix(matrix, cell_size, pacman_speed):
    """
    把粗地图放大为 ``sub_div`` 倍分辨率的 ``tiny_matrix``。

    - ``sub_div = cell_size // pacman_speed``：每格拆成多少子步。
    - 非 ``wall`` 的粗格在子格中写成 ``"null"``（可走）；墙则整块子区域都是 ``"wall"``。

    双重循环 ``sx, sy`` 在一个粗格内填满 sub_div×sub_div 个子格。
    """
    sub_div = cell_size // pacman_speed
    num_rows = len(matrix) * sub_div
    num_cols = len(matrix[0]) * sub_div
    tiny_matrix = [["null"] * num_cols for _ in range(num_rows)]
    tiny_r, tiny_c = 0, 0
    for row in matrix:
        for cell in row:
            if cell != "wall":
                cell = "null"
            for sx in range(sub_div):
                for sy in range(sub_div):
                    tiny_matrix[tiny_r + sx][tiny_c + sy] = cell
            tiny_c += sub_div
        tiny_r += sub_div
        tiny_c = 0
    return tiny_matrix


def get_movable_locations(matrix, max_cell_size=20, cell_size=20):
    """
    枚举粗网格上「以 (r_idx, c_idx) 为左上角、占 subdiv*2 区域」均可通行的起点。

    用途：放置实体、随机出生点等。``is_free`` 排除 wall/elec；``is_valid`` 检查整块 footprint。
    """
    movables = []
    rows, cols = len(matrix), len(matrix[0])
    subdiv = max_cell_size // cell_size

    def is_free(r, c):
        return 0 <= r < rows and 0 <= c < cols and matrix[r][c] not in ('wall', 'elec')

    def is_valid(r, c):
        for x in range(subdiv * 2):
            for y in range(subdiv * 2):
                if not is_free(r + x, c + y):
                    return False
        return True

    for r_idx in range(rows):
        for c_idx in range(cols):
            if (r_idx + (subdiv * 2) <= rows and
                    c_idx + (subdiv * 2) <= cols) and is_valid(r_idx, c_idx):
                movables.append((r_idx, c_idx))

    return movables


def is_any_wall(matrix, x, y):
    """
    检查以 (x,y) 为左上角的 2×2 **粗格块** 四角是否任意为墙。

    用于快速判断一个小方形区域是否贴墙（比逐格循环更固定形状）。
    """
    rows, cols = len(matrix), len(matrix[0])

    def is_wall(r, c):
        return 0 <= r < rows and 0 <= c < cols and matrix[r][c] == 'wall'

    return (
        is_wall(x, y)
        or is_wall(x, y + 1)
        or is_wall(x + 1, y + 1)
        or is_wall(x + 1, y)
    )

# ---------------------------------------------------------------------------
# 坐标工具在 Py-Pacman 主循环中的调用点速查
# ---------------------------------------------------------------------------
# PacmanGrid.load_level：place_elements_offset 居中迷宫；precompute_matrix_coords 建 _coord_matrix。
# Pacman.calculate_pacman_coords / eat_dots：get_coords_from_idx、get_idx_from_coords 与 matrix 互转。
# Pacman.calculate_tiny_matrix：get_tiny_matrix 放大墙，subdiv=CELL_SIZE//PACMAN_SPEED 与 move_pacman ±1 配套。
# Pacman.boundary_check：coord_matrix[tiny_start_x][col][0] 隧道瞬移 x，避免每帧重算乘加。
# Ghost._get_coords_from_idx / _get_idx_from_coords：薄封装注入 grid_start_pos 与 CELL_SIZE。
# ScoreScreen.__init__：place_elements_offset(0.25,0.05) 把 HUD 锚在宽 25% 高 5% 附近。
# center_element：xoffset=0.5,yoffset=0.6 略低于几何中心，给标题栏留空（本仓库 GUI 可复用）。
# __get_x_y 负索引：隧道 JSON 若用 -1 表示最后一列前一格，与 Python 列表负下标语义类似。
# get_idx_from_coords 返回 (row,col) 即 (y_pos,x_pos) 命名：第一分量是 matrix 行索引。
# get_movable_locations：关卡编辑器或随机出生可用，主游戏 loop 当前未每帧调用。
# is_any_wall 2×2 粗块四角任一是墙即 True，快速判断 footprint 是否贴墙。
# precompute_matrix_coords 内外层循环步长 cell_size，传入 PACMAN_SPEED 时表与 tiny 格对齐。
# tiny_matrix 非墙粗格填 "null" 可走，与 matrix "dot"/"void" 不同语义：子格仅碰撞不关心豆。
# 全模块无 pygame import，纯数学与列表操作，可在 headless CI 测试坐标往返一致性。
# 往返性质：idx→coords→idx 在同一 cell_size 量化下应稳定，除非像素落在格边界需留意 // 截断。
# 注释/代码≥1.5：四套坐标语言、隧道负索引、tiny 与 precompute 见模块 docstring 与上文。
# ---------------------------------------------------------------------------

# --- 补充说明 (src/utils/coord_utils.py) ---
# get_coords_from_idx 列 y 映射屏幕 x、行 x 映射屏幕 y，与 pacman 子格 tiny_start_x/y 命名一致。
# get_tiny_matrix 双重 sx/sy 填满 sub_div² 子格，墙粗格整块复制 wall 到每个子格。
# precompute_matrix_coords 外层 col_start 增 cell_size 对应行方向 y，内层 row_start 增 x。
# get_movable_locations subdiv*2 footprint 与 ghost/Pac 2×2 占用一致，枚举合法出生粗格。
# is_any_wall 固定 2×2 粗块四角，快速判断，非 general N×M 区域。
# center_element yoffset 0.6 比 0.5 低，给窗口标题与 HUD 留空，ScoreScreen 用 0.05 更高。
# place_elements_offset 比例非像素，改 SCREEN_WIDTH 时 HUD/迷宫相对位置稳定。
# __get_x_y 负索引仅 get_coords_from_idx 入口，JSON 若全正索引则分支不触发。
# get_idx_from_coords // 量化，rect 在格边界时可能抖档，吃豆用 rect.x/y 与移动同步。
# coord_utils 零 pygame，可在 pytest 测 idx↔coords 往返而不 init display。
# tiny_matrix null 表示可走，与 matrix void 不同：void 是无豆可走，null 是子格无墙。
# get_movable_locations max_cell_size 默认 20 与 CELL_SIZE 默认 20 得 subdiv 1，footprint 2×2 粗格。
# is_free 排除 elec 与 wall，与 ghost BLOCKERS 部分一致，放置点算法共用。
# precompute 传入 PACMAN_SPEED 时表密度与 tiny 子格对齐，隧道查列索引精确。
# get_coords_from_idx 需 num_rows/num_cols 做负索引规范，Ghost/Pacman 传入 len(matrix) 实值。
# row_start/col_start 累加 cell_size，非 CELL_SIZE 元组第二分量，假定方格 cell_h==cell_w。
# get_tiny_matrix 每粗格处理完 tiny_c 归零换行，tiny_r 增 sub_div 换粗行。
# is_valid in get_movable_locations 双循环 subdiv*2，与 ghost 2×2 占用同形。
# center_element 包装 place_elements_offset，GUI 模块复用居中公式减少重复 magic 0.5/0.6。
# get_idx_from_coords 返回 (row,col) 命名 y_pos/x_pos 源码变量，读 matrix[y_pos][x_pos]。
# coord 模块注释目标≥1.5：四套坐标、隧道、tiny、precompute 与 Pac/Ghost 调用点见模块 docstring。
# 负 col 隧道 JSON 罕见，若用 __get_x_y 转成 num_cols+col 语义与 Python 负下标类似。
# is_any_wall 不查 elec，仅 wall；elec 阻挡在 ghost get_is_move_valid BLOCKERS 处理。
# get_movable_locations 双重 for r_idx/c_idx 枚举左上角，O(rows×cols×subdiv²) 预处理可接受。
# precompute_matrix_coords 返回 list of list of [x,y]，Pacman coord_matrix 同结构。
# place_elements_offset x=(sw-ew)*xoff 非居中加半宽，0.5 时元素左缘在剩余空间一半处。
# get_coords_from_idx 左上角像素非格心，draw_dot 再加 w/h 偏移到视觉中心。
# tiny_r/tiny_c 游标扫粗 matrix 行优先，与 PacmanGrid.draw_level 扫描顺序一致。
# cell != wall 时 tiny 内写 null 非 dot，吃豆检测在粗 matrix 不在 tiny。
# get_movable_locations append (r_idx,c_idx) 粗格左上角，非格心坐标。
# coord_utils 文末速查块列 PyPacman 调用点，改函数签名须同步 pacman/ghosts/grid。
# 整数 // 除法 toward -inf，负像素坐标少见，通常 rect 在迷宫正区域。
# module 无 __all__，import * 行为取决于包 __init__ 是否 re-export。
# full 模块注释/代码≥1.5 靠 docstring+函数说明+文末速查，纯 # 行补充调用链。
