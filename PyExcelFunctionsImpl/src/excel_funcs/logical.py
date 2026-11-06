"""
Layer 1 — 逻辑与条件类函数（IF / AND / OR / IFERROR …）
=======================================================

**小白记一点**  
Excel 里 ``=IF(A1>0, 算很重的式子1, 算很重的式子2)`` 可能**只算其中一边**（短路）。  
在 Python 里写 ``IF(条件, 式子1, 式子2)`` 时，**两边都会先算完**再挑一个返回值——
若式子里有「读文件、改数据库」等副作用，就和 Excel 不一样了。教学上仍把
``IF`` 当**纯数学关系**最稳。

**错误值**  
参数里若已有 ``ExcelErrorValue``，``AND``/``OR`` 等会按 Excel 习惯**先传错误**，
见各函数体内分支。

**与 Facade 的对应**  
:mod:`excel_funcs.facades.LogicalFuncs` 里方法名带 ``_``（如 ``if_``），因为
``if`` 是 Python 关键字。
"""

from __future__ import annotations

from typing import Any

from excel_funcs.errors import NA, ExcelErrorValue, is_error, is_na


def TRUE() -> bool:
    """
    对应工作表常数 **TRUE**（真）。

    **在 Excel 里**  
    写 ``=TRUE()`` 或某些比较结果为真，单元格显示 ``TRUE``。本实现返回 Python
    内置 ``True``，便于与 ``and``/``or``/``if`` 等混用。

    **教学提醒**  
    不要把 ``True`` 与数字 **1** 完全等同：在 Python 中 ``True == 1`` 为真，但
    类型不同；在聚合函数如 ``SUM`` 中布尔有时按 0/1 计，以各函数说明为准。

    **课堂可练**  
    在 Python 里 ``print(TRUE())`` 与在单元格里显示 ``TRUE`` 分别看到什么？思考
    「显示」与「求值结果」的区别。

    Returns:
        恒为 ``True``，类型 ``bool``。
    """

    return True


def FALSE() -> bool:
    """
    对应工作表常数 **FALSE**（假）。

    **在 Excel 里**  
    ``=FALSE()`` 与条件为假时类同。本函数返回 ``False``。

    **和 ``TRUE`` 成对**  
    在 ``IF(条件, TRUE(), FALSE())`` 这类写法的教学里，可对照「两分支的占位」。
    注意：在 Python 调用中**两个分支都会先被求值**（与 Excel 短路可能不同），
    见 :func:`IF` 的说明。

    **课堂可练**  
    写出 ``IF(x>0, TRUE(), FALSE())`` 的等价 Python 条件表达式，并比较可读性。

    Returns:
        恒为 ``False``，类型 ``bool``。
    """

    return False


def IF(condition: Any, value_if_true: Any, value_if_false: Any) -> Any:
    """
    Excel ``IF``：条件为**真**（见下方 ``bool`` 规则）时返回第二参，否则第三参。

    **与 Excel 的关键差异（必读）**  
    在 Python 中，**调用** ``IF`` 时解释器会**先**对三个实参**全部求值**，再
    进函数体。故「假分支里很重的计算」在 Excel 里可能不算，在 Python 里**照样算**。

    **条件怎么变 bool**  
    使用标准 ``bool(condition)``：空串、空列表、0、``None`` 等规则与 Python
    一致，与 Excel 里「空单元格当 0/假」在边界上可能不同，重要业务请**显式
    写比较式**如 ``x is not None``。
    """

    # 三元表达式：只在此行「二选一」，但 value_if_true / value_if_false 已被外层求值
    return value_if_true if bool(condition) else value_if_false


def IFERROR(value: Any, value_if_error: Any) -> Any:
    """Excel ``IFERROR``：若 ``value`` 为任意 :class:`~excel_funcs.errors.ExcelErrorValue` 则返回备用值。"""

    if is_error(value):
        return value_if_error
    return value


def IFNA(value: Any, value_if_na: Any) -> Any:
    """
    对应 **IFNA**：**仅**当第一参数为 **#N/A**（本库即单例 :data:`~excel_funcs.errors.NA`）时
    返回第二参数，否则返回第一参数原值。

    **和 IFERROR 的区别**  
    ``IFERROR`` 会捕获**任意** :class:`~excel_funcs.errors.ExcelErrorValue`；  
    ``IFNA`` **只**处理 ``#N/A``。当你希望 ``#VALUE!``、``#REF!`` 等仍冒泡
    时，用 ``IFNA`` 更精确（与 Excel 帮助一致）。

    **典型场景**  
    查找没命中时返回 ``#N/A``，用 ``IFNA`` 给默认展示「未找到」而不要把其它
    错也吃掉。

    Args:
        value: 可能是正常值、或 ``#N/A`` 等错误对象。
        value_if_na: 当且仅当 ``value`` 为 ``#N/A`` 时采用的结果。

    Returns:
        见上；类型随分支而定。

    **易错点**  
    用 ``is`` 与 ``==`` 比较错误单例时，本库中 ``#N/A`` 用 ``is`` 最稳
    （见 :func:`excel_funcs.errors.is_na`）。
    """

    if is_na(value):
        return value_if_na
    return value


def AND(*args: Any) -> bool | ExcelErrorValue:
    """
    Excel ``AND``：全为真则真；任一参数为错误则返回该错误；空参数在 Excel 中为 ``#VALUE!``，此处返回 ``False`` 与部分版本不同，建议始终传入条件。
    """

    if not args:
        from excel_funcs.errors import VALUE

        return VALUE
    for a in args:
        if is_error(a):
            return a  # type: ignore[return-value]
        if not bool(a):
            return False
    return True


def OR(*args: Any) -> bool | ExcelErrorValue:
    """
    对应 **OR**：**任一**条件为真则整体为真；若有一个参数是工作表**错误值**，
    则**先返回该错误**（在布尔判断之前「短路为错误」），与常见表格行为一致。

    **空参数**  
    无参数时返回 ``#VALUE!``（:data:`~excel_funcs.errors.VALUE`），与 Excel
    对 ``OR()`` 的提示一致，提醒学生不要漏写条件。

    **真值规则**  
    使用 ``bool(参数)`` 解释每一格；与空白、0、空串在 Excel 中的细微差异请注意，
    重要逻辑请**显式**写比较式。

    Args:
        *args: 多个条件，可展平为若干项（本实现不自动展平区域，与「直接多参」
            的用法一致，教学时可让学生传 ``(a, b, c)`` 若需要）。

    Returns:
        有真则 ``True``，全假则 ``False``，遇错误则返回该 :class:`ExcelErrorValue`。

    **课堂可练**  
    用 ``OR(A1>0, B1<10)`` 的对应 Python 写法，体会在单元格中「一块区域当条件」
    与「拆成多参」在本库中的传参方式。
    """
    if not args:
        from excel_funcs.errors import VALUE

        return VALUE
    any_true = False
    for a in args:
        if is_error(a):
            return a  # type: ignore[return-value]
        if bool(a):
            any_true = True
    return any_true


def NOT(value: Any) -> bool | ExcelErrorValue:
    """
    对应 **NOT**：对**逻辑值**取反。若参数本身是错误值，则**返回该错误**而非
    对错误取反（Excel 中也不是「把 #VALUE! 变真/假」）。

    Args:
        value: 任意可 ``bool`` 化的对象，或 :class:`ExcelErrorValue`。

    Returns:
        成功时为 ``not bool(value)``；若 ``value`` 为错误，则原样返回该错误。

    **易错**  
    ``NOT(0)`` 在 Python/多数语境下为 ``True``（0 为假再取反）；与某些严格
    区分数值/逻辑的表格设置可能不同，需课堂讨论。
    """
    if is_error(value):
        return value  # type: ignore[return-value]
    return not bool(value)


def XOR(*args: Any) -> bool | ExcelErrorValue:
    """
    对应 **XOR**（**异或**）：在「把每个参数当条件」的语境下，**真条件个数**为
    **奇数** 时结果为真，**偶数** 时为假；无参时 ``#VALUE!``。

    **直观理解**  
    两参时与「要么 A 要么 B，但不能两个都对」的「排他或」在真值表上常一致；  
    多参时 Excel 用「奇偶」规则推广。

    **错误优先**  
    若任一参数是错误，**先**返回该错误，与 **AND**/**OR** 风格一致。

    Returns:
        奇数个真为 ``True``，否则 ``False``；无参为 ``#VALUE!``。

    **课堂可练**  
    用真值表验证 ``XOR(TRUE, FALSE)`` 与 ``XOR(TRUE, TRUE)`` 的结果；再试三参。
    """
    if not args:
        from excel_funcs.errors import VALUE

        return VALUE
    c = 0
    for a in args:
        if is_error(a):
            return a  # type: ignore[return-value]
        if bool(a):
            c += 1
    return c % 2 == 1


def IFS(*pairs: Any) -> Any:
    """
    对应 **IFS**：**从左到右** 评估成对的 ``(test_i, value_i)``，**第一个**为真的
    ``test`` 的对应 ``value`` 被返回；若**全不匹配**，返回 **#N/A**。

    **参数形式**  
    以不定长实参依次传入：``test1, value1, test2, value2, ...``。成对数必须
    **偶数**，否则本实现返回 ``#VALUE!``，提醒学生数清楚逗号对。

    **和嵌套 ``IF`` 的对比**  
    多层 ``IF`` 难读，``IFS`` 是表格里常见的「多分支、按顺序选第一个命中」
    的糖衣语法；在 Python 里写教学代码时，也鼓励学生把「成对条件」排整齐。

    **与 ``SWITCH`` 不同**  
    ``IFS`` 是**真值测试**；``SWITCH`` 是**相等**匹配。别混用。

    Returns:
        命中的 ``value``；全不命中为 :data:`~excel_funcs.errors.NA`；形参不配偶为
        ``#VALUE!``。若某 ``test`` 本身为错误，**按 Excel 习惯先返回该错误**。
    """

    if len(pairs) % 2 != 0:
        from excel_funcs.errors import VALUE

        return VALUE
    for i in range(0, len(pairs), 2):
        cond = pairs[i]
        val = pairs[i + 1]
        if is_error(cond):
            return cond
        if bool(cond):
            return val
    return NA


def SWITCH(expression: Any, *values: Any) -> Any:
    """
    Excel ``SWITCH`` 近似：``SWITCH(expr, key1, val1, key2, val2, ..., [default])``。

    当 ``values`` 长度为奇数时，最后一项视为 **default**（与 Excel 一致）。
    """

    if not values:
        from excel_funcs.errors import VALUE

        return VALUE
    if len(values) % 2 == 1:
        *pairs, default = values
    else:
        pairs = values
        default = NA
    for i in range(0, len(pairs), 2):
        key = pairs[i]
        res = pairs[i + 1]
        if expression == key:
            return res
    return default
