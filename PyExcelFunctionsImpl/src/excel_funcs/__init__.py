"""
excel-funcs-py：在 Python 里用「接近 Excel」的方式做常用计算
============================================================

**新手先读什么？** 仓库根目录的 ``README.md`` 和 ``docs/beginner-guide.md``（白话概念），
再回来看本文件里 ``from excel_funcs import ...`` 能拿到哪些名字。

**本包提供三类东西**：

1. **:class:`excel_funcs.engine.ExcelFunctions`（推荐总入口）**  
   实例上挂有 ``.math``、``.text``、``.logical`` 等，名称贴近 Excel 功能区，
   适合在 IDE 里点出方法名学习。

2. **Layer1 大写函数（本模块直接 ``import``）**  
   如 ``SUM``、``IF``、``AVERAGE``，与 Excel 工作表函数名**风格一致**，
   便于从表格思维迁移。注意：工作表 **VALUE**（文本转数字）在代码里为
   ``VALUE_FROM_TEXT``，因为 ``VALUE`` 已用于表示错误 ``#VALUE!``。

3. **错误与判断**  
   ``NA``、``VALUE``、``REF`` 等是「像单元格里的 #N/A、#VALUE!」的**值**，不是
   Python 异常；配合 ``is_error``、``is_na`` 使用，详见 ``excel_funcs.errors``。

**版本号** 写在文件末尾的 ``__version__`` 与根目录 ``pyproject.toml`` 的 ``[project]`` 中，
二者应一致。

--------------------------------------------------------------------
**导入示例**（在任意 ``.py`` 里）::

    from excel_funcs import ExcelFunctions, SUM, IF, VALUE_FROM_TEXT
    from excel_funcs.errors import NA, VALUE, is_error

--------------------------------------------------------------------
下表是 ``__all__`` 的「人类可读目录」，具体以列表为准。
"""

from excel_funcs.engine import ExcelFunctions
from excel_funcs.errors import (
    DIV0,
    ExcelErrorValue,
    NA,
    NAME,
    NULL,
    NUM,
    REF,
    VALUE,
    is_error,
    is_na,
)
from excel_funcs.logical import AND, FALSE, IF, IFERROR, IFNA, IFS, NOT, OR, SWITCH, TRUE, XOR
from excel_funcs.math_agg import (
    ABS,
    AGGREGATE,
    AVERAGE,
    AVERAGEA,
    AVERAGEIF,
    AVERAGEIFS,
    CEILING_MATH,
    COMBIN,
    COUNT,
    COUNTA,
    COUNTBLANK,
    COUNTIF,
    COUNTIFS,
    EXP,
    FACT,
    FLOOR_MATH,
    GCD,
    INT,
    LCM,
    LN,
    LOG,
    LOG10,
    MAX,
    MAXA,
    MAXIFS,
    MEDIAN,
    MIN,
    MINA,
    MINIFS,
    MOD,
    MODE_SNGL,
    MROUND,
    PERMUT,
    PI,
    POWER,
    PRODUCT,
    QUOTIENT,
    RAND,
    RANDBETWEEN,
    ROUND,
    ROUNDDOWN,
    ROUNDUP,
    SIGN,
    SQRT,
    SUBTOTAL,
    SUM,
    SUMIF,
    SUMIFS,
    SUMPRODUCT,
    TRUNC,
)
from excel_funcs.text import (
    CHAR,
    CLEAN,
    CODE,
    CONCAT,
    EXACT,
    FIND,
    FIXED,
    LEFT,
    LEN,
    LENB,
    LOWER,
    MID,
    PROPER,
    REPLACE,
    REPT,
    RIGHT,
    SEARCH,
    SUBSTITUTE,
    TEXT,
    TEXTJOIN,
    T,
    TRIM,
    UPPER,
    VALUE_FROM_TEXT,
)

__all__ = [
    # 引擎
    "ExcelFunctions",
    # 错误
    "ExcelErrorValue",
    "NA",
    "VALUE",
    "REF",
    "DIV0",
    "NUM",
    "NAME",
    "NULL",
    "is_error",
    "is_na",
    # 数学（部分在 __init__ 再导出扩展）
    "SUM",
    "AVERAGE",
    "AVERAGEA",
    "COUNT",
    "COUNTA",
    "COUNTBLANK",
    "MAX",
    "MAXA",
    "MIN",
    "MINA",
    "MEDIAN",
    "MODE_SNGL",
    "PRODUCT",
    "SUMPRODUCT",
    "SUMIF",
    "SUMIFS",
    "COUNTIF",
    "COUNTIFS",
    "AVERAGEIF",
    "AVERAGEIFS",
    "MAXIFS",
    "MINIFS",
    "SUBTOTAL",
    "AGGREGATE",
    "ROUND",
    "ROUNDDOWN",
    "ROUNDUP",
    "MROUND",
    "CEILING_MATH",
    "FLOOR_MATH",
    "INT",
    "TRUNC",
    "ABS",
    "SIGN",
    "MOD",
    "POWER",
    "SQRT",
    "EXP",
    "LN",
    "LOG",
    "LOG10",
    "PI",
    "RAND",
    "RANDBETWEEN",
    "FACT",
    "COMBIN",
    "PERMUT",
    "GCD",
    "LCM",
    "QUOTIENT",
    # 逻辑
    "IF",
    "IFS",
    "SWITCH",
    "AND",
    "OR",
    "NOT",
    "XOR",
    "TRUE",
    "FALSE",
    "IFERROR",
    "IFNA",
    # 文本
    "CONCAT",
    "TEXTJOIN",
    "LEFT",
    "RIGHT",
    "MID",
    "LEN",
    "LENB",
    "T",
    "TRIM",
    "UPPER",
    "LOWER",
    "PROPER",
    "SUBSTITUTE",
    "REPLACE",
    "REPT",
    "FIND",
    "SEARCH",
    "TEXT",
    "VALUE_FROM_TEXT",
    "CHAR",
    "CODE",
    "EXACT",
    "FIXED",
    "CLEAN",
]

__version__ = "0.1.0"
