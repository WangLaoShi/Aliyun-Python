from pygame import draw  # 从 pygame 导入绘图模块


def draw_rect(x, y, w, h, screen, color, fill=0):  # 定义绘制矩形的方法
    draw.rect(screen, color, (x, y, w, h), fill)  # 使用 pygame 的 draw.rect 方法在屏幕上绘制矩形


def draw_circle(x, y, radius, screen, color):  # 定义绘制圆的方法
    draw.circle(screen, color, (x, y), radius)  # 使用 pygame 的 draw.circle 方法在屏幕上绘制圆


def draw_debug_rects(start_x, start_y, num_rows, num_cols, cell_size, color, screen):  # 定义绘制调试矩形的方法
    curr_x, curr_y = start_x, start_y  # 初始化当前坐标为起始坐标
    for _ in range(num_rows):  # 遍历每一行
        for _ in range(num_cols):  # 遍历每一列
            draw.rect(screen, color, (curr_x, curr_y, cell_size, cell_size), 1)  # 绘制一个边框为 1 的矩形
            curr_x += cell_size  # 更新 x 坐标
        curr_y += cell_size  # 更新 y 坐标
        curr_x = start_x  # 重置 x 坐标为起始 x 坐标
