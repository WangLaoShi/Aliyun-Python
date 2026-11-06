"""
Py-Pacman 程序入口（Entry Point）。

Python 会把每个 .py 文件当作「模块」。当用户双击或在终端执行
``python main.py`` 时，解释器会先从头到尾执行本文件顶层的语句。
真正启动游戏的是 ``GameRun`` 类（定义在 ``src.runner`` 里），
本文件只负责「创建对象并调用 main()」，这是常见的小型项目结构：
入口越薄，逻辑越集中在 src/ 包内，便于阅读和测试。
"""

# 从 src 包中的 runner 模块导入 GameRun 类。
# 「from 包.模块 import 名字」表示：只把 GameRun 这个名字放进当前命名空间，
# 使用时写 GameRun() 即可，不必写 src.runner.GameRun()。
from src.runner import GameRun

# ---------------------------------------------------------------------------
# 仅在本文件被「直接运行」时执行的块（不是被 import 时执行）。
# ---------------------------------------------------------------------------
# __name__ 是 Python 内置变量：若文件作为脚本运行，值为 '__main__'；
# 若被其他文件 import，则为模块名（如 'main'）。因此把启动代码放在
# if __name__ == '__main__' 里，可以避免「被 import 时误启动游戏」。
if __name__=='__main__':
    # 实例化：GameRun.__init__ 会初始化 pygame、窗口、状态、事件与 GUI。
    gr = GameRun()
    # 进入主循环（事件 → 绘制 → 更新），直到玩家退出。
    gr.main()
