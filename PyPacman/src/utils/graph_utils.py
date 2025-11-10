import heapq  # 导入堆队列模块，用于优先队列操作

def a_star(matrix, start, target, subdivs=4):  # 定义 A* 算法函数
    rows, cols = len(matrix), len(matrix[0])  # 获取矩阵的行数和列数

    def is_valid(x, y):  # 定义检查位置是否有效的方法
        """Check if all cells in the subdivs x subdivs block are valid."""  # 检查 subdivs x subdivs 区块中的所有单元格是否有效
        if not (0 <= x < rows and 0 <= y < cols):  # 如果位置超出矩阵边界
            return False  # 返回 False
        for dx in range(subdivs*2):  # 遍历 x 方向的子划分
            for dy in range(subdivs*2):  # 遍历 y 方向的子划分
                if x + dx >= rows or y + dy >= cols or matrix[x + dx][y + dy] == 'wall':  # 如果位置超出边界或是墙
                    return False  # 返回 False
        return True  # 返回 True

    def heuristic(a, b):  # 定义启发式函数
        """Calculate Manhattan distance."""  # 计算曼哈顿距离
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # 返回两点之间的曼哈顿距离
    
    def path_builder(current, came_from):  # 定义路径构建函数
        path = []  # 初始化路径列表
        while current in came_from:  # 当当前节点在路径字典中
            path.append(current)  # 将当前节点添加到路径
            current = came_from[current]  # 更新当前节点为其前驱节点
        path.append(start)  # 将起始节点添加到路径
        return path[::-1]  # 返回反转后的路径

    # Directions: Up, Down, Left, Right  # 定义移动方向
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1)  # 上、下、左、右
    ]

    open_set = []  # 初始化开放集
    heapq.heappush(open_set, (0, start))  # 将起始节点添加到开放集，优先级为 0
    came_from = {}  # 初始化路径字典

    g_score = {start: 0}  # 初始化起始节点的 g 值
    f_score = {start: heuristic(start, target)}  # 初始化起始节点的 f 值
    closest_node = start  # 初始化最近节点为起始节点
    closest_distance = heuristic(start, target)  # 初始化最近距离为起始节点到目标的距离

    while open_set:  # 当开放集不为空
        _, current = heapq.heappop(open_set)  # 从开放集中取出优先级最低的节点

        if current == target:  # 如果当前节点是目标节点
            return path_builder(current, came_from)  # 返回构建的路径

        for dx, dy in directions:  # 遍历每个方向
            neighbor = (current[0] + dx, current[1] + dy)  # 计算邻居节点

            if is_valid(neighbor[0], neighbor[1]):  # 如果邻居节点有效
                tentative_g_score = g_score[current] + 1  # 计算临时 g 值
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:  # 如果邻居节点未访问或有更优路径
                    came_from[neighbor] = current  # 更新邻居节点的前驱节点
                    g_score[neighbor] = tentative_g_score  # 更新邻居节点的 g 值
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, target)  # 更新邻居节点的 f 值

                    if neighbor not in [pos for _, pos in open_set]:  # 如果邻居节点不在开放集中
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))  # 将邻居节点添加到开放集
                
                h_dist = heuristic(neighbor, target)  # 计算邻居节点到目标的启发式距离
                if h_dist < closest_distance:  # 如果启发式距离小于最近距离
                    closest_node = neighbor  # 更新最近节点
                    closest_distance = h_dist  # 更新最近距离

    return path_builder(closest_node, came_from)  # 返回最近节点的路径