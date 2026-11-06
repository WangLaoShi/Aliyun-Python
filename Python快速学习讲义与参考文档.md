# Python 快速学习讲义与参考文档

> **用途**：在较短时间内系统回顾 Python 语法与常用写法，并作为日常查阅手册。内容整理自《阿里云天池 Python 训练营》Part1–Part5，并补充职场常见操作与 Excel 函数在 Python/pandas 中的对应思路。  
> **使用方式**：按章节顺序适合入门速通；目录可直接跳转到所需条目。  
> **配套练习与扩展示例**：[Python快速学习讲义-扩展示例与练习.md](Python快速学习讲义-扩展示例与练习.md)（与本文 §0–§12、附录 A/B 逐节对照，含例题与参考答案）。

---

## 目录

- [0. 中英术语速查](#0-中英术语速查)
- [1. 程序是什么 · Python 怎么写](#1-程序是什么--python-怎么写)
- [2. 对象、变量与命名](#2-对象变量与命名)
- [3. 数字与字符串](#3-数字与字符串)
- [4. 运算符](#4-运算符)
- [5. 模块、包与第三方库](#5-模块包与第三方库)
- [6. 条件与循环](#6-条件与循环)
- [7. 推导式](#7-推导式)
- [8. 字符串进阶](#8-字符串进阶)
- [9. 列表、元组、字典、集合](#9-列表元组字典集合)
- [10. 函数](#10-函数)
- [11. 面向对象入门](#11-面向对象入门)
- [12. 异常处理](#12-异常处理)
- [附录 A 职场常用片段](#附录-a-职场常用片段)
- [附录 B Excel 函数与 Python / pandas 对照](#附录-b-excel-函数与-python--pandas-对照)
- [来源与使用说明](#来源与使用说明)

---

## 0. 中英术语速查

| 英文 | 中文 |
|------|------|
| int / float / bool | 整数 / 浮点数 / 布尔 |
| str / list / tuple / dict / set | 字符串 / 列表 / 元组 / 字典 / 集合 |
| if / elif / else | 条件分支 |
| for / while / break / continue | 循环 / 跳出与继续 |
| def / return / lambda | 定义函数 / 返回 / 匿名函数 |
| import / from ... import | 导入模块 |
| class / method / self | 类 / 方法 / 自身引用 |
| try / except / finally / raise | 异常捕获与抛出 |
| iterator / generator | 迭代器 / 生成器 |

---

## 1. 程序是什么 · Python 怎么写

程序是指令的集合，常见类别包括：**输入**、**输出**、**数学运算**、**条件执行**、**重复执行**。再复杂的软件也可拆解为上述基本操作的组合。

**形式语言**（如编程语言）语法严格、歧义少；**自然语言**歧义多、冗余多。读代码时要在脑中解析**记号**（token）与**结构**（缩进、括号配对等），细节错误常直接导致运行失败。

Python 用**缩进**（通常 4 个空格）表示代码块，同一层级必须一致。

```python
# 单行注释以 # 开头

"""
多行字符串可作文档字符串（docstring），
常用于模块/函数说明。
"""

print("Hello", end=" ")
print("World")
# name = input("请输入姓名：")  # 交互环境可取消注释试运行
```

---

## 2. 对象、变量与命名

Python 中数据皆为**对象**。对象有：

- **身份**：`id(x)`，内存中地址标识（进程内可区分对象，数值不必死记）。
- **类型**：`type(x)`，如 `int`、`str`、`list`。
- **值**：具体数据；有的类型**不可变**（如 `int`、`str`、`tuple`），有的**可变**（如 `list`、`dict`、`set`）。

**变量**是绑定到对象的名称：`a = 1` 表示名称 `a` 引用整数对象 `1`。

**命名规则**：字母、数字、下划线；**不能**以数字开头；**不能**与关键字冲突；避免使用无意义单字母（循环索引 `i` 除外）。

```python
x = 10
y = x
print(id(x), id(y))  # 小整数可能被缓存，id 可能相同
print(type(x))
```

---

## 3. 数字与字符串

### 3.1 数字

- **整数 `int`**、**浮点数 `float`**、**复数 `complex`**（一般入门少用）。
- 转换：`int()`、`float()`、`str()`。

```python
print(int("99"), float("3.14"))
print(10 / 3)   # 真除法，结果为 float
print(10 // 3)  # 地板除
print(10 % 3)   # 取余
print(2 ** 10)  # 幂
```

### 3.2 字符串 `str`

用成对单引号或双引号表示。转义：`\n` 换行、`\t` 制表符等；**原始字符串**前缀 `r"..."` 中反斜杠不转义。

```python
s = "ab" + "cd"      # 连接
print("ha" * 3)      # 重复
print(r"C:\new")     # 原始字符串
```

---

## 4. 运算符

### 4.1 算术

`+ - * / // % **`（见上）。`+` 还可连接序列（字符串、列表、元组）；`*` 可对序列做重复。

### 4.2 比较

`== != < > <= >=`，结果为 `bool`。

### 4.3 逻辑

`and` `or` `not`。**短路求值**：`a and b` 若 `a` 为假则不计算 `b`。

### 4.4 成员与同一性

- `in` / `not in`：成员检测。
- `is` / `is not`：是否同一对象（少用；判断 `None` 用 `x is None`）。
- 一般比较**值**用 `==`，不要用 `is` 比较可能驻留的小整数以外的值。

```python
print(3 < 5 and 5 < 9)
print("a" in "abc")
```

---

## 5. 模块、包与第三方库

**模块**：`.py` 文件；**包**：含 `__init__.py` 的目录（Python 3.3+ 命名空间包可无此文件，但传统包仍常见）。

```python
import math
from math import sqrt
print(sqrt(16))

# import 别名
import datetime as dt
print(dt.date.today())
```

安装第三方库（在终端）：

```bash
pip install 包名
pip install pandas openpyxl
pip list
pip install --upgrade 包名
```

建议使用**虚拟环境**（`python -m venv .venv`）隔离项目依赖。

---

## 6. 条件与循环

### 6.1 `if`

```python
score = 85
if score >= 90:
    grade = "A"
elif score >= 60:
    grade = "C"
else:
    grade = "D"

# 条件表达式（三元）
label = "及格" if score >= 60 else "不及格"
```

### 6.2 `assert`

条件为假时抛出 `AssertionError`，适合调试与契约检查。

```python
assert score >= 0, "分数不能为负"
```

### 6.3 `while`

```python
n, s = 1, 0
while n <= 5:
    s += n
    n += 1
print(s)  # 15
```

### 6.4 `for` 与 `range`

```python
for ch in "abc":
    print(ch)

for i in range(3):       # 0,1,2
    print(i)

for i in range(1, 5, 2): # 1,3
    print(i)

# break / continue
for i in range(10):
    if i == 3:
        continue
    if i == 7:
        break
    print(i, end=" ")
```

### 6.5 `pass`

占位，语法上需要语句但暂无逻辑时使用。

---

## 7. 推导式

列表 / 集合 / 字典推导是构建容器的简洁写法。

```python
squares = [x * x for x in range(5)]
evens = [x for x in range(10) if x % 2 == 0]

unique_len = {len(w) for w in ["aa", "bbb", "aa"]}

m = {x: x ** 2 for x in (1, 2, 3)}
```

---

## 8. 字符串进阶

**切片**：`s[start:end:step]`，`end` 不含；负索引从末尾计；`s[::-1]` 反转。

```python
s = "Python与Excel"
print(s[0], s[-1])
print(s[2:9])
print(s[::2])
```

常用方法：

- `len(s)` 长度；`s.count(sub)` 子串出现次数。
- `s.find(sub)` 找不到返回 `-1`；`s.index(sub)` 找不到抛异常。
- `s.strip()` / `lstrip()` / `rstrip()` 去空白。
- `s.split(sep)` 分割；`sep.join(iterable)` 连接。
- `s.replace(old, new)`；`s.startswith` / `s.endswith`。

```python
line = "  a,b,c  "
print(line.strip().split(","))
print("-".join(["2026", "04", "05"]))
```

---

## 9. 列表、元组、字典、集合

### 9.1 列表 `list`（可变、有序）

```python
a = [1, 2, 3]
a.append(4)
a.extend([5, 6])
a.insert(0, 0)
x = a.pop()
a[1] = 99
a.sort()              # 原地排序
b = sorted([3, 1, 2]) # 新列表
```

### 9.2 元组 `tuple`（不可变、有序）

```python
t = (1, 2, 3)
# t[0] = 0  # 错误
one, two = (1, 2)  # 解包
```

### 9.3 字典 `dict`（键值映射）

```python
d = {"name": "Li", "age": 20}
print(d.get("age"), d.get("city", "未知"))
for k, v in d.items():
    print(k, v)
d["city"] = "Beijing"
```

### 9.4 集合 `set`（无序、元素唯一）

```python
s1 = {1, 2, 3}
s2 = {2, 3, 4}
print(s1 | s2, s1 & s2, s1 - s2)
```

---

## 10. 函数

```python
def add(a, b=0):
    """返回 a 与 b 的和。"""
    return a + b

print(add(3), add(3, 4))
```

- **位置参数**在前，**默认参数**在后；默认参数在定义时求值一次（可变默认值慎用）。
- **可变位置参数** `*args`，**可变关键字参数** `**kwargs`：

```python
def f(a, *args, **kwargs):
    print(a, args, kwargs)

f(1, 2, 3, x=9)
```

- **lambda**：单行匿名函数：`lambda x: x * 2`。
- **作用域**：函数内赋值默认创建局部变量；读外层变量可读；若需修改外层用 `nonlocal`（嵌套）或 `global`（模块级），应谨慎使用。

---

## 11. 面向对象入门

```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def intro(self):
        return f"{self.name}, {self.age} 岁"


class Worker(Student):
    def __init__(self, name, age, job):
        super().__init__(name, age)
        self.job = job

    def intro(self):  # 重写
        return super().intro() + f", {self.job}"


w = Worker("王", 30, "Dev")
print(w.intro())
```

- **封装**：对外暴露接口，内部状态通过方法访问。
- **继承**：子类复用父类行为并可重写。
- **多态**：同一接口不同类可有不同实现。
- **“私有”约定**：单下划线 `_attr` 表示内部使用；名称改写 `__attr` 触发名称修饰（了解即可）。

---

## 12. 异常处理

```python
try:
    x = int("abc")
except ValueError as e:
    print("转换失败:", e)
else:
    print("无异常时执行")
finally:
    print("总会执行")

def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为 0")
    return a / b
```

常见异常：`ValueError`、`TypeError`、`KeyError`、`IndexError`、`FileNotFoundError` 等。

---

## 附录 A 职场常用片段

### A.1 路径与文本文件

```python
from pathlib import Path

root = Path(".")
p = root / "data" / "note.txt"
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text("hello\n", encoding="utf-8")
print(p.read_text(encoding="utf-8"))
```

### A.2 JSON

```python
import json

data = {"ok": True, "items": [1, 2, 3]}
s = json.dumps(data, ensure_ascii=False)
obj = json.loads(s)
```

### A.3 CSV

```python
import csv

with open("t.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["name", "score"])
    w.writerow(["Amy", 90])

with open("t.csv", encoding="utf-8") as f:
    for row in csv.reader(f):
        print(row)
```

### A.4 环境变量

```python
import os

token = os.environ.get("API_TOKEN", "")
```

### A.5 日期时间

```python
from datetime import date, datetime, timedelta

today = date.today()
now = datetime.now()
later = now + timedelta(days=7)
print(today.isoformat(), now.strftime("%Y-%m-%d %H:%M:%S"))
```

### A.6 正则 `re`

```python
import re

m = re.search(r"\d+", "abc123def")
print(m.group() if m else None)
print(re.findall(r"\w+", "a b,c"))
```

### A.7 调用外部命令

```python
import subprocess

r = subprocess.run(["python", "--version"], capture_output=True, text=True)
print(r.stdout.strip())
```

### A.8 表格数据（pandas，需安装）

```python
import pandas as pd

df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
print(df.head())
# 读 xlsx 需 openpyxl：pd.read_excel("file.xlsx", engine="openpyxl")
```

---

## 附录 B Excel 函数与 Python / pandas 对照

下列与 [阿里云天池Python训练营-Part5.md](阿里云天池Python训练营-Part5.md) 中 Excel 说明对应；表格场景优先用 **pandas** 表达。

| Excel | 含义（简述） | Python / pandas 思路 |
|-------|----------------|------------------------|
| MID | 从指定位置截取指定长度 | 字符串切片；`Series.str.slice` |
| CONCATENATE / & | 拼接文本 | `+`、`''.join`、`Series.str.cat` |
| AND | 多条件全为真 | `cond1 & cond2`（注意加括号）；`df.query` |
| IF | 条件取值 | `np.where`；`Series.where` / `mask` |
| DATEDIF | 日期间隔（年/月/日等） | `datetime` 相减；`Series.dt`；`DateOffset` |
| COUNTIF | 条件计数 | `(s == v).sum()`；`(s > 0).sum()` |
| SUMIF | 条件求和 | `df.loc[mask, "金额"].sum()` |
| DCOUNT | 数据库条件计数 | 筛选后 `len(df)` 或 `df.shape[0]` |

### B.1 MID

```python
text = "ABCDEFGH"
# Excel MID(text, 3, 4) → 从第3字符起4个（Excel 中起始为1）
excel_style = text[2:6]  # Python 0 起始：第3字符索引为2
print(excel_style)

import pandas as pd
s = pd.Series(["abcdef", "123456"])
print(s.str.slice(1, 5))  # 类似 Python slice [1:5)
```

### B.2 CONCATENATE / &

```python
first, last = "Li", "Ming"
print(first + last)
print("".join([first, last]))

import pandas as pd
df = pd.DataFrame({"a": ["x", "y"], "b": ["1", "2"]})
print(df["a"].str.cat(df["b"], sep="-"))
```

### B.3 AND

```python
import pandas as pd

df = pd.DataFrame({"x": [1, 5, 10], "y": [2, 6, 2]})
mask = (df["x"] > 3) & (df["y"] > 1)  # 位与要对每条件加括号
print(df.loc[mask])  # 第 2、3 行满足
```

### B.4 IF

```python
import numpy as np
import pandas as pd

s = pd.Series([55, 72, 90])
print(np.where(s >= 60, "及格", "不及格"))
print(s.where(s >= 60, other=0))  # 不满足处替换
```

### B.5 DATEDIF（用日期差近似）

Excel 的 DATEDIF 各单位规则较细；Python 用 `datetime` 与 `relativedelta`（`dateutil` 库）或 pandas 处理。

```python
from datetime import date

d1 = date(2020, 1, 15)
d2 = date(2026, 4, 5)
print((d2 - d1).days)  # 总天数

# 满月、满年等更复杂需求可用 dateutil.relativedelta 或 pandas
import pandas as pd
ts = pd.to_datetime(["2020-01-15", "2026-04-05"])
print((ts.iloc[1] - ts.iloc[0]).days)
```

### B.6 COUNTIF

```python
import pandas as pd

s = pd.Series([1, -2, 5, 5, 139])
print((s == 5).sum())
print((s < 0).sum())
print((s != 0).sum())

# 不重复个数（对照 Part5 中数组公式思路）
print(s.nunique())
```

### B.7 SUMIF

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["文胸A", "文胸B", "其他"],
    "qty": [3, 10, 2],
})
mask = df["name"].str.startswith("文胸", na=False)
print(df.loc[mask, "qty"].sum())
```

### B.8 DCOUNT（条件计数）

```python
import pandas as pd

df = pd.DataFrame({
    "date": ["2026-10-08", "2026-10-10", "2026-10-15"],
    "amt": [100, 200, 150],
})
sub = df.query("amt >= 150")
print(len(sub))  # 满足条件的记录数
```

---

## 来源与使用说明

- 本讲义由 **《阿里云天池 Python 训练营》** 教材 Part1–Part5 提炼重组，并增加附录 A、B 的通用工程示例；原教材在国际人学校组织的训练营中使用，由林肯老师等组织编辑（参见各 Part 文首说明）。
- 原教材以 **CC 开源** 精神传播知识；整理稿同样欢迎学习与非独占性再利用，**请保留原始来源**（阿里云天池 Python 训练营 / 本仓库讲义文件名）。
- 若运行示例依赖第三方库，请先：`pip install pandas openpyxl`（读 Excel 时常用）。

---

*文档版本：与仓库内容同步维护。*
