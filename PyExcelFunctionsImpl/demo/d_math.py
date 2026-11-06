"""
数学 / 统计 / 条件汇总 演示（对照 function-list 约 #1–#48）
=======================================================

**本脚本里有什么**  
``SUM``、``AVERAGE``、四舍五入、``RANDBETWEEN``、``SUMIFS``、``SUBTOTAL`` 等，
每组 ``show("说明", 函数(...))`` 都是**可改数字**的实验台。

**顺序**  
大致从「基础四则统计」→「舍入」→「随机/阶乘」→「条件汇总」；与 Excel
功能区的物理顺序**不必**一致。

**若某行报错**  
先看是不是传了**类型不对**（例如把字符串当数字列）。再查 ``src/excel_funcs/math_agg.py``
里对应 ``def 函数名``。
"""

from __future__ import annotations

from demo.common import section, show


def run() -> None:
    """
    运行本文件的**全部** ``section``/``show`` 块：演示 :mod:`excel_funcs.math_agg` 中
    求和、平均、舍入、随机、条件汇总等。供 ``python -m demo.d_math`` 或 :mod:`demo.run_all` 调用.
    """
    # 大列表：从包根一次性导入，避免 40 个单独 import 行；与 __init__.py 导出表一致
    from excel_funcs import (
        ABS,
        AGGREGATE,
        AVERAGE,
        AVERAGEA,
        AVERAGEIF,
        AVERAGEIFS,
        CEILING_MATH,
        COMBIN,
        COUNT,
        COUNTA,
        COUNTBLANK,
        COUNTIF,
        COUNTIFS,
        EXP,
        FACT,
        FLOOR_MATH,
        GCD,
        INT,
        LCM,
        LN,
        LOG,
        LOG10,
        MAX,
        MAXA,
        MAXIFS,
        MEDIAN,
        MIN,
        MINA,
        MINIFS,
        MOD,
        MODE_SNGL,
        MROUND,
        PERMUT,
        PI,
        POWER,
        PRODUCT,
        QUOTIENT,
        RAND,
        RANDBETWEEN,
        ROUND,
        ROUNDDOWN,
        ROUNDUP,
        SIGN,
        SQRT,
        SUBTOTAL,
        SUM,
        SUMIF,
        SUMIFS,
        SUMPRODUCT,
        TRUNC,
    )

    section("SUM / AVERAGE / AVERAGEA")
    show("SUM(1,2,3)", SUM(1, 2, 3))
    show("SUM(1,[2,3],4)", SUM(1, [2, 3], 4))
    show("AVERAGE(10,20,30)", AVERAGE(10, 20, 30))
    show("AVERAGEA(TRUE,FALSE,'a')", AVERAGEA(True, False, "a"))

    section("COUNT / COUNTA / COUNTBLANK")
    show("COUNT(1,'x',True)", COUNT(1, "x", True))
    show("COUNTA(1,'',2)", COUNTA(1, "", 2))
    show("COUNTBLANK(None,'',1)", COUNTBLANK(None, "", 1))

    section("MAX / MIN / MEDIAN / MAXA / MINA / MODE.SNGL")
    show("MAX(1,5,3)", MAX(1, 5, 3))
    show("MIN(1,5,3)", MIN(1, 5, 3))
    show("MEDIAN(1,2,3,4)", MEDIAN(1, 2, 3, 4))
    show("MAXA(1,TRUE,'9')", MAXA(1, True, "9"))
    show("MINA(2,FALSE,'x')", MINA(2, False, "x"))
    show("MODE_SNGL(1,2,2,3)", MODE_SNGL(1, 2, 2, 3))

    section("PRODUCT / SUMPRODUCT")
    show("PRODUCT(2,3,4)", PRODUCT(2, 3, 4))
    show("SUMPRODUCT([1,2],[3,4])", SUMPRODUCT([1, 2], [3, 4]))

    section("SUBTOTAL / AGGREGATE")
    show("SUBTOTAL(9,1,2,3)", SUBTOTAL(9, 1, 2, 3))
    show("SUBTOTAL(1,10,20,30)", SUBTOTAL(1, 10, 20, 30))
    show("SUBTOTAL(7,2,4,6)", SUBTOTAL(7, 2, 4, 6))
    show("AGGREGATE(9,0,1,2,3)", AGGREGATE(9, 0, 1, 2, 3))

    section("ROUND 族 / MROUND / CEILING / FLOOR / INT / TRUNC")
    show("ROUND(2.5,0)", ROUND(2.5, 0))
    show("ROUNDDOWN(2.99,1)", ROUNDDOWN(2.99, 1))
    show("ROUNDUP(2.01,1)", ROUNDUP(2.01, 1))
    show("MROUND(10,3)", MROUND(10, 3))
    show("CEILING_MATH(4.2,1)", CEILING_MATH(4.2, 1))
    show("FLOOR_MATH(4.2,1)", FLOOR_MATH(4.2, 1))
    show("INT(-3.7)", INT(-3.7))
    show("TRUNC(3.14159,2)", TRUNC(3.14159, 2))

    section("ABS / SIGN / MOD / POWER / SQRT / EXP / LN / LOG / LOG10 / PI")
    show("ABS(-5)", ABS(-5))
    show("SIGN(-2)", SIGN(-2))
    show("MOD(10,3)", MOD(10, 3))
    show("POWER(2,8)", POWER(2, 8))
    show("SQRT(16)", SQRT(16))
    show("EXP(1)≈e", round(EXP(1), 6))
    show("LN(2.718281828)", round(LN(2.718281828), 6))
    show("LOG(100)", LOG(100))
    show("LOG10(1000)", LOG10(1000))
    show("PI()", PI())

    section("RAND / RANDBETWEEN / FACT / COMBIN / PERMUT / GCD / LCM / QUOTIENT")
    show("RAND() in (0,1)", 0 < RAND() < 1)
    show("RANDBETWEEN(1,6)", RANDBETWEEN(1, 6))
    show("FACT(5)", FACT(5))
    show("COMBIN(5,2)", COMBIN(5, 2))
    show("PERMUT(5,2)", PERMUT(5, 2))
    show("GCD(12,18)", GCD(12, 18))
    show("LCM(4,6)", LCM(4, 6))
    show("QUOTIENT(10,3)", QUOTIENT(10, 3))

    section("SUMIF / SUMIFS / COUNTIF / COUNTIFS / AVERAGEIF / AVERAGEIFS / MAXIFS / MINIFS")
    r1 = [1, 2, 3, 4]
    r2 = ["a", "a", "b", "b"]
    show("SUMIF(r2,'a',r1)", SUMIF(r2, "a", r1))
    show("SUMIFS(r1,r2,'b')", SUMIFS(r1, r2, "b"))
    show("COUNTIF(r1,'>2')", COUNTIF(r1, ">2"))
    show("COUNTIFS(r1,'>1',r2,'a')", COUNTIFS(r1, ">1", r2, "a"))
    show("AVERAGEIF(r2,'b',r1)", AVERAGEIF(r2, "b", r1))
    show("AVERAGEIFS(r1,r2,'a')", AVERAGEIFS(r1, r2, "a"))
    show("MAXIFS(r1,r2,'a')", MAXIFS(r1, r2, "a"))
    show("MINIFS(r1,r2,'b')", MINIFS(r1, r2, "b"))


if __name__ == "__main__":
    run()
