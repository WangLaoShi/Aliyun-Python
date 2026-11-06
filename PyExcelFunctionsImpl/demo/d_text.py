"""
文本函数演示：拼接、子串、大小写、LENB、T、文本转数
==============================================

**为何有两处 import 文本**  
- ``VALUE_FROM_TEXT`` 在包根也导出，方便 ``from excel_funcs import VALUE_FROM_TEXT``。  
- ``CHAR``/``CLEAN`` 等仍从 ``excel_funcs.text`` 子模块取，**展示**子模块与根导出
  的两种用法；新手任选一种风格即可。

**易混**  
- ``VALUE``（错误，``#VALUE!``）和 ``VALUE_FROM_TEXT``（函数）**不是**同一个名字。
"""

from __future__ import annotations

from demo.common import section, show


def run() -> None:
    """
    演示 :mod:`excel_funcs.text` 中文本拼接、子串、格式、``VALUE_FROM_TEXT`` 等；
    供 ``python -m demo.d_text`` 或总入口 ``demo.run_all`` 调用.
    """
    from excel_funcs import VALUE_FROM_TEXT
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
        T,
        TEXT,
        TEXTJOIN,
        TRIM,
        UPPER,
    )
    from datetime import date

    section("CONCAT / TEXTJOIN")
    show("CONCAT('a','b',1)", CONCAT("a", "b", 1))
    show("TEXTJOIN(',',True,'a','','b')", TEXTJOIN(",", True, "a", "", "b"))

    section("LEFT / RIGHT / MID / LEN / LENB")
    show("LEFT('abcdef',3)", LEFT("abcdef", 3))
    show("RIGHT('abcdef',2)", RIGHT("abcdef", 2))
    show("MID('abcdef',2,3)", MID("abcdef", 2, 3))
    show("LEN('abc')", LEN("abc"))
    show("LENB('中文')", LENB("中文"))
    show("LENB('ASCII')", LENB("ASCII"))

    section("TRIM / UPPER / LOWER / PROPER")
    show("TRIM('  x  y  ')", TRIM("  x  y  "))
    show("UPPER('ab')", UPPER("ab"))
    show("LOWER('CD')", LOWER("CD"))
    show("PROPER('hello world')", PROPER("hello world"))

    section("SUBSTITUTE / REPLACE / REPT")
    show("SUBSTITUTE('aa','a','b')", SUBSTITUTE("aa", "a", "b"))
    show("SUBSTITUTE('aa','a','b',2)", SUBSTITUTE("aa", "a", "b", 2))
    show("REPLACE('abcdef',2,3,'ZZ')", REPLACE("abcdef", 2, 3, "ZZ"))
    show("REPT('*',5)", REPT("*", 5))

    section("FIND / SEARCH")
    show("FIND('b','abcb')", FIND("b", "abcb"))
    show("SEARCH('B','abc')", SEARCH("B", "abc"))

    section("TEXT / VALUE_FROM_TEXT / CHAR / CODE")
    show("TEXT(date,'yyyy-mm-dd')", TEXT(date(2024, 6, 1), "yyyy-mm-dd"))
    show("VALUE_FROM_TEXT('  12.5 ')", VALUE_FROM_TEXT("  12.5 "))
    show("CHAR(65)", CHAR(65))
    show("CODE('A')", CODE("A"))

    section("EXACT / FIXED / CLEAN / T")
    show("EXACT('a','a')", EXACT("a", "a"))
    show("FIXED(1234.5,2)", FIXED(1234.5, 2))
    show("CLEAN('a\\x07b')", CLEAN("a\x07b"))
    show("T('hi')", T("hi"))
    show("T(123)", T(123))


if __name__ == "__main__":
    run()
