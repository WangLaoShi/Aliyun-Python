"""MODE_SNGL、MAXA/MINA、SUBTOTAL 统计、INDIRECT/OFFSET、LENB、T、二维 UNIQUE。"""

from excel_funcs.array_funcs import UNIQUE
from excel_funcs.errors import REF, VALUE
from excel_funcs.lookup import INDIRECT, OFFSET
from excel_funcs.math_agg import DIV0, MAXA, MINA, MODE_SNGL, SUBTOTAL
from excel_funcs.text import LENB, T


def test_mode_sngl() -> None:
    """
    验证 :func:`MODE.SNGL` / :func:`MODE_SNGL` **众** 数** 。
    """
    assert MODE_SNGL(1, 2, 2, 3) == 2.0


def test_maxa_mina() -> None:
    """
    验证 :func:`MAXA`、:func:`MINA` **文** 本** **当** **0** **、** **逻** 辑** **当** **0/1** 。
    """
    assert MAXA(1, True, "x") == 1.0
    assert MINA(1, False, "x") == 0.0


def test_subtotal_stdev_var() -> None:
    """
    验证 :func:`SUBTOTAL` 7/8/10/107 的映射，以及**样本** 不足 2 个时**标准差** 得 DIV0 。
    """
    data = [10, 20, 30]
    assert abs(SUBTOTAL(7, data) - SUBTOTAL(107, data)) < 1e-9
    assert SUBTOTAL(8, data) > 0
    assert SUBTOTAL(10, data) > 0
    assert SUBTOTAL(7, [1]) is DIV0


def test_indirect_workbook() -> None:
    """
    验证 :func:`INDIRECT` 在**提供** ``workbook`` 字典**时** 按**地址** 取** 值** 、**不** 区** 分** **大小** 写** 。
    """
    wb = {"A1": 100, "b2": "hi"}
    assert INDIRECT("A1", True, workbook=wb) == 100
    assert INDIRECT("B2", True, workbook=wb) == "hi"
    assert INDIRECT("Z9", True, workbook=wb) is REF


def test_offset_slice() -> None:
    """
    验证 :func:`OFFSET` **子** 区** 缺** 省** **高** 宽** **与** **指** 定** **高** 宽** 。
    """
    m = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert OFFSET(m, 1, 1) == [[5, 6], [8, 9]]
    assert OFFSET(m, 0, 0, 2, 2) == [[1, 2], [4, 5]]


def test_lenb_t() -> None:
    """
    验证 :func:`LENB` **UTF-8** **字** 节** 长** 、:func:`T` **对** 文** 本** **/** **数** **/** **错** 误** 的** 行** 为** 。
    """
    assert LENB("中文") == 6
    assert T("a") == "a"
    assert T(123) == ""
    assert T(VALUE) is VALUE


def test_unique_2d_rows() -> None:
    """
    验证 :func:`UNIQUE` **二** 维** **按** **行** **去** 重**（** **整** 行** **tuple** **比** 较** **） 。
    """
    rows = [[1, 2], [1, 2], [3, 4]]
    u = UNIQUE(rows)
    assert len(u) == 2
    assert (1, 2) in u and (3, 4) in u
