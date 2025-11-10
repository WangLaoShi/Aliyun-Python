import math  # 导入数学模块

DIRECTION_MAPPER = {  # 定义方向映射字典
    "up": [(-1, 0), (-1, 1)],  # 向上移动的坐标变化
    "left": [(0, -1), (1, -1)],  # 向左移动的坐标变化
    "down": [(2, 0), (2, 1)],  # 向下移动的坐标变化
    "right": [(0, 2), (1, 2)]  # 向右移动的坐标变化
}
BLOCKERS = ['wall', 'elec']  # 定义阻挡物列表

def get_is_move_valid(curr_pos, direction, matrix):  # 定义检查移动是否有效的方法
    next_indices = DIRECTION_MAPPER[direction]  # 获取方向对应的坐标变化
    for r, c in next_indices:  # 遍历坐标变化
        next_c = curr_pos[1] + c  # 计算下一个位置的列坐标
        if next_c < 0 or next_c >= len(matrix[0]):  # 如果下一个位置超出边界
            continue  # 跳过
        if matrix[curr_pos[0] + r][curr_pos[1] + c] in BLOCKERS:  # 如果下一个位置是阻挡物
            return False  # 返回 False
    return True  # 返回 True

def eucliad_distance(point1, point2):  # 定义计算欧几里得距离的方法
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)  # 返回两点之间的距离

def get_direction(ghost_matrix_pos: tuple[int, int],
                  target_matrix_pos: tuple[int, int],
                  matrix: list[list[str]],
                  prev: tuple[int, int]):  # 定义获取方向的方法
    g1, g2 = ghost_matrix_pos  # 解包幽灵的矩阵位置
    t1, t2 = target_matrix_pos  # 解包目标的矩阵位置
    num_rows, _ = len(matrix), len(matrix[0])  # 获取矩阵的行数和列数
    next_direction_mapper = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}  # 定义下一个方向映射
    directions = ['up', 'left', 'down', 'right']  # 定义可能的方向列表
    curr_min = float('inf')  # 初始化当前最小距离为无穷大
    target_dir = None  # 初始化目标方向为 None
    for direction in directions:  # 遍历每个方向
        is_movable = get_is_move_valid((g1, g2), direction, matrix)  # 检查该方向是否可移动
        if not is_movable:  # 如果不可移动
            continue  # 跳过
        direction_additives = next_direction_mapper[direction]  # 获取方向对应的坐标变化
        next_x, next_y = g1 + direction_additives[0], g2 + direction_additives[1]  # 计算下一个位置
        if next_x >= num_rows or next_x < 0:  # 如果下一个位置超出边界
            continue  # 跳过
        if next_direction_mapper[direction] == prev:  # 如果方向与前一个方向相同
            continue  # 跳过
        distance = eucliad_distance((next_x, next_y), (t1, t2))  # 计算到目标的距离
        if distance < curr_min:  # 如果距离小于当前最小距离
            curr_min = distance  # 更新当前最小距离
            target_dir = direction  # 更新目标方向
    if target_dir is None:  # 如果没有找到目标方向
        print('error', prev, ghost_matrix_pos, matrix[ghost_matrix_pos[0]][ghost_matrix_pos[1]])  # 打印错误信息
        raise ValueError("Oh my god, I don't know what to do, im crashing the game")  # 抛出异常
    return next_direction_mapper[target_dir]  # 返回目标方向的坐标变化

def get_is_intersection(ghost_matrix_pos: tuple[int, int], 
                        matrix: list[list[str]],
                        prev=None):  # 定义检查是否是交叉路口的方法
    possible_moves = 0  # 初始化可能的移动次数为 0
    for k, _ in DIRECTION_MAPPER.items():  # 遍历每个方向
        if prev == k:  # 如果方向与前一个方向相同
            continue  # 跳过
        if get_is_move_valid(ghost_matrix_pos, k, matrix):  # 如果该方向可移动
            possible_moves += 1  # 增加可能的移动次数
    return possible_moves > 1  # 返回是否有多个可能的移动方向


