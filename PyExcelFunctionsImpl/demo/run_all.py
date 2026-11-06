"""
一键跑完所有 ``demo/d_*.py`` 的 ``run()``
====================================

**用途**  
第一次克隆仓库、装完环境后，执行::

    python -m demo.run_all

终端会刷一大段输出——**能跑通**基本说明：``excel_funcs`` 能 import、各 demo
没有明显语法/导入错误。

**实现说明**  
下面每个 ``d_xxx.run()`` 是**独立模块**，顺序无所谓；若中间某类报错，后面
不会执行，请根据**最先** Traceback 修。

**和 ``python -m excel_funcs`` 区别**  
后者只跑包内置的几行 sanity check；本脚本覆盖**数学/文本/逻辑/查找/数组/
日期/财务/信息** 八大块。
"""

from __future__ import annotations


def main() -> None:
    """
    总演示入口：依次调用各 ``demo.d_*.run()``，一次性跑通数学/文本/逻辑/查找/数组/
    日期/财务/信息八类示例。若中间失败，可单独 ``python -m demo.d_math`` 等缩小范围.
    """
    # 分开 import 以便某模块坏了时，栈信息里能直接看到是哪一个 d_ 文件
    from demo import d_array
    from demo import d_datetime
    from demo import d_financial
    from demo import d_info
    from demo import d_logical
    from demo import d_lookup
    from demo import d_math
    from demo import d_text

    print("excel_funcs — 全部分类演示（可滚动回看；嫌长可只跑: python -m demo.d_math）")
    d_math.run()
    d_text.run()
    d_logical.run()
    d_lookup.run()
    d_array.run()
    d_datetime.run()
    d_financial.run()
    d_info.run()
    print("\n全部演示结束。")


if __name__ == "__main__":
    main()
