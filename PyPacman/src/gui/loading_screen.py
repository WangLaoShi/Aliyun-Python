"""
加载画面：在资源尚未就绪时显示 GIF（当前项目里 ScreenManager 可扩展调用）。

``pygame.image.load`` 读入磁盘文件为 Surface；``transform.scale`` 改变像素尺寸
而不改路径。``blit`` 像「把一张图贴到画布指定左上角坐标」。
"""

from src.configs import loading_screen_gif
from pygame import image, transform


class LoadingScreen:
    def __init__(self, screen):
        # screen 是 runner 里 ``set_mode`` 得到的整窗 Surface，绘制都画在它上面。
        self.screen = screen
        # load 返回 Surface；路径错误会抛 pygame.error。
        self.loading_image = image.load(loading_screen_gif)
        # scale 生成新 Surface，原图仍在内存直到被覆盖/回收。
        self.loading_image = transform.scale(self.loading_image, (192, 192))

    def draw_loading(self):
        # blit(源, 目标左上角)；未 flip 前玩家看不到，flip 在 runner.main。
        self.screen.blit(self.loading_image, (500, 500))

# LoadingScreen 无 game_state 依赖，仅持有 screen 与缩放后的 GIF Surface。
# 坐标 (500,500) 硬编码，未用 place_elements_offset 居中。
# GIF 在 pygame 中常只显示第一帧，非动画 unless 手动换帧。
# loading_screen_gif 路径在 configs 模块，改 GIF 只改 configs 一处。
# __init__ 在 ScreenManager 构造时执行 load+scale，非懒加载。
# draw_loading 可多次调用，同一帧重复 blit 无害。
