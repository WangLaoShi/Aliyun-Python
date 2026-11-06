"""
Layer 1 — 查找与引用（VLOOKUP / INDEX / MATCH / OFFSET …）
=========================================================

**小白记一点**  
在 Excel 里你选「一块表」当 ``table_array``。在 Python 里请用 **二维 list**：
``[[第1行], [第2行], …]``，即**外层列表 = 行**，**内层列表 = 列**。  
和你在表里「从左到右、从上到下」的顺序一致，就不容易传反。

**为什么叫「简化」？**  
工作簿、工作表、A1 引用、动态数组溢出等，在纯 Python 里要另建**上下文**模型。
本文件多数函数在「已经给你的 list 上」做查找；**INDIRECT** 在标准两参下返回
``#REF!``，若你传入扩展关键字 ``workbook=字典`` 则可模拟「从地址取缓存值」
（教学/测试用，见函数 docstring）。

**与 Excel 行为差异**  
- ``VLOOKUP``/``HLOOKUP`` 的**近似匹配**（最后一个参数为 TRUE）**未**完全按 Excel
  的排序与分段规则实现时，会在各函数中注明。
- **OFFSET** 以传入的矩阵容器左上角为 (0,0) 做偏移，不是解析工作表名。
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Sequence

from excel_funcs._utils import coerce_float
from excel_funcs.errors import NA, REF, VALUE, ExcelErrorValue, is_error


def _ensure_table(table: Any) -> list[list[Any]] | ExcelErrorValue:
    """
    把「像表」的输入规范成**二维** ``list[list]``，供 :func:`VLOOKUP`、:func:`INDEX`
    等共用，保证**外层=行、内层=列** 的约定一致.

    - 空表或非 list/tuple → **#VALUE!**。  
    - 若某行不是 list/tuple，则包成 ``[该行单值]``，仍算一行一列的二维表。

    Returns:
        规范化后的行列表，或 **#VALUE!**。
    """
    if not isinstance(table, (list, tuple)) or not table:
        return VALUE
    rows = [list(r) if isinstance(r, (list, tuple)) else [r] for r in table]
    return rows


def VLOOKUP(
    lookup_value: Any,
    table_array: Any,
    col_index_num: Any,
    range_lookup: Any = False,
) -> Any:
    """
    对应 **VLOOKUP**：在二维 ``table_array`` 中**首列** 为查找键，自左向右取
    第 ``col_index_num`` 列（**从 1 起算**）为返回值.

    **精确匹配**（``range_lookup`` 为假，默认）  
    自上而下**第一次** 键等于 ``lookup_value`` 时，返回该行的目标列；否则 #N/A。

    **近似匹配**（``range_lookup`` 为真，教学简化版）  
    将首列能转成**浮点** 的行按**数值键** 排序，找**最后一个** 键 **≤**  ``lookup_value``
    的浮点**近似** 所对应的行；与 Excel 全细节可能略有差异，重要业务请对拍帮助。

    若 ``lookup_value`` 已是错误值则**原样** 返回；列号 <1 或越界 → #REF!；表非法 →
    #VALUE!。内部 ``row_key(r)`` 取该行**首格** 供近似分支排序。

    **课堂可练**  
    用 ``list`` 做学号-姓名-成绩**模拟表** ，分别试精确/近似。
    """

    if is_error(lookup_value):
        return lookup_value
    rows = _ensure_table(table_array)
    if isinstance(rows, ExcelErrorValue):
        return rows
    try:
        ci = int(col_index_num)
    except (TypeError, ValueError):
        return VALUE
    if ci < 1 or ci > len(rows[0]):
        return REF
    approx = bool(range_lookup)

    def row_key(r: list[Any]) -> Any:
        """
        近似匹配时本行的**查找键**（首列格），即 ``r[0]``，供转浮点后排序.
        """
        return r[0]

    if not approx:
        for r in rows:
            if is_error(r[0]):
                return r[0]
            if r[0] == lookup_value:
                return r[ci - 1]
        return NA

    # 近似：按首列数值排序后找最后一个 <= lookup_value
    nums: list[tuple[float, list[Any]]] = []
    for r in rows:
        from excel_funcs._utils import coerce_float

        k = coerce_float(row_key(r))
        if k is None:
            continue
        nums.append((k, r))
    if not nums:
        return NA
    nums.sort(key=lambda x: x[0])
    best: list[Any] | None = None
    lk = lookup_value
    from excel_funcs._utils import coerce_float as _cf

    lv = _cf(lk)
    if lv is None:
        return NA
    for k, r in nums:
        if k <= lv:
            best = r
        else:
            break
    if best is None:
        return NA
    return best[ci - 1]


def HLOOKUP(
    lookup_value: Any,
    table_array: Any,
    row_index_num: Any,
    range_lookup: Any = False,
) -> Any:
    """
    对应 **HLOOKUP**：在**首行** 为查找键的**水平** 表里，取第 ``row_index_num`` 行
   （从 1 起算）的交叉值。本实现**先** 把 ``table_array`` **转置**，再调 :func:`VLOOKUP`，
    把「行当字段、首行当键」 转成「首列当键」 的标准 VLOOKUP 形态，便于在课上**画矩阵转置** 理解。

    ``range_lookup`` 与 :func:`VLOOKUP` 同义.
    """
    rows = _ensure_table(table_array)
    if isinstance(rows, ExcelErrorValue):
        return rows
    if not rows:
        return VALUE
    ncols = len(rows[0])
    table_t: list[list[Any]] = []
    for c in range(ncols):
        table_t.append([rows[r][c] for r in range(len(rows))])
    return VLOOKUP(lookup_value, table_t, row_index_num, range_lookup)


def INDEX(array: Any, row_num: Any, column_num: Any | None = None) -> Any:
    """
    对应 **INDEX**：``row_num``、``column_num`` 均为 **1 基**。

    - **一维** ``array``：省略 ``column_num``，只按 ``row_num`` 取第几个元素.  
    - **二维**（经 :func:`_ensure_table`）：取 ``(row_num, column_num)`` 交叉格.

    越界 → #REF!；类型非法 → #VALUE!。常与 :func:`MATCH` 联用，模拟**动态** 下标取值.

    """
    if column_num is None:
        # 一维
        if not isinstance(array, (list, tuple)):
            return VALUE
        try:
            r = int(row_num)
        except (TypeError, ValueError):
            return VALUE
        if r < 1 or r > len(array):
            return REF
        v = array[r - 1]
        return v
    rows = _ensure_table(array)
    if isinstance(rows, ExcelErrorValue):
        return rows
    try:
        r = int(row_num)
        c = int(column_num)
    except (TypeError, ValueError):
        return VALUE
    if r < 1 or c < 1 or r > len(rows) or c > len(rows[0]):
        return REF
    return rows[r - 1][c - 1]


def MATCH(
    lookup_value: Any,
    lookup_array: Sequence[Any],
    match_type: Any = 0,
) -> int | ExcelErrorValue:
    """
    对应 **MATCH**：在 ``lookup_array`` 中查找 ``lookup_value``，返回**第一次** 命中的
    **1 基** 下标；未找到**多数** 情况为 #N/A。

    ``match_type``：  
    - ``0``：精确相等.  
    - ``1``：升序、数值可比前提下，**最后一个** 仍 **≤** 查找值的位置（**教学** 线性近似）.  
    - ``-1``：降序下 **第一个** 仍 **≥** 查找值（同上）.  
    非 0/1/-1 → #VALUE!。

    与 :func:`INDEX` 成对出现，课堂常讲「**先 MATCH 行号/列号，再 INDEX 取格**」.
    """

    arr = list(lookup_array)
    try:
        mt = int(match_type)
    except (TypeError, ValueError):
        return VALUE
    if mt == 0:
        for i, v in enumerate(arr):
            if v == lookup_value:
                return i + 1
        return NA
    from excel_funcs._utils import coerce_float

    lv = coerce_float(lookup_value)
    if lv is None:
        return NA
    nums = [(i, coerce_float(x)) for i, x in enumerate(arr)]
    nums = [(i, v) for i, v in nums if v is not None]
    if mt == 1:
        nums.sort(key=lambda t: t[1])
        best = None
        for i, v in nums:
            if v <= lv:
                best = (i, v)
            else:
                break
        if best is None:
            return NA
        return best[0] + 1
    if mt == -1:
        nums.sort(key=lambda t: t[1], reverse=True)
        best = None
        for i, v in nums:
            if v >= lv:
                best = (i, v)
            else:
                break
        if best is None:
            return NA
        return best[0] + 1
    return VALUE


def CHOOSE(index_num: Any, *values: Any) -> Any:
    """
    对应 **CHOOSE**：从 ``*values`` 里按 **1 起** 的下标选第 ``k`` 项返回（``k = index_num`` 转 int）.

    下标 <1 或 > 参数个数、或非整数可转 → #VALUE!。与深嵌 **IF** 相比，适合**少** 数
    **离散** 选项的课堂阅读.

    **注意** ``*values`` 是**不定长** 实参，第 1 个选项是 ``values[0]`` 当 ``index_num==1`` 。
    """
    try:
        k = int(index_num)
    except (TypeError, ValueError):
        return VALUE
    if k < 1 or k > len(values):
        return VALUE
    return values[k - 1]


def ADDRESS(
    row_num: Any,
    column_num: Any,
    abs_num: Any = 1,
    a1: Any = True,
    sheet_text: Any = "",
) -> str | ExcelErrorValue:
    """
    对应 **ADDRESS** 的**极简** 版：用 **1 基** 的 ``row_num``、``column_num`` 拼出
    **A1 型** 地址字符串，如 ``B3``。若传 ``sheet_text``，前加 ``表名!``，如
    ``数据!A1``。

    ``abs_num``、``a1`` 在 Excel 中控制**引用类型/样式** ；本处**不** 完整实现.
    行、列不合法或无法转 int → #VALUE!。内部用 **26 进制** 的 ``col_letters`` 把列
    号变成 ``A..Z, AA..``，适合单独**板书** 算法.
    """
    try:
        r = int(row_num)
        c = int(column_num)
    except (TypeError, ValueError):
        return VALUE
    if r < 1 or c < 1:
        return VALUE

    def col_letters(n: int) -> str:
        """
        将 **1 基** 列号 n 变为 Excel 列字母：1→A、26→Z、27→AA…（循环 ``divmod(n-1, 26)`` 的经典写法).
        """
        s = ""
        while n:
            n, rem = divmod(n - 1, 26)
            s = chr(65 + rem) + s
        return s

    addr = f"{col_letters(c)}{r}"
    st = str(sheet_text) if sheet_text else ""
    if st:
        return f"{st}!{addr}"
    return addr


def ROW(reference: Any = None) -> int | list[int]:
    """
    对应 **ROW** 的**占位** 实现：无**工作表** 时不知道公式在**第几行** ，无参时**固** 定
    返回 **1**，与 Excel 里随**单元格** 而变的行号**不同** ，备课时需说明**局限** 。

    有参时本库也**未** 返回**多** 行区域**逐** 行行号，避免误导；**扩展** 可自建 ``reference`` 类型.
    """
    if reference is None:
        return 1
    return 1


def COLUMN(reference: Any = None) -> int:
    """
    对应 **COLUMN** 的**占位** 实现：同 :func:`ROW`，无工作表上下文时**恒** 为 **1** 。

    真实列号请在**自己** 的数据结构或调用层维护.
    """
    if reference is None:
        return 1
    return 1


def ROWS(array: Any) -> int | ExcelErrorValue:
    """
    对应 **ROWS**：返回二维表的**行数**（最外层 ``list`` 长度）。经 :func:`_ensure_table` ；
    非表 → #VALUE!。
    """
    rows = _ensure_table(array)
    if isinstance(rows, ExcelErrorValue):
        return rows
    return len(rows)


def COLUMNS(array: Any) -> int | ExcelErrorValue:
    """
    对应 **COLUMNS**：取**第一** 行长度作为**列数**（**矩形** 表；与 :func:`_ensure_table` 的用法一致) 。非表 → #VALUE!。
    """
    rows = _ensure_table(array)
    if isinstance(rows, ExcelErrorValue):
        return rows
    return len(rows[0])


def TRANSPOSE(array: Any) -> list[list[Any]] | ExcelErrorValue:
    """
    对应 **TRANSPOSE**：矩阵**转置** ``[list(c) for c in zip(*rows)]``。非表 → #VALUE!。
    与 :func:`HLOOKUP` 中手写转置**同一** 类操作.
    """
    rows = _ensure_table(array)
    if isinstance(rows, ExcelErrorValue):
        return rows
    return [list(col) for col in zip(*rows)]


def OFFSET(reference: Any, rows: Any, cols: Any, height: Any | None = None, width: Any | None = None) -> Any:
    """
    对应 **OFFSET** 教学版：``reference`` 为二维 ``list``，**不** 解析**工作表** 名**；
    以**左上角 (0,0) 为基准，向下** 偏移 ``rows``、向** 右** 偏移 ``cols`` 得子区**起点**；
    ``height``/``width`` 缺省时，一直取到**下**、**右** 边界**剩余** 整块**。

    子区越界 → #REF!；高宽非法 → #VALUE!。与**真实** A1 地址**无** 关，**纯** 下标.
    """
    tbl = _ensure_table(reference)
    if isinstance(tbl, ExcelErrorValue):
        return tbl
    rr = coerce_float(rows)
    cc = coerce_float(cols)
    if rr is None or cc is None:
        return VALUE
    r0, c0 = int(rr), int(cc)
    if r0 < 0 or c0 < 0 or r0 >= len(tbl) or c0 >= len(tbl[0]):
        return REF
    h_full = len(tbl) - r0
    w_full = len(tbl[0]) - c0
    if height is None:
        h = h_full
    else:
        ch = coerce_float(height)
        if ch is None or int(ch) < 1:
            return VALUE
        h = int(ch)
    if width is None:
        w = w_full
    else:
        cw = coerce_float(width)
        if cw is None or int(cw) < 1:
            return VALUE
        w = int(cw)
    if r0 + h > len(tbl) or c0 + w > len(tbl[0]):
        return REF
    return [list(row[c0 : c0 + w]) for row in tbl[r0 : r0 + h]]


def INDIRECT(
    ref_text: Any,
    a1: Any = True,
    *,
    workbook: Mapping[str, Any] | None = None,
) -> Any:
    """
    对应 **INDIRECT**：无**工作簿/网格** 模型时，仅 ``ref_text, a1`` 两参**默认** 返回
    **#REF!**，**说明** 间接引用依赖**地址解析器** 。

    可选 **``workbook=``** 传入 ``{"A1": 值, ...}`` 字典（**键** 不区分**大小** 写、可
    用**单** 引号**包** 名），**模拟** 由**文本** 取**格** ；未命中**键** **→** #REF! 。
    """
    _ = a1
    if workbook is None:
        return REF
    key = str(ref_text).strip()
    if len(key) >= 2 and key[0] == "'" and key[-1] == "'":
        key = key[1:-1]
    lk = key.upper()
    for addr, val in workbook.items():
        if str(addr).strip().upper() == lk:
            return val
    return REF


def XLOOKUP(
    lookup_value: Any,
    lookup_array: Sequence[Any],
    return_array: Sequence[Any],
    if_not_found: Any | None = None,
    match_mode: Any = 0,
    search_mode: Any = 1,
) -> Any:
    """
    对应 **XLOOKUP** 简化：仅**精确** 匹配、**自上而下** 第一次命中；``match_mode``/``search_mode`` 的**完整** Excel 语义本处**未** 全实现.

    ``lookup_array`` 与 ``return_array`` 须**等长** ，否则 #VALUE!。未找到时：若给
    ``if_not_found`` 则返回该值，否则 #N/A。与 VLOOKUP 相比，**不** 需要数「从左第几列」.
    """
    _ = match_mode, search_mode
    la = list(lookup_array)
    ra = list(return_array)
    if len(la) != len(ra):
        return VALUE
    for i, v in enumerate(la):
        if v == lookup_value:
            return ra[i]
    if if_not_found is not None:
        return if_not_found
    return NA


def XMATCH(lookup_value: Any, lookup_array: Sequence[Any], match_mode: Any = 0) -> int | ExcelErrorValue:
    """
    对应 **XMATCH** 的**极简** 封装：**当前** 直接** 转** 发** ``MATCH(lookup, arr, 0)`` ；
    ``match_mode`` **保** 留** **参** 数** 位** 、** 完** 整** 语** 义** 可** 在** 课** 上** 对** 照** 官** 方** 再** 扩** 展** 。

    **与** **MATCH** **差** 异** **在** **Excel** **里** **主** 要** 是** **搜** 索** 方** 向** 等** ；** 本** 处** 先** 统** 一** 为** 精** 确** 索** 引** 。
    """
    _ = match_mode
    return MATCH(lookup_value, lookup_array, 0)


def LOOKUP(lookup_value: Any, lookup_vector: Sequence[Any], result_vector: Sequence[Any] | None = None) -> Any:
    """
    对应 **LOOKUP**（**向量** 形式）的教学退化：用 :func:`MATCH`（``match_type=1``，**升序**
    **小于等于** 近似**）得** 下标，再取 ``result_vector`` 同**下标** 元素.

    若 ``result_vector`` 为 ``None`` 则**直接** 返回 #N/A；两向量须**等长** ，否则
    #VALUE!。与**完整** Excel 向量 LOOKUP/近似规则**可能** 有差，**重要** 题请**对拍** 。
    """
    lv = list(lookup_vector)
    if result_vector is None:
        return NA
    rv = list(result_vector)
    if len(lv) != len(rv):
        return VALUE
    idx = MATCH(lookup_value, lv, 1)
    if isinstance(idx, ExcelErrorValue):
        return idx
    return rv[idx - 1]
