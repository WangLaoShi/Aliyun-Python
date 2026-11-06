"""
demo 子包共用的**打印格式**和 **sys.path 引导**（小白读这段即可懂干什么）

为什么要动 sys.path？
----------------------
执行 ``python -m demo.run_all`` 时，Python 会加载本文件；本文件位于 ``demo/`` 下，
而真正的包 ``excel_funcs`` 在上一级 ``src/excel_funcs/`` 里。  
若你**没有**先 ``pip install -e .``，直接克隆仓库就运行，默认 **找不到** ``excel_funcs``。  
所以这里把 ``项目根/src`` 插进 ``sys.path``，让你**不装可编辑包也能跑 demo**（教学场景常用）。

如果已经 ``pip install -e .``，多插一次 ``src`` 一般也无害（有 ``if`` 去重）。

section / show 干什么？
----------------------
让终端里输出**带小标题、对齐**的文本，比一堆裸 ``print`` 好读。  
你改 ``demo/d_*.py`` 时，只要 ``show("说明文字", 表达式)`` 就能同时看到**人话标签**和**结果**。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 项目根 = 本文件所在 package 的上一级（与 pyproject.toml 同级）
_root = Path(__file__).resolve().parent.parent
_src = _root / "src"
if _src.is_dir() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))


def section(title: str) -> None:
    """
    打印约 60 列宽的分隔线与 ``title`` 小标题，便于在长 **demo** 输出中**扫读** 结构；
    与 :func:`show` 搭配：先 ``section`` 再若干 ``show`` 。
    """
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def show(label: str, value: object) -> None:
    """``label`` 是给人看的说明；``value`` 用 ``repr`` 印出，方便区分 str / int 等类型。"""
    print(f"  {label}: {value!r}")
