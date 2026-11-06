"""
信息类函数演示：IS* / N / TYPE / ERROR.TYPE
==========================================

**适合干什么**  
学会「在 Python 里问：这是空吗？是数吗？是 #VALUE! 吗？」——和你在 Excel
里用 IS 系列是同一类需求。

**怎么读输出**  
每行是 ``说明文字: 结果``；``True``/``False`` 即布尔。``VALUE`` 是错误**对象**（不是
字符串 ``"#VALUE!"`` 除非 ``repr`` 打出来长那样）。

**练习建议**  
把 ``show("...", ... 某函数(...))`` 里的参数换成你自己的变量，看结果变不变。
"""

from __future__ import annotations

# 先加载 common：会插入 src 到 path，并拿到 section / show
from demo.common import section, show


def run() -> None:
    """
    演示 :mod:`excel_funcs.info` 中 ISNUMBER、ISBLANK、TYPE、N 等**类型** 与**元信息** 判断.
    """
    # 从包根导出「错误常数 VALUE」，和 info 里具体函数分两个 import，避免和函数名混在一大行里
    from excel_funcs import VALUE
    from excel_funcs.info import (
        ERROR_TYPE,
        ISBLANK,
        ISERR,
        ISERROR,
        ISFORMULA,
        ISLOGICAL,
        ISNA,
        ISNUMBER,
        ISREF,
        ISTEXT,
        N,
        TYPE,
    )

    # ISBLANK/ISNUMBER/...：最基础的「类型+空」四连问
    section("ISBLANK / ISNUMBER / ISTEXT / ISLOGICAL")
    show("ISBLANK(None) — 空用 None 模拟", ISBLANK(None))
    show("ISNUMBER(3.14)", ISNUMBER(3.14))
    show("ISTEXT('x')", ISTEXT("x"))
    show("ISLOGICAL(True) — 注意 1 不是 True", ISLOGICAL(True))

    # 错误三件套：ISERROR 最宽；ISERR 排除 NA；ISNA 只管 NA
    section("ISERROR / ISERR / ISNA")
    show("ISERROR(VALUE) — 错误也算「值」", ISERROR(VALUE))
    show("ISNA(VALUE) — #VALUE! 不是 #N/A 故为 False", ISNA(VALUE))

    # 这两个在本仓库里是「教学占位」，结果固定，看注释在源码里
    section("ISFORMULA / ISREF")
    show("ISFORMULA(1) — 无工作表，恒假", ISFORMULA(1))
    show("ISREF([[1,2]]) — 嵌套 list 当「区域」粗判", ISREF([[1, 2]]))

    # N 转数字、TYPE 看 Excel 式类型码、ERROR.TYPE 把错误变整数代码
    section("N / TYPE / ERROR.TYPE")
    show("N(42)", N(42))
    show("TYPE('a') — 文本=2 见 help", TYPE("a"))
    show("ERROR.TYPE(VALUE) — 对应 #VALUE! 的编号", ERROR_TYPE(VALUE))


if __name__ == "__main__":
    run()
