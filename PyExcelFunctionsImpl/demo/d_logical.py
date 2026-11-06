"""
逻辑与条件：IF、IFS、IFERROR、AND、OR、NOT、XOR …
===============================================

**重要**（读三遍）  
Python 里 ``IF(条件, 真值, 假值)`` 会**先计算**真值、假值再选，**没有** Excel
的「短路不计算另一边」。分支里不要写「改文件、发网络」**副作用**。

**本文件**  
用 ``IFERROR``/``IFNA`` 时，从 ``excel_funcs`` 根导入 ``VALUE``/``NA`` 表示错误单例。

"""

from __future__ import annotations

from demo.common import section, show


def run() -> None:
    """
    演示 :mod:`excel_funcs.logical` 中 IF、AND、OR、IFS 等逻辑函数与**错误** 值配合用法.
    """
    from excel_funcs import NA, VALUE
    from excel_funcs.logical import (
        AND,
        FALSE,
        IF,
        IFERROR,
        IFNA,
        IFS,
        NOT,
        OR,
        SWITCH,
        TRUE,
        XOR,
    )

    section("TRUE / FALSE / IF")
    show("TRUE()", TRUE())
    show("FALSE()", FALSE())
    show("IF(1>0,'Y','N')", IF(1 > 0, "Y", "N"))

    section("IFERROR / IFNA")
    show("IFERROR(1,0)", IFERROR(1, 0))
    show("IFERROR(VALUE,99)", IFERROR(VALUE, 99))
    show("IFNA(NA,'fallback')", IFNA(NA, "fallback"))

    section("IFS / SWITCH")
    show("IFS(False,'a',True,'b')", IFS(False, "a", True, "b"))
    show("SWITCH(2,1,'a',2,'b','z')", SWITCH(2, 1, "a", 2, "b", "z"))

    section("AND / OR / NOT / XOR")
    show("AND(True,True)", AND(True, True))
    show("OR(False,True)", OR(False, True))
    show("NOT(True)", NOT(True))
    show("XOR(True,False,True)", XOR(True, False, True))


if __name__ == "__main__":
    run()
