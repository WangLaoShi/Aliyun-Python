"""
Layer 2 — 按「Excel 功能区」分类的 Facade（外观）类
====================================================

**新手理解**：  
Layer1 里函数是「散」在各文件里的，例如 ``math_agg.SUM``、``text.LEFT``。
这里是**按主题归类**，用类把函数「挂名」在属性上，方便：

- ``ExcelFunctions().math.sum`` 点出来的一串方法都在「数学/统计」一类；
- 方法名用 **小写+下划线**（Python 正常风格），**不等同** Excel 里的大写
  函数名——对应关系见各类下面的注释。

**@staticmethod 是什么？**  
表示「这方法不需要某个对象的专属状态」，只借用**类作命名空间**。
数学上仍是非面向对象的一等函数，只是**收纳**在 ``MathFuncs`` 里。

**import 名 ``xf_text``**  
因 ``TextFuncs`` 里需要绑 Excel 的 ``TEXT`` 函数，而模块名 ``text`` 会
在类体里和属性名冲突，故用 ``import excel_funcs.text as xf_text``。

**阅读顺序**  
与 :mod:`excel_funcs.engine` 中 ``ExcelFunctions`` 各属性一一对应。
"""

from __future__ import annotations

import excel_funcs.array_funcs as array_funcs
import excel_funcs.datetime_funcs as datetime_funcs
import excel_funcs.financial as financial
import excel_funcs.info as info
import excel_funcs.logical as logical
import excel_funcs.lookup as lookup
import excel_funcs.math_agg as math_agg
import excel_funcs.text as xf_text


class MathFuncs:
    """
    数学/统计/条件汇总门面：把 :mod:`excel_funcs.math_agg` 的函数按「课堂常见分类」
    暴露为 ``xf.math.xxx``。

    典型映射（Python 方法 → Excel 名）：
    - ``sum`` → ``SUM``，``average`` → ``AVERAGE``，``count`` → ``COUNT``
    - ``sumif``/``sumifs``/``countifs`` → 条件汇总族
    - ``round``/``rounddown``/``mround`` → 舍入族
    - ``subtotal``/``aggregate`` → 小计与聚合

    使用示例：
        >>> xf.math.sum(1, 2, 3)
        6.0

    本类不保存状态，全部是 ``staticmethod`` 转发.
    """

    # 每一行：左边是 Python 方法名（小写），右边是 Layer1 里真正干活的函数对象。
    sum = staticmethod(math_agg.SUM)
    average = staticmethod(math_agg.AVERAGE)
    averagea = staticmethod(math_agg.AVERAGEA)
    count = staticmethod(math_agg.COUNT)
    counta = staticmethod(math_agg.COUNTA)
    countblank = staticmethod(math_agg.COUNTBLANK)
    max = staticmethod(math_agg.MAX)
    min = staticmethod(math_agg.MIN)
    maxa = staticmethod(math_agg.MAXA)
    mina = staticmethod(math_agg.MINA)
    median = staticmethod(math_agg.MEDIAN)
    mode_sngl = staticmethod(math_agg.MODE_SNGL)
    product = staticmethod(math_agg.PRODUCT)
    sumproduct = staticmethod(math_agg.SUMPRODUCT)
    sumif = staticmethod(math_agg.SUMIF)
    sumifs = staticmethod(math_agg.SUMIFS)
    countif = staticmethod(math_agg.COUNTIF)
    countifs = staticmethod(math_agg.COUNTIFS)
    averageif = staticmethod(math_agg.AVERAGEIF)
    averageifs = staticmethod(math_agg.AVERAGEIFS)
    maxifs = staticmethod(math_agg.MAXIFS)
    minifs = staticmethod(math_agg.MINIFS)
    subtotal = staticmethod(math_agg.SUBTOTAL)
    aggregate = staticmethod(math_agg.AGGREGATE)
    round = staticmethod(math_agg.ROUND)
    rounddown = staticmethod(math_agg.ROUNDDOWN)
    roundup = staticmethod(math_agg.ROUNDUP)
    mround = staticmethod(math_agg.MROUND)
    ceiling_math = staticmethod(math_agg.CEILING_MATH)
    floor_math = staticmethod(math_agg.FLOOR_MATH)
    int = staticmethod(math_agg.INT)
    trunc = staticmethod(math_agg.TRUNC)
    abs = staticmethod(math_agg.ABS)
    sign = staticmethod(math_agg.SIGN)
    mod = staticmethod(math_agg.MOD)
    power = staticmethod(math_agg.POWER)
    sqrt = staticmethod(math_agg.SQRT)
    exp = staticmethod(math_agg.EXP)
    ln = staticmethod(math_agg.LN)
    log = staticmethod(math_agg.LOG)
    log10 = staticmethod(math_agg.LOG10)
    pi = staticmethod(math_agg.PI)
    rand = staticmethod(math_agg.RAND)
    randbetween = staticmethod(math_agg.RANDBETWEEN)
    fact = staticmethod(math_agg.FACT)
    combin = staticmethod(math_agg.COMBIN)
    permut = staticmethod(math_agg.PERMUT)
    gcd = staticmethod(math_agg.GCD)
    lcm = staticmethod(math_agg.LCM)
    quotient = staticmethod(math_agg.QUOTIENT)


class TextFuncs:
    """
    文本函数门面，对应 :mod:`excel_funcs.text`。

    常见映射：
    - ``left/right/mid`` → ``LEFT/RIGHT/MID``
    - ``trim/upper/lower/proper`` → 清洗与大小写
    - ``find/search`` → 定位（区分大小写 / 不区分）
    - ``value`` → Excel ``VALUE``（实现函数名为 ``VALUE_FROM_TEXT``，防与错误常量重名）

    使用示例：
        >>> xf.text.left("abcd", 2)
        'ab'
    """

    concat = staticmethod(xf_text.CONCAT)
    textjoin = staticmethod(xf_text.TEXTJOIN)
    left = staticmethod(xf_text.LEFT)
    right = staticmethod(xf_text.RIGHT)
    mid = staticmethod(xf_text.MID)
    len = staticmethod(xf_text.LEN)
    lenb = staticmethod(xf_text.LENB)
    t = staticmethod(xf_text.T)
    trim = staticmethod(xf_text.TRIM)
    upper = staticmethod(xf_text.UPPER)
    lower = staticmethod(xf_text.LOWER)
    proper = staticmethod(xf_text.PROPER)
    substitute = staticmethod(xf_text.SUBSTITUTE)
    replace = staticmethod(xf_text.REPLACE)
    rept = staticmethod(xf_text.REPT)
    find = staticmethod(xf_text.FIND)
    search = staticmethod(xf_text.SEARCH)
    text = staticmethod(xf_text.TEXT)
    value = staticmethod(xf_text.VALUE_FROM_TEXT)
    char = staticmethod(xf_text.CHAR)
    code = staticmethod(xf_text.CODE)
    exact = staticmethod(xf_text.EXACT)
    fixed = staticmethod(xf_text.FIXED)
    clean = staticmethod(xf_text.CLEAN)


class LogicalFuncs:
    """
    逻辑函数门面，对应 :mod:`excel_funcs.logical`。

    保留字处理：``if``/``and``/``or`` 在 Python 中是关键字，所以使用
    ``if_``/``and_``/``or_``。

    常见映射：
    - ``if_`` → ``IF``
    - ``iferror``/``ifna`` → 错误兜底
    - ``ifs``/``switch`` → 多分支
    - ``not_``/``xor`` → 逻辑运算
    """

    true = staticmethod(logical.TRUE)
    false = staticmethod(logical.FALSE)
    if_ = staticmethod(logical.IF)
    iferror = staticmethod(logical.IFERROR)
    ifna = staticmethod(logical.IFNA)
    ifs = staticmethod(logical.IFS)
    switch = staticmethod(logical.SWITCH)
    and_ = staticmethod(logical.AND)
    or_ = staticmethod(logical.OR)
    not_ = staticmethod(logical.NOT)
    xor = staticmethod(logical.XOR)


class LookupFuncs:
    """
    查找与引用门面，对应 :mod:`excel_funcs.lookup`。

    区域数据统一用二维 ``list`` 表示（外层=行，内层=列）。

    常见映射：
    - ``vlookup/hlookup`` → ``VLOOKUP/HLOOKUP``
    - ``index/match`` → ``INDEX/MATCH``
    - ``xlookup/xmatch`` → 新版查找族（本库为教学简化）
    - ``offset/indirect`` → 引用偏移与间接引用（需看函数文档了解简化边界）
    """

    vlookup = staticmethod(lookup.VLOOKUP)
    hlookup = staticmethod(lookup.HLOOKUP)
    index = staticmethod(lookup.INDEX)
    match = staticmethod(lookup.MATCH)
    choose = staticmethod(lookup.CHOOSE)
    address = staticmethod(lookup.ADDRESS)
    row = staticmethod(lookup.ROW)
    column = staticmethod(lookup.COLUMN)
    rows = staticmethod(lookup.ROWS)
    columns = staticmethod(lookup.COLUMNS)
    transpose = staticmethod(lookup.TRANSPOSE)
    offset = staticmethod(lookup.OFFSET)
    indirect = staticmethod(lookup.INDIRECT)
    xlookup = staticmethod(lookup.XLOOKUP)
    xmatch = staticmethod(lookup.XMATCH)
    lookup = staticmethod(lookup.LOOKUP)


class DateFuncs:
    """
    日期时间门面，对应 :mod:`excel_funcs.datetime_funcs`。

    典型映射：
    - ``date/time/today/now`` → 基础日期时间构造与当前时刻
    - ``year/month/day`` 与 ``hour/minute/second`` → 分量提取
    - ``edate/eomonth/networkdays/workday`` → 日历运算
    - ``date_to_serial`` → 与 Excel 序列号互转

    多数返回 ``date``/``datetime``，不是字符串；展示格式可配合 ``xf.text.text``.
    """

    today = staticmethod(datetime_funcs.TODAY)
    now = staticmethod(datetime_funcs.NOW)
    date = staticmethod(datetime_funcs.DATE)
    time = staticmethod(datetime_funcs.TIME)
    year = staticmethod(datetime_funcs.YEAR)
    month = staticmethod(datetime_funcs.MONTH)
    day = staticmethod(datetime_funcs.DAY)
    hour = staticmethod(datetime_funcs.HOUR)
    minute = staticmethod(datetime_funcs.MINUTE)
    second = staticmethod(datetime_funcs.SECOND)
    edate = staticmethod(datetime_funcs.EDATE)
    eomonth = staticmethod(datetime_funcs.EOMONTH)
    weekday = staticmethod(datetime_funcs.WEEKDAY)
    weeknum = staticmethod(datetime_funcs.WEEKNUM)
    isoweeknum = staticmethod(datetime_funcs.ISOWEEKNUM)
    datevalue = staticmethod(datetime_funcs.DATEVALUE)
    timevalue = staticmethod(datetime_funcs.TIMEVALUE)
    networkdays = staticmethod(datetime_funcs.NETWORKDAYS)
    workday = staticmethod(datetime_funcs.WORKDAY)
    datedif = staticmethod(datetime_funcs.DATEDIF)
    date_to_serial = staticmethod(datetime_funcs.date_to_serial)


class FinancialFuncs:
    """
    财务函数门面，对应 :mod:`excel_funcs.financial`。

    典型映射：
    - ``pv/fv/pmt/nper/rate`` → 年金五兄弟
    - ``npv/irr`` 与 ``xnpv/xirr`` → 现金流贴现与收益率
    - ``ipmt/ppmt`` → 分期利息/本金拆分

    重点教学提醒：``rate`` 与 ``nper`` 必须同周期（年-年、月-月）。
    """

    pv = staticmethod(financial.PV)
    fv = staticmethod(financial.FV)
    pmt = staticmethod(financial.PMT)
    nper = staticmethod(financial.NPER)
    rate = staticmethod(financial.RATE)
    ipmt = staticmethod(financial.IPMT)
    ppmt = staticmethod(financial.PPMT)
    npv = staticmethod(financial.NPV)
    irr = staticmethod(financial.IRR)
    xirr = staticmethod(financial.XIRR)
    xnpv = staticmethod(financial.XNPV)


class InfoFuncs:
    """
    信息判断门面，对应 :mod:`excel_funcs.info`。

    常见映射：
    - ``isblank/isnumber/istext/islogical`` → 类型判断
    - ``iserror/iserr/isna`` → 错误分类判断
    - ``n/type/error_type`` → 类型与错误编码转换

    适合与 ``if_`` 联用，构成「先判型再计算」的教学套路.
    """

    isblank = staticmethod(info.ISBLANK)
    isnumber = staticmethod(info.ISNUMBER)
    istext = staticmethod(info.ISTEXT)
    islogical = staticmethod(info.ISLOGICAL)
    iserror = staticmethod(info.ISERROR)
    iserr = staticmethod(info.ISERR)
    isna = staticmethod(info.ISNA)
    isformula = staticmethod(info.ISFORMULA)
    isref = staticmethod(info.ISREF)
    n = staticmethod(info.N)
    type = staticmethod(info.TYPE)
    error_type = staticmethod(info.ERROR_TYPE)


class ArrayFuncs:
    """
    数组函数门面，对应 :mod:`excel_funcs.array_funcs`。

    典型映射：
    - ``unique`` → ``UNIQUE``
    - ``sort/sortby`` → ``SORT/SORTBY``
    - ``filter`` → ``FILTER``
    - ``sequence`` → ``SEQUENCE``
    - ``randarray`` → ``RANDARRAY``

    返回值均为 Python ``list``/``list[list]``；Excel 365 的溢出区域语义在本库中以
    「返回数据结构」形式表达。
    """

    unique = staticmethod(array_funcs.UNIQUE)
    sort = staticmethod(array_funcs.SORT)
    sortby = staticmethod(array_funcs.SORTBY)
    filter = staticmethod(array_funcs.FILTER)
    sequence = staticmethod(array_funcs.SEQUENCE)
    randarray = staticmethod(array_funcs.RANDARRAY)
