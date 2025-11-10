def center_element(screen_width, screen_height, element_width, element_height):  # 定义居中元素的方法
    # 调用 place_elements_offset 函数以特定偏移量居中元素
    return place_elements_offset(
        screen_width, screen_height, element_width, element_height, 0.5, 0.6
    )


def place_elements_offset(
    screen_width, screen_height, element_width, element_height, xoffset, yoffset
):  # 定义放置元素偏移的方法
    x = (screen_width - element_width) * xoffset  # 计算元素的 x 坐标
    y = (screen_height - element_height) * yoffset  # 计算元素的 y 坐标
    return x, y  # 返回计算的坐标


def __get_x_y(pos, num_rows, num_cols):  # 定义获取 x 和 y 坐标的私有方法
    x = pos[0]  # 获取位置的 x 坐标
    y = pos[1]  # 获取位置的 y 坐标
    if pos[0] < 0:  # 如果 x 坐标小于 0
        x = num_rows + x  # 调整 x 坐标
    if pos[1] < 0:  # 如果 y 坐标小于 0
        y = num_cols + y  # 调整 y 坐标
    return x, y  # 返回调整后的坐标


def get_coords_from_idx(
    pacman_pos, start_x, start_y, cell_w, cell_h, num_rows, num_cols
):  # 定义从索引获取坐标的方法
    x, y = __get_x_y(pacman_pos, num_rows, num_cols)  # 获取调整后的 x 和 y 坐标
    x_coord = start_x + (y * cell_w)  # 计算 x 坐标
    y_coord = start_y + (x * cell_h)  # 计算 y 坐标
    return x_coord, y_coord  # 返回计算的坐标


def precompute_matrix_coords(start_x, start_y, cell_size, num_rows, num_cols):  # 定义预计算矩阵坐标的方法
    matrix_coords = []  # 初始化矩阵坐标列表
    col_start = start_y  # 初始化列起始位置
    for _ in range(num_rows):  # 遍历每一行
        row_start = start_x  # 初始化行起始位置
        m = []  # 初始化行坐标列表
        for _ in range(num_cols):  # 遍历每一列
            m.append([row_start, col_start])  # 添加坐标到行列表
            row_start += cell_size  # 更新行起始位置
        col_start += cell_size  # 更新列起始位置
        matrix_coords.append(m)  # 添加行坐标到矩阵列表
    return matrix_coords  # 返回矩阵坐标列表


def get_idx_from_coords(x_coord, y_coord, start_x, start_y, cell_size):  # 定义从坐标获取索引的方法
    x_pos = int((x_coord - start_x) // cell_size)  # 计算 x 索引
    y_pos = int((y_coord - start_y) // cell_size)  # 计算 y 索引
    return y_pos, x_pos  # 返回计算的索引

def get_tiny_matrix(matrix, cell_size, pacman_speed):  # 定义获取微型矩阵的方法
    sub_div = cell_size // pacman_speed  # 计算子划分
    num_rows = len(matrix) * sub_div  # 计算微型矩阵的行数
    num_cols = len(matrix[0]) * sub_div  # 计算微型矩阵的列数
    tiny_matrix = [["null"] * num_cols for _ in range(num_rows)]  # 初始化微型矩阵
    tiny_r, tiny_c = 0, 0  # 初始化微型矩阵的行和列索引
    for row in matrix:  # 遍历矩阵的每一行
        for cell in row:  # 遍历行中的每一个单元格
            if cell != "wall":  # 如果单元格不是墙
                cell = "null"  # 设置为 null
            for sx in range(sub_div):  # 遍历子划分的 x 方向
                for sy in range(sub_div):  # 遍历子划分的 y 方向
                    tiny_matrix[tiny_r + sx][tiny_c + sy] = cell  # 设置微型矩阵的值
            tiny_c += sub_div  # 更新微型矩阵的列索引
        tiny_r += sub_div  # 更新微型矩阵的行索引
        tiny_c = 0  # 重置微型矩阵的列索引
    return tiny_matrix  # 返回微型矩阵

def get_movable_locations(matrix, max_cell_size=20, 
                          cell_size=20):  # 定义获取可移动位置的方法
    movables = []  # 初始化可移动位置列表
    rows, cols = len(matrix), len(matrix[0])  # 获取矩阵的行数和列数
    subdiv = max_cell_size // cell_size  # 计算子划分

    def is_free(r, c):  # 定义检查位置是否空闲的方法
        return 0 <= r < rows and 0 <= c < cols and matrix[r][c] not in ('wall', 'elec')  # 返回位置是否空闲
    
    def is_valid(r, c):  # 定义检查位置是否有效的方法
        for x in range(subdiv*2):  # 遍历子划分的 x 方向
            for y in range(subdiv*2):  # 遍历子划分的 y 方向
                if not is_free(r+x, c+y):  # 如果位置不空闲
                    return False  # 返回 False
        return True  # 返回 True

    for r_idx in range(rows):  # 遍历每一行
        for c_idx in range(cols):  # 遍历每一列
            if (r_idx + (subdiv*2) <= rows and \
                 c_idx + (subdiv*2) <= cols) and is_valid(r_idx, c_idx):  # 如果位置有效
                movables.append((r_idx, c_idx))  # 添加到可移动位置列表

    return movables  # 返回可移动位置列表

def is_any_wall(matrix, x, y):  # 定义检查是否有墙的方法
    rows, cols = len(matrix), len(matrix[0])  # 获取矩阵的行数和列数

    def is_wall(r, c):  # 定义检查位置是否是墙的方法
        """Check if the cell is 'wall' and within bounds."""  # 检查单元格是否是墙且在边界内
        return 0 <= r < rows and 0 <= c < cols and matrix[r][c] == 'wall'  # 返回位置是否是墙

    # Check all four positions  # 检查四个位置
    return (
        is_wall(x, y) or  # 检查当前位置
        is_wall(x, y + 1) or  # 检查右边位置
        is_wall(x + 1, y + 1) or  # 检查右下位置
        is_wall(x + 1, y)  # 检查下边位置
    )