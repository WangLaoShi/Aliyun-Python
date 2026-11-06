"""
Layer 1 — 数组/类动态数组：UNIQUE、SORT、FILTER、SEQUENCE、RANDARRAY
====================================================================

**和 Excel 365 的「动态数组」关系**  
Excel 里一行公式可以「溢出」多格。在 Python 里我们**只返回** ``list`` 或
``list[list]``，没有工作表，也就没有溢出区域——**语义对齐到「值」**即可。

**性能**  
实现以纯 Python 为主，大列表时请自测；需要时可在外部换 ``numpy`` 自己包装。

**UNIQUE 的 `by_col`**  
二维时 ``by_col=True`` 会按**列**抽成元组再比是否重复，适合「几列合起来算一条」
的去重，与 Excel 的「按列 / 按行」选区有关，但细节仍读函数内注释。
"""

from __future__ import annotations

import random
from collections import Counter
from typing import Any, Sequence

from excel_funcs.errors import VALUE


def UNIQUE(data: Sequence[Any], by_col: bool = False, exactly_once: bool = False) -> list[Any]:
    """
    Excel ``UNIQUE`` 的列表版。

    参数说明：

    - ``data``：一维时元素去重；若**整表**是「行列表的列表」且**每一行**都是 list/tuple，
      则进入二维模式，默认按**行**去重（整行打 tuple 后比较）。
    - ``by_col``：仅二维有意义；为 True 时把每一**列**抽成元组，对列去重（少见，用于演示）。
    - ``exactly_once``：为 True 时只保留在序列里**恰好出现 1 次**的项，顺序按**首次出现**遍历。
    """

    flat = list(data)  # 先 materialize，避免迭代器只扫一遍的坑

    # 是否「每行都是子列表」→ 走二维行/列去重；否则当一维
    if flat and all(isinstance(x, (list, tuple)) for x in flat):
        if by_col:
            # 列去重：每列 = 各行在该列的取值拼成 tuple
            ncols = min(len(row) for row in flat) if flat else 0
            cols: list[tuple[Any, ...]] = []
            for c in range(ncols):
                cols.append(tuple(row[c] if c < len(row) else None for row in flat))
            seq: list[Any] = cols
        else:
            # 行去重：每行变 tuple 以便可 hash、可比较
            seq = [tuple(row) for row in flat]  # type: ignore[list-item]
    else:
        _ = by_col  # 一维时忽略 by_col
        seq = flat

    if exactly_once:
        cnt = Counter(seq)  # 数每个「键」出现次数
        return [x for x in seq if cnt[x] == 1]

    # 标准 UNIQUE：先见先留
    seen: set[Any] = set()
    out: list[Any] = []
    for x in seq:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def SORT(
    array: Sequence[Any], sort_index: int = 1, sort_order: int = 1, by_col: bool = False
) -> list[Any]:
    """
    对应 **SORT** 的一维教学版：``sort_order=1`` 升序、``-1`` 降序。``sort_index``/``by_col`` 为**保留位** ，
    多列/多维的完整 **SORT** 本处**未** 实现，避免与**类型混杂** 一起讲糊.

    若元素**不可** 比较，``TypeError`` 被捕获后**返回** ``list(array)`` 的**副本** ，**不** 等于排好序.

    **建** 议** 课** 上** 先** 做** 类型** 清** 洗** 再** 调** 用** 。
    """
    _ = sort_index, by_col
    arr = list(array)
    rev = sort_order == -1
    try:
        return sorted(arr, reverse=rev)
    except TypeError:
        return arr


def SORTBY(array: Sequence[Any], *by_arrays: Any) -> list[Any]:
    """
    对应 **SORTBY** 单键**简化**：用 ``by_arrays[0]`` 与 ``array`` **同** 下标** 组成
    键值对，**按** 键** 排序** 后** 重** 排 ``array`` 的**行** 。

    **多** 个** 键** 、**混** 合** 升** 降** 本** 处** 未** 实现. ``len(keys) != len(array)`` → #VALUE!。不可比较时
    与 :func:`SORT` 一样**退回** 原**列表** 副本.
    """
    if not by_arrays:
        return list(array)
    keys = list(by_arrays[0])
    arr = list(array)
    if len(keys) != len(arr):
        return VALUE  # type: ignore[return-value]
    try:
        return [x for _, x in sorted(zip(keys, arr), key=lambda t: t[0])]
    except TypeError:
        return arr


def FILTER(array: Sequence[Any], include: Sequence[bool], if_empty: Any | None = None) -> list[Any] | Any:
    """
    对应 **FILTER**：仅**保留** ``include[i]`` 为**真** 的 ``array[i]``，保持**原序** 。

    与 ``array`` 不等长 → #VALUE!。若**全部** 被滤掉**且** 给了 ``if_empty``，**返回** 该
    值（**如** 课堂用**字符串** "无"）。``include`` 需**外界** 先算好**布尔** 列，**不是** 传 lambda.
    """
    if len(include) != len(array):
        return VALUE
    out = [x for x, ok in zip(array, include) if ok]
    if not out and if_empty is not None:
        return if_empty
    return out


def SEQUENCE(rows: Any, columns: Any = 1, start: Any = 1, step: Any = 1) -> list[list[float]] | Any:
    """
    对应 **SEQUENCE**：**行主序** 填 **rows × columns** 的矩阵，自 ``start`` 起每**格** 加
    ``step`` ；每**行** 填完，下一**行** 首格 = 上一**行** 末**格** 再**加** 一个 **step**（见
    行尾 ``val += st * c`` ） 。

    用于**教** 序号表、**观察** 嵌套**循环** 与**二** 维** 下** 标。行列非**正** 或 参数非法 →
    #VALUE! 。
    """
    try:
        r = int(rows)
        c = int(columns)
        s = float(start)
        st = float(step)
    except (TypeError, ValueError):
        return VALUE
    if r < 1 or c < 1:
        return VALUE
    out: list[list[float]] = []
    val = s  # 每行起点的首格值
    for _ in range(r):
        row: list[float] = []
        v = val
        for _ in range(c):
            row.append(v)
            v += st  # 沿行推进
        out.append(row)
        val += st * c  # 换行后下一行起点
    return out


def RANDARRAY(
    rows: Any,
    columns: Any = 1,
    min_: Any = 0,
    max_: Any = 1,
    integer: bool = False,
) -> list[list[float]] | Any:
    """
    对应 **RANDARRAY**：``rows``×``columns`` 矩阵，每格在 ``[min_, max_]`` 上 **均匀** 分布
   （`random.uniform`）。``integer=True`` 时对**每** 格**四舍五入** 为**整数** ；**仅** 教学/
    演示，**不** 用于**安全** 随机.

    行列不合法 → #VALUE! 。
    """
    try:
        r = int(rows)
        c = int(columns)
        lo = float(min_)
        hi = float(max_)
    except (TypeError, ValueError):
        return VALUE
    if r < 1 or c < 1:
        return VALUE
    out: list[list[float]] = []
    for _ in range(r):
        row: list[float] = []
        for _ in range(c):
            x = random.uniform(lo, hi)
            row.append(float(int(round(x))) if integer else x)
        out.append(row)
    return out
