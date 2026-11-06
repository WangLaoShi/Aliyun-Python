"""
分数 HUD：在迷宫上方/侧边绘制当前分与历史最高分。

流程典型为：字符串 → ``Font.render`` 得到带 alpha 的 Surface → ``blit`` 到主屏。
``place_elements_offset`` 按屏幕宽高比例算锚点，使不同分辨率下位置相对稳定。
"""

# Surface 类型注解：表示「可绘制像素缓冲区」。
from pygame.surface import Surface
# font 子模块：TrueType/默认位图字体渲染。
from pygame import font

# GameState 提供 points / highscore 数值。
from src.game.state_management import GameState
# 导入 Colors、SCREEN_WIDTH 等常量。
from src.configs import *
# 按屏幕比例计算 HUD 左上角像素坐标。
from src.utils.coord_utils import place_elements_offset

# ---------------------------------------------------------------------------
# Pygame 文字绘制三步（本类 draw_scores 即遵循此流程）
# ---------------------------------------------------------------------------
# 1) Font.render(text, antialias, color) → Surface（位图文字）
# 2) blit(surface, (x,y)) 贴到主 screen
# 3) 主循环末尾 display.flip() 才真正显示（在 runner 里）
# place_elements_offset 的 0.25/0.05 是相对于屏幕宽高的比例，不是像素绝对值。
# ---------------------------------------------------------------------------


# 分数界面：无 pygame.sprite.Sprite，每帧直接 blit 文字。
class ScoreScreen:
    # 类型注解帮助 IDE；运行时不强制检查。
    def __init__(self,
                 screen: Surface,
                 game_state: GameState):
        # 保存主屏引用，draw 时 blit 目标。
        self._screen = screen
        # 只读分数时通过 game_state.points 属性访问。
        self._game_state = game_state
        # 200×200 为占位「逻辑块」尺寸，用于 offset 公式，非实际文字大小。
        self.start_x, self.start_y = place_elements_offset(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            200,
            200,
            0.25,
            0.05
        )
        # 若主程序已 pygame.init()，font.init 通常可省略但无害。
        font.init()
        # None 表示 pygame 默认字体；36 是字号（像素高度量级）。
        self.font = font.Font(None, 36)

    # 每帧由 ScreenManager.draw_screens 调用一次。
    def draw_scores(self):
        # str() 把整数分转成可渲染字符串。
        score_text = "SCORE: " + str(self._game_state.points)
        # True 表示抗锯齿；颜色来自 configs.Colors。
        score_surface = self.font.render(score_text, True, Colors.WHITE)
        # 第一段文字贴在 (start_x, start_y)。
        self._screen.blit(score_surface, (self.start_x, self.start_y))

        highscore_text = "HIGHSCORE: " + str(self._game_state.highscore)
        hs_surface = self.font.render(highscore_text, True, Colors.WHITE)
        # 相对 SCORE 向右偏移 300 像素，避免两段文字重叠。
        self._screen.blit(hs_surface, (self.start_x + 300, self.start_y))

# ScoreScreen 非 Sprite：不参与 Group.update，只负责静态文字 blit。
# place_elements_offset 第三四参数 200,200 为布局算法占位尺寸，非文字 bbox。
# Font(None, 36) 使用 pygame 内置默认字体，中文可能显示为 tofu 取决于系统。
# render 第三参数 Colors.WHITE 来自 configs 星号导入。
# points/highscore 均读 GameState property，不写 HUD 内分数。
# blit 不自动刷新屏幕，依赖 runner flip。
# 类型注解 GameState/Surface 仅静态检查，CPython 运行时忽略。
# highscore 文本 x 偏移 +300 像素，与 SCORE 同一 baseline y。
# draw_scores 无参数，每帧全量重绘文字，未做脏矩形优化。
# points 初值 -DOT_POINT 在 GameState，第一次吃豆后 HUD 才显示 0 而非 -10。
# highscore 仅在 runner 退出前写 stats.json，游戏中只读显示，破纪录时内存即时更新。

# --- 补充说明 (src/gui/score_screen.py) ---
# Font(None,36) 默认位图字体，中文系统可能缺字，SCORE/HIGHSCORE 英文 ASCII 无问题。
