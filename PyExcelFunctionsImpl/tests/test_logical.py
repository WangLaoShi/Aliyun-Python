"""逻辑函数测试。"""

from excel_funcs import IF, IFERROR
from excel_funcs.errors import VALUE


def test_if_basic() -> None:
    """
    验证 :func:`IF` 真**假** 两**分支** 返回值 。
    """
    assert IF(True, 1, 2) == 1
    assert IF(False, 1, 2) == 2


def test_iferror() -> None:
    """
    验证 :func:`IFERROR`：遇 ``ExcelErrorValue`` 时**改** 为**备** 用** 值** 。
    """
    assert IFERROR(1, 2) == 1
    assert IFERROR(VALUE, 2) == 2
