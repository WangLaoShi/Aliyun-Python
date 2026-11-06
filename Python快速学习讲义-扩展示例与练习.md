# Python 快速学习讲义 — 扩展示例与练习

本文件与 [Python快速学习讲义与参考文档.md](Python快速学习讲义与参考文档.md) **逐节对照**：每节包含「对照要点」「扩展示例」「练习题」「参考答案」。建议先阅读主文档对应小节，再在本文中动手敲代码。

---

## 目录（对照主文档）

| 主文档章节 | 本文锚点 |
|------------|----------|
| §0 术语速查 | [§0](#0-中英术语速查--扩展示例与练习) |
| §1 程序与写法 | [§1](#1-程序是什么--python-怎么写--扩展示例与练习) |
| §2 对象与变量 | [§2](#2-对象变量与命名--扩展示例与练习) |
| §3 数字与字符串 | [§3](#3-数字与字符串--扩展示例与练习) |
| §4 运算符 | [§4](#4-运算符--扩展示例与练习) |
| §5 模块与包 | [§5](#5-模块包与第三方库--扩展示例与练习) |
| §6 条件与循环 | [§6](#6-条件与循环--扩展示例与练习) |
| §7 推导式 | [§7](#7-推导式--扩展示例与练习) |
| §8 字符串进阶 | [§8](#8-字符串进阶--扩展示例与练习) |
| §9 容器 | [§9](#9-列表元组字典集合--扩展示例与练习) |
| §10 函数 | [§10](#10-函数--扩展示例与练习) |
| §11 面向对象 | [§11](#11-面向对象入门--扩展示例与练习) |
| §12 异常 | [§12](#12-异常处理--扩展示例与练习) |
| 附录 A | [附录 A](#附录-a-职场常用片段--扩展示例与练习) |
| 附录 B | [附录 B](#附录-b-excel-与-pandas--扩展示例与练习) |

---

## 0. 中英术语速查 — 扩展示例与练习

### 对照要点

主文档 §0 是检索表。学习时不必死记英文拼写，但要能在报错信息里认出 **TypeError、KeyError** 等关键词，便于搜索解决方案。

### 扩展示例

```python
# 故意触发常见异常，观察英文关键词（运行后阅读 Traceback）
# int("x")        # ValueError
# [][1]           # IndexError
# {}["no_key"]    # KeyError
```

### 练习

1. **基础**：写出与「整数、列表、字典、定义函数」对应的英文术语各一个。
2. **进阶**：在 Python 交互环境中执行 `help(str.split)`，记下文档里出现的 2 个英文动词（如 return、split）。

### 参考答案

1. 例如：`int`、`list`、`dict`、`def`（或 `function` 作一般用语）。
2. 示例：`Return`、`split`（以实际 `help` 输出为准）。

---

## 1. 程序是什么 · Python 怎么写 — 扩展示例与练习

### 对照要点

理解 **缩进即结构**：同一层级对齐；增加一层缩进表示「从属于上一行带冒号的语句」。

### 扩展示例

```python
# 错误示范（若取消下面三行注释会 SyntaxError）：if 下一行未缩进
# if True:
# print("不会执行")

# 正确：多层缩进
score = 92
if score >= 60:
    if score >= 90:
        print("优秀")
    else:
        print("及格")
```

`print` 的 `sep` 与 `end` 参数便于控制输出格式：

```python
print("2026", "04", "05", sep="-")
for i in range(3):
    print(i, end=" ")
print()  # 换行
```

### 练习

1. **基础**：编写程序，在同一行打印 `A`、`B`、`C`，中间用竖线 `|` 分隔（查 `print` 的 `sep`）。
2. **进阶**：用两层 `if` 判断：变量 `n` 为正偶数时打印 `"ok"`，否则不打印。

### 参考答案

```python
# 1
print("A", "B", "C", sep="|")

# 2
n = 4
if n > 0:
    if n % 2 == 0:
        print("ok")
```

---

## 2. 对象、变量与命名 — 扩展示例与练习

### 对照要点

**赋值**是绑定名字到对象；`a = b` 后 `a`、`b` 可能指向同一对象（可变对象要小心「共享引用」）。

### 扩展示例

```python
# 不可变：重新赋值不影响另一个名字
a = "hi"
b = a
a = "bye"
print(b)  # hi

# 可变：两个名字指向同一列表时，改一处两处都变
x = [1, 2]
y = x
x.append(3)
print(y)  # [1, 2, 3]
```

### 练习

1. **基础**：预测并运行：`m = [10]; n = m; m = [20]` 后 `print(n)` 输出什么？
2. **进阶**：为什么 `x is y` 在上一段「列表共享」代码里通常为 `True`？再新建 `z = list(x)` 后 `x is z` 是 True 吗？

### 参考答案

1. `n` 仍为 `[10]`，因为 `m` 后来指向了新列表 `[20]`，`n` 仍指向原列表。
2. `x`、`y` 指向同一列表对象，故 `x is y` 为 True。`z = list(x)` 创建新列表，内容相同但是新对象，`x is z` 为 False。

---

## 3. 数字与字符串 — 扩展示例与练习

### 对照要点

**浮点误差**：二进制浮点不能精确表示所有十进制小数；金额等场景可用 `decimal.Decimal`。

### 扩展示例

```python
print(0.1 + 0.2)  # 常不是 0.3 的精确十进制显示

from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2"))

# 字符串与数字不能混算
# "10" - 5  # TypeError
print(int("10") - 5)
```

### 练习

1. **基础**：用 `//` 和 `%` 计算 17 除以 5 的商和余数。
2. **进阶**：用户输入为字符串 `"3.14"`，如何安全转为浮点数并加 1？

### 参考答案

```python
# 1
print(17 // 5, 17 % 5)

# 2
s = "3.14"
print(float(s) + 1)
```

---

## 4. 运算符 — 扩展示例与练习

### 对照要点

**短路**：`a and b` 若 `a` 假则不再求 `b`；`a or b` 若 `a` 真则不再求 `b`。可用于设置默认值：`name = s or "匿名"`。

### 扩展示例

```python
# 链式比较
x = 5
print(1 < x < 10)

# 注意：不要用 is 比较大整数或字符串内容
a = 300
b = 300
print(a == b, a is b)  # True True 或 True False 依实现而定，比较值请用 ==
```

### 练习

1. **基础**：表达式 `(3 > 5) and print("hi")` 会打印吗？为什么？
2. **进阶**：用 `in` 判断字符串 `s` 是否同时包含 `"@"` 和 `"."`（简单邮箱形状检测，不要求 RFC 完备）。

### 参考答案

1. 不会打印。`3 > 5` 为 False，`and` 短路，右侧 `print` 不求值。
2. `("@" in s) and ("." in s)`。

---

## 5. 模块、包与第三方库 — 扩展示例与练习

### 对照要点

`from math import *` 会污染命名空间，教学与工程中更推荐 `import math` 或 `from math import sqrt`。

### 扩展示例

```python
import random
print(random.randint(1, 6))  # 骰子

# 查看模块位置
import math
print(math.__file__)
```

### 练习

1. **基础**：写一行代码求 `sqrt(2)`，使用 `import math` 形式。
2. **进阶**：新建文件 `mymod.py`，内含 `def greet(name): return "Hi, " + name`，在另一段代码中用 `import mymod` 调用（需在同一目录或 `PYTHONPATH` 下）。

### 参考答案

```python
# 1
import math
print(math.sqrt(2))

# 2（示意）
# import mymod
# print(mymod.greet("Ada"))
```

---

## 6. 条件与循环 — 扩展示例与练习

### 对照要点

`for` 遍历**可迭代对象**；`range` 常用于固定次数循环。`while` 需确保某时刻条件能变为假，避免死循环。

### 扩展示例

```python
# 累加 1 到 100
print(sum(range(1, 101)))

# enumerate 同时需要下标与元素
for i, ch in enumerate("abc"):
    print(i, ch)
```

### 练习

1. **基础**：用 `for` 打印 1 到 10 中所有偶数。
2. **进阶**：输入若干正整数（可用列表写死），统计大于平均值的个数（先求平均再遍历计数）。

### 参考答案

```python
# 1
for n in range(2, 11, 2):
    print(n)

# 2
nums = [3, 8, 1, 9, 2]
avg = sum(nums) / len(nums)
cnt = sum(1 for x in nums if x > avg)
print(cnt)
```

---

## 7. 推导式 — 扩展示例与练习

### 对照要点

推导式是**语法糖**：可读性优先时，不必强行一行写完；复杂逻辑用普通 `for` 更清晰。

### 扩展示例

```python
# 嵌套：先外后内对应 for 顺序
pairs = [(x, y) for x in range(2) for y in range(2)]
print(pairs)

# 字典：翻转键值（值必须可哈希时才能作新键）
inv = {v: k for k, v in {"a": 1, "b": 2}.items()}
```

### 练习

1. **基础**：用列表推导得到 `[0, 2, 4, 6, 8]`。
2. **进阶**：用集合推导从字符串 `"hello"` 得到出现过的字符集合。

### 参考答案

```python
# 1
print([x * 2 for x in range(5)])

# 2
print({c for c in "hello"})
```

---

## 8. 字符串进阶 — 扩展示例与练习

### 对照要点

**切片**不越界时很安全；`index` 找不到会崩，不确定时用 `find`。

### 扩展示例

```python
s = "2026-04-05"
parts = s.split("-")
print(parts)
y, m, d = parts
print(int(y))

# 格式化：f-string（推荐）
name = "Ada"
print(f"{name=!s}")  # name='Ada'，调试友好
```

### 练习

1. **基础**：字符串 `"abcde"`，取出中间字符（奇数长度时正中间一个）。
2. **进阶**：实现「去掉首尾空白后，若以 `http` 开头则打印 `yes`」。

### 参考答案

```python
# 1
s = "abcde"
mid = len(s) // 2
print(s[mid])

# 2
url = "  http://example.com  "
t = url.strip()
if t.startswith("http"):
    print("yes")
```

---

## 9. 列表、元组、字典、集合 — 扩展示例与练习

### 对照要点

列表**切片赋值**、字典**默认值**（`collections.defaultdict`）、集合**去重**是日常高频。

### 扩展示例

```python
from collections import defaultdict

dd = defaultdict(list)
dd["a"].append(1)
dd["a"].append(2)
print(dict(dd))

# 列表去重且保持顺序（3.7+ 字典有序）
items = [3, 1, 3, 2]
print(list(dict.fromkeys(items)))
```

### 练习

1. **基础**：合并两个字典 `d1`、`d2`（Python 3.9+ 可用 `{**d1, **d2}`）。
2. **进阶**：列表 `words` 中统计每个词出现次数，用字典完成（不用 `Counter` 先手写一遍）。

### 参考答案

```python
# 1
d1, d2 = {"a": 1}, {"b": 2}
print({**d1, **d2})

# 2
words = ["a", "b", "a", "a"]
count = {}
for w in words:
    count[w] = count.get(w, 0) + 1
print(count)
```

---

## 10. 函数 — 扩展示例与练习

### 对照要点

**可变默认参数陷阱**：默认不要用 `def f(x, lst=[])`，应改为 `def f(x, lst=None): lst = lst or []`。

### 扩展示例

```python
def bad(a, items=[]):
    items.append(a)
    return items

print(bad(1))  # [1]
print(bad(2))  # [1, 2] — 同一列表被复用！

def good(a, items=None):
    if items is None:
        items = []
    items.append(a)
    return items

print(good(1), good(2))  # [1] [2]
```

### 练习

1. **基础**：写函数 `max3(a, b, c)` 返回三者最大值（可用 `if` 或内置 `max`）。
2. **进阶**：写函数接收任意多个数 `*nums`，返回它们的平均值。

### 参考答案

```python
# 1
def max3(a, b, c):
    return max(a, b, c)

# 2
def avg(*nums):
    return sum(nums) / len(nums) if nums else 0

print(avg(1, 2, 3, 4))
```

---

## 11. 面向对象入门 — 扩展示例与练习

### 对照要点

**类变量**与**实例变量**区别：在 `__init__` 里赋给 `self.x` 的一般是实例属性；直接写在类体里且未挂 `self` 的可能是类属性（各实例共享）。

### 扩展示例

```python
class Counter:
    species = "counter"  # 类属性

    def __init__(self):
        self.n = 0

    def inc(self):
        self.n += 1
        return self.n


c1, c2 = Counter(), Counter()
c1.inc()
print(c1.n, c2.n)  # 1 0
print(c1.species, Counter.species)
```

### 练习

1. **基础**：定义 `Rectangle(w, h)`，方法 `area()` 返回面积。
2. **进阶**：定义 `Square(Rectangle)` 子类，只接受边长 `s`，内部调用父类初始化。

### 参考答案

```python
# 1
class Rectangle:
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h


# 2
class Square(Rectangle):
    def __init__(self, s):
        super().__init__(s, s)
```

---

## 12. 异常处理 — 扩展示例与练习

### 对照要点

**捕获具体异常**优于裸 `except:`；`finally` 里适合释放资源（文件等）；日常也可用**上下文管理器** `with`（见附录 A）。

### 扩展示例

```python
def safe_int(s, default=0):
    try:
        return int(s)
    except ValueError:
        return default

print(safe_int("99"), safe_int("x"))
```

### 练习

1. **基础**：用 `try/except` 捕获 `ZeroDivisionError`，在除数为 0 时返回 `None`。
2. **进阶**：写函数读文本文件路径，若文件不存在返回空字符串，不向外抛异常。

### 参考答案

```python
# 1
def div(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None


# 2
from pathlib import Path

def read_or_empty(path):
    p = Path(path)
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
```

---

## 附录 A 职场常用片段 — 扩展示例与练习

### 对照要点

与主文档 A.1–A.8 一一对应：路径、JSON、CSV、环境变量、时间、正则、子进程、pandas。

### A.1 路径与文本 — 扩展示例

```python
from pathlib import Path

# 遍历目录下所有 .txt
for p in Path(".").glob("*.txt"):
    print(p.name, p.stat().st_size)
```

**练习**：在当前目录创建 `data/a.txt`，写入两行文字，再读回并打印行数。

**参考**：

```python
from pathlib import Path
p = Path("data") / "a.txt"
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text("line1\nline2\n", encoding="utf-8")
print(len(p.read_text(encoding="utf-8").splitlines()))
```

### A.2 JSON — 扩展示例

```python
import json
obj = {"中文": "测试"}
s = json.dumps(obj, ensure_ascii=False)
print(s)
print(json.loads(s)["中文"])
```

**练习**：将列表 `[1,2,3]` 写入字符串再解析回 Python 对象。

### A.3 CSV — 扩展示例

**练习**：用 `csv.DictReader` 读取含表头的 CSV（自建 `demo.csv` 字符串用 `io.StringIO` 模拟也可）。

**参考**：

```python
import csv
import io

sample = "name,age\nAda,36\nBob,20\n"
f = io.StringIO(sample)
for row in csv.DictReader(f):
    print(row["name"], row["age"])
```

### A.4–A.7 — 小练习

1. 用 `os.environ.get("HOME", "")`（Windows 上可能是 `USERPROFILE`）打印用户主目录概念（跨平台仅作了解）。
2. 用 `datetime` 计算 30 天后的日期。
3. 用 `re.sub` 把字符串中所有数字换成 `#`。
4. `subprocess.run` 执行 `echo hello`（Windows 用 `cmd /c echo hello`）。

### A.8 pandas — 扩展示例

```python
import pandas as pd

df = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]})
print(df.describe())
print(df[df["x"] >= 2])
```

**练习**：构造 DataFrame，新增列 `z = x + y`。

**参考**：

```python
import pandas as pd
df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
df["z"] = df["x"] + df["y"]
print(df)
```

---

## 附录 B Excel 与 pandas — 扩展示例与练习

### 对照要点

Excel **行号从 1、列从 A** 思考；Python **索引从 0**。`MID(text, 3, 4)` 对应 Python 切片时先减 1 再切片。

### 扩展示例（综合小表）

```python
import numpy as np
import pandas as pd

df = pd.DataFrame({
    "产品": ["苹果", "苹果", "梨"],
    "数量": [5, 3, 2],
    "单价": [2.0, 2.0, 3.0],
})
df["金额"] = df["数量"] * df["单价"]
print(df.groupby("产品")["金额"].sum())
```

### 练习（与主文档 B.1–B.8 对应）

1. **MID**：对 Series `["ABCD", "EF"]` 取「从第 2 个字符起共 2 个」（Excel 习惯：起始 2，长度 2 → Python 切片 `[1:3]`）。
2. **IF**：新建列 `等级`，数量 ≥ 4 为 `"多"` 否则 `"少"`。
3. **COUNTIF**：统计 `产品` 列等于 `"苹果"` 的行数。
4. **SUMIF**：对 `产品=="苹果"` 的 `金额` 求和。
5. **不重复计数**：对 `产品` 列统计不重复值个数。

### 参考答案

```python
import numpy as np
import pandas as pd

s = pd.Series(["ABCD", "EF"])
# Excel MID(s,2,2) → 第2字符起2个 → 索引1起2个字符
print(s.str.slice(1, 3))

df = pd.DataFrame({
    "产品": ["苹果", "苹果", "梨"],
    "数量": [5, 3, 2],
})
df["单价"] = [2.0, 2.0, 3.0]
df["金额"] = df["数量"] * df["单价"]
df["等级"] = np.where(df["数量"] >= 4, "多", "少")

print((df["产品"] == "苹果").sum())
print(df.loc[df["产品"] == "苹果", "金额"].sum())
print(df["产品"].nunique())
```

（若不想依赖 `numpy`，可用：`df["等级"] = df["数量"].apply(lambda x: "多" if x >= 4 else "少")`。）

---

## 使用建议

1. **顺序**：与主文档同序刷一遍，每读完一节在本文做 1～2 道基础题即可。
2. **自测**：先盖住「参考答案」自己写，再对比差异。
3. **环境**：pandas 练习前执行 `pip install pandas numpy openpyxl`。

---

*与 [Python快速学习讲义与参考文档.md](Python快速学习讲义与参考文档.md) 配套使用。*
