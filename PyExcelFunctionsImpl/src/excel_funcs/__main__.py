"""
支持命令行: ``python -m excel_funcs``

在终端里快速看一眼「能算 SUM / IF、能调 ExcelFunctions」是否安装成功。
更完整的按分类输出请用: ``python -m demo.run_all``（需在项目根，见 demo/README.md）。
"""

from __future__ import annotations

from excel_funcs import ExcelFunctions, IF, SUM


def main() -> None:
    """
    ``python -m excel_funcs`` 时的**入口**：打印几条 Layer1 与 :class:`~excel_funcs.engine.ExcelFunctions`
    的**自检** 输出，**不** 替代 ``pytest``。用于装包后**快速** 确认环境。

    **教学**  
    对照「**直接** ``SUM``/``IF``」与 ``xf.math`` / ``xf.text`` 的**两种** 调用习惯。
    更多分类见 ``python -m demo.run_all``（若已含 demo 包）.
    """
    # 用两种方式各演示一条，帮新手建立「大写函数」和「xf.math」两种用法的联系。
    xf = ExcelFunctions()
    print("excel_funcs 极简自检（可忽略输出内容，能跑通即说明包可用）")
    print("  SUM(1,2,3) =>", SUM(1, 2, 3))
    print("  IF(True,'Y','N') =>", IF(True, "Y", "N"))
    print("  xf.math.average(10,20,30) =>", xf.math.average(10, 20, 30))
    print("  xf.text.proper('hello world') =>", xf.text.proper("hello world"))


if __name__ == "__main__":
    main()
