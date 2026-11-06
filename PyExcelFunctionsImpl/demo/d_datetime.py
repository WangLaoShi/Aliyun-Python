"""
日期与时间：TODAY、DATE、NETWORKDAYS、DATEDIF …
===============================================

**类型**  
多数返回 ``datetime.date`` 或带日期的 ``datetime``；**不是** Excel 的「序列数」
除非你自己调 ``date_to_serial`` 对照。

**NETWORKDAYS**  
演示里用两个 ``date`` 字面量；节假日列表可传第三个参数，见 API docstring。

"""

from __future__ import annotations

from demo.common import section, show


def run() -> None:
    """
    演示 :mod:`excel_funcs.datetime_funcs` 中 TODAY、DATE、NETWORKDAYS、EDATE 等日期**与** 序列号.
    """
    from datetime import date  # 标准库日期，和 Excel 日期是不同表示，本库在内部会换算

    from excel_funcs.datetime_funcs import (
        DATE,
        DATEDIF,
        DATEVALUE,
        DAY,
        EDATE,
        EOMONTH,
        HOUR,
        ISOWEEKNUM,
        MINUTE,
        MONTH,
        NETWORKDAYS,
        NOW,
        SECOND,
        TIME,
        TIMEVALUE,
        TODAY,
        WEEKDAY,
        WEEKNUM,
        WORKDAY,
        YEAR,
        date_to_serial,
    )

    section("TODAY / NOW / DATE / TIME")
    show("TODAY()", TODAY())
    show("NOW()", NOW())
    d = DATE(2024, 1, 15)
    show("DATE(2024,1,15)", d)
    show("TIME(12,30,0)", TIME(12, 30, 0))

    section("YEAR / MONTH / DAY / HOUR / MINUTE / SECOND")
    show("YEAR(d)", YEAR(d))
    show("MONTH(d)", MONTH(d))
    show("DAY(d)", DAY(d))
    t0 = TIME(14, 5, 30)
    show("HOUR(TIME(...))", HOUR(t0))
    show("MINUTE(TIME(...))", MINUTE(t0))
    show("SECOND(TIME(...))", SECOND(t0))

    section("WEEKDAY / ISOWEEKNUM / WEEKNUM")
    show("WEEKDAY(d)", WEEKDAY(d))
    show("ISOWEEKNUM(d)", ISOWEEKNUM(d))
    show("WEEKNUM(d)", WEEKNUM(d))

    section("EDATE / EOMONTH / NETWORKDAYS / WORKDAY / DATEDIF")
    show("EDATE(d,1)", EDATE(d, 1))
    show("EOMONTH(d,0)", EOMONTH(d, 0))
    a, b = date(2024, 1, 1), date(2024, 1, 14)
    show("NETWORKDAYS(a,b)", NETWORKDAYS(a, b))
    show("WORKDAY(a,5)", WORKDAY(a, 5))
    show("DATEDIF(DATE(2020,1,1),DATE(2024,6,1),'Y')", DATEDIF(DATE(2020, 1, 1), DATE(2024, 6, 1), "Y"))

    section("DATEVALUE / TIMEVALUE / date_to_serial")
    show("DATEVALUE('2024-01-01')", DATEVALUE("2024-01-01"))
    show("TIMEVALUE('12:30:00')", round(TIMEVALUE("12:30:00"), 6))
    show("date_to_serial(TODAY())", date_to_serial(TODAY()))


if __name__ == "__main__":
    run()
