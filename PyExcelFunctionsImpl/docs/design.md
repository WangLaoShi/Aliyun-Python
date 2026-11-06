# 设计说明

> **第一次接触本仓库？** 请先读 [beginner-guide.md](beginner-guide.md)（更白话），再回来看本文的**约定**与**术语**。

## 三层架构

1. **Layer 1**（`math_agg.py`、`text.py`、`logical.py` 等）：无状态纯函数，便于单测与组合。
2. **Layer 2**（`facades.py`）：`MathFuncs`、`TextFuncs` 等，将 Layer 1 绑定为 `staticmethod`。
3. **Layer 3**（`engine.py`）：`ExcelFunctions` 聚合各 Facade。

## 错误值与 ``VALUE`` 命名

- Excel 错误 ``#VALUE!`` 对应单例 ``excel_funcs.errors.VALUE``。
- 工作表函数 ``VALUE``（文本转数字）在 Python 中实现为 ``VALUE_FROM_TEXT``，避免与上述错误常量同名冲突；Facade 仍暴露为 ``xf.text.value(...)``。

## 日期系统

- 序列号与 `datetime.date` 互转采用锚点 **1899-12-30**（与常见开源库对 Windows Excel 的兼容方式一致），未完整模拟 Excel 1900 年闰年 bug。

## 与 Excel 的差异摘要

- 公式**短路求值**：``IF`` 在 Python 中会先计算两个分支。
- **区域**：以嵌套 `list` 表示；隐藏行、三维引用未实现。
- **INDIRECT**：未传扩展参数 ``workbook`` 时返回 ``#REF!``；可传入 ``workbook={"A1": 值, ...}``（键大小写不敏感）模拟地址解析。
- **OFFSET**：对二维 ``list`` 从左上角按 ``(rows, cols)`` 偏移并可选 ``height`` × ``width`` 切片；越界 ``#REF!``。
- **LENB**：本库按 **UTF-8 字节长度**；Excel DBCS 区域下 ``LENB`` 与中文/日文传统结果可能不同。
