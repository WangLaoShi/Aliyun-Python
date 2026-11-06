"""
Excel 风格错误值与类型判断（给新手：为什么不用 raise？）
================================================================

**在 Excel 里**  
公式出问题时单元格里显示 ``#N/A``、``#VALUE!`` 等——它们仍是「**一个值**」，
可以当作 ``IF``、``IFERROR`` 的输入被处理。

**在普通 Python 里**  
我们习惯用 ``try/except`` 或 ``raise``。那样写**不像表格**：错误一旦变成异常，
就要到处捕获，和 ``=IFERROR(A1,0)`` 这种写法不对味。

**本库的做法**  
用 :class:`ExcelErrorValue` 的**小对象**表示常见错误，例如下面导入的
``NA``、``VALUE``。函数可以 ``return VALUE`` 表示「本格是 #VALUE!」；
再用 :func:`is_error` 判断，对应 Excel 的 **ISERROR**。

**和 Excel 显示的关系**  
``NA.code`` 为 ``"#N/A"``，与界面上一致，便于print调试。

**若你是库作者**  
在需要中断流程时仍可使用 ``raise``；对**模拟工作表**的 API，优先返回
``ExcelErrorValue`` 更符合用户心智。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final


@dataclass(frozen=True, slots=True)
class ExcelErrorValue:
    """
    表示单个 Excel 错误字面量，例如 ``#N/A``。

    Attributes:
        code: 与 Excel 状态栏一致的错误字符串，含前导 ``#``。

    **教学要点**  
    这是**值**，不是**异常**；在 REPL 里 ``print(NA)`` 会得到类似
    ``ExcelErrorValue('#N/A')`` 的表示。这样设计才能链式做 ``IFERROR``。

    **冻结与 slots**  
    ``frozen=True`` 使实例像「不可变常量」；``slots`` 省内存。对新手只需知道
    **每种错误在程序里通常只有一个单例**（如 ``NA``），用 ``is`` 比较即可。
    """

    code: str

    def __repr__(self) -> str:  # pragma: no cover - 调试友好
        """
        调试用表示：``ExcelErrorValue('#N/A')`` 形式，方便与 Python 的 ``repr`` 习惯
        统一，在日志里**一眼**看出是哪类工作表错误。

        **和 ``str()``**  
        dataclass 未自定义 ``__str__`` 时，打印行为与 ``repr`` 相关；在教学中可
        与 Excel 格子里显示的纯 ``#N/A`` 文字对比，强调「**对象** vs **界面
        字符串**」。

        Returns:
            可 ``eval`` 再认出来的字符串（``code`` 用 ``!r`` 转义）。
        """
        return f"ExcelErrorValue({self.code!r})"


# 以下为**单例**：整个程序里同种错误用「同一个对象」比较引用即可（is NA）。
# 名称尽量与 Excel 状态栏/单元格里看到的字符串一致，方便对照帮助文档。
NA: Final[ExcelErrorValue] = ExcelErrorValue("#N/A")  # 找不到、IFS 无匹配时常见
VALUE: Final[ExcelErrorValue] = ExcelErrorValue("#VALUE!")  # 类型不对、无法转换
REF: Final[ExcelErrorValue] = ExcelErrorValue("#REF!")  # 引用无效、区域越界等
DIV0: Final[ExcelErrorValue] = ExcelErrorValue("#DIV/0!")  # 除数为零
NUM: Final[ExcelErrorValue] = ExcelErrorValue("#NUM!")  # 数值越域、不收敛等
NAME: Final[ExcelErrorValue] = ExcelErrorValue("#NAME?")  # 名称未定义
NULL: Final[ExcelErrorValue] = ExcelErrorValue("#NULL!")  # 交集为空等


def is_error(value: Any) -> bool:
    """
    对应 Excel ``ISERROR``：任意错误类型（含 ``#N/A``）为真。

    Args:
        value: 任意 Python 对象。

    Returns:
        若为 :class:`ExcelErrorValue` 则 ``True``；否则 ``False``。
        说明：Python 内置 ``Exception`` 不计入，以保持类型明确。
    """

    return isinstance(value, ExcelErrorValue)


def is_na(value: Any) -> bool:
    """
    对应工作表 **ISNA**：**仅**当值为 **#N/A**（本库单例 ``NA``）时返回
    ``True``；其它任何错误、正常值、``None`` 都是 ``False``。

    **为什么用 ``is`` 不用 ``==``**  
    ``NA`` 是**单例**；``is`` 比类型+字符串比较快且意图清晰。学生若用 ``==`` 与
    自造 ``ExcelErrorValue("#N/A")`` 去比，在默认 dataclass 下可能为真也可能需
    要 ``==`` 重载——**教学代码里请用库提供的 ``NA``**。

    **和 ``ISERR``/``ISERROR`` 的关系**  
    - ``is_error``：任意错误。  
    - ``is_err``：有错误但**不是** ``#N/A``。  
    - ``is_na``：**只是** ``#N/A``。

    Args:
        value: 任意对象。

    Returns:
        ``value is NA`` 的布尔结果。

    **课堂可练**  
    讨论「lookup 没命中」与「公式写错」在表格里一个常是 #N/A、一个常是 #REF! 或
    #NAME?，为何要用不同函数接。
    """

    return value is NA


def is_err(value: Any) -> bool:
    """
    对应工作表 **ISERR**：是 **#VALUE!、#REF!、#NUM!、#NAME?、#NULL!、#DIV/0!** 等
    任意**非** ``#N/A`` 的 Excel 风格错误时返回 ``True``；正常值或 ``#N/A`` 为
    ``False``。

    **和 ISNA 的互斥**  
    在 Excel 里常一起教：先 ``ISNA`` 处理「没找到」，再 ``ISERROR``/``ISERR``
    看其它问题。本库中 ``#N/A`` 用 :func:`is_na`；其它错误用 ``is_err`` 与
    :func:`is_error` 搭配。

    Args:
        value: 待判定的对象；若不是 :class:`ExcelErrorValue` 则直接 ``False``。

    Returns:
        是否为「除 #N/A 外的工作表类错误」。

    **易错**  
    Python 的 ``Exception`` **不**被当成 Excel 错误；本库不混用两种模型。

    **课堂可练**  
    画韦恩图：``is_error``、``is_na``、``is_err`` 三者的包含关系，并各举一个
    用例格子的典型场景。
    """

    return isinstance(value, ExcelErrorValue) and value is not NA
