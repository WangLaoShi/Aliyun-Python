"""
数组/类动态数组：UNIQUE、SORT、FILTER、SEQUENCE、RANDARRAY
===================================================

**和 Excel 365 区别**  
这里每个函数**返回**一个普通 ``list``，没有「整列溢出」到格子的效果；**数值**
上可对齐理解即可。

**UNIQUE 二维**  
多行时「相同行」指整行元组相同；可打开 ``array_funcs.UNIQUE`` 看 ``by_col`` 含义。

"""

from __future__ import annotations

from demo.common import section, show


def run() -> None:
    """
    演示 :mod:`excel_funcs.array_funcs` 中 UNIQUE、SORT、FILTER、SEQUENCE、RANDARRAY 等**列表** 级函数.
    """
    from excel_funcs.array_funcs import FILTER, RANDARRAY, SEQUENCE, SORT, SORTBY, UNIQUE

    section("UNIQUE（一维 / 二维按行）")
    show("UNIQUE([1,2,1,3])", UNIQUE([1, 2, 1, 3]))
    show("UNIQUE([[1,2],[1,2],[3,4]])", UNIQUE([[1, 2], [1, 2], [3, 4]]))
    show("UNIQUE(...,exactly_once=True)", UNIQUE([1, 2, 2, 3], exactly_once=True))

    section("SORT / SORTBY")
    show("SORT([3,1,4])", SORT([3, 1, 4]))
    show("SORT(...,sort_order=-1)", SORT([3, 1, 4], sort_order=-1))
    show("SORTBY(['b','a','c'],[2,1,3])", SORTBY(["b", "a", "c"], [2, 1, 3]))

    section("FILTER / SEQUENCE / RANDARRAY")
    show("FILTER([1,2,3],[True,False,True])", FILTER([1, 2, 3], [True, False, True]))
    show("SEQUENCE(2,3)", SEQUENCE(2, 3))
    show("RANDARRAY(2,2,0,1,integer=True)", RANDARRAY(2, 2, 0, 1, integer=True))


if __name__ == "__main__":
    run()
