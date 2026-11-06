"""
Layer 1 — 财务函数：PV、FV、PMT、NPV、IRR、XNPV、XIRR 等
========================================================

**公式的参数习惯**（新手务必读）  
Excel 的 ``rate`` 通常和 ``nper`` **同一周期**：月付就用**月利率**和**月数**；
年付就用**年利率**和**年数**。混用年利 12% 和「月数=60」却不除 12，会得到
天文数字一样的结果——**这不是 bug，是量纲没对齐**。

**现金流符号**（Excel 同）  
借入本金常为正、还款现金流常为负，或整反；只要**一套约定自洽**，现值/IRR
的相对关系可对。和 Excel 对拍时，请用**同一组数**在表里验一条。

**迭代函数**（``RATE``、``IRR``、``XIRR``）  
使用牛顿/类似迭代，**初值**、**不收敛**时可能得 ``#NUM!``，与表软件在病态
数据上也可能不一致。

**本文件内**  
各函数在 docstring 中写清**输入输出含义**；行内注释标出 0 利率退化分支、奇点。
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from excel_funcs._utils import coerce_float
from excel_funcs.errors import NUM, VALUE, ExcelErrorValue


def PV(
    rate: Any,
    nper: Any,
    pmt: Any,
    fv: Any = 0,
    type_: Any = 0,
) -> float | ExcelErrorValue:
    """
    对应 **PV**（**Present Value / 现值**）：在已知每期利率、期数、年金支付、
    终值与**期初/期末付**约定下，求**期初**那一笔**等价现值**（现金流符号
    与 Excel 帮助一致，教学时需强调「借入/还款谁为正」一套约定要自洽）。

    **参数**  
    - ``rate``：每期利率，与 ``nper`` 同周期（年利率+年数，或月利率+月数）。  
    - ``nper``：总期数。  
    - ``pmt``：每期支付（年金）；可为负表示流出。  
    - ``fv``：第 ``nper`` 期**之后**的终值，缺省 0。  
    - ``type_``：0=期末付（**普通年金**），1=**期初付**（**即付年金**）。

    **0 利率退化**  
    若 ``r==0``，本实现用线性累加，与表软件在退化情形一致，避免 0/0。

    **返回**  
    成功为 ``float``；任一数无法转为浮点则 ``#VALUE!``。

    **课堂可练**  
    用同一组参数在 Excel 的 ``=PV`` 对拍，再改 ``type_`` 观察现值如何变。
    """

    r = coerce_float(rate)
    n = coerce_float(nper)
    p = coerce_float(pmt)
    f = coerce_float(fv)
    t = int(coerce_float(type_) or 0)  # 0=期末付，1=期初付
    if r is None or n is None or p is None or f is None:
        return VALUE
    if r == 0:
        # 无利息：现值=现金流简单加总（与 Excel 退化一致）
        return -(p * n + f)
    # 一般情形：标准年金现值公式的变体
    pv = (-p * (1 + r * t) * ((1 + r) ** n - 1) / r - f) / (1 + r) ** n
    return float(pv)


def FV(
    rate: Any,
    nper: Any,
    pmt: Any,
    pv: Any = 0,
    type_: Any = 0,
) -> float | ExcelErrorValue:
    """
    对应 **FV**（**Future Value / 终值**）：由**现值**、定期 **PMT**、利率与
    期数推第 ``nper`` 期**末**（或即付年金的等价时点）的**终值**。

    **和 PV 的逆关系**  
    在数学上，同一组符号约定下 ``PV``/``FV``/``PMT``/``NPER``/``RATE`` 是联立的；
    教学上建议用**现金流图**把箭头画清楚再敲公式。

    **0 利率**  
    无利时，终值=现值+期数×年金（在代码里单独分支，避免用 ``(1+r)^n`` 的 0/0).

    **易错**  
    ``rate``/``nper`` **量纲**混用是新手第一大坑，错误结果往往「大得离谱」。

    **课堂可练**  
    设月存 100、月利 0.1%，60 期后有多少；与心算 6000+ 利息对比，体会复利增长。
    """

    r = coerce_float(rate)
    n = coerce_float(nper)
    p = coerce_float(pmt)
    present = coerce_float(pv)
    t = int(coerce_float(type_) or 0)
    if r is None or n is None or p is None or present is None:
        return VALUE
    if r == 0:
        return float(-(present + p * n))
    fv = -present * (1 + r) ** n - p * (1 + r * t) * ((1 + r) ** n - 1) / r
    return float(fv)


def PMT(
    rate: Any,
    nper: Any,
    pv: Any,
    fv: Any = 0,
    type_: Any = 0,
) -> float | ExcelErrorValue:
    """
    对应 **PMT**：在利率、期数、现值、终值与期初/期末付给定下，求**使等式成立**
    的**每期**均匀支付（**年金**的一期额）。

    **典型故事**  
    房贷/车贷：知道借多少（|pv|）、还几期、利率，求「每期还多少」。

    **符号**  
    若你约定「借入 pv 为正」，则**还款**的 ``pmt`` 在 Excel 里常为**负**；本
    实现按标准年金公式，与 Excel 对拍时**用同一组正负**。

    **0 利率**  
    平均摊还无利息时，返回 ``-(pv+fv)/nper`` 形态（见实现）。

    **课堂可练**  
    用 **Goal Seek** 思想：在表里反推，再和 ``PMT`` 结果对拍。
    """

    r = coerce_float(rate)
    n = coerce_float(nper)
    p = coerce_float(pv)
    f = coerce_float(fv)
    t = int(coerce_float(type_) or 0)
    if r is None or n is None or p is None or f is None:
        return VALUE
    if r == 0:
        return float(-(p + f) / n)
    q = (1 + r) ** n
    return float(-(p * q + f) * r / ((1 + r * t) * (q - 1)))


def NPER(
    rate: Any,
    pmt: Any,
    pv: Any,
    fv: Any = 0,
    type_: Any = 0,
) -> float | ExcelErrorValue:
    """
    对应 **NPER**：在已知**每期**利率、**每期**支付、现值/终值与期初/期末付时，
    求**需要多少期**才还清/达到终值。即「还完债要几个月」的函数。

    **0 利率**  
    若 ``r=0`` 且 ``pmt=0``，无法定周期，本实现返回 ``#NUM!``；若 ``pmt`` 非 0
    用线性式 ``-(pv+fv)/pmt``。

    **对数**  
    非零利率用 ``log`` 解指数方程；病态参数可能 ``#NUM!``。

    **教学**  
    让学生先**手算**一年两期的极简例子，再跑 ``NPER`` 建立信心。

    Returns:
        期数，可为**非**整数在 Excel 里也有，这里返回 ``float``。
    """
    r = coerce_float(rate)
    p = coerce_float(pmt)
    present = coerce_float(pv)
    f = coerce_float(fv)
    t = int(coerce_float(type_) or 0)
    if r is None or p is None or present is None or f is None:
        return VALUE
    if r == 0:
        if p == 0:
            return NUM
        return float(-(present + f) / p)
    try:
        import math

        num = p * (1 + r * t) - f * r
        den = present * r + p * (1 + r * t)
        if num == 0 or den == 0:
            return NUM
        val = math.log(num / den) / math.log(1 + r)
        return float(val)
    except (ValueError, ZeroDivisionError):
        return NUM


def RATE(
    nper: Any,
    pmt: Any,
    pv: Any,
    fv: Any = 0,
    type_: Any = 0,
    guess: Any = 0.1,
) -> float | ExcelErrorValue:
    """
    对应 **RATE**：在其它参数已知时，**反解**出使年金方程成立的**每期**内部
    利率。没有闭式，迭代（本实现**牛顿法**到收敛或失败）。

    **``guess``**  
    初值，缺省 0.1（10%）；多解或病态时可能不收敛，返回 ``#NUM!``。

    **和 IRR**  
    概念相关：``RATE`` 更偏「等额分期」的**单期**折现率；``IRR`` 是**一列
    非等额**现金流的**同一**折现率使 NPV=0。课堂可画对比表。

    **小 ``r`` 奇点**  
    实现里对 ``r`` 过小作地板，避免分母 0，仍可能在极端数上失败（见 **NUM!**).

    **课堂可练**  
    用已知利率反造 ``PV``/``PMT``，再 ``RATE`` 应能**收回**原利率，验代码。
    """
    n = coerce_float(nper)
    p = coerce_float(pmt)
    present = coerce_float(pv)
    f = coerce_float(fv)
    g = coerce_float(guess)
    t = int(coerce_float(type_) or 0)
    if n is None or p is None or present is None or f is None or g is None:
        return VALUE
    r = g
    for _ in range(100):
        if abs(r) < 1e-12:
            r = 1e-12
        q = (1 + r) ** n
        dr = n * (1 + r) ** (n - 1)
        num = present * q + p * (1 + r * t) * (q - 1) / r + f
        dnum = (
            present * dr
            + p
            * (
                t * (q - 1) / r
                + (1 + r * t) * (dr / r - (q - 1) / (r * r))
            )
        )
        if dnum == 0:
            break
        r_new = r - num / dnum
        if abs(r_new - r) < 1e-8:
            return float(r_new)
        r = r_new
    return NUM


def IPMT(
    rate: Any,
    per: Any,
    nper: Any,
    pv: Any,
    fv: Any = 0,
    type_: Any = 0,
) -> float | ExcelErrorValue:
    """
    对应 **IPMT**（**某期**应付**利息**部分）的**教学向简化实现**：

    先求整段 **PMT**，再从第 1 期滚到第 ``per-1`` 期的**余额**，第 ``per`` 期
    利息=余额×利率。这是**标准摊还**思路的直观版；与 Excel 在边界/即付/舍入
    上**可能有微小差**，以课堂「看懂现金流滚动」为主。

    **``per``**  
    1 基索引；越界时 ``#VALUE!``。若 ``PMT``/中间步出错则冒泡该错误。

    **和 PPMT**  
    一期还款 = 利息 + 本金，``PPMT = PMT - IPMT``（在合法期内）。

    **课堂可练**  
    用 Excel 展开前 3 期**分期表**，手工核对 ``IPMT``/``PPMT``/余额。
    """
    r = coerce_float(rate)
    k = coerce_float(per)
    n = coerce_float(nper)
    p = coerce_float(pv)
    f = coerce_float(fv)
    if None in (r, k, n, p, f) or k < 1 or k > n:
        return VALUE
    pay = PMT(r, n, p, f, type_)
    if isinstance(pay, ExcelErrorValue):
        return pay
    bal = p
    for period in range(1, int(k)):
        interest = bal * r
        principal = pay - interest
        bal -= principal
    return float(bal * r)


def PPMT(
    rate: Any,
    per: Any,
    nper: Any,
    pv: Any,
    fv: Any = 0,
    type_: Any = 0,
) -> float | ExcelErrorValue:
    """
    对应 **PPMT**：**第** ``per`` 期**本金**偿还部分。本实现为 **PMT − IPMT**。

    依赖 :func:`PMT` 与 :func:`IPMT` 的一致性；任一方返回错误则**优先**把错误
    传回（与链式公式的可观察行为类似）。

    **教学**  
    让学生理解「**前期**利息多、本金少，后期反过来」的**原因**是余额在变。

    Returns:
        该期本金为 ``float``；或 ``#VALUE!`` 等。
    """
    r = coerce_float(rate)
    k = coerce_float(per)
    n = coerce_float(nper)
    p = coerce_float(pv)
    f = coerce_float(fv)
    if None in (r, k, n, p, f):
        return VALUE
    pay = PMT(r, n, p, f, type_)
    ip = IPMT(r, k, n, p, f, type_)
    if isinstance(pay, ExcelErrorValue) or isinstance(ip, ExcelErrorValue):
        return pay if isinstance(pay, ExcelErrorValue) else ip  # type: ignore[return-value]
    return float(pay - ip)


def NPV(rate: Any, *values: Any) -> float | ExcelErrorValue:
    """
    对应 **NPV**（**净现值**）：给定**各期现金流**与**每期的折现率** ``rate``，
    用标准教科书公式**从第 1 期**起折现到第 0 期（**注意**与 Excel 帮助里
    是否含第 0 期投资的约定，教学时要读帮助并对拍）。

    **本实现**  
    ``values[0]`` 折到 ``(1+r)^1`` 分母，依此类推，即 N 个现金流从 **i=1** 到 **N**。

    **和 XNPV**  
    这里假设**等间隔**；**不等间隔、真实日历**用 :func:`XNPV`。

    **课堂可练**  
    手算 3 期现金流、折现，再和 ``NPV`` 对拍，建立**折现因子**的直觉。

    **错误**  
    任一格不能转数 → ``#VALUE!``；``rate`` 不合法同。
    """
    r = coerce_float(rate)
    if r is None:
        return VALUE
    total = 0.0
    for i, v in enumerate(values):
        c = coerce_float(v)
        if c is None:
            return VALUE
        total += c / (1 + r) ** (i + 1)
    return float(total)


def IRR(values: Any, guess: Any = 0.1) -> float | ExcelErrorValue:
    """
    对应 **IRR**（**内部收益率**）：找使 **NPV=0** 的折现率 ``r``，现金流为
    **一列**（通常含初始投资为负、后续为正的收益）。本实现**牛顿迭代**在导数
    上更新 ``r``。

    **前题**  
    至少两期、均可转数；含 ``#VALUE!`` 的格子在这里用 ``coerce_float``，失败
    整段 ``#VALUE!``。

    **不收敛**  
    多解、无解、平直线附近 → 若干步后可能 ``#NUM!``；与表软件在病态例上
    **可不一致**，课堂说明「数值」与「经济含义多解」。

    **和 RATE 对比**  
    见 :func:`RATE` 的说明：现金流形状不同。

    **课堂可练**  
    让学生构造「先花 1000，后收 500、600」的列表，**手画** NPV-利率 曲线斜率
    直觉，再跑 ``IRR``。
    """
    if not isinstance(values, (list, tuple)) or len(values) < 2:
        return VALUE
    cfs = [coerce_float(x) for x in values]
    if any(x is None for x in cfs):
        return VALUE
    cfs_f = [float(x) for x in cfs]  # type: ignore[list-item]
    r = coerce_float(guess) or 0.1
    if r is None:
        return VALUE
    for _ in range(100):
        npv = sum(cf / (1 + r) ** i for i, cf in enumerate(cfs_f))
        # NPV'(r) = sum_i -i * cf_i / (1+r)^(i+1)；i=0 项为 0
        dnpv = sum(-i * cf / (1 + r) ** (i + 1) for i, cf in enumerate(cfs_f))
        if dnpv == 0:
            break
        r_new = r - npv / dnpv
        if abs(r_new - r) < 1e-8:
            return float(r_new)
        r = r_new
    return NUM


def XNPV(rate: Any, values: Any, dates: Any) -> float | ExcelErrorValue:
    """
    对应 **XNPV**：在**不**等间隔的**真实日期**上，以**年**为单位的折现率
    ``rate``（实现里用 ``(days/365)`` 指数，与简化的「一年=365 天」**一致
    于常见教学代码**；与 365/366、Excel 的基准日**可能有细微**差）。

    **``dates[0]`` 为**锚**  
    每个现金流用与第一日期的**天数差**折现，故整体平移**不改变** NPV 的
    相对值（在 ``r`` 固定时）。

    **与 NPV 区别**  
    不等时间间隔、真实项目里程碑 → 用 XNPV；等间隔、每期长度相同 → 教学可先用
    NPV。

    **错误**  
    长度不对、非 ``date``/``datetime``、不可转数 → ``#VALUE!``。

    **课堂可练**  
    用同一三笔现金，**人为改**中间一期的日子，看 NPV 比「等距」时如何变。
    """
    r = coerce_float(rate)
    if r is None or not isinstance(values, (list, tuple)) or not isinstance(dates, (list, tuple)):
        return VALUE
    if len(values) != len(dates):
        return VALUE
    d0 = dates[0]
    if isinstance(d0, datetime):
        d0 = d0.date()
    elif not isinstance(d0, date):
        return VALUE
    total = 0.0
    for v, d in zip(values, dates):
        cf = coerce_float(v)
        if cf is None:
            return VALUE
        if isinstance(d, datetime):
            dd = d.date()
        elif isinstance(d, date):
            dd = d
        else:
            return VALUE
        days = (dd - d0).days
        total += cf / (1 + r) ** (days / 365.0)
    return float(total)


def XIRR(values: Any, dates: Any, guess: Any = 0.1) -> float | ExcelErrorValue:
    """
    对应 **XIRR**：在带**真实日期**的现金流上，求使**折现和为 0** 的**年**
    内部收益率。本实现为 :func:`XNPV` 对 ``r`` 的导数+牛顿**简化版**。

    **和 IRR**  
    形状相同；这里时间轴用**年分数**（距第一日的天数/365.0）而非 1,2,3 期号。

    **不收敛**  
    同 ``IRR`` 的病态讨论；多解时初值可影响落到哪个解。

    **课堂可练**  
    与 Excel 的 ``=XIRR`` 用**同一**两列，检查差异来源（年基数、闰年、第一日
    的基准）。

    Returns:
        内部收益率的 ``float`` 估计；或 ``#VALUE!``/``#NUM!``。
    """
    r = coerce_float(guess) or 0.1
    if not isinstance(values, (list, tuple)) or not isinstance(dates, (list, tuple)):
        return VALUE
    d0 = dates[0]
    if isinstance(d0, datetime):
        d0 = d0.date()
    elif not isinstance(d0, date):
        return VALUE
    cfs = []
    for v, d in zip(values, dates):
        cf = coerce_float(v)
        if cf is None:
            return VALUE
        if isinstance(d, datetime):
            dd = d.date()
        elif isinstance(d, date):
            dd = d
        else:
            return VALUE
        cfs.append((cf, (dd - d0).days / 365.0))
    for _ in range(100):
        npv = sum(cf / (1 + r) ** t for cf, t in cfs)
        dnpv = sum(-t * cf / (1 + r) ** (t + 1) for cf, t in cfs)
        if dnpv == 0:
            break
        r_new = r - npv / dnpv
        if abs(r_new - r) < 1e-8:
            return float(r_new)
        r = r_new
    return NUM
