"""分层 API 测试。"""

from excel_funcs import ExcelFunctions


def test_excel_functions_facades() -> None:
    """
    验证 :class:`ExcelFunctions` 门面将 ``math`` / ``logical`` / ``text`` 等转发到 Layer1 实现.
    """
    xf = ExcelFunctions()
    assert xf.math.sum(1, 2, 3) == 6.0
    assert xf.logical.if_(True, "Y", "N") == "Y"
    assert xf.text.upper("ab") == "AB"
