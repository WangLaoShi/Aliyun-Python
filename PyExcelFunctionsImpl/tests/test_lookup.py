"""查找函数测试。"""

from excel_funcs.lookup import INDEX, MATCH, VLOOKUP, XLOOKUP


def test_vlookup_exact() -> None:
    """
    验证 :func:`VLOOKUP` 精确匹配与列索引.
    """
    table = [[1, "a"], [2, "b"]]
    assert VLOOKUP(2, table, 2, False) == "b"


def test_match_exact() -> None:
    """
    验证 :func:`MATCH` 在 match_type=0 时返回 1 基下标.
    """
    assert MATCH("b", ["a", "b", "c"], 0) == 2


def test_index() -> None:
    """
    验证 :func:`INDEX` 二维 1 基下标取值.
    """
    assert INDEX([[10, 20], [30, 40]], 2, 2) == 40


def test_xlookup() -> None:
    """
    验证 :func:`XLOOKUP` 在等长两列上精确匹配.
    """
    assert XLOOKUP(2, [1, 2, 3], ["x", "y", "z"]) == "y"
