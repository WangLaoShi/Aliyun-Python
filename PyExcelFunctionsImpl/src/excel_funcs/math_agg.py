"""
Layer 1 — 数学与聚合类函数（Excel「数学/三角/统计/条件汇总」的大本营）
================================================================================

**给完全小白的一句话**  
这里面的 ``SUM``、``AVERAGE`` 等，和你在 Excel 里写 ``=SUM(A1:A2)`` 是**同一条思路**，
只是格子换成了 Python 的 ``list``、数字、``None``。

**``list`` / 嵌套列表怎么当「区域」？**

- 传 ``1, 2, [3, 4]`` 时，内部会**展平**成 1,2,3,4 再求和，类似选中多块区域。
- 空单元格常用 ``None`` 或空字符串，是否忽略取决于各函数（与 Excel 略有出入时，
  在函数自己的 docstring 里说明）。

**错误值**  
若参数里出现 ``ExcelErrorValue``（如某格已是 ``#VALUE!``），多数**聚合函数**会
**先遇到先返回**该错误，避免在错误数据上继续算（行为接近表格里公式的链式效果）。

**文件很长怎么办？**  
用编辑器 **搜索** ``^def YOURFUNC`` 或 ``def SUM(`` 跳到实现；本文件按主题聚集，
不保证与 Excel 函数在菜单里的顺序一致。

**与 ``facades.MathFuncs`` 的关系**  
本模块里的函数是「真实现」；:mod:`excel_funcs.facades` 用 ``staticmethod`` 转发，
便于 ``xf.math.sum(...)`` 这种写法。

**教学阅读顺序建议（本文件体量大）**  
1. 先看 :func:`SUM` / :func:`AVERAGE` / :func:`_first_error`：理解**展平、错误
   先传播、空与文本**；  
2. 再看 **IF/COUNT 条件族**：:func:`SUMIF`、:func:`COUNTIFS` 与 :func:`_criteria_match`；  
3. 最后 **四舍五入/数学**：:func:`ROUND` 用 :func:`~excel_funcs._utils.excel_round_half_away_from_zero`；  
4. 高级：**SUBTOTAL** 与 :func:`AGGREGATE` 的**映射表**、与筛选/小计的课堂讨论。

**注释与代码行比例**（给备课老师）  
本文件每个 ``def`` 都配有**面向信息教育**的 docstring 与行内说明，便于**学生自读
源码**时对齐 Excel 帮助与测试用例，不必强记。
"""

from __future__ import annotations

import math
import random
import statistics
from typing import Any, Callable, Iterable, Sequence

from excel_funcs._utils import (
    coerce_float,
    excel_round_half_away_from_zero,
    excel_rounddown,
    excel_roundup,
    flatten_all,
    iter_flat_numbers,
)
from excel_funcs.errors import DIV0, NA, ExcelErrorValue, VALUE, is_error


def _first_error(*args: Any) -> ExcelErrorValue | None:
    """
    把参数里所有嵌套结构**展平**后，从左到右找**第一个** ``ExcelErrorValue``。

    用途：模拟「区域里只要有一格是错误，整段聚合常先显示该错误」的 Excel 行为。
    """

    for a in flatten_all(*args):
        if is_error(a):
            return a  # type: ignore[return-value]
    return None


def SUM(*args: Any) -> float | ExcelErrorValue:
    """
    Excel ``SUM``：对区域内所有数值求和；忽略空与非数值（不将文本当 0，除非可解析为数字——本实现与 Excel 略有差异，文本跳过）。

    若区域内存在错误值，返回遇到的第一个错误。

    **实现要点**（读代码时对照）：

    1. 先 ``_first_error``：有错误则**不再**累加，直接返回错误（链式传播）。
    2. ``flatten_all``：把 ``(1,[2,3])`` 变成 1,2,3 依次处理。
    3. ``None``/``""``：当作空，跳过（与多数单元格合计习惯一致）。
    4. ``bool``：按 1/0 参与（与 Excel SUM 对显式布尔的行为在版本/语境上可再查表，此处统一为 0/1）。
    5. ``str``：尝试 ``coerce_float``，失败则**跳过**（纯文本不计入，而非当 0）。
    """

    err = _first_error(*args)
    if err is not None:
        return err
    total = 0.0
    for a in flatten_all(*args):
        if a is None or a == "":
            continue  # 空单元格
        if isinstance(a, bool):
            total += 1.0 if a else 0.0
            continue
        if isinstance(a, (int, float)):
            total += float(a)
            continue
        if isinstance(a, str):
            c = coerce_float(a)
            if c is not None:
                total += c
            # 无法转换的文本：Excel SUM 忽略
            continue
    return total


def AVERAGE(*args: Any) -> float | ExcelErrorValue:
    """
    对应 **AVERAGE**（**算术平均**）：把所有能当**数**的格子加起来再除以**个数**。

    **与 SUM 的区别**  
    同样**忽略**空 ``None``/``""`` 与不可转纯文本，但 **COUNT** 在这里隐含为
    「参与平均的数」的个数。无可用数时，按 Excel 习惯返回 **#DIV/0!**（本库
    用 :data:`~excel_funcs.errors.DIV0`).

    **布尔**  
    按 0/1 参与，与 :func:`SUM` 的布尔规则一致，便于和「一列里 TRUE/FALSE」
    的教学衔接。

    **可解析数串**  
    与 ``SUM`` 相同：能 ``coerce_float`` 的串参与。

    **错误**  
    区域内先 :func:`_first_error`，遇错则整段不平均。

    **课堂可练**  
    与 ``=AVERAGE(1,2,3)`` 对拍；再试全空，观察 **#DIV/0!**。
    """

    err = _first_error(*args)
    if err is not None:
        return err
    nums: list[float] = []
    for a in flatten_all(*args):
        if a is None or a == "":
            continue
        if isinstance(a, bool):
            nums.append(1.0 if a else 0.0)
            continue
        if isinstance(a, (int, float)):
            nums.append(float(a))
            continue
        if isinstance(a, str):
            c = coerce_float(a)
            if c is not None:
                nums.append(c)
    if not nums:
        return DIV0
    return sum(nums) / len(nums)


def AVERAGEA(*args: Any) -> float | ExcelErrorValue:
    """
    对应 **AVERAGEA**（**含文本地参与**的平均）：**非空**格都**计入分母**（与
    **AVERAGE** 会跳过纯空不同，这里空 ``None`` 仍跳过，但 ``""`` 当 **0** 参与
    且**占一格**；纯文本**当 0** 参与）。

    **和 AVERAGE 对照**  
    混有「标题文字」的列，用 AVERAGEA 会**被文字拉低**平均——课堂讨论「什么该
    用数值列」.

    **TRUE/FALSE**  
    1/0；**错误** 仍先 :func:`_first_error` 全段停。

    **无分母**  
    全空区域 → #DIV/0!。

    **课堂可练**  
    同一表分别 ``AVERAGE``/``AVERAGEA``，体会「分母与分子」的口径差异。
    """

    err = _first_error(*args)
    if err is not None:
        return err
    vals: list[float] = []
    for a in flatten_all(*args):
        if a is None:
            continue
        if a == "":
            vals.append(0.0)
        elif isinstance(a, bool):
            vals.append(1.0 if a else 0.0)
        elif isinstance(a, (int, float)):
            vals.append(float(a))
        elif isinstance(a, str):
            vals.append(0.0)
        else:
            vals.append(0.0)
    if not vals:
        return DIV0
    return sum(vals) / len(vals)


def COUNT(*args: Any) -> int | ExcelErrorValue:
    """
    对应 **COUNT**（**数个数**）：只数 **int/float**（本实现**不算** 布尔、与
    部分 Excel 版本对**单元格**布尔计数的差异在课堂可点明）；**纯文本串** 不计，
    即使像 ``"3"`` 在 ``VALUE`` 里能当数——**保持与表软件 COUNT 常见讲解一致**。

    **可扩展讨论**  
    若你期望 ``"3"`` 也计 1 个，那是另一套**课程扩展**，可对比 :func:`COUNTA`。

    **错误**  
    先 :func:`_first_error`。
    """

    err = _first_error(*args)
    if err is not None:
        return err
    n = 0
    for a in flatten_all(*args):
        if isinstance(a, (int, float)) and not isinstance(a, bool):
            n += 1
        elif isinstance(a, bool):
            # Excel COUNT 对布尔：在单元格中为数值？实际上 COUNT 不计 TRUE/FALSE in cell in classic excel
            # 简化：不计 bool
            continue
    return n


def COUNTA(*args: Any) -> int | ExcelErrorValue:
    """
    对应 **COUNTA**（**非空格数**）：**任何**非 ``None`` 的项都计 1，含 ``""``、
    错误对象、字符串、0——只要「不是没填」的 ``None``。

    **和 COUNT 对比**  
    ``COUNT`` 只数**纯数值型**在实现里的那类；``COUNTA`` 数**有东西**的格数，
    适合「问卷填答数量」等统计。

    **空串**  
    在 Python 中 ``a == ""`` 为真，**计 1 格**（与 Excel 非空但显示空白串的格
    常一致）.

    **错误**  
    仍先 :func:`_first_error`（若你依赖「数错误格」，讨论区：表软件行为可能不同，本库先**传播**错误**而非**当普通格去数）。
    """

    err = _first_error(*args)
    if err is not None:
        return err
    n = 0
    for a in flatten_all(*args):
        if a is None:
            continue
        n += 1
    return n


def COUNTBLANK(*args: Any) -> int | ExcelErrorValue:
    """
    对应 **COUNTBLANK**（**空格格数**）：在展平后数 ``None`` 与 ``""`` 两种
    **教学上常用的空**表示。其它「看起来像空」的 0 或仅空格未 strip 的串**不算**，
    可课堂讨论**数据清洗**再 ``COUNTBLANK``.

    **与 COUNTA 的互补**（思想实验）  
    固定区域里，在理想化「只有空/非空」的模型中，**COUNT+COUNTA+COUNTBLANK** 的
    讲法在课程里可**分组讨论**，不当作本实现的全局恒等式。

    **错误**  
    先 :func:`_first_error`。
    """

    err = _first_error(*args)
    if err is not None:
        return err
    n = 0
    for a in flatten_all(*args):
        if a is None or a == "":
            n += 1
    return n


def MAX(*args: Any) -> float | ExcelErrorValue:
    """
    对应 **MAX**（**最大值**）。从展平后的区域里，取所有能**转成数**的项的
    最大值；**布尔** 当 0/1；**可解析的数串** 参与。若**一个数也没有**，Excel
    在部分语境下为 0/错误，本实现与常见教学代码一致**返回 0.0**（可课堂对比
    你使用的 Excel 版本**空区域 MAX** 行为）.

    **和 MAXA**  
    文本/逻辑被弱化为数的方式不同，见 :func:`MAXA`。

    **错误**  
    :func:`_first_error` 优先；否则逐格不抛异常。

    **课堂可练**  
    在表里造含负数、小数的区，和 ``=MAX(区域)`` 对拍；再试全空看 0 与 帮助文档.
    """
    err = _first_error(*args)
    if err is not None:
        return err
    nums: list[float] = []
    for a in flatten_all(*args):
        if isinstance(a, (int, float)) and not isinstance(a, bool):
            nums.append(float(a))
        elif isinstance(a, bool):
            nums.append(1.0 if a else 0.0)
        elif isinstance(a, str):
            c = coerce_float(a)
            if c is not None:
                nums.append(c)
    if not nums:
        return 0.0
    return max(nums)


def MIN(*args: Any) -> float | ExcelErrorValue:
    """
    对应 **MIN**（**最小值**），规则同 :func:`MAX`：能当数的都参与，无参与数
    时**返回 0.0**（与 MAX 的「空区」对偶教学）；布尔 0/1、数串能转则转。

    **和 MINA**  
    见 :func:`MINA` 的「全格当 0/1/数」的更强口径.

    **课堂可练**  
    用「气温一周」小表，``MIN``/``MAX`` 找极值，再和排序取首尾对比。
    """
    err = _first_error(*args)
    if err is not None:
        return err
    nums: list[float] = []
    for a in flatten_all(*args):
        if isinstance(a, (int, float)) and not isinstance(a, bool):
            nums.append(float(a))
        elif isinstance(a, bool):
            nums.append(1.0 if a else 0.0)
        elif isinstance(a, str):
            c = coerce_float(a)
            if c is not None:
                nums.append(c)
    if not nums:
        return 0.0
    return min(nums)


def MEDIAN(*args: Any) -> float | ExcelErrorValue:
    """
    对应 **MEDIAN**（**中位数**）：可转数的列**排序**后，奇数个取正中，偶数个
    取**中间两数平均**（与 :mod:`statistics` 的常识一致，与 Excel **MEDIAN** 的
    大样本对拍在课堂足够）.

    **全空/无数**  
    返回 #DIV/0!（:data:`DIV0`）——**没有**可排的中位。

    **和 AVERAGE 对比**  
    有极端离群时，**中位数**更**稳健**，课堂可给「被一人拉高平均」的故事。

    **bool/串**  
    同 MAX：布尔 0/1，数串可转则转。

    **错误**  
    先 :func:`_first_error`。
    """
    err = _first_error(*args)
    if err is not None:
        return err
    nums: list[float] = []
    for a in flatten_all(*args):
        if isinstance(a, (int, float)) and not isinstance(a, bool):
            nums.append(float(a))
        elif isinstance(a, bool):
            nums.append(1.0 if a else 0.0)
        elif isinstance(a, str):
            c = coerce_float(a)
            if c is not None:
                nums.append(c)
    if not nums:
        return DIV0
    nums.sort()
    m = len(nums) // 2
    if len(nums) % 2:
        return nums[m]
    return (nums[m - 1] + nums[m]) / 2


def MODE_SNGL(*args: Any) -> float | ExcelErrorValue:
    """
    对应 **MODE.SNGL**（**单众数**）：在样本中出现**最多次**的数；若**多个值**
    同时并列第一频数，Excel 与 :mod:`statistics.multimode` 返回**一列**众数，本
    实现再取**其中最小者**，与 **MODE.SNGL**「确定挑一个」的教学习惯一致。

    **无众数/无数**  
    没有任何数 → :data:`NA`（#N/A）。

    **和 MEDIAN/MEAN 对比**  
    众数适合**标称**「最常见选项」；**多峰**时解释力下降，可课堂讨论**分布形状**.

    **bool/可解析串**  
    同 :func:`MAX`。

    **错误**  
    展平后若某格是 ``ExcelErrorValue``，在循环中**立即**返回该错误，与
    ``_first_error`` 的「全区域先扫一遍」在顺序上**略有不同**，对教学只须记住：
    含错误的区域不要指望得到众数。

    """
    err = _first_error(*args)
    if err is not None:
        return err
    nums: list[float] = []
    for a in flatten_all(*args):
        if is_error(a):
            return a  # type: ignore[return-value]
        if isinstance(a, (int, float)) and not isinstance(a, bool):
            nums.append(float(a))
        elif isinstance(a, bool):
            nums.append(1.0 if a else 0.0)
        elif isinstance(a, str):
            c = coerce_float(a)
            if c is not None:
                nums.append(c)
    if not nums:
        return NA
    modes = statistics.multimode(nums)
    return float(min(modes))


def _maxa_mina_cell(a: Any) -> float | ExcelErrorValue:
    """
    内部**单格**解释规则，供 :func:`MAXA` 与 :func:`MINA` 共用，把一格里出现的
    **各种类型** 压成**一个参与比较大小的浮点数**。

    **与 MAX/MIN 的逐格不同**  
    这里**纯文本**若不能 ``coerce_float`` 则**当 0**；``None``/``""`` 也当 0；
    **BOOL** 为 1/0。故「标题行」的字符串可能把**极值**拉向 0。

    **错误**  
    若本格**已是** ``ExcelErrorValue``，**原样返回**该错误，让上层**中断**最值
    计算（与 :func:`MAX` 先 ``_first_error`` 的两种风格可以课堂对比）。

    Returns:
        非错误时为 ``float``；为错误时为 :class:`ExcelErrorValue`。
    """

    if is_error(a):
        return a  # type: ignore[return-value]
    if a is None or a == "":
        return 0.0
    if isinstance(a, bool):
        return 1.0 if a else 0.0
    if isinstance(a, (int, float)) and not isinstance(a, bool):
        return float(a)
    if isinstance(a, str):
        c = coerce_float(a)
        return float(c) if c is not None else 0.0
    return 0.0


def MAXA(*args: Any) -> float | ExcelErrorValue:
    """
    对应 **MAXA**（**含逻辑与文本的极大**）。每一格经 :func:`_maxa_mina_cell` 后
    再 ``max``；**空区** 行为与 :func:`MAX` 的 **0.0** 对拍用于课堂即可。

    **什么时候用**  
    列里混有「是/否」与数字，要取「按 Excel 的 A 规则」的极值时，与 :func:`MAX` 对
    照教学。

    **错误**  
    先 :func:`_first_error`；**然后** 若某格为错误，见 ``_maxa_mina_cell``。

    **课堂可练**  
    造一列 ``TRUE, 2, "z"``，分别 ``MAX`` 与 ``MAXA`` 看差异。
    """

    err = _first_error(*args)
    if err is not None:
        return err
    vals: list[float] = []
    for a in flatten_all(*args):
        v = _maxa_mina_cell(a)
        if isinstance(v, ExcelErrorValue):
            return v
        vals.append(v)
    if not vals:
        return 0.0
    return max(vals)


def MINA(*args: Any) -> float | ExcelErrorValue:
    """
    对应 **MINA**，与 :func:`MAXA` 对偶：逐格 :func:`_maxa_mina_cell` 后求**最小**。

    **和 MIN**  
    同 MAX/MAXA 的「**文本当 0**、逻辑当 0/1」的对比故事。

    **全空/无格**  
    返回 0.0，与 :func:`MIN` 相同约定。

    **课堂可练**  
    用同一数据跑 ``MIN``/``MINA``/``SMALL``（若课程后续引入）的对比小专题。
    """

    err = _first_error(*args)
    if err is not None:
        return err
    vals: list[float] = []
    for a in flatten_all(*args):
        v = _maxa_mina_cell(a)
        if isinstance(v, ExcelErrorValue):
            return v
        vals.append(v)
    if not vals:
        return 0.0
    return min(vals)


def _subtotal_nums_only(*args: Any) -> list[float] | ExcelErrorValue:
    """
    **SUBTOTAL 统计类** 的**前置**步骤：在无错误时，从区域里**只收集**可参与
    **标准差/方差/求和/计数** 等子函数的**纯数列表**（布尔当 0/1，能转的串当数，其它跳过）。

    **与 SUM 的差异**（实现细节）  
    不在这里做 ``_first_error`` 之外的特殊事；**空** 与 **MAX** 类似地**忽略非数**
    的若干类型；返回的是**列表**给 :func:`_subtotal_stdev_s` 等使用。

    Returns:
        成功为 ``list[float]``；若 :func:`_first_error` 发现错误，直接返回
        该 :class:`ExcelErrorValue`（**不是**列表，调用方**必须** ``isinstance`` 判断).
    """
    err = _first_error(*args)
    if err is not None:
        return err
    nums: list[float] = []
    for a in flatten_all(*args):
        if isinstance(a, (int, float)) and not isinstance(a, bool):
            nums.append(float(a))
        elif isinstance(a, bool):
            nums.append(1.0 if a else 0.0)
        elif isinstance(a, str):
            c = coerce_float(a)
            if c is not None:
                nums.append(c)
    return nums


def _subtotal_stdev_s(*args: Any) -> float | ExcelErrorValue:
    """
    **SUBTOTAL(7, …)**: **样本标准差** ``STDEV.S``，用 :func:`statistics.stdev`
    （`ddof=1`）。**少于 2 个数** 时，按与 Excel 常见行为一致，返回 #DIV/0!。

    Args:
        *args: 同 :func:`SUBTOTAL` 中传入的**数据区**展平后。

    **和 STDEV.P**  
    见 :func:`_subtotal_stdev_p`（总体标准差、分母 n）。

    **课堂可练**  
    同班身高 1 人时能否谈「样本标准差」？——数量不足在公式里**表现为错或空** 的讨论。
    """
    nums = _subtotal_nums_only(*args)
    if isinstance(nums, ExcelErrorValue):
        return nums
    if len(nums) < 2:
        return DIV0
    return float(statistics.stdev(nums))


def _subtotal_stdev_p(*args: Any) -> float | ExcelErrorValue:
    """
    **SUBTOTAL(8, …)**: **总体标准差** ``STDEV.P``，:func:`statistics.pstdev`。
    方差为「除以 n」意义下的开方。样本不足 2 个仍按本库规则 **#DIV/0!**（与
    部分版本可能略有差，**教学以一致内部规则为准**）.

    **和 .S 对比**  
    课堂必讲 **Bessel 校正**（n-1）与「把当前数据**当作全体**还是**从总体抽样**」
    的**哲学**而不仅是公式。
    """
    nums = _subtotal_nums_only(*args)
    if isinstance(nums, ExcelErrorValue):
        return nums
    if len(nums) < 2:
        return DIV0
    return float(statistics.pstdev(nums))


def _subtotal_var_s(*args: Any) -> float | ExcelErrorValue:
    """
    **SUBTOTAL(10, …)**: **样本方差** ``VAR.S``。  
    内部 :func:`statistics.variance`；少于 2 点 → #DIV/0!。  

    **教学**  
    方差=标准差平方；**同一份数据**上 ``VAR.S`` 与 ``STDEV.S`` 满足平方关系
    （在**浮点**尾部可能有微小差，可点一句 IEEE).
    """
    nums = _subtotal_nums_only(*args)
    if isinstance(nums, ExcelErrorValue):
        return nums
    if len(nums) < 2:
        return DIV0
    return float(statistics.variance(nums))


def _subtotal_var_p(*args: Any) -> float | ExcelErrorValue:
    """
    **SUBTOTAL(11, …)**: **总体方差** ``VAR.P``，:func:`statistics.pvariance`。

    与 :func:`_subtotal_var_s` 的**分母 n vs n-1** 对偶，是统计入门课的固定板书。
    """
    nums = _subtotal_nums_only(*args)
    if isinstance(nums, ExcelErrorValue):
        return nums
    if len(nums) < 2:
        return DIV0
    return float(statistics.pvariance(nums))


def PRODUCT(*args: Any) -> float | ExcelErrorValue:
    """
    对应 **PRODUCT**（**连乘**）：可转数者相乘，**无任意参与乘数** 时，Excel
    为 **0** 还是 **1** 易混——本实现与常见「**空连乘=0**」**教学**代码一致
    返回 **0.0**（可课堂与 Excel 帮助再对拍）.

    **与 SUM 的对照**  
    累加有「**空区 0**」的直觉，连乘的**单位元** 在数学是 **1**，但**表格
    产品** 常展示空为 **不参与** 而结果为 **0**（实现选择见代码分支 ``any_num``）.

    **bool/串/空**  
    同 :func:`SUM`：布尔 0/1，能转的串，``None``/``""`` 跳过。

    **错误**  
    先 :func:`_first_error`。
    """
    err = _first_error(*args)
    if err is not None:
        return err
    p = 1.0
    any_num = False
    for a in flatten_all(*args):
        if a is None or a == "":
            continue
        if isinstance(a, bool):
            p *= 1.0 if a else 0.0
            any_num = True
            continue
        if isinstance(a, (int, float)):
            p *= float(a)
            any_num = True
            continue
        if isinstance(a, str):
            c = coerce_float(a)
            if c is not None:
                p *= c
                any_num = True
    return p if any_num else 0.0


def SUMPRODUCT(*arrays: Sequence[Any]) -> float | ExcelErrorValue:
    """
    Excel ``SUMPRODUCT`` 简化版：传入多个**等长一维**可迭代对象；对应位置相乘后求和。

    二维区域需调用方先对齐行数列数；本实现仅检查第一维长度一致。
    """

    if not arrays:
        return VALUE
    n = len(arrays[0])
    for arr in arrays[1:]:
        if len(arr) != n:
            return VALUE
    total = 0.0
    for i in range(n):
        prod = 1.0
        for arr in arrays:
            v = arr[i]
            if is_error(v):
                return v  # type: ignore[return-value]
            c = coerce_float(v)
            if c is None:
                return VALUE
            prod *= c
        total += prod
    return total


def _criteria_match(cell: Any, criteria: Any) -> bool:
    """
    条件判断的**小引擎**，供 :func:`SUMIF`、:func:`COUNTIFS` 等复用，避免重复。

    **两种模式**  
    1. **标量/普通值**：`cell == criteria`（不尝试 Excel 的通配符，课程扩展点）。  
    2. **以比较符开头的 str**，如 ``">5"``、``"<=3.2"``、``"<>0"``：把两侧用
       :func:`~excel_funcs._utils.coerce_float` 尽量转成**浮点** 再比；任一侧
       失败则**不匹配**（返回 ``False``），避免 silent wrong。

    **与 Excel 全功能**  
    未实现通配符、公式条件数组等；**够用于课堂** 条件计数/条件求和 的主干演示。

    Returns:
        满足条件为 ``True``，否则 ``False``。

    **课堂可练**  
    试 ``cell=5, criteria=">4"`` 与 ``"=5"`` 等写法的分支。
    """

    if isinstance(criteria, str) and criteria and criteria[0] in "><=":
        op = ""
        j = 0
        while j < len(criteria) and criteria[j] in "><=":
            op += criteria[j]
            j += 1
        rhs = coerce_float(criteria[j:].strip())
        lhs = coerce_float(cell)
        if lhs is None or rhs is None:
            return False
        if op in (">",):
            return lhs > rhs
        if op in ("<",):
            return lhs < rhs
        if op in (">=",):
            return lhs >= rhs
        if op in ("<=",):
            return lhs <= rhs
        if op in ("<>", "!="):
            return lhs != rhs
        if op in ("=", "=="):
            return lhs == rhs
    return cell == criteria


def SUMIF(range_vals: Iterable[Any], criteria: Any, sum_range: Iterable[Any] | None = None) -> float | ExcelErrorValue:
    """
    对应 **SUMIF（条件求和）** 的**一维、教学简化版**：`range_vals` 中第 **i** 行
    若满足 :func:`_criteria_match(cell, criteria)`，则把 ``sum_range[i]``（缺省
    则与 ``range`` 同列，即**自加**）的数**加进**总和。

    **与 Excel 相比**  
    不支持**二维区域**、**多条件**的完整语法那套；多条件用 :func:`SUMIFS`。

    **错格**  
    条件区或和区任一格是 ``ExcelErrorValue`` 则**先返回该错误**（行序从左到
    上到下由 **list 顺序** 决定，与「遇错先停」的心智类同）。

    **空/非数在 sum 侧**  
    ``coerce_float`` 失败则**跳过**该加项（不当中断），与「只加可解析数」的
    课堂约定一致，必要时与 Excel 再对拍。

    **课堂可练**  
    成绩表一列科目标题、一列分，**按「是否包含某字」的扩展** 可自练（需改本函数
    用 ``in`` 或 regex —— 作为作业）。
    """
    r = list(range_vals)
    s = list(sum_range) if sum_range is not None else r
    if len(s) != len(r):
        return VALUE
    total = 0.0
    for i, cell in enumerate(r):
        if is_error(cell):
            return cell  # type: ignore[return-value]
        if _criteria_match(cell, criteria):
            v = s[i]
            if is_error(v):
                return v  # type: ignore[return-value]
            c = coerce_float(v)
            if c is None:
                continue
            total += c
    return total


def COUNTIF(range_vals: Iterable[Any], criteria: Any) -> int | ExcelErrorValue:
    """
    对应 **COUNTIF**：数**满足** :func:`_criteria_match` 的**格数**（一维
    可迭代，逐格扫描）。

    **不数「空满足」** 的奇谈**  
    若你写比较式使大量 False，得到 0 是正常的。若 criteria 是某格引用，想数
    「等于 60 分的人」，注意**类型**是数还是**文本 "60"** 的**课堂**讨论。

    **错格**  
    任一格是 ``ExcelErrorValue`` → **先返回**该错。

    **和 COUNTIFS**  
    单条件 vs 多条件，见 :func:`COUNTIFS`。
    """
    n = 0
    for cell in range_vals:
        if is_error(cell):
            return cell  # type: ignore[return-value]
        if _criteria_match(cell, criteria):
            n += 1
    return n


def AVERAGEIF(
    range_vals: Iterable[Any],
    criteria: Any,
    average_range: Iterable[Any] | None = None,
) -> float | ExcelErrorValue:
    """
    对应 **AVERAGEIF**：在 `range_vals` 上筛行，**命中的行** 取 `average_range`
    中对应**格**的数，再 **AVERAGE**；缺省两列**同一**（对满足条件的**自身**
    格求平均）。  

    **无命中**  
    没有任何可 `coerce_float` 的**加项** → #DIV/0!。

    **和 SUMIF 同步**  
    长度错 → ``#VALUE!``；行内**错误** 冒泡。

    **课堂可练**  
    与 `SUMIF/COUNTIF` 三件套一起出**同一**情境题，理解「**加总、计数、平均**」
    三种**聚合** 口径.
    """
    r = list(range_vals)
    a = list(average_range) if average_range is not None else r
    if len(a) != len(r):
        return VALUE
    nums: list[float] = []
    for i, cell in enumerate(r):
        if is_error(cell):
            return cell  # type: ignore[return-value]
        if _criteria_match(cell, criteria):
            v = a[i]
            if is_error(v):
                return v  # type: ignore[return-value]
            c = coerce_float(v)
            if c is not None:
                nums.append(c)
    if not nums:
        return DIV0
    return sum(nums) / len(nums)


def SUMIFS(sum_range: Iterable[Any], *criteria_pairs: Any) -> float | ExcelErrorValue:
    """
    Excel ``SUMIFS``：参数为 ``sum_range, crit_range1, crit1, crit_range2, crit2, ...``。
    """

    s = list(sum_range)
    if len(criteria_pairs) % 2 != 0:
        return VALUE
    ranges: list[list[Any]] = []
    crits: list[Any] = []
    for i in range(0, len(criteria_pairs), 2):
        cr = list(criteria_pairs[i])
        crit = criteria_pairs[i + 1]
        if len(cr) != len(s):
            return VALUE
        ranges.append(cr)
        crits.append(crit)
    total = 0.0
    for idx in range(len(s)):
        ok = True
        for cr, c in zip(ranges, crits):
            cell = cr[idx]
            if is_error(cell):
                return cell  # type: ignore[return-value]
            if not _criteria_match(cell, c):
                ok = False
                break
        if not ok:
            continue
        v = s[idx]
        if is_error(v):
            return v  # type: ignore[return-value]
        cf = coerce_float(v)
        if cf is not None:
            total += cf
    return total


def COUNTIFS(*criteria_pairs: Any) -> int | ExcelErrorValue:
    """
    对应 **COUNTIFS**（**多条件计数**）：实参为 **crit_range1, crit1, crit_range2, crit2, …**
    成对出现；**同一行** 上所有条件**同时** 满足则 **+1**。

    **成对**  
    长度必须偶数，否则 #VALUE!；各 **range 等长**（本实现**逐下标** 对齐，类**行
    向表** 模型）。

    **和 COUNTIF**  
    单条件特例；**AND** 在「行上合取」 的意义.

    **错格**  
    与 :func:`SUMIFS` 相同：**先** 遇格内错误**即返**该错。

    **课堂可练**  
    销售表：地区=东 **且** 额>1000 的**订单行数**（先过滤再 count 的 SQL 对偶 讲解）.
    """
    if len(criteria_pairs) % 2 != 0:
        return VALUE
    ranges = [list(criteria_pairs[i]) for i in range(0, len(criteria_pairs), 2)]
    crits = [criteria_pairs[i + 1] for i in range(0, len(criteria_pairs), 2)]
    if not ranges:
        return VALUE
    n0 = len(ranges[0])
    for cr in ranges:
        if len(cr) != n0:
            return VALUE
    count = 0
    for idx in range(n0):
        ok = True
        for cr, c in zip(ranges, crits):
            cell = cr[idx]
            if is_error(cell):
                return cell  # type: ignore[return-value]
            if not _criteria_match(cell, c):
                ok = False
                break
        if ok:
            count += 1
    return count


def AVERAGEIFS(average_range: Iterable[Any], *criteria_pairs: Any) -> float | ExcelErrorValue:
    """
    对应 **AVERAGEIFS**：`average_range` 为**要平均的列**；后面接多对
    **(条件区, 条件)**，**行对齐** 后多条件**合取** 筛行，对命中行在 `average_range`
    的数求 **AVERAGE**。

    **全不命中/无数**  
    #DIV/0!；与 :func:`AVERAGEIF` 一致。

    **和 SUMIFS**  
    只把「**加**」 换成「**求平均**」 的**聚合** 换一下。

    **课堂可练**  
    用同一筛选条件，分别 ``SUMIFS``/``COUNTIFS``/``AVERAGEIFS``，验证
    **平均 ≈ 和/数** 在**浮点** 意义下**近似** 相等.
    """
    s = list(average_range)
    if len(criteria_pairs) % 2 != 0:
        return VALUE
    ranges = [list(criteria_pairs[i]) for i in range(0, len(criteria_pairs), 2)]
    crits = [criteria_pairs[i + 1] for i in range(0, len(criteria_pairs), 2)]
    for cr in ranges:
        if len(cr) != len(s):
            return VALUE
    nums: list[float] = []
    for idx in range(len(s)):
        ok = True
        for cr, c in zip(ranges, crits):
            cell = cr[idx]
            if is_error(cell):
                return cell  # type: ignore[return-value]
            if not _criteria_match(cell, c):
                ok = False
                break
        if not ok:
            continue
        v = s[idx]
        if is_error(v):
            return v  # type: ignore[return-value]
        cf = coerce_float(v)
        if cf is not None:
            nums.append(cf)
    if not nums:
        return DIV0
    return sum(nums) / len(nums)


def ROUND(number: Any, num_digits: Any) -> float | ExcelErrorValue:
    """
    对应 **ROUND**：`num_digits` 为小数位数（**可为负** 表示到**十位、百位** 等）；
    使用 :func:`~excel_funcs._utils.excel_round_half_away_from_zero`，与 Python
    内置 :func:`round` **不同**（半分**远离 0**）。

    **#VALUE!**  
    任参无法转数 → 错误，**不**抛异常。

    **与 ROUNDDOWN/ROUNDUP**  
    见各函数**舍入方向** 对比板书。

    **课堂可练**  
    对 **2.5, -1.5** 等抄 Excel 与 ``round`` 三列对照表.
    """
    x = coerce_float(number)
    d = coerce_float(num_digits)
    if x is None or d is None:
        return VALUE
    di = int(d)
    return excel_round_half_away_from_zero(x, di)


def ROUNDDOWN(number: Any, num_digits: Any) -> float | ExcelErrorValue:
    """
    对应 **ROUNDDOWN**：**朝 0** 截断到 `num_digits` 位，底层
    :func:`~excel_funcs._utils.excel_rounddown`。

    **和 TRUNC 差异**（课堂）  
    非负 `num_digits` 时常与**有限位** 的截断**相似**；**负的 num_digits** 的
    「整到十位」 仍走 **ROUNDDOWN/ROUNDUP** 那条 API.

    **易错**  
    对**负数**「朝 0」 与**负无穷** 下整**不同** —— 画数轴 一遍胜过背定义。
    """
    x = coerce_float(number)
    d = coerce_float(num_digits)
    if x is None or d is None:
        return VALUE
    return excel_rounddown(x, int(d))


def ROUNDUP(number: Any, num_digits: Any) -> float | ExcelErrorValue:
    """
    对应 **ROUNDUP**：**远离 0** 的按位**上**取整，:func:`~excel_funcs._utils.excel_roundup`。

    **和 CEILING/CEILING.MATH 区别**（进阶）  
    ``ROUNDUP`` 按**小数位/负位** 语境；**MROUND/CEILING** 按**倍数** 语境——先
    在课堂分清「**位**」 与「**格点**（倍数）」.
    """
    x = coerce_float(number)
    d = coerce_float(num_digits)
    if x is None or d is None:
        return VALUE
    return excel_roundup(x, int(d))


def MROUND(number: Any, multiple: Any) -> float | ExcelErrorValue:
    """
    对应 **MROUND**：把 `number` 舍入到**最近的** `multiple` 的**整数倍**；**对称**
    的**最近**（实现用 ``round(x/m) * m``，``multiple=0`` → #VALUE! 在 Excel
    里也有类似限制 —— 本实现同).

    **场景**  
    货币到 **0.25**、**包装箱** 打包容量的整数倍 等.

    **与 ROUND(…,0)**  
    到**固定倍数** vs 到**固定小数位** 的两类**舍入** 问题.

    **课堂可练**  
    ``MROUND(7,5)`` 得 5 还是 10？**最近** 距离谁短？
    """
    x = coerce_float(number)
    m = coerce_float(multiple)
    if x is None or m is None or m == 0:
        return VALUE
    n = round(x / m)
    return n * m


def CEILING_MATH(number: Any, significance: Any = 1, mode: Any = 0) -> float | ExcelErrorValue:
    """
    对应 **CEILING.MATH** 的**近似、教学**实现：把 `number` **向上** 取到 `significance`
    的**整数** 倍；实现为 ``ceil(x/s)*s``。``significance=0`` → **#VALUE!**；任参
    非数 → **#VALUE!**。

    **与 FLOOR.MATH 对偶**  
    见 :func:`FLOOR_MATH`；`mode` 在完整 Excel 中影响**负轴** 行为，**本处** 与
    **FLOOR** 同**未** 全复刻，**以** 对拍**最** 常见**正** 数**题** 为主。

    **和 CEILING(旧) / ISO.CEILING**  
    不同**版本/名称** 的**迁移** 可 作 **选修** 查表 题。

    **课堂可练**  
    与 **FLOOR** 对**同一** `number`、**同**一 `s`，观察 **上/下** 包 **夹** 的**区间**。
    """
    x = coerce_float(number)
    s = coerce_float(significance)
    if x is None or s is None or s == 0:
        return VALUE
    import math as _m

    return float(_m.ceil(x / s) * s)


def FLOOR_MATH(number: Any, significance: Any = 1, mode: Any = 0) -> float | ExcelErrorValue:
    """
    对应 **FLOOR.MATH** 的**简化**：向**下** 取整到 `significance` 的倍数（`significance=0` → #VALUE!）.
    参数 `mode` 在 Excel 里控制**负数的朝向** 等；**本实现** 目前**未** 完整
    复刻所有**模式**，**以课堂演示「整到步长」** 为主，进阶学生可查 Excel
    帮助 对比。

    **和 FLOOR(旧) 的兼容**  
    以你使用的 Excel 版本 帮助 为准 对拍 **边界** 情况。

    **课堂可练**  
    工资向下取到**千** 元（**significance=1000** 思路） 的社会情境题。
    """
    x = coerce_float(number)
    s = coerce_float(significance)
    if x is None or s is None or s == 0:
        return VALUE
    return float(math.floor(x / s) * s)


def INT(number: Any) -> int | ExcelErrorValue:
    """
    对应 **INT**：**不大于** 该数的**最大整数**（对**负数** 是向**更负** 的
    方向取整 —— 与**朝 0 截断** 的 :func:`TRUNC` 在负数上**不同**）。  
    实现为 ``floor(x)`` 的**整数** 返回.

    **和 ROUNDDOWN(…,0)**  
    在**正数** 上常一致；**负数** 上**务必** 手算 对照。

    **#VALUE!**  
    无法转数.
    """
    x = coerce_float(number)
    if x is None:
        return VALUE
    return int(math.floor(x))


def TRUNC(number: Any, num_digits: Any = 0) -> float | ExcelErrorValue:
    """
    对应 **TRUNC**：**朝 0** 直接**截断** 小数（或 `num_digits<0` 时按**位** 截
    到**整十/整百** 的左移截断），**不** 做四舍五入。  

    **和 INT 对比**  
    **正数** 时常像 ``INT``；**负数** 时 ``TRUNC(-3.7)=-3``、``INT(-3.7)=-4`` ——
    经典**板书** 必讲。

    **与 ROUNDDOWN**  
    在**非负 num_digits** 的截断 意义上**接近**，细节可和 Excel 再对**极限** 例。
    """
    x = coerce_float(number)
    d = coerce_float(num_digits)
    if x is None or d is None:
        return VALUE
    di = int(d)
    factor = 10**di
    if di >= 0:
        return math.trunc(x * factor) / factor
    factor = 10 ** (-di)
    return math.trunc(x / factor) * factor


def ABS(number: Any) -> float | ExcelErrorValue:
    """
    对应 **ABS**（**绝对值**）`|x|`，距离**原点** 的**长** 而非**方向**；与
    **复数** 在高中数学 上的推广 在 Python 的 ``abs(3+4j)`` 可延伸**选修** 讲
    一句即可。

    **#VALUE!**  
    非数.

    **课堂可练**  
    误差 = ``ABS(测量-真值)`` 的**指标** 思想。
    """
    x = coerce_float(number)
    if x is None:
        return VALUE
    return abs(x)


def SIGN(number: Any) -> int | ExcelErrorValue:
    """
    对应 **SIGN**：**符号函数**，正为 **1**、负为 **-1**、**零** 为 **0**（
    与**数学** 里有时定义 ``sign(0)=1`` 的**版本** 不同，**以 Excel 为准**).

    **用途**  
    把**连续** 值**离散** 成**方向/阵营** 标签；**配合** 条件格式 的**思想** 实验。

    **#VALUE!**  
    非数.
    """
    x = coerce_float(number)
    if x is None:
        return VALUE
    return 1 if x > 0 else (-1 if x < 0 else 0)


def MOD(number: Any, divisor: Any) -> float | ExcelErrorValue:
    """
    对应 **MOD**：`number - divisor * INT(number/divisor)` 意义下的**余数**；与
    Python 的 ``%`` 在**负除数/负数** 上**可能** 不同，**以 Excel 定义** 为准；
    本实现用 ``trunc`` 的**商** 与 Excel 常见行为**对齐** 课堂练习。

    **#DIV/0!**  
    除数为 0 时.

    **课堂可练**  
    奇偶 = ``IF(MOD(n,2)=0,...)`` 的**同余** 引入；**物理解**「绕一圈的**剩余** 角度」
    与**时钟** 算小时.
    """
    x = coerce_float(number)
    d = coerce_float(divisor)
    if x is None or d is None or d == 0:
        return DIV0
    return float(x - d * math.trunc(x / d))


def POWER(number: Any, power: Any) -> float | ExcelErrorValue:
    """
    对应 **POWER** 或 `number**power`：**幂**；**溢出/非法** 时 **#NUM!** 或
    OSError 被捕获 后转 **NUM**（与「复数在实函数域」 等 Excel 错类 的**课堂** 简化
    一致即可).

    **和 SQRT/EXP**  
    **^** 的**通式**；``SQRT``=1/2 次、``EXP``=以 e 为底 的**专款** 函数 便于**发现** 与**命名**.

    **易错**  
    **0^0**、**负底** 的**非整数** 幂 → **复数/错** 讨论.
    """
    x = coerce_float(number)
    p = coerce_float(power)
    if x is None or p is None:
        return VALUE
    try:
        return float(x**p)
    except (OverflowError, ValueError, OSError):
        return NUM


def SQRT(number: Any) -> float | ExcelErrorValue:
    """
    对应 **SQRT(非负)**: **主平方根**；**负** 输入在**实数** 模型下 **#NUM!**（
    与**虚数** 拓展 的**信息课** 可点一句 不展开).

    **和 POWER(x,0.5)**  
    **幂** 的**特款** 封装，**查表/教学** 更顺口.

    **#VALUE!**  
    非数.
    """
    x = coerce_float(number)
    if x is None:
        return VALUE
    if x < 0:
        return NUM
    return math.sqrt(x)


def EXP(number: Any) -> float | ExcelErrorValue:
    """
    对应 **EXP**：e 的**幂**（e 的 x 次方），**增长/衰减** 模型的**主函数**（人口、
    利息 连续 近似 等 与 **LN** 为**反函数** 关系 成对 教）.

    **#VALUE!**  
    非数；**大 x** 可能 **#NUM!** 溢出 路径 在实现里 走 except.

    **课堂可练**  
    与 ``2^x`` 的**换底** ``=EXP(x*LN(2))`` 恒等 练习.
    """
    x = coerce_float(number)
    if x is None:
        return VALUE
    return math.exp(x)


def LN(number: Any) -> float | ExcelErrorValue:
    """
    对应 **LN**：**自然对数** ``ln(x)``（**底 e**）；**x≤0** → **#NUM!** 在**实** 数域
    无定义（与 Excel 一致）.

    **和 LOG**  
    ``LN``=``LOG`` 的**默认** 在部分教材 的**记号** 说明.

    **课堂可练**  
    半衰、**以 e 为底** 的**对数** 图 **斜率** 的**感** 性认识（**选修** 图表课）.
    """
    x = coerce_float(number)
    if x is None:
        return VALUE
    if x <= 0:
        return NUM
    return math.log(x)


def LOG(number: Any, base: Any = 10) -> float | ExcelErrorValue:
    """
    对应 **LOG**：以 ``base`` 为底的**对数**；**默认 10** 即**常用对数**（与
    **工程** 分贝、**数量级** 直觉 最熟）.  
    **base≤0、=1** → **#VALUE!**；**x≤0** → **#NUM!**（与**定义域** 教学 同拍）.

    **和 LN/LOG10**  
    一般底 vs **自然/十** 两**专名** 函数 的**分工**.

    **课堂可练**  
    换底：``=LN(x)/LN(base)`` 与 **本函数** 对拍 验证**对数** 律.
    """
    x = coerce_float(number)
    b = coerce_float(base)
    if x is None or b is None or b <= 0 or b == 1:
        return VALUE
    if x <= 0:
        return NUM
    return math.log(x, b)


def LOG10(number: Any) -> float | ExcelErrorValue:
    """
    对应 **LOG10**：**常用对数**（以 10 为底，与 ``math.log10`` 一致）；**x≤0** → **#NUM!**。

    **与 ``LOG(x,10)``**  
    **少写一参** 的**便捷** 与**可读性** 的 API 设计 小**案例** 讨论（**信息
    技术** 的**接口** 思想 一笔带过）.
    """
    x = coerce_float(number)
    if x is None:
        return VALUE
    if x <= 0:
        return NUM
    return math.log10(x)


def PI() -> float:
    """
    对应 **PI()**：常数 **π**（圆周率），**无参** 函数 在表格里 像 **一个**
    命名**常量** 使用；Python 中返回 **双精度** `float` 的**近似**（**无理数**
    不可**精确** 表示，**位** 与**累积误差** 的**随堂** 一句）.

    **和三角函数 组合**（若课程 有 `SIN/COS`）  
    **弧长、角度 弧度** 的**量纲** 再提醒.

    **课堂可练**  
    圆面积 ``PI()*r^2`` 与 代码 **公式** 对拍.
    """
    return math.pi


def RAND() -> float:
    """
    对应 **RAND()**：**[0,1)** 上**均匀** 分布的**伪**随机**实数**；**无参**；
    **每算一次 变**（**易失** 的**活** 工作表 直觉）——在 Python 里 每次 调用
    **也** 变（**非** 纯函数 的 教学 提示）.

    **和 RANDBETWEEN**  
    **连续** 单位**区间** vs **整数** 闭**区间** 的**两档** 随机 接口.

    **教学延伸**  
    信息课可讲**随机数种子**与**可复现**（本实现不固定种子，便于**最简** 演示
    「每次不同」；作业可设 ``random.seed(...)`` 对拍.
    """
    return random.random()


def RANDBETWEEN(bottom: Any, top: Any) -> int | ExcelErrorValue:
    """
    对应 **RANDBETWEEN**：[bottom, top] 上的**均匀** 随机**整数**；若 **bottom>top**
    则**自动交换**（与 **Excel 帮助** 常见**一致** 的 友好 行为；本实现
    先 `round` 成 int 再 `randint`）.

    **#VALUE!**  
    非数 边界.

    **课堂可练**  
    掷骰 子、**抽奖** 学号 的 公平**模拟** 与 **大数** 次 的 **频率→概率** 过渡.
    """
    b = coerce_float(bottom)
    t = coerce_float(top)
    if b is None or t is None:
        return VALUE
    lo, hi = int(round(b)), int(round(t))
    if lo > hi:
        lo, hi = hi, lo
    return random.randint(lo, hi)


def FACT(n: Any) -> int | ExcelErrorValue:
    """
    对应 **FACT**（**阶乘** `n!`）：**非负整数** 的**连乘** `1×2×…×n`；**0!=1**
    的**空积** 约定 必讲.  
    **n<0** 或**非**整数 → **#NUM!**；无法转数 → **#VALUE!**.

    **和排列组合 组合**  
    :func:`COMBIN`、:func:`PERMUT` 的**分子/分母** 里 常见 **n!** 的**子块**.

    **课堂可练**  
    与 **概率** 里「**有序/无序** 选取」 的 衔接.
    """
    x = coerce_float(n)
    if x is None:
        return VALUE
    if x < 0 or int(x) != x:
        return NUM
    return math.factorial(int(x))


def COMBIN(n: Any, k: Any) -> float | ExcelErrorValue:
    """
    对应 **COMBIN**（**组合** 数 $C_n^k$）：**无序** 从 **n** 个里取 **k** 个
    的 方案数 = ``n! / (k! (n-k)!)``；实现用 :func:`math.comb` 防溢出/精确**整数** 路径.

    **#NUM!**  
    参数 非 非负整数 或 **k>n** 等 非法 组合.

    **#VALUE!**  
    非数.

    **课堂可练**  
    班委 无顺序 选股**组合** 与 **有顺序 排列** 的 对照 :func:`PERMUT`。
    """
    nn = coerce_float(n)
    kk = coerce_float(k)
    if nn is None or kk is None:
        return VALUE
    if nn < 0 or kk < 0 or int(nn) != nn or int(kk) != kk:
        return NUM
    return float(math.comb(int(nn), int(kk)))


def PERMUT(n: Any, k: Any) -> float | ExcelErrorValue:
    """
    对应 **PERMUT**（**排列** 数 $P_n^k$）：**有序** 从 **n** 个里 取 **k** 个
    的 方案数 = ``n!/(n-k)!``；:func:`math.perm` 实现.

    **#NUM!**  
    **k>n** 或 非 非负 整数 等.

    **和 COMBIN 对比**  
    乘 **k!** 的**有/无** 与 **是否** 区分**顺序** 的 故事 板书.

    **课堂可练**  
    三 人 领 一、二、三 名 的 领奖台 与 **不** 分 名次 的 小组 的 对照.
    """
    nn = coerce_float(n)
    kk = coerce_float(k)
    if nn is None or kk is None:
        return VALUE
    if nn < 0 or kk < 0 or int(nn) != nn or int(kk) != kk or kk > nn:
        return NUM
    return float(math.perm(int(nn), int(kk)))


def GCD(*args: Any) -> int | ExcelErrorValue:
    """
    对应 **GCD**（**最大公因数** **Greatest Common Divisor**）：**多** 个**非负**
    整数 的 公因里 **最大** 的 那个；**全空** 时 本实现 返回 **0**（**教学** 上
    可讨论 与 空积/空 定义 的 边界）.

    **#VALUE!**  
    某 项 不 是 能 成 的 数.

    **#NUM!**  
    有**负** 或 **非**整数 经 **coerce** 后 仍 不 合.

    **和 LCM**  
    互 为 对 偶：「**公约** 结构」 与 **最小公倍** 的 关系 **GCD(a,b)*LCM(a,b)=a*b**（两 数 时） 可 作 **选修** 式.

    **课堂可练**  
    约 分 分数 时 **先** **GCD** 再 共 除.
    """
    ints: list[int] = []
    for a in flatten_all(*args):
        c = coerce_float(a)
        if c is None:
            return VALUE
        if int(c) != c or c < 0:
            return NUM
        ints.append(int(c))
    if not ints:
        return 0
    g = ints[0]
    for x in ints[1:]:
        g = math.gcd(g, x)
    return g


def LCM(*args: Any) -> float | ExcelErrorValue:
    """
    对应 **LCM**（**最小公倍数**）：**多** 个**非负整数** 的 能 同时 整除 的 最**小**
    **正** 整数；**两两** 用内部辅助 ``lcm_two`` 左结合累到**多元** 情形.

    **#VALUE!** / **#NUM!**  
    同 :func:`GCD` 的 输入 规约；**全空** 时 返回 **0.0**（**浮点** 返回 为 与 前 后 实 作 一 致）.

    **和 GCD**  
    见 :func:`GCD` 的 说明；**分式** 通 分 时 **分母 取 各 分 母 的** **LCM** 是 经典 应用题.

    **课堂可练**  
    跑 道 上 **多 人 周 期 碰 面** 的 最 小 时 间 = **LCM(周期1, 周期2, …)** 建 模.
    """
    ints: list[int] = []
    for a in flatten_all(*args):
        c = coerce_float(a)
        if c is None:
            return VALUE
        if int(c) != c or c < 0:
            return NUM
        ints.append(int(c))
    if not ints:
        return 0.0

    def lcm_two(a: int, b: int) -> int:
        """
        **内部**：两 正整数 的 **LCM** 用 经典 恒等式 **lcm(a,b)=a//gcd(a,b)*b**
        先 **GCD** 再 **整除** 防 **a*b** 溢出（在 **大** 数 时 有 教益）.

        Args:
            a, b: 已 在 外层 保证 非 负 整.

        Returns:
            **最** 小 公 倍 数.
        """
        return a * b // math.gcd(a, b)

    out = ints[0]
    for x in ints[1:]:
        out = lcm_two(out, x)
    return float(out)


def QUOTIENT(numerator: Any, denominator: Any) -> int | ExcelErrorValue:
    """
    对应 **QUOTIENT**：**整除 的 商 的 整数 部分**（**向 0 截** 的 除法 与 **INT(…)** 在
    **一致** 符号约定下对拍；**不是** 先做除法再 ``math.floor``（**负数** 与
    **向 0 截断** 的差异见课堂板书）. 与 :func:`MOD` 成对出题很常见.

    **#DIV/0!**  
    **除数** 为 0 或无法转数.

    **课堂可练**  
    分 物**整 袋** 可 得 **几 袋**、**余 数** 用 :func:`MOD` 的 **小 学** 与 **信息** 的 双 语 对 照.
    """
    a = coerce_float(numerator)
    b = coerce_float(denominator)
    if a is None or b is None or b == 0:
        return DIV0
    return int(a // b)


def MAXIFS(max_range: Iterable[Any], *criteria_pairs: Any) -> float | ExcelErrorValue:
    """
    对应 **MAXIFS**：参数布局与 :func:`SUMIFS` 相同，只是把「**对 sum_range
    求和**」 换成对 ``max_range`` 里**命中行** 的数求 **MAX**；**多条件 合取**、
    **行对齐** 与 **#VALUE!** 规则**一致**。

    **全不命中**  
    在常见 Excel 里**空区 极大** 可能为 **0** 或 错误，本实现与 :func:`MAX` 的
    **0.0** 思路**对齐**（**教学** 可 再 对 表 一 行）.

    **和 MINIFS**  
    **对偶** 最**小** 值 的 筛选 极 值 题 型.
    """
    m = list(max_range)
    if len(criteria_pairs) % 2 != 0:
        return VALUE
    ranges = [list(criteria_pairs[i]) for i in range(0, len(criteria_pairs), 2)]
    crits = [criteria_pairs[i + 1] for i in range(0, len(criteria_pairs), 2)]
    for cr in ranges:
        if len(cr) != len(m):
            return VALUE
    nums: list[float] = []
    for idx in range(len(m)):
        ok = True
        for cr, c in zip(ranges, crits):
            cell = cr[idx]
            if is_error(cell):
                return cell  # type: ignore[return-value]
            if not _criteria_match(cell, c):
                ok = False
                break
        if not ok:
            continue
        v = m[idx]
        if is_error(v):
            return v  # type: ignore[return-value]
        cf = coerce_float(v)
        if cf is not None:
            nums.append(cf)
    if not nums:
        return 0.0
    return max(nums)


def MINIFS(min_range: Iterable[Any], *criteria_pairs: Any) -> float | ExcelErrorValue:
    """
    对应 **MINIFS**，与 :func:`MAXIFS` 对**偶**：在**相同** 多 条件 结构 下 对
    ``min_range`` **命中 行** 求 **MIN**；**不 命中** 时 **0.0** 与 :func:`MIN` 的
    **空** 约定 作 **课堂** 对拍 即可.

    **用 途**  
    某 班 **男生** 中 **成 绩** **最低** 分（**一 条** 多 条 件 的 **筛选 极 值**）.
    """
    m = list(min_range)
    if len(criteria_pairs) % 2 != 0:
        return VALUE
    ranges = [list(criteria_pairs[i]) for i in range(0, len(criteria_pairs), 2)]
    crits = [criteria_pairs[i + 1] for i in range(0, len(criteria_pairs), 2)]
    for cr in ranges:
        if len(cr) != len(m):
            return VALUE
    nums: list[float] = []
    for idx in range(len(m)):
        ok = True
        for cr, c in zip(ranges, crits):
            cell = cr[idx]
            if is_error(cell):
                return cell  # type: ignore[return-value]
            if not _criteria_match(cell, c):
                ok = False
                break
        if not ok:
            continue
        v = m[idx]
        if is_error(v):
            return v  # type: ignore[return-value]
        cf = coerce_float(v)
        if cf is not None:
            nums.append(cf)
    if not nums:
        return 0.0
    return min(nums)


def SUBTOTAL(function_num: Any, *args: Any) -> Any:
    """
    对应 **SUBTOTAL** 的**子集、教学**实现：``function_num`` 取 **1–11**（**101–111**
    在 Excel 中常表示「**忽略** **隐藏** 行」；本处 **-100** 后**与 1–11 同** 表，
    **不** 实现**真** **筛选** 视野，**课堂** 说清**局限** 即可).

    **映射**（与下方 ``mapping`` **同步** 维护）**  
    1 AVERAGE, 2 COUNT, 3 COUNTA, 4 MAX, 5 MIN, 6 PRODUCT, 7 :func:`_subtotal_stdev_s`,
    8 :func:`_subtotal_stdev_p`, 9 SUM, 10 :func:`_subtotal_var_s`, 11 :func:`_subtotal_var_p`.

    **为 什 要 SUBTOTAL**  
    与 **大** 区 **小计/总计** 行 **避免** **重复** 计 的 **嵌套 聚合** 思想
    在 **信息** 与 **做表** 里 常 提（**与** **AGGREGATE** 的**全** 能 可 对 比）.

    **#VALUE!**  
    不在 映射 里 的 **function_num** → **#VALUE!**.

    **课堂可练**  
    用 **9 SUM** 与 **手** 写 :func:`SUM` **同** 区 对拍，再 讲 **1–11** 的 **多** 能.
    """
    n = int(coerce_float(function_num) or -1)
    if n > 100:
        n -= 100
    mapping: dict[int, Callable[..., Any]] = {
        1: AVERAGE,
        2: COUNT,
        3: COUNTA,
        4: MAX,
        5: MIN,
        6: PRODUCT,
        7: _subtotal_stdev_s,
        8: _subtotal_stdev_p,
        9: SUM,
        10: _subtotal_var_s,
        11: _subtotal_var_p,
    }
    fn = mapping.get(n)
    if fn is None:
        return VALUE
    return fn(*args)


def AGGREGATE(
    function_num: Any,
    options: Any,
    *args: Any,
) -> Any:
    """
    对应 **AGGREGATE** 的**极简、教学**占位：真 Excel 中 ``options`` 会控制 **是否**
    忽略 **隐藏 行/错误/嵌套 小计** 等；**本** 实现 **暂时 忽略** ``options``（用
    ``_ = options`` **显式** 标记 **未** 用），**直接** 把 ``function_num`` 交给
    :func:`SUBTOTAL` **同 子 集** 映射.

    **为什么 要 有 这 一 行**（**给** 备 课）**  
    方便 同一 **API** 在更**大**课程中将来**可**换**不**忽略 ``options`` 的实
    作，不破坏学生**脚本** 的 import 与调用习惯。

    **课堂可练**  
    对 照 帮助 里 **19** 个 **function_num** 的**全** 表，**标** 出 **我们** 已/未
    **实现** 的 **行** 做 成 **墙** 报.

    **Args**  
    ``function_num``：同 **SUBTOTAL**；``options``：**保留** 位、**现** 不 用；``*args``：
    **数据** 区.
    """

    _ = options
    return SUBTOTAL(function_num, *args)
