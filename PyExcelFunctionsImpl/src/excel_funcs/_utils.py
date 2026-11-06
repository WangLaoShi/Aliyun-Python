"""
内部工具：区域扁平化、数值试探、Excel 式四舍五入等
====================================================

**给读者的话（含新手）**  
你一般**不需要** ``import`` 本模块；它给 ``math_agg``、``text`` 等提供公共逻辑，
避免在几十个函数里重复写「如何把嵌套 list 展平」。

**为什么不对外当稳定 API？**  
下划线 ``_`` 开头模块表示**内部使用**；若将来换实现，不保证不破坏
「偷偷依赖 _utils 的外部代码」。

**常干的几件事**（读代码时可对照函数名）：

- ``flatten_all``：把 ``(1, [2,3], None)`` 展成一维，用于 SUM 类。
- ``coerce_float``：尽量把 ``"12.3"`` 变浮点；变不了就 ``None``，上层再变 ``#VALUE!``。
- ``excel_round_*``：按 Excel 的**远离 0 的半分**规则舍入，与 Python 3 ``round()``
  的 bankers rounding 可能不同，故单独写。

本模块不对外承诺稳定 API，仅供 ``excel_funcs`` 包内使用。
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN, ROUND_UP
from typing import Any, Iterator


def iter_flat_numbers(
    *args: Any,
    booleans_as_numbers: bool = True,
) -> Iterator[float | int]:
    """
    将任意嵌套的 ``list``/``tuple`` 与标量**按需**（惰性）展开为**数值**迭代器。

    **在库里干什么用**  
    像 ``SUM`` 一类函数在统计前需要「只拿到数字流」，用生成器可省内存、逻辑清晰。
    与 :func:`flatten_all` 不同，这里**只产出能当数字用的项**，非数值的文本等
    会被**跳过**（不 append、不 error），让上层 :func:`SUM` 等决定其它规则。

    **参数**  
    - ``booleans_as_numbers``：为 ``True`` 时，``True``/``False`` 变成 ``1``/``0``，
      与 Excel 里 SUM 对布尔在常见行为上的教学对齐；为 ``False`` 时可不产出布尔
     （视分支而定——阅读下方 ``for`` 体）。

    **和 ``flatten_all`` 的分工**  
    需要**保留** ``None``、错误值、原样字符串时，用 ``flatten_all`` 再分支；
    本函数更偏**纯数管道**。

    Yields:
        ``int``/``float`` 元素；嵌套会递归 :func:`iter_flat_numbers` 自身。

    **教学练习**  
    对比 ``list(iter_flat_numbers(1, [2, [3, None, 4]]))`` 与把 ``None`` 当 0
    两种哲学，讨论「空单元格」在表格里的意义。
    """

    for a in args:
        if a is None:
            continue
        if isinstance(a, (list, tuple)):
            yield from iter_flat_numbers(*a, booleans_as_numbers=booleans_as_numbers)
        elif isinstance(a, bool) and booleans_as_numbers:
            yield 1 if a else 0
        elif isinstance(a, (int, float)) and not isinstance(a, bool):
            yield a
        else:
            # 非数值留给上层决定是否当作 0 或错误
            continue


def flatten_all(*args: Any) -> list[Any]:
    """
    递归展平**所有**可迭代嵌套，输出**一维** ``list``，用于 ``SUM``/``MAX`` 等
    「区域里多格、多层列表」的输入。

    **与 ``iter_flat_numbers`` 的关键区别**  
    本函数**保留** ``None``、``str``、非 list/tuple 的其它对象，便于后续判断
    「这格是空、是错误、是文本」等；**不会**在展平时把非数扔掉。

    **``str``/``bytes`` 为什么不再往下拆**  
    在 Python 中字符串也是「可迭代」的，但拆成一个个字符**不像**选「一块单元格
    区域里的文本」；所以约定：**字符串整格保留**。

    **内部辅助** :func:`_walk` 对单个节点递归；最终顺序为**深度优先、从左到右**。

    Returns:
        新列表，不修改你传入的原始嵌套（浅层元素引用仍可能共享）。

    **课堂可练**  
    手算 ``flatten_all([[1, 2], 3, ("ab", "cd")])`` 里元组、列表谁被拆谁保留。
    """

    out: list[Any] = []

    def _walk(x: Any) -> None:
        """
        对单个对象 ``x`` 做一步展平，结果追加到外层 ``out``。

        - ``None``：当作单独一格，追加 ``None``（表示空单元格等）。
        - ``str``/``bytes``：整段追加，**不**按字符拆。
        - ``list``/``tuple``：对其中每个子元素再调用 ``_walk``。
        - 其它标量：直接追加（数字、错误对象、自定义类型等原样进列表）。

        这是**闭包**：内层函数能读写外层 ``out``，学生可联想「在纸上从左到右
        记格子 ID」的扫描过程。

        Args:
            x: 树状结构中的当前节点。

        副作用:
            向 ``out`` 追加 0~若干项，无返回值（``None``）。
        """
        if x is None:
            out.append(None)
        elif isinstance(x, (str, bytes)):
            out.append(x)
        elif isinstance(x, (list, tuple)):
            for i in x:
                _walk(i)
        else:
            out.append(x)

    for a in args:
        _walk(a)
    return out


def coerce_float(x: Any) -> float | None:
    """
    **尽力**把标量类输入变成 Python ``float``；转换失败时返回 ``None``，由上层
    视情况返回 :data:`excel_funcs.errors.VALUE` 等。

    **会接受什么**  
    - 空/空白：``None``、空串 ``""`` → ``None``（与「空单元格没数」教学一致）。  
    - 布尔：``True``/``False`` → ``1.0``/``0.0``。  
    - ``int``/``float``：转 ``float``（注意大整数在极端情况下有精度问题，课堂可
      点一句 IEEE754）。  
    - ``str``：``strip`` 后调用 ``float``；非数字文 → ``None``。

    **不会**  
    接受 ``list``/区域为「一个数」；那是上层 :func:`flatten_all` 后再逐格
    调本函数。也不会 ``raise``，以免破坏「工作表里错误是值不是异常」的心智。

    Returns:
        成功为 ``float``，失败为 ``None``。

    **易错**  
    ``"12.3 "`` 可转；``"1,200"``（带千分位逗号）本实现不处理，会失败——可与 Excel
    的本地化解析对比，讨论**课程外**的扩展点。
    """

    if x is None or x == "":
        return None
    if isinstance(x, bool):
        return float(int(x))
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        try:
            return float(x.strip())
        except ValueError:
            return None
    return None


def excel_round_half_away_from_zero(value: float, digits: int) -> float:
    """
    实现与 Excel **ROUND** 一致的**舍入到指定位数**规则：**半分远离 0**（half
    away from zero），**不是** Python 3 内置 :func:`round` 的「银行家舍入」。

    **为什么要单独写**  
    在 ``round(2.5)`` 得到 ``2`` 这类例子会让学生怀疑人生；和 Excel 对拍时，必须用
    ``Decimal`` 明确舍入方式（本实现内部用 :data:`decimal.ROUND_HALF_UP` 等
    组合实现）。

    **``digits`` 为负**  
    与 Excel 相同：向**整十/整百**舍入。例如 ``digits=-1`` 表示到十位。

    Args:
        value: 已能当 ``float`` 用的数（注意二进制浮点先被 ``str`` 再进
            ``Decimal`` 的路径，和 Excel/Decimal 的十进制心模更合）。
        digits: 小数位数；可为负（往左的位）。

    Returns:
        ``float`` 结果。

    **课堂可练**  
    在 Excel 和本函数上分别对 ``1.5``、``2.5``、``-1.5`` 用 ``ROUND(x,0)``，
    和 ``round`` 对比记录差异。
    """

    if digits < 0:
        factor = 10 ** (-digits)
        q = Decimal(str(value / factor))
        rounded = q.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return float(rounded * factor)
    q = Decimal(str(value)).quantize(Decimal(10) ** -digits, rounding=ROUND_HALF_UP)
    return float(q)


def excel_rounddown(value: float, digits: int) -> float:
    """
    对应 **ROUNDDOWN**（**向 0 方向截断**到指定位数，即**下取整**的按位变体；对
    正数与负数分别「朝 0 靠近」切）。

    使用 ``Decimal`` 的 ``ROUND_DOWN`` 模式，在 ``digits`` 非负时量化到
    ``10**(-digits)`` 精度；**负的 ``digits``** 时先除因子再下取整、再乘回，
    与 Excel 行为对齐。

    Args:
        value: 要处理的浮点数（调用方应已用 ``coerce_float`` 等保证合法）。
        digits: 小数位；为负时往左「整到十位、百位」。

    Returns:
        舍入后的 ``float``。

    **和 ``TRUNC`` 的关系**  
    在 ``num_digits=0`` 的思路上有重叠，但 **ROUNDDOWN** 支持负 ``digits`` 的
    「整到十位」而 **TRUNC** 有另一套 API；教学时以 Excel 帮助为准对拍。

    **课堂可练**  
    对 **-3.7** 做 **ROUNDDOWN(...,0)** 与向负无穷下取整有何异同，分别画数轴说明。
    """
    if digits >= 0:
        q = Decimal(str(value)).quantize(Decimal(10) ** -digits, rounding=ROUND_DOWN)
        return float(q)
    factor = 10 ** (-digits)
    q = Decimal(str(value / factor)).quantize(Decimal("1"), rounding=ROUND_DOWN)
    return float(q * factor)


def excel_roundup(value: float, digits: int) -> float:
    """
    对应 **ROUNDUP**（**远离 0** 的按位上取整到指定位数，与 ROUNDDOWN 对称）。

    用 ``Decimal`` 的 ``ROUND_UP`` 模式。正数**进位**、负数在绝对值上**进位**，
    与 Excel 对 **-3.2** 到整数位的表现一致，教学时可与 ``math.ceil`` 的「向正
    无穷」对比，强调 **ROUNDUP/ROUNDDOWN 都是朝远离 0**。

    Args:
        value: 待舍入的数。
        digits: 保留小数位，可为负（整到十位等）。

    Returns:
        舍入后的 ``float``。

    **易错**  
    先把 ``value``/``digits`` 从单元格**转成 float/int**，本函数不做 ``#VALUE!``
    判断，那是 :mod:`math_agg` 里 `ROUND` 包装层的职责。

    **课堂可练**  
    用同一组数跑 **ROUNDDOWN** 与 **ROUNDUP**，观察对称性；再和 **MROUND** 到
    **倍数** 比较用途差异。
    """
    if digits >= 0:
        q = Decimal(str(value)).quantize(Decimal(10) ** -digits, rounding=ROUND_UP)
        return float(q)
    factor = 10 ** (-digits)
    q = Decimal(str(value / factor)).quantize(Decimal("1"), rounding=ROUND_UP)
    return float(q * factor)
