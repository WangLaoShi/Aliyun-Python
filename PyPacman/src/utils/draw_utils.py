"""
Pygame 绘图小工具模块（draw_utils）。

初学者可以把它理解成「在屏幕上画几何图形」的薄封装：
- 游戏主循环里已经有了 ``screen``（Surface 对象），
- 本模块的函数负责调用 ``pygame.draw``，避免在业务代码里重复写参数格式。

设计要点：
- **单一职责**：只关心「画什么、画在哪、什么颜色」，不关心吃豆人逻辑。
- **调试辅助**：``draw_debug_rects`` 用来在开发阶段可视化网格，正式版可不用。
"""

from pygame import draw  # pygame 内置矢量绘图 API（矩形、圆、线等）


def draw_rect(x, y, w, h, screen, color, fill=0):
    """
    在屏幕上画矩形。

    参数说明（像素坐标系：左上角为原点，x 向右增，y 向下增）：
    - (x, y)：矩形左上角
    - w, h：宽、高
    - screen：pygame Surface，即要绘制到的画布
    - color：RGB 元组，例如 (255, 255, 0)
    - fill：0 表示只画边框；非 0 表示用 color 填充内部
    """
    # pygame.draw.rect(表面, 颜色, (x, y, 宽, 高), 线宽或填充标志)
    draw.rect(screen, color, (x, y, w, h), fill)


def draw_circle(x, y, radius, screen, color):
    """
    在屏幕上画圆（常用于豆点、能量豆等）。

    - (x, y)：圆心坐标（注意与矩形左上角不同）
    - radius：半径（像素）
    """
    draw.circle(screen, color, (x, y), radius)


def draw_debug_rects(start_x, start_y, num_rows, num_cols, cell_size, color, screen):
    """
    按行列铺一层「网格线」矩形，便于对齐地图与碰撞体。

    双重循环结构：
    - 外层：每一行，行结束后 curr_y 下移一格，curr_x 回到 start_x
    - 内层：每一列，curr_x 右移 cell_size

    最后一个参数 ``1`` 表示线宽为 1 像素（空心网格）。
    """
    curr_x, curr_y = start_x, start_y
    for _ in range(num_rows):
        for _ in range(num_cols):
            draw.rect(screen, color, (curr_x, curr_y, cell_size, cell_size), 1)
            curr_x += cell_size
        curr_y += cell_size
        curr_x = start_x
