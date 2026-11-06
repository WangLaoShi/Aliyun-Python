"""日期函数测试。"""

from datetime import date

from excel_funcs.datetime_funcs import DATE, EDATE, EOMONTH, NETWORKDAYS, date_to_serial


def test_date_edate_eomonth() -> None:
    """
    验证 :func:`DATE`、:func:`EDATE` **月** 推移 与 :func:`EOMONTH` **月** 末** 日** 。
    """
    d = DATE(2024, 1, 15)
    assert isinstance(d, date)
    e = EDATE(d, 1)
    assert e.month == 2
    assert EOMONTH(d, 0).day == 31


def test_networkdays() -> None:
    """
    验证 :func:`NETWORKDAYS` 工作日计数（周末 Mon–Fri 模型，见实现）.
    """
    a = date(2024, 1, 1)
    b = date(2024, 1, 7)
    # Mon..Sun: weekdays Mon-Fri = 5
    assert NETWORKDAYS(a, b) == 5


def test_date_to_serial_roundtrip_order() -> None:
    """
    验证 :func:`date_to_serial` 序列号处于与 1900 日期**系统** 相符的量级.
    """
    d = date(2024, 6, 1)
    s = date_to_serial(d)
    assert s > 40000
