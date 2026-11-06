# demo：一边跑一边学 ``excel_funcs``

## 这文件夹是干什么的？

把 Excel 里常见的函数（`SUM`、`IF`、 `VLOOKUP` …）在 Python 里**真算一遍**，
用终端打印出来，**对照**你在表格里的直觉是否一致。适合**新手**、**想快速扫一遍能力边界**的人。

- **不替代** 单元测试（那在 `tests/`）；
- **不替代** 文档（大段概念在 `docs/beginner-guide.md` 与根目录 `README.md`）；
- **是**：可改、可断点、可复制的**例子集合**。

## 怎么运行？（在 `PyExcelFunctionsImpl` 根目录，与 `pyproject.toml` 同级）

```bash
# 全部分类各跑一遍（推荐第一次）
python -m demo.run_all
```

`demo/common.py` 已尝试把 `src` 加进 `sys.path`，所以**不先** `pip install -e .` 往往也能跑；若报错
`No module named excel_funcs`，再执行：

```bash
pip install -e .
python -m demo.run_all
```

## 想只跑某一类？

```bash
python -m demo.d_math
python -m demo.d_text
python -m demo.d_logical
# …… 同目录下其它 d_*.py
```

## 各文件大概对应什么？

| 文件 | 内容方向 |
|------|----------|
| `d_math.py` | 求和、平均、四舍五入、条件求和、SUBTOTAL 等 |
| `d_text.py` | 左右截取、TRIM、LENB、T、文本转数等 |
| `d_logical.py` | IF、IFS、IFERROR、AND/OR 等 |
| `d_lookup.py` | VLOOKUP、INDEX、OFFSET、带 workbook 的 INDIRECT 等 |
| `d_array.py` | UNIQUE、SORT、SEQUENCE 等 |
| `d_datetime.py` | 今天、日期差、工作日等 |
| `d_financial.py` | 年金、现值、IRR 等 |
| `d_info.py` | ISNUMBER、ISBLANK 等 |

## 怎么自己加例子？

1. 打开例如 `d_math.py`；
2. 在 `run()` 里加一行 `show("你的说明", 某函数(参数))`；
3. 再跑 `python -m demo.d_math` 看终端。

**提示**：`show` 第二个参数是**任意对象**，`repr` 后打印，复杂对象会很长，属于正常现象。
