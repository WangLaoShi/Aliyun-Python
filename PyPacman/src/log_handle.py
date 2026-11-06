"""
日志工具：为各模块提供统一格式的 ``logging.Logger``。

为什么需要它？
- ``print`` 无法区分 DEBUG/INFO/ERROR，也难以关掉或重定向到文件。
- 标准库 ``logging`` 用「记录器 Logger + 处理器 Handler + 格式 Formatter」
  分层输出；同一模块多次 ``get_logger(__name__)`` 应得到同一配置，避免重复刷屏。

``__name__`` 在 runner.py 里是 ``src.runner``，在 pacman_grid 里是 ``src.gui.pacman_grid``，
便于在控制台里看出日志来自哪个文件。
"""

import logging


def get_logger(name: str, level: int = logging.DEBUG):
    """
    返回已配置好控制台输出的 Logger 实例。

    Parameters:
        name: 通常传调用方的 ``__name__``，作为 Logger 在 logging 树中的名字。
        level: 最低输出级别；DEBUG 最啰嗦，INFO/WARNING/ERROR 依次更少。

    Returns:
        logging.Logger: 可直接 ``logger.info("...")`` 使用。
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 同一 name 的 logger 是单例；若每次 import 都 addHandler，会重复打印 N 遍。
    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger

# --- log_handle 补充 ---
# get_logger(__name__) 返回模块级 logger，runner/sprites/gui 共用配置，级别在 log_handle 模块设置。
# DEBUG 默认时 Ghost.prepare_movement 卡死前 print 与 logger 可并存，生产可改 INFO 减噪。
