"""
Layer 3 — 统一入口 ``ExcelFunctions``（给新手用的「总控制台」）
================================================================

**为什么要有这一层？**  
在 Excel 里，你会在「公式」「数据」「开始」等选项卡里找功能。这里用 **属性**
把同类函数收在一起，例如 ``xf.math`` 下都是数学/统计，**不用记** ``SUM`` 在
``math_agg`` 里、``IF`` 在 ``logical`` 里。

**和直接 ``from excel_funcs import SUM`` 有何区别？**  
功能相同，都是调用底层实现。``ExcelFunctions`` 更适合：教学、在大型项目里
**只注入一个对象**、以及 IDE 自动补全（输入 ``xf.`` 看分组）。

**依赖关系**（从下到上，单向）：  
``math_agg / text / ...`` → ``facades`` 中的 ``MathFuncs`` 等 → 本文件中的
:class:`ExcelFunctions`。

阅读顺序建议：本类 → :mod:`excel_funcs.facades` → 各 Layer1 模块。
"""

from __future__ import annotations

from excel_funcs.facades import (
    ArrayFuncs,
    DateFuncs,
    FinancialFuncs,
    InfoFuncs,
    LogicalFuncs,
    LookupFuncs,
    MathFuncs,
    TextFuncs,
)


class ExcelFunctions:
    """
    对新手最友好的**统一入口**：用「分类」组织 Excel 式函数。

    **各属性在模仿 Excel 的哪一块**（可对照 Excel 功能区分组）：

    - ``math``：求和、平均、四舍五入、随机、组合等（原「数学/统计」一类）。
    - ``text``：拼字符串、取左右子串、大小写、``VALUE`` 的文本转数等。
    - ``logical``：``if_``、``and_``、``or_`` 等；注意方法名在 Python 里加 ``_``
      因为 ``if``/``and``/``or`` 是**语言关键字**。
    - ``lookup``：``VLOOKUP``、``INDEX``、``MATCH`` 等（用 ``list`` 当表）。
    - ``date``：日期、星期、工作日等（多用 ``datetime``）。
    - ``financial``：现值、年金、内部收益率等。
    - ``info``：``ISNUMBER``、``ISBLANK`` 等「判断单元格类型」类函数。
    - ``array``：``UNIQUE``、``SORT`` 等（列表级简化实现）。

    **小提示**：下面示例里的 ``.sum`` 是 Python 方法名**小写**；底层仍对应
    Excel 的 **SUM** 语义。

    Example:
        >>> xf = ExcelFunctions()
        >>> xf.math.sum(1, 2, 3)  # 即 SUM(1,2,3) 的语义
        6.0
    """

    # __slots__ 限制能绑定的属性名，避免手滑拼错属性；与上方文档中的分组一一对应。
    __slots__ = ("math", "text", "logical", "lookup", "date", "financial", "info", "array")

    def __init__(self) -> None:
        """
        构造「**一站式**」访问器：在内存里挂上八个分组门面（facade）实例，每个
        门面对应 Excel 里一大类公式的**教学分组**（数学、文本、逻辑……）。

        **无参**  
        本库不在构造时连真实工作表或文件；**纯函数 + 你传入的 list/标量** 即算
        一张「小表」。

        **每行在干什么**（读源码时自顶向下）  
        依次 ``MathFuncs()`` 等，得到带 ``@staticmethod`` 转发的**薄包装**，真正
        演算在 :mod:`excel_funcs.math_agg`、:mod:`excel_funcs.text` 等里。

        **可扩展**  
        若课程要加新分组，需同步改 :attr:`__slots__` 与本文档表，保持 IDE 补全
        不迷路。

        Side effects:
            在 ``self`` 上绑定 ``math``、``text`` 等 8 个只读名（受 ``__slots__`` 限）。
        """
        # 每行创建一个「空壳类」实例，其方法内部转发到对应 Layer1 实现（见 facades.py）。
        self.math = MathFuncs()
        self.text = TextFuncs()
        self.logical = LogicalFuncs()
        self.lookup = LookupFuncs()
        self.date = DateFuncs()
        self.financial = FinancialFuncs()
        self.info = InfoFuncs()
        self.array = ArrayFuncs()
