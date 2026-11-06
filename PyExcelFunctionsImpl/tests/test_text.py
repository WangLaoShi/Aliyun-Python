"""文本函数测试。"""

from excel_funcs import LEFT, MID, TRIM, UPPER


def test_trim_upper_left() -> None:
    """
    验证 :func:`TRIM`、:func:`UPPER`、:func:`LEFT` 的基本行为.
    """
    assert TRIM("  a  b  ") == "a b"
    assert UPPER("ab") == "AB"
    assert LEFT("abcd", 2) == "ab"


def test_mid() -> None:
    """
    验证 :func:`MID` 的**1 基** 起始 与 长度 。
    """
    assert MID("abcdef", 2, 3) == "bcd"
