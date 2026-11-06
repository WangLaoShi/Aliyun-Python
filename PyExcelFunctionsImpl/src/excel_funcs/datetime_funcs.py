"""
Layer 1 — 日期与时间（TODAY、DATE、NETWORKDAYS、EDATE …）
========================================================

**为什么用 ``datetime``，不全程用「序列数」？**  
Python 生态里日期**最自然**的是 ``datetime.date``；序列数只是 Excel 显示与
互操作时的数字。本模块在**需要**与 Excel 数字对拍时提供 ``date_to_serial``、
``_excel_serial_to_date`` 等。

**锚点 1899-12-30**  
与常见库对「Windows Excel 1900 日期系统」的兼容方式一致；**不**在这里完整
复刻「1900 是闰年」的历史 bug，除非函数另有说明。

**NETWORKDAYS / WORKDAY**  
第三个参数「假日」为**可选 list**，传则扣掉这些 date；与区域设置、周末定义
以各函数 docstring 为准。

**新手**  
先会 ``from datetime import date`` 再读本文件；若看到 ``TIME`` 返回带
``1899-12-30`` 的 ``datetime``，是**时间-only** 与旧版 COM 约定混排时的常见折中。
"""

from __future__ import annotations

import calendar
from datetime import date, datetime, timedelta
from typing import Any

from excel_funcs._utils import coerce_float
from excel_funcs.errors import NUM, VALUE, ExcelErrorValue


def _excel_serial_to_date(serial: int) -> date:
    """
    内部**序列号→日历**：在 **1900 日期系统** 下，把 Excel 的**整数**序列
    转成 :class:`datetime.date`。**锚** 为 **1899-12-30**（与 :func:`_date_to_excel_serial`
    **互逆**），不在这里完整复刻「1900 年被当成闰年」的**史** 上 bug，与多数
    **开源/互操作** 库一致，课堂可与**某格** 对拍说明.

    Args:
        serial: 可 ``int`` 的序列（先由调用方**截断/转换**）.

    Returns:
        对应**本地** 日历日.
    """
    # Excel day 1 = 1900-01-01 as serial 1 in Excel - actually Excel thinks 1900 is leap year
    # Simplified: use anchor 1899-12-30 which matches openpyxl convention
    base = date(1899, 12, 30)
    return base + timedelta(days=int(serial))


def _date_to_excel_serial(d: date) -> int:
    """
    内部**日历→序列号**：与 :func:`_excel_serial_to_date` **对偶**；**同一天**
    往返应**一致**（在锚点与截断规则不变前提下）.
    """
    base = date(1899, 12, 30)
    return (d - base).days


def date_to_serial(d: date) -> int:
    """
    将 ``datetime.date`` 转为 Excel 1900 系统序列号（与 ``DATEVALUE`` 解析后一致）。

    说明：锚点采用 1899-12-30，与常见开源库对 Windows Excel 的兼容方式一致。
    """

    return _date_to_excel_serial(d)


def DATE(year: Any, month: Any, day: Any) -> date | ExcelErrorValue:
    """
    对应 **DATE(y,m,d)**：用**年/月/日** 三数合成一个 :class:`date`；非法**日历**
    （如 2 月 30 日）→ :data:`NUM`；**无法** 转整 → :data:`VALUE` 。

    **和 date 构造**  
    即 ``datetime.date(int(y),int(m),int(d))`` 的**教学** 封装，**表** 里**三** 格
    填数**常** 用.

    **课堂可练**  
    输入 **13 月** 或**闰** 年 **2 月 29** 的**合法/非法** 对拍.
    """
    try:
        y = int(year)
        m = int(month)
        da = int(day)
    except (TypeError, ValueError):
        return VALUE
    try:
        return date(y, m, da)
    except ValueError:
        return NUM


def TIME(hour: Any, minute: Any, second: Any) -> datetime | ExcelErrorValue:
    """
    对应 **TIME**：**仅** 时间分量，**无** 独立「日期**部分**」 时，用**旧**约定
    把日期钉在 **1899-12-30** 上组成 ``datetime``，只**为** 在 Python 中**有**
    一个**可** 存**时间** 的**对象**；**与** **TIMEVALUE** 的**小数** 天**对** 照
    教学.

    各分量**带** 取模 到 合法**时** 分**秒**；**非** 数 → **#VALUE!** 。
    """
    h = coerce_float(hour)
    mi = coerce_float(minute)
    s = coerce_float(second)
    if h is None or mi is None or s is None:
        return VALUE
    try:
        return datetime(1899, 12, 30, int(h) % 24, int(mi) % 60, int(s) % 60)
    except ValueError:
        return NUM


def TODAY() -> date:
    """
    对应 **TODAY()**：**无参**，返回**本机** **今天** 的**日期**（**不含** 时间**）；
    每次**调用** 在**你** 运行 的那**一刻** 取**系** 统** 日期** 与**表** 里
    **F9**/重算 行为**对** 照** 讨论.

    **与 NOW 对比**  
    :func:`NOW` 含**时** 分**秒** 。
    """
    return date.today()


def NOW() -> datetime:
    """
    对应 **NOW()**：**无参**，**当前** **日期+时间**（**本机** 时**区/夏令时** 依
    **系** 统** 设置**；**不** 做 **UTC** 教学**时** 可**在** 课**上** 点一句）.
    """
    return datetime.now()


def YEAR(serial: Any) -> int | ExcelErrorValue:
    """
    对应 **YEAR**：从 **date/datetime** 或**序列** 数取**年** 份**四位** 数.

    若为**浮** 点**序列**（**含** **时间** **小数**），**先** 取**整** **日** 部**分**
    再 :func:`_excel_serial_to_date` ；**不** 能**转** → #VALUE! 。
    """
    if isinstance(serial, datetime):
        return serial.year
    if isinstance(serial, date):
        return serial.year
    x = coerce_float(serial)
    if x is None:
        return VALUE
    d = _excel_serial_to_date(int(x))
    return d.year


def MONTH(serial: Any) -> int | ExcelErrorValue:
    """
    对应 **MONTH**（返回 1–12）**：规则同 :func:`YEAR`，取**月份** 整数.
    """
    if isinstance(serial, datetime):
        return serial.month
    if isinstance(serial, date):
        return serial.month
    x = coerce_float(serial)
    if x is None:
        return VALUE
    return _excel_serial_to_date(int(x)).month


def DAY(serial: Any) -> int | ExcelErrorValue:
    """
    对应 **DAY**（**一** 月**内** **的** 日**号，1–31）**：**同** :func:`YEAR` 的
    **多** 态** 入参.
    """
    if isinstance(serial, datetime):
        return serial.day
    if isinstance(serial, date):
        return serial.day
    x = coerce_float(serial)
    if x is None:
        return VALUE
    return _excel_serial_to_date(int(x)).day


def HOUR(serial: Any) -> int | ExcelErrorValue:
    """
    对应 **HOUR**：**datetime** 直**接** 取**时** ；**纯** 序列**数** 则**取** **小数** **部** **分**
    为**一** 天**内** **的** **秒** **再** **折** 成 **0–23** 的**时** 。

    **与** 表** 里** **时间** **小** 数** 解释** 一**致** ；**#VALUE!** 非**数** 。
    """
    if isinstance(serial, datetime):
        return serial.hour
    x = coerce_float(serial)
    if x is None:
        return VALUE
    # 小数天：一天内的秒
    frac = x - int(x)
    secs = int(round(frac * 86400))
    return (secs // 3600) % 24


def MINUTE(serial: Any) -> int | ExcelErrorValue:
    """
    对应 **MINUTE**（0–59）**：**同** :func:`HOUR` 的**序列** 小**数** 析**取** **逻辑** 。
    """
    if isinstance(serial, datetime):
        return serial.minute
    x = coerce_float(serial)
    if x is None:
        return VALUE
    frac = x - int(x)
    secs = int(round(frac * 86400))
    return (secs // 60) % 60


def SECOND(serial: Any) -> int | ExcelErrorValue:
    """
    对应 **SECOND**（0–59）**：**同** :func:`HOUR` 的**小数** 天**的** 秒** 取** 余.
    """
    if isinstance(serial, datetime):
        return serial.second
    x = coerce_float(serial)
    if x is None:
        return VALUE
    frac = x - int(x)
    secs = int(round(frac * 86400))
    return secs % 60


def EDATE(start_date: Any, months: Any) -> date | ExcelErrorValue:
    """
    对应 **EDATE**：在起始日期上**加/减** 若干**整** 月，**尽量** 保持**同一日号**；若
    目标月**没有** 该日（如 1/31 加一个月），则**退** 到**月末**（见
    :func:`calendar.monthrange` 与 ``min(原日, 末天)`` 在代码里）.

    可接受 ``date``/``datetime``/序列**整数** ；非法返 **#VALUE!** 或 **#NUM!** 。
    """
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if not isinstance(start_date, date):
        x = coerce_float(start_date)
        if x is None:
            return VALUE
        start_date = _excel_serial_to_date(int(x))
    m = coerce_float(months)
    if m is None:
        return VALUE
    mi = int(m)
    y = start_date.year * 12 + start_date.month - 1 + mi
    ny, nm = divmod(y, 12)
    nm += 1
    last = calendar.monthrange(ny, nm)[1]
    d = min(start_date.day, last)
    try:
        return date(ny, nm, d)
    except ValueError:
        return NUM


def EOMONTH(start_date: Any, months: Any) -> date | ExcelErrorValue:
    """
    对应 **EOMONTH**：**先** :func:`EDATE` 平**移** 到**目标** 月，**再** 取**该** **月** **最** **后** **一** **天** 。

    **用** 途**  
    账**期** 截**止** 日、**月** 末** 报** 表** 日** 等** 。
    """
    d0 = EDATE(start_date, months)
    if isinstance(d0, ExcelErrorValue):
        return d0
    last = calendar.monthrange(d0.year, d0.month)[1]
    return date(d0.year, d0.month, last)


def WEEKDAY(serial_date: Any, return_type: Any = 1) -> int | ExcelErrorValue:
    """
    对应 **WEEKDAY**：**星期** 的**编号** 依 ``return_type`` 不同（**1**=日**一**=1…
    常**见** 等**多种** 教材**表**）：本实现**把** :func:`date.weekday` 的
    **周** 一=0 映**到** 帮助**里** 常**见** 的**几** 种** 编号** 。

    **#VALUE!**  
    **不** 能**得** 到**有** 效** 日** 的** 输入** 。

    **行** 内** 注** 释** 与** 各 **rt** **分** 支** 请** 对**照** 源** 码** 讲** 板** 书.
    """
    if isinstance(serial_date, datetime):
        wd = serial_date.weekday()  # Mon=0
    elif isinstance(serial_date, date):
        wd = serial_date.weekday()
    else:
        x = coerce_float(serial_date)
        if x is None:
            return VALUE
        wd = _excel_serial_to_date(int(x)).weekday()
    rt = int(return_type) if coerce_float(return_type) is not None else 1
    # Excel: Sun=1..Sat=7 for return_type 1
    if rt == 1:
        return (wd + 2) % 7 or 7
    if rt == 2:
        return wd + 1
    if rt == 3:
        # Excel：周一=0 …… 周日=6（与 Python weekday 一致）
        return wd
    return (wd + 2) % 7 or 7


def ISOWEEKNUM(date_value: Any) -> int | ExcelErrorValue:
    """
    对应 **ISOWEEKNUM**：**ISO** **周** **序** 号**（1–53 依** 年**）**，** 用
    ``date.isocalendar()[1]`` ；**一** 年**第** 一**周** 的**定** 义** 与** **ISO
    周** 一** 起** 的** 规** 则** 一** 致** 。

    **#VALUE!**  
    **不** 能**转** 成** 日** 的** 值** 。
    """
    if isinstance(date_value, datetime):
        d = date_value.date()
    elif isinstance(date_value, date):
        d = date_value
    else:
        x = coerce_float(date_value)
        if x is None:
            return VALUE
        d = _excel_serial_to_date(int(x))
    iso = d.isocalendar()
    return int(iso[1])


def DATEVALUE(date_text: Any) -> int | ExcelErrorValue:
    """
    对应 **DATEVALUE**：**把** 若**干** 常**见** 格** 式** 的** 文** 本** 日** 期** 解** 析
    成** **Excel** **序** 列** 号**（**与** :func:`_date_to_excel_serial` **一** 致** ）** 。

    **不** 能**解** 则 **#VALUE!** 。**列** 表** 里** 的 **fmt** **可** **课** 上** 扩** 。
    """
    s = str(date_text).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(s, fmt)
            return _date_to_excel_serial(dt.date())
        except ValueError:
            continue
    return VALUE


def TIMEVALUE(time_text: Any) -> float | ExcelErrorValue:
    """
    对应 **TIMEVALUE**：**只** 时**间** 文** 本** 转** 成** **0–1** **的** **小** 数** **天**（**一** 天** 的** 比** 例** ）**，** 与**
    :func:`HOUR` 等** 从** **小** 数** 天** **析** 取** 为** 对** 偶** 。

    **#VALUE!** **解** 不** 出** 。
    """
    s = str(time_text).strip()
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            t = datetime.strptime(s, fmt)
            return (t.hour * 3600 + t.minute * 60 + t.second) / 86400.0
        except ValueError:
            continue
    return VALUE


def NETWORKDAYS(start_date: Any, end_date: Any, holidays: list[Any] | None = None) -> int | ExcelErrorValue:
    """
    对应 **NETWORKDAYS**：**起** **止** 日** 之** **间**（**含** **端** **点**）**的** **工** **作** **日** **天** **数**，
    **周** 末** 六** **日** **不** **计**（**不** 含** 区** 域** **「** 周** **末** 是** 周** 五** 六** 」** 的** 完** 整** 复** 刻**）** ；**holidays** **列** 表** 里** 的** 日** **也** **扣** **掉** 。

    **起** **止** **反** 了** 会** **自** 动** **调** 换** 。

    **内** 部 **``_to_date``** **：** **统** 一** 把** **各** 种** 入** 参** 变** 成** **date** **或** **错** 。
    """
    def _to_date(x: Any) -> date | ExcelErrorValue:
        """**单** 实参 转 **date** 或 **#VALUE!**；与 :func:`WORKDAY` 内同名辅助逻辑一致（闭包不共享）。"""
        if isinstance(x, datetime):
            return x.date()
        if isinstance(x, date):
            return x
        cf = coerce_float(x)
        if cf is None:
            return VALUE
        return _excel_serial_to_date(int(cf))

    a = _to_date(start_date)
    b = _to_date(end_date)
    if isinstance(a, ExcelErrorValue) or isinstance(b, ExcelErrorValue):
        return a if isinstance(a, ExcelErrorValue) else b
    if a > b:
        a, b = b, a
    hol = set()
    if holidays:
        for h in holidays:
            dh = _to_date(h)
            if isinstance(dh, date):
                hol.add(dh)
    n = 0
    cur = a
    while cur <= b:
        if cur.weekday() < 5 and cur not in hol:
            n += 1
        cur += timedelta(days=1)
    return n


def WORKDAY(start_date: Any, days: Any, holidays: list[Any] | None = None) -> date | ExcelErrorValue:
    """
    对应 **WORKDAY**：从**起始** 日起**数** 第 n 个**工作日**（n 为负则**向过去** 数）；
    **周末** 与 **holidays** 约定同 :func:`NETWORKDAYS` 的「周一到周五、排除假日」.

    起点或天数非法 → #VALUE! 等见实现。
    """
    def _to_date(x: Any) -> date | ExcelErrorValue:
        """**单** 实参 转 **date** 或 **#VALUE!**；与 :func:`NETWORKDAYS` 内同名**逻辑** 一致（各自闭包）。"""
        if isinstance(x, datetime):
            return x.date()
        if isinstance(x, date):
            return x
        cf = coerce_float(x)
        if cf is None:
            return VALUE
        return _excel_serial_to_date(int(cf))

    d0 = _to_date(start_date)
    nd = coerce_float(days)
    if isinstance(d0, ExcelErrorValue) or nd is None:
        return d0 if isinstance(d0, ExcelErrorValue) else VALUE
    n = int(nd)
    hol = set()
    if holidays:
        for h in holidays:
            dh = _to_date(h)
            if isinstance(dh, date):
                hol.add(dh)
    step = 1 if n >= 0 else -1
    cur = d0
    left = abs(n)
    while left > 0:
        cur += timedelta(days=step)
        if cur.weekday() < 5 and cur not in hol:
            left -= 1
    return cur


def WEEKNUM(serial_date: Any, return_type: Any = 1) -> int | ExcelErrorValue:
    """
    对应 **WEEKNUM** 的**教学** 简化：``return_type=21`` 时**委托** :func:`ISOWEEKNUM`；
    **其** 他** 值** **当** 前** 简** 化** 为** **也** 调** **ISOWEEKNUM**（**与** **全** **部** **Excel** **回** **合** 类** 型** **未** 完** 全** 一** 致** **，** 板** 书** 标** 明** **「** 简** 化** 」** ）** 。

    **进** 阶** **可** **按** 帮** 助** **的** 周** 起** 始** 规** 则** 补** 全** 。
    """
    rt = int(return_type) if coerce_float(return_type) is not None else 1
    if rt == 21:
        return ISOWEEKNUM(serial_date)
    return ISOWEEKNUM(serial_date)


def DATEDIF(start_date: Any, end_date: Any, unit: Any) -> int | ExcelErrorValue:
    """
    对应 **DATEDIF**（**年** 资** 等** 常** 用**）：**单** 位 **Y/M/D** 的** 简** 化** 实** 现** ；
    **起** 止** 反** 了** 会** **对** 调** 后** 再** **算**；**Y**=**整** **年** **差** **、** **M**=**月** **差** **、** **D**=**日** **差** 。

    **不** 支** 持** 的** 单** 位** → **#VALUE!** 。**学** 生** 应** 与** 帮** 助** 里** 其** 他** 单** 位** 的** 完** 整** 表** 对** 照** 。

    **内** 部 **``_to_date``** **：** **同** 上.
    """

    def _to_date(x: Any) -> date | ExcelErrorValue:
        """**将** 入** 参** **合** 一** 为** **date** **或** **#VALUE!** 。"""
        if isinstance(x, datetime):
            return x.date()
        if isinstance(x, date):
            return x
        cf = coerce_float(x)
        if cf is None:
            return VALUE
        return _excel_serial_to_date(int(cf))

    a = _to_date(start_date)
    b = _to_date(end_date)
    if isinstance(a, ExcelErrorValue) or isinstance(b, ExcelErrorValue):
        return a if isinstance(a, ExcelErrorValue) else b
    u = str(unit).upper()
    if a > b:
        a, b = b, a
    if u == "D":
        return (b - a).days
    if u == "M":
        return (b.year - a.year) * 12 + (b.month - a.month)
    if u == "Y":
        y = b.year - a.year
        if (b.month, b.day) < (a.month, a.day):
            y -= 1
        return y
    return VALUE
