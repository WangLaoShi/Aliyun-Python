import logging  # 导入日志模块

def get_logger(name: str, level: int = logging.DEBUG):  # 定义获取日志记录器的方法
    """
    Returns a preconfigured logger instance.  # 返回一个预配置的日志记录器实例
    
    Parameters:
        name (str): Name of the logger, typically __name__ of the module.  # 日志记录器的名称，通常是模块的 __name__
        level (int): Logging level. Defaults to DEBUG.  # 日志级别，默认为 DEBUG

    Returns:
        logging.Logger: Configured logger instance.  # 配置好的日志记录器实例
    """
    logger = logging.getLogger(name)  # 创建一个日志记录器
    logger.setLevel(level)  # 设置日志记录器的级别

    if not logger.hasHandlers():  # 检查日志记录器是否已经有处理器，避免重复日志
        console_handler = logging.StreamHandler()  # 创建一个控制台处理器
        console_handler.setLevel(level)  # 设置控制台处理器的级别

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # 定义日志格式
        console_handler.setFormatter(formatter)  # 设置控制台处理器的格式

        logger.addHandler(console_handler)  # 将控制台处理器添加到日志记录器

    return logger  # 返回配置好的日志记录器
