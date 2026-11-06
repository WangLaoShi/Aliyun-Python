# 新手入门：从零理解 PyExcelFunctionsImpl（excel-funcs-py）

> 目标读者：会一点 Python 基础（变量、函数、列表 `list`、导入 `import`），在 Excel 里用过公式。读完应能**明白项目是干什么的、代码往哪看、怎么自己试**。

---

## 1. 用一句话说：这个项目是干什么的？

在 Excel 里你写 `=SUM(A1:A10)`。这个仓库在 **Python 里提供类似功写的函数**（如 `SUM(1,2,3)`），帮你：

- 在 **脚本/自动化** 里做和表格类似的计算；
- **学习** Excel 函数在「纯 Python 数据」上如何表现（列表代替单元格）；
- 为以后接 **pandas、数据库、网络数据** 打基础——数据用 Python 结构表示，用同一套「Excel 式」逻辑处理。

**它不是** 操作 `.xlsx` 文件的库（开表、改单元格请用 `openpyxl` 等）；这里只管「算式」这一层。

---

## 2. 你需要准备什么知识？

| 你已有 | 项目里会用到 |
|--------|----------------|
| Excel 中 `SUM`、`IF`、`VLOOKUP` 等**概念** | 同名或接近的函数名、参数含义（数字、区域） |
| Python 的 `1 + 1`、`"hello"`、`[1,2,3]` | 用列表/数字代替单元格和区域 |
| `from 模块 import 函数` | 从 `excel_funcs` 里导入 `SUM`、`IF` 等 |
| 可选：虚拟环境 `venv` | 建议隔离依赖：`python -m venv .venv` 再 `pip install -e .` |

若还不会 `import`，建议先看 [Python 官方 tutorial 6. 模块](https://docs.python.org/zh-cn/3/tutorial/modules.html) 再回来。

---

## 3. 项目里为什么写「三层」？（给小白的大白话）

可以把它想成**从「零件」到「工具箱」再到「总控制台」**：

1. **Layer 1（底层）**  
   各 `.py` 里真正的 Python **函数**，例如 `math_agg.SUM()`、`text.LEFT()`。  
   - 特点：名字通常对应 **Excel 英文名的大写**（如 `SUM`），**没有界面**，就是纯计算。

2. **Layer 2（分类外壳）**  
   类 `MathFuncs`、`TextFuncs` 等，里面把 Layer1 的函数用 `staticmethod` 包一层。  
   - 作用：在 IDE 里打 `xf.math.` 会列出数学相关，**像 Excel 的功能区**（开始、公式、数据）。

3. **Layer 3（一个总入口）**  
   类 `ExcelFunctions`，里面有属性 `math`、`text`、`logical`……  
   - 使用方式：`xf = ExcelFunctions()`，然后 `xf.math.sum(1,2,3)`，**对新手很友好，不容易迷路**。

**结论**：你既可以 `from excel_funcs import SUM`（像直接背公式），也可以用 `ExcelFunctions().math.sum(...)`（像打开一个「Excel 式菜单」）。

---

## 4. 在 Python 里「单元格」和「区域」怎么表示？

| Excel 里的东西 | 在本项目里常见写法 | 小提示 |
|----------------|--------------------|--------|
| 空单元格 | `None` 或 `""`（看函数，有的把空当 0 或忽略） | 和 Excel 的「真空白」有细微差别，见主 README 差异表 |
| 一行/一列数 | 一维列表：`[1, 2, 3]` | 相当于一列 A1:A3 |
| 一块表 | 二维列表：`[[1,2],[3,4]]` | 外层 = 行，内层 = 列 |

**练习**：在 Python 里 `SUM(1, 2, [3, 4])` 会先把里外层展平再相加，和「选多个不连续区域」的直觉类似。

---

## 5. 错误值 `#N/A`、`#VALUE!` 在 Python 里长什么样？

Excel 里公式错了会显示 `#VALUE!` 等。本仓库用**小对象**表示这些，例如：

- `from excel_funcs.errors import VALUE, NA, REF`  
- 在 Python 里 `result` 可能是数字，也可能是 `VALUE` 这种**特殊值**（不是 `Exception` 异常，除非你自行 `raise`）。

为什么要这样？因为 Excel 里**错误可以当作 IF 的输入、被 IFERROR 吃掉**；用返回值比到处 `try/except` 更接近表格逻辑。

`ISERROR(x)` 就是帮你判断 `x` 是不是这类错误值。

---

## 6. 和 Excel 不一样的地方（新手最容易踩坑）

- **`IF` 不短路**：Python 会**先算完** `value_if_true` 和 `value_if_false` 再挑一个，和 Excel 里「只算选中的那一支」不完全一样。重计算分支时要小心**副作用**（如改文件）。
- **日期**：多用 `datetime.date`；和 Excel 的「序列号 44927」的互换见 `docs/design.md`。
- **文本转数字**：工作表里的 `VALUE` 函数在代码里叫 **`VALUE_FROM_TEXT`**，避免和错误常量 `VALUE`（`#VALUE!`）同名冲突。

更全的差异见仓库根目录 [README.md](../README.md) 的表格。

---

## 7. 建议的阅读顺序（第一次克隆仓库）

1. 根目录 `README.md`（安装 + 快速例子）  
2. 本文件 `docs/beginner-guide.md`（概念）  
3. `docs/design.md`（设计约定，稍短）  
4. `docs/function-list.md`（有哪些函数、实现到什么程度）  
5. 用编辑器打开 `src/excel_funcs/__init__.py`，看**公开导出了哪些名字**  
6. 运行 `python -m demo.run_all` 看终端输出，对照 `demo/d_math.py` 等里的例子  

有精力再读：`math_agg.py`（算数字）、`logical.py`（条件）、`text.py`（字符串）。

---

## 8. 小词典（看到缩写不慌）

| 词 | 含义 |
|----|------|
| **PyPI** | Python 包索引网站，用 `pip install` 装包时多半从这里下 |
| **Facade** | 设计模式里的「对外一层简单门面」，这里指 `MathFuncs` 等分类类 |
| **staticmethod** | 绑在类上、**不需要** `self` 的函数，仅为了归类 |
| **SDist / Wheel** | 源码包 / 安装包，发布到 PyPI 时会打这两种 |
| **UTF-8** | 一种文字编码；`LENB` 在代码里用 UTF-8 字节长，和 Excel 在日文系统上的 DBCS 可能不同 |

---

## 9. 自己改代码、跑测试

```bash
cd PyExcelFunctionsImpl
pip install -e ".[dev]"
PYTHONPATH=src python -m pytest tests -q
```

- 全绿：当前测试通过。  
- 你改了某个函数，可先在 `tests/` 里**仿照已有测试**加一个小用例，再改实现。

---

## 10. 还是看不懂怎么办？

- 从 **`demo/d_math.py`** 里找一行 `show("标签", 某个函数(...))`，在交互环境里自己敲同样的调用。  
- 打开 **`src/excel_funcs/math_agg.py`** 里对应函数，读函数上方的 **docstring**（三引号里的说明）。  
- 在仓库里用编辑器 **全文搜索** 函数名（如 `def SUM`），看参数怎么处理。

学编程和用 Excel 一样：**多试、改数字看结果变不变**，就熟了。

---

祝学习愉快。若你改进文档或发现描述不清的地方，欢迎提 issue 或直接补充本文件。
