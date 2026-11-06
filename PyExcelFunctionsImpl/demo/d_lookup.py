"""
查找与引用：VLOOKUP、INDEX、MATCH、XLOOKUP、INDIRECT、OFFSET
=======================================================

**区域怎么写**  
``[[a,b],[c,d]]`` 表示两行两列，**外列表=行、内列表=列**，和一般「行优先」
二维数组一致。``VLOOKUP(查找值, 整个表, 第几列, 是否模糊)`` 的列号从 1 计。

**INDIRECT 扩展**  
标准 Excel 下本库**没有工作表**；要演示「从地址取 Python 里存的值」时，用
关键字参数 ``workbook={'A1': 值, ...}``（**仅本 Python 包扩展**，已写在源码 docstring）。

**OFFSET**  
对**二维 list** 做子矩形切片；行、列从 0 开始偏移是**相对**你传入的矩阵左上角。
"""

from __future__ import annotations

from demo.common import section, show


def run() -> None:
    """
    演示 :mod:`excel_funcs.lookup` 中 VLOOKUP、INDEX、MATCH、XLOOKUP、OFFSET 等**表** 上查找.
    """
    from excel_funcs.lookup import (
        ADDRESS,
        CHOOSE,
        COLUMN,
        COLUMNS,
        HLOOKUP,
        INDEX,
        INDIRECT,
        LOOKUP,
        MATCH,
        OFFSET,
        ROW,
        ROWS,
        TRANSPOSE,
        VLOOKUP,
        XLOOKUP,
        XMATCH,
    )

    section("VLOOKUP / HLOOKUP")
    tbl = [[1, "一"], [2, "二"], [3, "三"]]
    show("VLOOKUP(2,tbl,2)", VLOOKUP(2, tbl, 2, False))
    ht = [[1, 2, 3], ["a", "b", "c"]]
    show("HLOOKUP(2,ht,2)", HLOOKUP(2, ht, 2, False))

    section("INDEX / MATCH / CHOOSE")
    show("INDEX([[10,20],[30,40]],2,1)", INDEX([[10, 20], [30, 40]], 2, 1))
    show("MATCH('b',['a','b','c'],0)", MATCH("b", ["a", "b", "c"], 0))
    show("CHOOSE(2,'a','b','c')", CHOOSE(2, "a", "b", "c"))

    section("ADDRESS / ROW / COLUMN / ROWS / COLUMNS")
    show("ADDRESS(3,2)", ADDRESS(3, 2))
    show("ROW()", ROW())
    show("COLUMN()", COLUMN())
    show("ROWS(tbl)", ROWS(tbl))
    show("COLUMNS(tbl)", COLUMNS(tbl))

    section("TRANSPOSE")
    show("TRANSPOSE([[1,2],[3,4]])", TRANSPOSE([[1, 2], [3, 4]]))

    section("XLOOKUP / XMATCH / LOOKUP")
    show("XLOOKUP(2,[1,2],[10,20])", XLOOKUP(2, [1, 2], [10, 20]))
    show("XMATCH('b',['a','b'])", XMATCH("b", ["a", "b"]))
    show("LOOKUP(2,[1,2,3],[10,20,30])", LOOKUP(2, [1, 2, 3], [10, 20, 30]))

    section("INDIRECT（无 workbook → #REF!；有 workbook 扩展）")
    show("INDIRECT('A1')", INDIRECT("A1"))
    wb = {"A1": 999, "B2": "OK"}
    show("INDIRECT('A1',workbook=wb)", INDIRECT("A1", True, workbook=wb))

    section("OFFSET 二维切片")
    m = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    show("OFFSET(m,1,1)", OFFSET(m, 1, 1))
    show("OFFSET(m,0,0,2,2)", OFFSET(m, 0, 0, 2, 2))


if __name__ == "__main__":
    run()
