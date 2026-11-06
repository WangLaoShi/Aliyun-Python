"""数学与聚合函数与 Excel 常见用例对照。"""

from excel_funcs import AVERAGE, COUNT, COUNTA, DIV0, ROUND, SUM, SUMIFS


def test_sum_flat_and_nested() -> None:
    """
    验证 :func:`SUM`：标量与**嵌套** list 展平后求和，与**教学** 用例一致.
    """
    assert SUM(1, 2, [3, 4]) == 10.0


def test_average_empty_div0() -> None:
    """
    验证 :func:`AVERAGE`：无**可用** 数时与 Excel 类似返回 **#DIV/0!**（``DIV0`` 单例）.
    """
    assert AVERAGE() is DIV0
    assert AVERAGE([]) is DIV0  # type: ignore[arg-type]


def test_count_counta() -> None:
    """
    验证 :func:`COUNT` **只** 计**纯** 数 ；:func:`COUNTA` 计**非** 空** 格** 数（**含** 空串）.
    """
    assert COUNT(1, "x", True) == 1
    assert COUNTA(1, "", "a") == 3


def test_round_half_away_from_zero() -> None:
    """
    验证 :func:`ROUND` 为**半分远离 0** ；与 Python 自带 ``round`` 的**银行家** 舍入不同.
    """
    assert ROUND(2.5, 0) == 3.0
    assert ROUND(-2.5, 0) == -3.0


def test_sumifs() -> None:
    """
    验证 :func:`SUMIFS`：多**列** **等** 长** 、** **条** 件** 列** **与** **求** 和** 列** **对** 齐** 。
    """
    r1 = [1, 2, 3, 4]
    r2 = ["a", "a", "b", "b"]
    assert SUMIFS(r1, r2, "a") == 3.0
