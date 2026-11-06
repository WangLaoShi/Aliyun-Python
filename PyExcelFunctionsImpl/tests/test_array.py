"""数组函数测试。"""

from excel_funcs.array_funcs import SEQUENCE, SORT, UNIQUE


def test_unique() -> None:
    """
    验证 :func:`UNIQUE` 一维去重且保序.
    """
    assert UNIQUE([1, 2, 1, 3]) == [1, 2, 3]


def test_sort() -> None:
    """
    验证 :func:`SORT` 升序.
    """
    assert SORT([3, 1, 2]) == [1, 2, 3]


def test_sequence_shape() -> None:
    """
    验证 :func:`SEQUENCE` 返回的二维形状（行数×列数）.
    """
    m = SEQUENCE(2, 3)
    assert len(m) == 2 and len(m[0]) == 3
