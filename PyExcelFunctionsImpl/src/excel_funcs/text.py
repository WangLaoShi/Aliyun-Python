"""
Layer 1 — 文本函数（LEFT / CONCAT / TRIM / VALUE_FROM_TEXT …）
===============================================================

**小白记一点**  
Excel 单元格里的「文本」在 Python 里多半用 **str**（引号包起来的字符串）。  
``None`` 或空串有时表示空单元格，各函数处理略不同，读具体函数的说明。

**命名：为什么有 ``VALUE_FROM_TEXT``？**  
Excel 工作表函数 **VALUE**（把可转换的文本变成数字）若也起名为 ``VALUE``，
会和表示 **#VALUE!** 错误的 ``excel_funcs.errors.VALUE`` 撞名。  
所以实现函数叫 ``VALUE_FROM_TEXT``；通过 :class:`excel_funcs.facades.TextFuncs`
属性 ``.value`` 访问时，**仍接近**「点 value 就是工作表 VALUE」的心智。

**FIND 与 SEARCH**  
``FIND`` 大小写敏感；``SEARCH`` 本实现为**不区分大小写**的子串查找，**未**
实现 Excel 通配符 ``*``/``?`` 的完整规则。

**LENB**  
按 **UTF-8 字节数**计长；与中文 Windows 下 Excel 的 DBCS 可能不一致，见 docstring。
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

from excel_funcs._utils import coerce_float
from excel_funcs.errors import VALUE as VALUE_ERROR
from excel_funcs.errors import ExcelErrorValue


def _as_str(x: Any) -> str | ExcelErrorValue:
    """
    **内部**：把一「格」**标量** 变成**字符串** 参与文本运算；`None` → 空串
    `""`（**空** 单元格 常见）；遇 :class:`ExcelErrorValue` **原样** 传回 让
    上层 决定 **是** 拼进串 还 **是** 冒泡 错（**本** 层 **不** 强转 错 为 字）.

    **为** 什 不 在 这 **raise**  
    与 全 库「**表** 格 **错 误** 是 **值**」 的 教学 主 线 一 致.

    Returns:
        正常 时 ``str``；**错误** 时 该 错误 对象 本 身（**类型** 不 是 str，**调** 用
        方 **必须** `isinstance` 判）.
    """
    if x is None:
        return ""
    if isinstance(x, ExcelErrorValue):
        return x
    return str(x)


def CONCAT(*texts: Any) -> str | ExcelErrorValue:
    """
    对应 **CONCAT** / 旧 名 **CONCATENATE**：**无 分隔 符** 的 **顺序** 拼接；`None` 经
    :func:`_as_str` 成 **空**；**任** 一 段 为 错 则 **整 式** 先 **停** 在 那 个 错.

    **和 TEXTJOIN 对比**  
    **不** 插 **分 隔 符**、**不** 选 **是** 否 **略** 空（**要** 空 就 **会** 长 出 **连** 在 一 起 的 空 串 段，**可** 教 **清洗** 再 来）.

    **和 ``+``**  
    纯 str 的 ``"a"+"b"`` 在 Python 很 好；**本** 函 数 是 **为** 了 **一** 口 **气** 接 **多** 格/多 **可** 变 **参** 与 **#VALUE!** 的 **一** 致 **处理**.

    **课堂可练**  
    用 **A 列 姓、B 列 名** 合 **成** 全 名；再 试 **B 列** 为 **#VALUE!** 的 **时** 整 行 **结果**.
    """
    parts: list[str] = []
    for t in texts:
        s = _as_str(t)
        if isinstance(s, ExcelErrorValue):
            return s
        parts.append(s)
    return "".join(parts)


def TEXTJOIN(delimiter: Any, ignore_empty: Any, *texts: Any) -> str | ExcelErrorValue:
    """
    对应 **TEXTJOIN**（**带 分 隔 符** 拼 接）：`delimiter` 在 **相** 邻 **两** 段
    **可** 见 **之** 间 插 入（**不** 在 **首** 尾 **多** 一 个 **头** 尾 **杠** 除 **非** 你 **故** 意 **多** 传 **空** 段，**以** 实 现 **为** 准 **读** 源 码）；
    `ignore_empty` 为 **真** 时 **不** 把  **仅** 为 **空** 的 段 加 进 **join** 列 表、**也** 可 **少** 些 **多** 余 **的** 分 **隔** 符.

    **与 CONCAT 对比**  
    适 合 **「** 姓、名、**中** 间 加 **逗 号** **」** 的 **人** 类 **读** 的 **输** 出.

    **#VALUE!**  
    某 个 **中** 间 **转** 串 **失** 败 **或** 错 格 依 **_as_str** 规 则.

    **课堂可练**  
    用 **同一** 三 个 **人** 名，**对** 比 `ignore_empty` **开/关** 的 **长** 度 与 **分** 隔 符 **个** 数.
    """
    d = _as_str(delimiter)
    if isinstance(d, ExcelErrorValue):
        return d
    ign = bool(ignore_empty)
    out: list[str] = []
    for t in texts:
        s = _as_str(t)
        if isinstance(s, ExcelErrorValue):
            return s
        if ign and s == "":
            continue
        out.append(s)
    return d.join(out)


def LEFT(text: Any, num_chars: Any = 1) -> str | ExcelErrorValue:
    """
    对应 **LEFT**：从**左侧**起取 ``num_chars`` 个**字符**（与 Excel 一致按字符
    而非按字节，复杂 Unicode 的计数差异见选修）。

    若 ``num_chars`` 无法转非负合理的数，返回 ``#VALUE!``。文本经 :func:`_as_str`。
    与 :func:`MID`、:func:`RIGHT` 为「子串三件套」。

    **课堂可练**  
    在固定编号的学号列中取前几位作为**年级或校区代码**（注意隐私与假数据）.
    """
    s = _as_str(text)
    if isinstance(s, ExcelErrorValue):
        return s
    n = coerce_float(num_chars)
    if n is None or n < 0:
        return VALUE_ERROR
    return s[: int(n)]


def RIGHT(text: Any, num_chars: Any = 1) -> str | ExcelErrorValue:
    """
    对应 **RIGHT**：从**右侧**保留最后 ``n`` 个字符；`n=0` 得空串；`n` 超过总长时
    得整串。参数与错误规则同 :func:`LEFT`。

    中间子串在教学中常用 :func:`MID`；用 RIGHT+LEFT 表示固定宽度也是一种思路。

    **课堂可练**  
    讨论「取扩展名」用字符串函数与用 ``pathlib`` 的优劣（信息课**文件路径**单元）.
    """
    s = _as_str(text)
    if isinstance(s, ExcelErrorValue):
        return s
    n = coerce_float(num_chars)
    if n is None or n < 0:
        return VALUE_ERROR
    ni = int(n)
    return s[-ni:] if ni else ""


def MID(text: Any, start_num: Any, num_chars: Any) -> str | ExcelErrorValue:
    """
    对应 **MID**：自第 ``start_num`` 个**字符**起取 ``num_chars`` 个，**Excel
    为 1 起算**；内部用 ``i = start-1`` 与 Python 切片 `s[i:j]` 对应，是**0 基
    与 1 基**的经典对照课。

    若起点越过字符串末尾，返回**空**而不报错。起点小于 1 或长度小于 0 等返回 #VALUE!。

    **课堂可练**  
    在**合规、脱敏**前提下用假数据讨论固定宽度字段的截取（不采集真实敏感信息）.
    """
    s = _as_str(text)
    if isinstance(s, ExcelErrorValue):
        return s
    st = coerce_float(start_num)
    ln = coerce_float(num_chars)
    if st is None or ln is None or st < 1 or ln < 0:
        return VALUE_ERROR
    # Excel 起始为 1
    i = int(st) - 1
    j = i + int(ln)
    if i >= len(s):
        return ""
    return s[i:j]


def LEN(text: Any) -> int | ExcelErrorValue:
    """
    对应 **LEN**（**字符长度**）：返回 Python 中 ``str`` 的字符个数，即 ``len(s)``。
    对「**代理对**、组合字符」与 Excel 的字符计数可能不完全一致，国际化为选修讨论；
    与 :func:`LENB` 对照可理解**字符**与 **UTF-8 字节** 的区别。

    若入参是 ``ExcelErrorValue``，则**原样返回**该错误（不在此函数中消除错误）。

    **课堂可练**  
    同一含中文的字符串，分别 ``LEN`` 与 ``LENB``，记录两个数字并解释差异来源。
    """
    s = _as_str(text)
    if isinstance(s, ExcelErrorValue):
        return s
    return len(s)


def LENB(text: Any) -> int | ExcelErrorValue:
    """
    Excel ``LENB``：按 **UTF-8 字节长度** 计数。

    说明：Excel 在 DBCS 区域为双字节字符计数；本实现固定 UTF-8，与日文/中文传统
    ``LENB`` 在 Excel 中的结果可能不同。
    """

    s = _as_str(text)
    if isinstance(s, ExcelErrorValue):
        return s
    return len(s.encode("utf-8"))


def T(value: Any) -> str | ExcelErrorValue:
    """
    对应 **T**：**仅**当实参是 ``str`` 时原样返回；**非**字符串（数、日期对象等）
    在 Excel 中常**不**把内容当「文本格」再展示，本实现统一返回**空串** ``""``。

    **错误值**  
    若实参是 ``ExcelErrorValue``，**不**被清空，**原样**返回，便于与 ``IF`` 等链式
    处理.

    **课堂可练**  
    对比 ``T(123)`` 与用 :func:`TEXT` 或格式得到的 ``"123"`` 何时出现。
    """

    if isinstance(value, ExcelErrorValue):
        return value
    if isinstance(value, str):
        return value
    return ""


def TRIM(text: Any) -> str | ExcelErrorValue:
    """
    对应 **TRIM**：删除**首尾**空白，并把**连续**的空白**压缩**为**单个**空格
   （正则 ``\\s+`` → 一空格），与从网页粘贴来的「多空格乱」**清洗** 场景契合。

    **与 ``str.strip``**  
    **仅** 两端时不如 TRIM 强；**中间** 多空格是 TRIM 的卖点.

    **课堂可练**  
    在表格里**故意**多打空格，再 ``TRIM`` 前后**单元格**内容对比.
    """
    s = _as_str(text)
    if isinstance(s, ExcelErrorValue):
        return s
    return re.sub(r"\s+", " ", s).strip()


def UPPER(text: Any) -> str | ExcelErrorValue:
    """
    对应 **UPPER**（**全大写**），语言相关的大小写由 Python ``str.upper`` 与 **locale
    无关**；德文 ß/土耳其语 i 等需**进阶** 国际化说明.

    **对** 照 **LOWER/PROPER** 做**姓名** 列 **三** 种 **展示** 的 **同一** 数据 **不** 同 **格** 式 题.
    """
    s = _as_str(text)
    if isinstance(s, ExcelErrorValue):
        return s
    return s.upper()


def LOWER(text: Any) -> str | ExcelErrorValue:
    """
    对应 **LOWER**（**全小写**）：实现手段 ``s.lower``；与 :func:`UPPER` 对偶.
    用于**不**区分大小写比较前的**规范化** 或与用户输入习惯**对齐** 的展示.
    """
    s = _as_str(text)
    if isinstance(s, ExcelErrorValue):
        return s
    return s.lower()


def PROPER(text: Any) -> str | ExcelErrorValue:
    """
    对应 **PROPER**（**词首** 字母大写、**词内** 小写）。按**空白** 分割（分隔符
    在 ``re.split`` 中保留再拼接），每段经内部 ``cap_word`` 处理。与英文
    *title case* 的小词规则**不必** 完全一致，以 Excel 对拍为课堂目标。

    **课堂可练**  
    姓名/地名混排一列，展示清洗前后在报表中的**可读性** 对比。
    """
    s = _as_str(text)
    if isinstance(s, ExcelErrorValue):
        return s

    def cap_word(w: str) -> str:
        """
        **PROPER 内部**：对**一个** 被 `re.split` 分出来的**词块** 做首字母大写、
        其余小写。空白分隔符在 ``re.split(r"(\\s+)", s)`` 中**保留** 为独立块，
        以维持原字符串的**空格** 模式（读源码时跟一遍 ``join`` 即懂）.

        **空 块**  
        原样**返回**，避免**多余** 清洗.

        **Args/Returns**  
        子串 ``w`` 与 同 类型**处理** 结果.
        """
        if not w:
            return w
        return w[0].upper() + w[1:].lower()

    return "".join(cap_word(t) for t in re.split(r"(\s+)", s))


def SUBSTITUTE(text: Any, old_text: Any, new_text: Any, instance_num: Any | None = None) -> str | ExcelErrorValue:
    """
    对应 **SUBSTITUTE**：在 ``text`` 中把 ``old_text`` **替换** 为 ``new_text``。
    若给 ``instance_num``，则**只**替换**第** k **次**出现；否则**全局**换（``str.replace`` 语义）。

    **old 为空**  
    返回 #VALUE!，与 Excel 防歧义. **错误** 在任一段 ``_as_str`` 中则冒泡.

    **与 REPLACE 对比**  
    **SUB** 是**子串** 等值替换；**REPLACE** 是**从第几个字符起改多长** 的**定位** 替换.

    **课堂可练**  
    把全文里的 ``,`` 与 ``.`` 用统一分隔符**一次性**/**分次** 替换的对比实验.
    """
    s = _as_str(text)
    o = _as_str(old_text)
    n = _as_str(new_text)
    for v in (s, o, n):
        if isinstance(v, ExcelErrorValue):
            return v
    if o == "":
        return VALUE_ERROR
    if instance_num is None:
        return s.replace(o, n)
    k = coerce_float(instance_num)
    if k is None or k < 1 or int(k) != k:
        return VALUE_ERROR
    idx = 0
    count = 0
    target = int(k)
    while True:
        pos = s.find(o, idx)
        if pos < 0:
            break
        count += 1
        if count == target:
            return s[:pos] + n + s[pos + len(o) :]
        idx = pos + len(o)
    return s


def REPLACE(old_text: Any, start_num: Any, num_chars: Any, new_text: Any) -> str | ExcelErrorValue:
    """
    对应 **REPLACE**（**按** **位置** **覆** 写）：**从** 第 ``start_num`` 个**字符**（1 基）起
    **删** 掉 ``num_chars`` 个**再** 插入 ``new_text``，等价**拼接** `s[:i] + n + s[j:]`.

    **与 SUBSTITUTE**  
    **不** 搜子串、**不** 管内容是否相等，**纯** 下标 手术，适合**定宽** 字段.

    **#VALUE!**  
    起点/长度非法. **和 MID 的 1-基** 同**一** 套** 习惯.

    **课堂可练**  
    在固定位把**年** 从 ``2020`` 改成 ``2024`` 的**模拟** 改号（**假** 数据）.
    """
    s = _as_str(old_text)
    n = _as_str(new_text)
    if isinstance(s, ExcelErrorValue) or isinstance(n, ExcelErrorValue):
        return s if isinstance(s, ExcelErrorValue) else n
    st = coerce_float(start_num)
    ln = coerce_float(num_chars)
    if st is None or ln is None or st < 1 or ln < 0:
        return VALUE_ERROR
    i = int(st) - 1
    j = i + int(ln)
    return s[:i] + n + s[j:]


def REPT(text: Any, number_times: Any) -> str | ExcelErrorValue:
    """
    对应 **REPT**：把 ``text`` **重复** ``number_times`` 次并拼接，即 ``text * n``。
    ``n`` 须为非负整数（可经 ``coerce_float`` 转），否则 #VALUE!。

    适合**等宽填充**、简易**文本进度条**等（与条件格式图表化对比）.

    **课堂可练**  
    用 ``REPT("█", k)`` 与某列数值成比例，做**纯字符**迷你条形图（k 取整需另讲）.
    """
    s = _as_str(text)
    if isinstance(s, ExcelErrorValue):
        return s
    nt = coerce_float(number_times)
    if nt is None or nt < 0 or int(nt) != nt:
        return VALUE_ERROR
    return s * int(nt)


def FIND(find_text: Any, within_text: Any, start_num: Any = 1) -> int | ExcelErrorValue:
    """
    对应 **FIND**：**大小写敏感** 的子串查找，返回**第一次**出现**位置**（**1 基**，
    与 Python ``str.find`` 的 0 基不同）。可从 ``start_num`` 起找（**1 基**）。

    **未找到**  
    返回 #VALUE!（本库用 ``VALUE_ERROR``），**不**用 -1，以贴近 Excel.

    **与 SEARCH**  
    :func:`SEARCH` **不** 区分大小写；**两者** 均**未** 实现 Excel **通配符** `*?`.

    **课堂可练**  
    混大小写英文里对比 FIND 与 SEARCH 的返回位置.
    """
    f = _as_str(find_text)
    w = _as_str(within_text)
    if isinstance(f, ExcelErrorValue) or isinstance(w, ExcelErrorValue):
        return f if isinstance(f, ExcelErrorValue) else w
    st = coerce_float(start_num)
    if st is None or st < 1:
        return VALUE_ERROR
    i = int(st) - 1
    pos = w.find(f, i)
    if pos < 0:
        return VALUE_ERROR
    return pos + 1


def SEARCH(find_text: Any, within_text: Any, start_num: Any = 1) -> int | ExcelErrorValue:
    """
    对应 **SEARCH**：**不** 区分大小写的子串查找；先 ``.lower()`` 再 ``find``，
    返回**1 基**位置。规则与 :func:`FIND` 相同，**含** 起搜位、**未** 找到则 #VALUE!。

    **通配符**  
    **未** 实现；课程延伸可讨论**正则** ``re`` 库.

    **课堂可练**  
    同一组数据，改**首字母**大小写，**仅** ``SEARCH`` 能**稳定** 找到.
    """
    f = _as_str(find_text)
    w = _as_str(within_text)
    if isinstance(f, ExcelErrorValue) or isinstance(w, ExcelErrorValue):
        return f if isinstance(f, ExcelErrorValue) else w
    st = coerce_float(start_num)
    if st is None or st < 1:
        return VALUE_ERROR
    i = int(st) - 1
    pos = w.lower().find(f.lower(), i)
    if pos < 0:
        return VALUE_ERROR
    return pos + 1


def VALUE_FROM_TEXT(text: Any) -> float | ExcelErrorValue:
    """
    对应工作表 **VALUE**（**文本** **转** **数值**）：`strip` 后 ``coerce_float``，
    成功为 ``float``，**空** 或**不可** 转 为 #VALUE!。

    **为何** 起名为 **VALUE_FROM_TEXT**  
    与错误字面量 :data:`excel_funcs.errors.VALUE`（#VALUE!）在 Python 中容易**同名
    冲突**，本包用长名；通过 Facade 的 ``.value`` 仍可对齐工作表**VALUE** 的心智.

    千分位、货币符等本地化格式在 Excel 中行为复杂，本实现仅 ``strip``+``coerce_float``，复杂样例与表软件**对拍** 验证.

    **课堂可练**  
    一列混「真数字格」与「像数字的文本格」，用本函数**统一**成可参加 ``SUM`` 的数前，讨论**类型** 与**清洗**.
    """

    s = _as_str(text)
    if isinstance(s, ExcelErrorValue):
        return s
    s = s.strip()
    if s == "":
        return VALUE_ERROR
    c = coerce_float(s)
    if c is None:
        return VALUE_ERROR
    return c


def CHAR(number: Any) -> str | ExcelErrorValue:
    """
    对应 **CHAR**：把 **1–255** 的整数用 ``chr`` 变成**一个**字符，常用于控制字符
    与**Latin-1** 范围教学；越界或**非**整数可转 → #VALUE!。

    与 :func:`CODE` 为**互逆** 概念；Unicode 多字节字需**进阶** 讨论码点与编码.

    **课堂可练**  
    打印可打印 ASCII 区字符，观察码与**键盘** 的对应关系.
    """
    n = coerce_float(number)
    if n is None or n < 1 or n > 255 or int(n) != n:
        return VALUE_ERROR
    return chr(int(n))


def CODE(text: Any) -> int | ExcelErrorValue:
    """
    对应 **CODE**：对 ``text`` 的**首字符** 取 ``ord`` 得到 **Unicode 码点**；空
    串则 #VALUE!。与 :func:`CHAR` 在单字符层面对偶.

    **教学**  
    解释「**字符**」 与**键盘** 背后**数字** 的对应；多字节**编码** 与码点
    的区分见信息课**编码** 单元.

    **课堂可练**  
    同一字母**大小** 写 的 ``CODE`` 值 **相差** 多少（固定**偏移** 观察）.
    """
    s = _as_str(text)
    if isinstance(s, ExcelErrorValue):
        return s
    if s == "":
        return VALUE_ERROR
    return ord(s[0])


def EXACT(text1: Any, text2: Any) -> bool | ExcelErrorValue:
    """
    对应 **EXACT**：**区分大小写** 的**严格** 相等；经 ``_as_str`` 后做 ``a == b``；
    与 Excel 里「有时按展示值宽松」 相比，**此处** 语义是**字面值逐字符** 一致.

    若任一侧是 ``ExcelErrorValue``，**返回** 该错误（不返回 bool）.

    **课堂可练**  
    比较 ``"A"`` 与 ``"a"``：``EXACT`` 为假，**不** 区分时可用 ``UPPER`` 再比.
    """
    a = _as_str(text1)
    b = _as_str(text2)
    if isinstance(a, ExcelErrorValue) or isinstance(b, ExcelErrorValue):
        return a if isinstance(a, ExcelErrorValue) else b
    return a == b


def FIXED(number: Any, decimals: Any = 2, no_commas: Any = False) -> str | ExcelErrorValue:
    """
    对应 **FIXED**：把**数值** 格式化为**固定** 小数位数的**文字**；``no_commas`` 为
    假时对**整数** 部分加**简版** 千分位逗号。非真正 Excel 区域格式引擎，小数点
    等本地化**未** 完整复刻，仅教学演示.

    无法转数 → #VALUE!。与 :func:`TEXT` 相比，FIXED 更偏**固定小数+千分** 的展示需求.
    """
    x = coerce_float(number)
    d = coerce_float(decimals)
    if x is None or d is None:
        return VALUE_ERROR
    fmt = f"{{:.{int(d)}f}}"
    s = fmt.format(x)
    if not no_commas:
        # 极简千分位
        sign = ""
        if s.startswith("-"):
            sign = "-"
            s = s[1:]
        if "." in s:
            ip, fp = s.split(".", 1)
        else:
            ip, fp = s, ""
        ip = f"{int(ip):,}"
        s = sign + ip + ("." + fp if fp or int(d) > 0 else "")
    return s


def CLEAN(text: Any) -> str | ExcelErrorValue:
    """
    对应 **CLEAN**：**去掉** 控制**字符**（**ASCII 码 0–31** 中**除** 制表/换行
    **\t\n\r** 外），常用来清洗从**旧系统** 或**复制** 来的**不可见** 杂讯.

    **不** 删**普通** 空格，**需** 配 :func:`TRIM` 或**正则** 再清.

    **课堂可练**  
    在**字符串** 里**塞** 入 **chr(7)** 等**控制** 符，**对比** **CLEAN** 前后**长度** 与**打印** 效果.
    """
    s = _as_str(text)
    if isinstance(s, ExcelErrorValue):
        return s
    return "".join(ch for ch in s if ord(ch) >= 32 or ch in "\t\n\r")


def TEXT(value: Any, format_text: Any) -> str | ExcelErrorValue:
    """
    对应工作表 **TEXT** 的**极简** 子集：把**数** 或 **date/datetime** 按 **format_text** 的
    占位符**粗** 替换（**不** 是完整 Excel 格式引擎，**不** 支持全部分号/颜色/条件
    等**高级** 语法）.

    **现** 支持** roughly**：数字侧 ``0``/``0.00`` 类小数位；日期侧 ``yyyy``、
    ``mm``、``dd`` 等**片段** 替换。详读**源码** 里的 ``replace`` 链即知**能力边界**.

    **#VALUE!**  
    非**数** 又**非** **日期** 时.

    与 :func:`FIXED`、单元格**数字格式** 对照：TEXT 的**结果** 是文本，若再参与
    运算需 :func:`VALUE_FROM_TEXT` 或**保持** 为**数** 类型**另** 存一列.

    **课堂可练**  
    同一**日** 期 **用** 不同**格式** 串** 输出** **年**-**月**-**日** 与**中文** 习惯.
    """

    fmt = _as_str(format_text)
    if isinstance(fmt, ExcelErrorValue):
        return fmt
    if isinstance(value, (datetime, date)):
        # 极简替换
        d = value if isinstance(value, date) else value.date()
        s = fmt
        s = s.replace("yyyy", f"{d.year:04d}")
        s = s.replace("yy", f"{d.year % 100:02d}")
        s = s.replace("mm", f"{d.month:02d}")
        s = s.replace("dd", f"{d.day:02d}")
        return s
    x = coerce_float(value)
    if x is None:
        return VALUE_ERROR
    if "." in fmt:
        # 小数位数 = fmt 中小数点后 0 的个数
        if "." in fmt:
            _, frac = fmt.split(".", 1)
            dec = len(frac)
        else:
            dec = 0
        return f"{x:.{dec}f}"
    return str(int(round(x)))
