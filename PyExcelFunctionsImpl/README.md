# PyExcelFunctionsImpl / excel-funcs-py

在 Python 中复现常用 **Microsoft Excel 工作表函数** 的行为，让熟悉表格公式的人能**在脚本里用同一套思路做计算**。

## 这个仓库适合谁？

- 会用 **Excel 函数**（如 `SUM`、`IF`、`VLOOKUP`），想迁移到 **Python 自动化**；
- 学 Python 时需要**有熟悉感的例子**（列表当区域、函数名当 `SUM`）；
- 需要把「公式逻辑」和「读 xlsx 文件」分开——**本库只管公式语义**，不打开 Excel 文件。

**不适合**：寻找「用 Python 打开/保存 `.xlsx`」的库——那请用 [openpyxl](https://openpyxl.readthedocs.io/) 等；本库可与它们配合使用。

## 阅读顺序（推荐，尤其新手）

1. 先看 **[docs/beginner-guide.md](docs/beginner-guide.md)**：用大白话讲「三层结构」「区域怎么表示」「错误值怎么表示」。
2. 再读本 README 的「快速开始」和「与 Excel 差异」表。
3. 需要时查阅 [docs/design.md](docs/design.md)（设计约定）和 [docs/function-list.md](docs/function-list.md)（函数清单与实现进度）。
4. 运行 `python -m demo.run_all` 看终端里的例子，并打开 `demo/d_*.py` 对照学习。

## 项目里「三层」是什么意思？（30 秒版）

- **Layer 1**：各模块里的**纯函数**（如 `math_agg.SUM`），和 Excel 函数一一对应，方便测试和复用。
- **Layer 2**：`MathFuncs`、`TextFuncs` 等**分类类**，用 `xf.math.sum(...)` 这种形式，像在 Excel 里点功能区。
- **Layer 3**：`ExcelFunctions` 一个类把上面**全部收在一起**，是推荐的「总入口」。

你不必一次全懂，会 `from excel_funcs import SUM` 就能先写起来。

## 安装

在终端进入本目录（与 `pyproject.toml` 同级）：

```bash
cd PyExcelFunctionsImpl
pip install -e .
```

开发本仓库时（跑测试、类型检查等）可装可选依赖：

```bash
pip install -e ".[dev]"
```

若使用虚拟环境（推荐，避免和系统 Python 混包）：

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

## 快速开始

```python
from excel_funcs import ExcelFunctions, SUM, IF

# 方式 A：大写名与 Excel 习惯接近（与 __init__.py 导出列表一致）
print(SUM(1, 2, 3, [4, 5]))  # 15.0
print(IF(True, "yes", "no"))

# 文本转数字在 Python 里叫 VALUE_FROM_TEXT，避免和错误值 VALUE（#VALUE!）重名
from excel_funcs import VALUE_FROM_TEXT
print(VALUE_FROM_TEXT("123.45"))

# 方式 B：用 ExcelFunctions 分类访问（对 IDE 补全更友好）
xf = ExcelFunctions()
print(xf.math.sum(1, 2, 3))
print(xf.logical.if_(True, "A", "B"))
```

**内置一行演示**（打印几行样例到终端）：

```bash
python -m excel_funcs
```

**完整分类演示**（数学、文本、逻辑、查找、日期、财务等）见 [demo/README.md](demo/README.md)：

```bash
python -m demo.run_all
```

## 与 Microsoft Excel 的差异（重要）

| 主题 | 说明 |
|------|------|
| 单元格与区域 | Python 用 `list` / 嵌套 `list` 表示一维或二维数据；**空**常用 `None` 或 `""`，是否参与运算依函数实现而定。 |
| 日期 | 默认是 `datetime.date` / `datetime.datetime`；与 Excel 序列号互换规则见 [docs/design.md](docs/design.md)。 |
| 错误值 | `#N/A` 等用 `ExcelErrorValue` 单例（如 `NA`、`VALUE`）表示，可用 `ISERROR` 判断；与「抛异常」是两套机制。 |
| `IF` 短路 | Python 会先求值再分支，**不保证**与 Excel 一样「只算选中分支」；带副作用的表达式要谨慎。 |
| 数组/动态数组 | `UNIQUE`、`SORT` 等以 `list` 为简化实现，与 Excel 365 的溢出/维度细节可能不同。 |
| 区域格式 | 不使用各国小数点/千分位规则，**一律 Python 字面量**（如 `3.14`）。 |

## 项目布局（你克隆下来会看到什么）

```
PyExcelFunctionsImpl/
  pyproject.toml     # 包名、版本、依赖、构建方式（hatchling）
  README.md         # 本说明
  LICENSE           # 开源协议（MIT）
  src/excel_funcs/  # 可 import 的包名：excel_funcs
    __init__.py     # 对外导出的「列表」与版本号
    engine.py       # Layer 3：ExcelFunctions
    facades.py      # Layer 2：MathFuncs、TextFuncs…
    math_agg.py 等  # Layer 1：按主题拆分的实现文件
  docs/             # 新手入门、设计说明、函数清单
  tests/            # 自动化测试（pytest）
  demo/             # 可运行的多示例脚本（学函数用）
```

- **想改实现**：进 `src/excel_funcs/`，用编辑器搜索函数名（如 `def SUM`）。
- **想确认有没有某个 Excel 函数**：看 [docs/function-list.md](docs/function-list.md)。

## 发布到 PyPI

1. 在 [PyPI](https://pypi.org) 搜索，确认发行名 **`excel-funcs-py`**（`pyproject.toml` 中 `[project] name`）尚未被占用。  
2. 安装工具：`pip install build twine`  
3. 构建：`python -m build`（生成 `dist/` 下 `.tar.gz` 和 `.whl`）  
4. 检查：`twine check dist/*`  
5. 可先到 TestPyPI 试传：`twine upload --repository testpypi dist/*`  
6. 正式上传：`twine upload dist/*`  

请使用 **API token** 等安全凭据，**不要**把 token 写进仓库或截图公开。

**说明**：PyPI 上的**项目名**（`excel-funcs-py`）与 Python 里 **import 的名字**（`excel_funcs`）可以不同，这是常见做法。

## 许可证

[MIT](LICENSE) — 可自由使用、修改、再发布，但需保留版权与许可声明。
