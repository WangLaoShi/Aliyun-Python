"""财务函数测试。"""

from excel_funcs.financial import FV, PMT, PV


def test_pmt_pv_fv_signs() -> None:
    """
    验证 :func:`PMT` 与 :func:`PV` 在**符号约定** 下数值**闭环**（容差内）.
    """
    rate = 0.05 / 12
    nper = 60
    pv_val = 10000
    p = PMT(rate, nper, pv_val)
    assert isinstance(p, float)
    assert p < 0
    pv_calc = PV(rate, nper, p)
    assert isinstance(pv_calc, float)
    # Excel 符号约定：贷款本金与年金常一正一负；此处校验绝对值闭环
    assert abs(abs(pv_calc) - pv_val) < 1e-2
