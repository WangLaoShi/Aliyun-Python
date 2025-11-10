from src.configs import loading_screen_gif  # 从配置文件中导入加载屏幕 GIF 的路径
from pygame import image, transform  # 从 pygame 导入图像和变换模块

class LoadingScreen:  # 定义加载屏幕类
    def __init__(self, screen):  # 初始化方法，接收屏幕对象
        self.screen = screen  # 保存屏幕对象
        self.loading_image = image.load(loading_screen_gif)  # 加载 GIF 图像
        self.loading_image = transform.scale(self.loading_image, (192, 192))  # 将图像缩放到 192x192 像素

    def draw_loading(self):  # 定义绘制加载图像的方法
        self.screen.blit(self.loading_image, (500, 500))  # 在屏幕的 (500, 500) 位置绘制加载图像