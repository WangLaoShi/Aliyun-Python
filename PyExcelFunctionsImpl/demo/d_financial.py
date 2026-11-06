"""
财务：PMT、PV、RATE、NPV、IRR、XNPV、XIRR
====================================

**量纲**  
下面 ``rate = 0.05/12`` 表示**月利率**（年 5% 分 12 月），``n = 60`` 表示 60 个月。
若误用**年数**+**年利率**却忘了对齐，结果会**错一个数量级**级别——和 Excel
里填错 E 格一样，不是库 bug。

**XIRR / XNPV**  
需要**成对**的现金流 ``values`` 与计息日期 ``dates``，长度须一致。

"""

from __future__ import annotations

from datetime import date

from demo.common import section, show


def run() -> None:
    """
    演示 :mod:`excel_funcs.financial` 中 PV、FV、PMT、NPV、IRR 等**现金流** 模型小例.
    """
    from excel_funcs.financial import IRR, NPV, PMT, PV, RATE, XIRR, XNPV

    section("PV / PMT")
    # 典型「车贷/分期」心算：5% 年 APR，60 期，借 1 万，每期还多少
    rate, n, pv0 = 0.05 / 12, 60, 10000
    p = PMT(rate, n, pv0)
    show("PMT(月利率,60,10000)", p)
    show("PV(月利率,60,PMT)", PV(rate, n, p))

    section("RATE")
    r_est = RATE(60, p, pv0)
    show("RATE(60,p,10000) 近似", r_est)

    section("NPV / IRR")
    show("NPV(0.1,-100,40,50,60)", NPV(0.1, -100, 40, 50, 60))
    show("IRR([-100,40,50,60])", IRR([-100, 40, 50, 60]))

    section("XNPV / XIRR")
    dates = [date(2024, 1, 1), date(2024, 7, 1), date(2025, 1, 1)]
    vals = [-1000, 400, 700]
    show("XNPV(0.1,vals,dates)", XNPV(0.1, vals, dates))
    show("XIRR(vals,dates)", XIRR(vals, dates))


if __name__ == "__main__":
    run()
