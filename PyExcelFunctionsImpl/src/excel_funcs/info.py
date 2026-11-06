"""
Layer 1 — 信息类函数：IS* / N / TYPE / ERROR.TYPE
================================================

**在 Excel 里**  
你常用 ``=ISNUMBER(A1)`` 判断格子里是不是数字、``=ISBLANK`` 是否为空。
本模块在 **Python 值** 上做同类判断：没有「单元格」对象，你传入的就是可能
从表里读出的 Python 标量或 ``list``。

**和 ``type()`` 的区别**  
Python 自带 ``type(x)`` 返回类型对象。Excel 的 ``TYPE`` 返回**约定数字**（1 数、
2 文、4 逻辑、16 错误、64 数组等），与 ``isinstance`` 的用法不同，见 :func:`TYPE`。

**无工作表时**  
``ISFORMULA`` 在纯数据场景下**无法**知道某值是否由公式产生，本实现**恒为 False**。
``ISREF`` 用「是否为嵌套 list 的第一行还是 list」这种**极粗**的启发式，仅作演示。

**阅读顺序**  
与 Excel 帮助里「信息函数」类名称一致；每个函数下均有中文说明。
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from excel_funcs.errors import ExcelErrorValue, NA, is_err, is_error, is_na


# ---------------------------------------------------------------------------
# 各类 “IS*” 判断：返回 True/False，不把「无法判断」和 False 混用
# ---------------------------------------------------------------------------


def ISBLANK(value: Any) -> bool:
    """
    对应 Excel ``ISBLANK``。

    - 仅当 ``value`` 为 ``None`` 或空字符串 ``""`` 时视为空（与「视觉空白」的细微差别
      在极端场合可能存在，以学习为主）。
    """

    return value is None or value == ""


def ISNUMBER(value: Any) -> bool:
    """
    对应 Excel ``ISNUMBER``：真数值（int/float，且非 bool 子类）、或可转为数字的字符串
    是否算「数」与 Excel 区域规则一致时较复杂，此处：**显式** ``int``/``float`` 为真；
    纯 **str** 再尝试 ``coerce_float``；**bool** 在 Excel 里有时当数，本实现**不算**
    纯数字（与 ``COUNT`` 对 bool 的忽略一致，减少歧义）。

    若 ``value`` 是 list/tuple/dict，视为**不是**单格数字，返回 False。
    """

    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    from excel_funcs._utils import coerce_float

    return coerce_float(value) is not None and not isinstance(value, (list, tuple, dict))


def ISTEXT(value: Any) -> bool:
    """
    对应 **ISTEXT**：**仅** 当值**运行时** 类型为 ``str`` 时为**真**（**不** 把「看
    起来像**数字的文本**」 自动当数——那是 :func:`ISNUMBER` 与 ``coerce`` 的**分工**) 。

    **和 Type** 列** 对** 照：学生常混「**格子里显** 示 123」 与 **``type`` 是 str** 。
    """

    return isinstance(value, str)


def ISLOGICAL(value: Any) -> bool:
    """
    对应 **ISLOGICAL**：**仅** ``bool`` 为真。整数 **1/0** 在 Python 里**不是** 逻辑
    型（**勿** 与**单元格** 里「像逻辑」 的**显示** 混**为一谈** ）。

    与 :func:`ISNUMBER` 分工明确，课堂可对比 ``True is 1`` 等题目**再** 讲** 。
    """
    return isinstance(value, bool)


def ISERROR(value: Any) -> bool:
    """
    对应 Excel ``ISERROR``：``value`` 是否为 :class:`excel_funcs.errors.ExcelErrorValue`
    任意一种（**包含** ``#N/A``）。若你只想判断 ``#N/A`` 用 :func:`ISNA`。
    """

    return is_error(value)


def ISERR(value: Any) -> bool:
    """
    对应 Excel ``ISERR``：是错误、但**不是** ``#N/A`` 时为真（若 ``#N/A`` 为假）。

    典型场景：配合 ``ISNA``/``IF`` 做错误分流。
    """

    return is_err(value)


def ISNA(value: Any) -> bool:
    """
    对应 **ISNA**：**仅** 为 :data:`~excel_funcs.errors.NA`（#N/A） 单例时为**真**；
    其它**任何** 错误 或 正常值 均为**假**（**用** ``is`` **比** 单例 最**稳** ） 。

    **和** :func:`ISERROR` / :func:`ISERR` **的** 包含** 关系** 可** 画** 文** 氏** 图** 一** 张** 。
    """
    return is_na(value)


def ISFORMULA(value: Any) -> bool:
    """
    对应 Excel ``ISFORMULA``。

    在**无工作簿模型**时无法得知某值是否由公式产生，本实现**恒返回 False**。
    若你扩展本库、传入「(cell, book)」元组，可在此处分支扩展。
    """

    return False


def ISREF(value: Any) -> bool:
    """
    对应 Excel ``ISREF`` 的**极简**版。

    若 ``value`` 为**非空**的 ``list``/``tuple``，且**首元素**仍是 ``list``/``tuple``，
    则粗略视为「二维区域」引用；否则为 False。这只是一种教学用启发，**不**表示
    与 Excel 引用的双射关系。
    """

    return isinstance(value, (list, tuple)) and len(value) > 0 and isinstance(value[0], (list, tuple))


# ---------------------------------------------------------------------------
# N / TYPE / ERROR.TYPE
# ---------------------------------------------------------------------------


def N(value: Any) -> float | ExcelErrorValue:
    """
    对应 Excel ``N``：把值转成**数字**语境下的标量；错误**原样返回**不转换。

    - 已是错误 → 原样返回（便于链式传下去）。
    - ``bool`` → 1.0 / 0.0
    - ``int``/``float`` → 转 ``float``
    - ``date``/``datetime`` → 用 ``date_to_serial`` 成序列数（与库内日期系统一致）
    - ``str`` → 能 ``coerce_float`` 则转浮点，否则作 **0.0**（与 Excel 常见行为近）
    - 其他 → 0.0
    """

    if is_error(value):
        return value  # type: ignore[return-value]
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, (datetime, date)):
        from excel_funcs.datetime_funcs import date_to_serial

        d = value if isinstance(value, date) else value.date()
        return float(date_to_serial(d))
    if isinstance(value, str):
        from excel_funcs._utils import coerce_float

        c = coerce_float(value)
        return 0.0 if c is None else c
    return 0.0


def TYPE(value: Any) -> int | ExcelErrorValue:
    """
    对应 Excel ``TYPE`` 的**简化数字编码**（与 help 中描述对齐程度有限，以文档为准）：

    - 错误 → 16
    - 逻辑 → 4
    - 数 → 1
    - 文本 → 2
    - 列表/元组（本实现中当作「数组」）→ 64
    - 其余回落为 1（与 Excel 边缘类型未一一对齐，避免误导）
    """

    if is_error(value):
        return 16
    if isinstance(value, bool):
        return 4
    if isinstance(value, (int, float)):
        return 1
    if isinstance(value, str):
        return 2
    if isinstance(value, (list, tuple)):
        return 64
    return 1


def ERROR_TYPE(value: Any) -> int | ExcelErrorValue:
    """
    对应 ``ERROR.TYPE``：输入**不是** :class:`ExcelErrorValue` 时返回 ``#N/A``（
    与「非错误不合法」的 Excel 行为在思想上接近）。

    各错误到整数的映射见 ``mapping`` 字典，未列出的 error code 归为 8。
    """

    if not isinstance(value, ExcelErrorValue):
        return NA
    mapping = {
        "#NULL!": 1,
        "#DIV/0!": 2,
        "#VALUE!": 3,
        "#REF!": 4,
        "#NAME?": 5,
        "#NUM!": 6,
        "#N/A": 7,
    }
    return mapping.get(value.code, 8)
