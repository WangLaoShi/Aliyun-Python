# 第一章 · Python 一篇概全

> 从一份学生成绩，到一份可以验证的报告。
>
> 本章目标：建立 Python 编程的完整基础地图，能阅读、解释、修改和验证小程序。
>
> 阅读约定：**主线**适合课堂快速串讲；**补充**保留必要细节，课上可以略过；**动手**用于检查是否理解。示例以 Python 3 为准。标有“故意错误”的代码用于观察错误，其余代码块需注意是否承接前文变量。

## 01 · 先看全貌：程序是什么

### 主线：输入 → 处理 → 输出

程序是一组明确的指令。Python 解释器执行这些指令，把输入转换为输出。输入可以来自键盘、文件、网络，也可以直接写在代码里。

先读一段完整程序，不要求立刻记住每个符号：

```python
students = [
    {"name": "小林", "score": 85},
    {"name": "小陈", "score": 58},
    {"name": "小周", "score": 92},
]


def get_level(score):
    if score >= 90:
        return "优秀"
    elif score >= 60:
        return "及格"
    else:
        return "待提高"


for student in students:
    level = get_level(student["score"])
    print(f'{student["name"]}：{student["score"]} 分，{level}')
```

输出：

```text
小林：85 分，及格
小陈：58 分，待提高
小周：92 分，优秀
```

这段程序已经包含许多程序共有的结构：**用数据描述对象，用条件表达规则，用循环批量执行，用函数封装任务。**

### 补充：代码怎样运行

- `.py` 是常见的 Python 源文件后缀。在终端执行 `python lesson.py` 可以运行文件；部分电脑命令是 `python3`。
- 解释器可以交互执行单条语句；Notebook 则把代码分成单元运行。Notebook 的运行顺序会影响变量状态，必要时重启后从头运行。
- 编辑器负责编辑，解释器负责执行。编辑器装好了，不代表解释器和依赖已经配置好。
- 顶层语句通常从上到下执行；条件决定分支，循环重复执行，函数体通常要等调用才执行。
- `#` 后是单行注释，不参与执行。三引号表示多行字符串，放在模块、类或函数开头时可作说明文档，并非专门的多行注释语法。
- Python 用缩进表示代码块，通常每层使用 4 个空格，不混用 Tab 与空格。英文冒号 `:` 常表示代码块即将开始。
- `()` 常用于调用和分组，`[]` 常用于列表和索引，`{}` 常用于字典和集合；含义需要结合上下文判断。

### 动手

先预测再运行：把小陈的分数改为 `60`，输出会怎样变化？如果删掉最后三行，会发生什么？

**问 AI：**“请把这段程序分成数据、规则、执行三个部分说明，不要新增代码。最后问我一道检查理解的问题。”

## 02 · 数据、变量与类型

### 主线：变量是名字，值有类型

```python
name = "小林"          # str：字符串
score = 85             # int：整数
average = 78.5         # float：浮点数
passed = True          # bool：布尔值，True 或 False
comment = None         # None：当前没有值

print(name, score)
print(type(score))     # <class 'int'>
score = score + 5
print(score)           # 90
```

`=` 是赋值：先计算右侧，再把左侧名字绑定到结果。`==` 才是判断两个值是否相等。

```python
text_score = "85"
score = int(text_score)
print(score + 5)        # 90
print(str(score) + "分") # 85分
```

`input()` 的返回值是字符串，即使输入看起来是数字：

```python
# 需要键盘输入，适合在终端单独运行
text = input("请输入分数：")
score = float(text)
print(score)
```

### 补充：必须认识的细节

| 类型 | 用途 | 示例 | 常见误区 |
|---|---|---|---|
| `int` | 个数、整数计算 | `42`、`-3` | `/` 的结果通常不是整数 |
| `float` | 小数计算 | `3.14` | 二进制浮点不能精确表示所有十进制小数 |
| `str` | 文本 | `"85"`、`'小林'` | 数字字符串不等于数字 |
| `bool` | 真或假 | `True`、`False` | 大小写必须正确 |
| `NoneType` | 缺失、尚无结果 | `None` | 不等于 `0` 或空字符串 |

- 变量名区分大小写；通常用 `student_name`，不能以数字开头，也不要覆盖 `list`、`str`、`sum` 等内置名字。
- Python 的变量不要求提前声明固定类型；同一个名字可以重新绑定其他类型，但随意改变含义会降低可读性。
- `int("85")` 可以，`int("85.5")` 会报错；`int(85.9)` 截去小数部分，不是四舍五入。
- `bool("")` 是 `False`，`bool("False")` 是 `True`，因为后者是非空字符串。
- `None` 常用 `value is None` 判断。
- `0.1 + 0.2 == 0.3` 通常为 `False`；近似比较可用 `math.isclose()`。涉及精确金额时应进一步学习 `decimal.Decimal`。

### 动手

解释 `85`、`"85"`、`85.0` 的区别。为什么 `input()` 的结果不能直接与数字相加？

## 03 · 表达式、运算与字符串

### 主线：表达式会产生一个值

```python
chinese = 85
math = 92
average = (chinese + math) / 2
passed = chinese >= 60 and math >= 60

print(f"平均分：{average:.1f}，全部及格：{passed}")
```

f-string 在字符串前加 `f`，在 `{}` 中放表达式；`:.1f` 表示显示一位小数。

| 类别 | 常用符号 | 含义 |
|---|---|---|
| 算术 | `+ - * /` | 加、减、乘、除 |
| 算术 | `// % **` | 向下取整除法、余数、幂 |
| 比较 | `== != > >= < <=` | 比较，通常得到布尔值 |
| 逻辑 | `and or not` | 与、或、非 |
| 成员 | `in`、`not in` | 是否属于一个容器 |
| 身份 | `is`、`is not` | 是否为同一个对象 |
| 更新 | `+=`、`-=` | 常见的累计或更新写法 |

### 补充：字符串是有顺序的文本

```python
text = "  Python,AI  "
clean = text.strip()
print(clean.lower())             # python,ai
print(clean.upper())             # PYTHON,AI
print(clean.split(","))           # ['Python', 'AI']
print(" / ".join(["Python", "AI"])) # Python / AI
print(clean.replace("AI", "编程")) # Python,编程
print(clean[0])                  # P，索引从 0 开始
print(clean[-1])                 # I，-1 是最后一个
print(clean[0:6])                # Python，包含起点，不包含终点
print("Python" in clean)         # True
print(len(clean))                # 9
```

- 字符串不可变；`strip()`、`replace()` 等返回新字符串，要保留结果需要赋值。
- 切片格式为 `[起点:终点:步长]`，可省略部分参数。索引越界会报错，切片通常会截取到有效边界。
- `\n` 表示换行，`\t` 表示制表符；原始字符串如 `r"a\nb"` 通常保留反斜杠。
- 比较值相等用 `==`，不要用 `is` 比较分数或字符串内容。
- `and` 和 `or` 会短路，且可能返回操作数本身；入门时先用它们组合明确的判断条件。
- 空字符串、空容器、零、`None` 在条件中通常视为假。字符串 `"0"` 为真。
- 运算优先级不确定时加括号；`-3 // 2` 是 `-2`，因为向负无穷方向取整。

### 动手

把 `" 85分 "` 转为数字 `85`。再思考：遇到 `"缺考"`，还能使用相同步骤吗？

## 04 · 容器：从一个值到一组记录

### 主线：列表存一组，字典描述一条

```python
scores = [85, 58, 92]
print(scores[0])                # 85
scores.append(76)
print(len(scores))             # 4

student = {"name": "小林", "score": 85}
print(student["name"])
student["score"] = 90
student["class"] = "一班"

students = [
    {"name": "小林", "score": 85},
    {"name": "小陈", "score": 58},
]
print(students[1]["score"])     # 58
```

`students[1]["score"]` 表示：先取列表中的第二条记录，再取这条记录的分数。

### 补充：四种常见容器

| 容器 | 示例 | 顺序与修改 | 适用场景 |
|---|---|---|---|
| 列表 `list` | `[85, 58]` | 有序，可修改，允许重复 | 多条记录、可变序列 |
| 元组 `tuple` | `(120, 30)` | 有序，元素引用不可重新赋值 | 坐标、固定组合 |
| 字典 `dict` | `{"name": "小林"}` | 保留插入顺序，键唯一，可修改 | 属性、查找、映射 |
| 集合 `set` | `{"一班", "二班"}` | 不承诺索引顺序，元素唯一 | 去重、交集、成员判断 |

```python
scores = [85, 58, 92]
scores[1] = 60
scores.extend([70, 80])
last = scores.pop()             # 移除并返回最后一个
ordered = sorted(scores)       # 返回新的排序列表
scores.sort()                  # 原地排序，返回 None

student = {"name": "小林", "score": 85}
print(student.get("comment", "暂无评语"))
print(list(student.keys()))
print(list(student.values()))
print(list(student.items()))

classes = ["一班", "一班", "二班"]
unique_classes = set(classes)
print(len(unique_classes))      # 2
print({"一班", "二班"} & {"二班", "三班"}) # {'二班'}
```

- `[]` 是空列表，`{}` 是空字典，`set()` 才是空集合，`(1,)` 是单元素元组。
- 字典缺失键使用 `student["missing"]` 会报 `KeyError`；`.get()` 可设置默认值，但不应借默认值掩盖必须存在的字段。
- 字典的键和集合的元素需要可哈希；字符串、整数常用，列表和字典不能直接使用。
- `del student["score"]` 可删除键，`scores.remove(60)` 按值删除首个匹配元素；目标不存在会报错。
- 元组不可变不代表内部对象都不可变，例如元组中包含的列表仍可被修改。

### 补充：赋值不等于复制

```python
a = [85, 58]
b = a
b.append(92)
print(a)                       # [85, 58, 92]，二者指向同一个列表

c = a.copy()
c.append(100)
print(a)                       # [85, 58, 92]
```

`copy()` 是浅复制；嵌套容器的内部对象仍可能共享，需要完全独立时再学习 `copy.deepcopy()`。理解可变对象，有助于排查“明明只改了另一份数据”的错误。

### 动手

为每个学生增加班级信息。尝试解释“列表中的字典”和“字典中的列表”分别适合表示什么。

## 05 · 条件：把规则变成分支

### 主线：条件顺序就是规则的一部分

```python
score = 85

if not 0 <= score <= 100:
    print("分数无效")
elif score >= 90:
    print("优秀")
elif score >= 60:
    print("及格")
else:
    print("待提高")
```

在一组 `if / elif / else` 中，只执行第一个条件为真的分支。如果先判断 `score >= 60`，90 分也会先落入“及格”。

### 补充：独立判断与互斥判断

- 多个独立的 `if` 可能执行多次；一组 `if / elif / else` 最多执行一个分支。
- `if score:` 判断的是分数的真假，不等于判断是否及格，也不能区分零分和缺失。
- `label = "及格" if score >= 60 else "待提高"` 是条件表达式，适用于简短选择。
- 嵌套条件可以表达复杂规则，但层数过多时应考虑拆成函数。
- `pass` 是空操作占位符，不代表退出或跳过循环。
- 判断条件要考虑边界：`>= 60` 与 `> 60` 的含义不同。

### 动手

为上述程序列出预期：`-1`、`0`、`59`、`60`、`89`、`90`、`100`、`101`。先写预期，再运行核对。

## 06 · 循环：批量处理与重复执行

### 主线：遍历、判断、累计

```python
scores = [85, 58, 92, 60]
passed_count = 0

for score in scores:
    if score >= 60:
        passed_count += 1

print(f"及格人数：{passed_count}") # 3
```

`for` 适合遍历已有数据；`while` 适合在条件仍满足时持续执行。

```python
remaining = 3
while remaining > 0:
    print(f"剩余尝试次数：{remaining}")
    remaining -= 1
```

### 补充：常用循环工具

```python
scores = [85, 58, 92]

for index, score in enumerate(scores, start=1):
    print(index, score)

for number in range(3):         # 依次为 0、1、2
    print(number)

names = ["小林", "小陈", "小周"]
for name, score in zip(names, scores):
    print(name, score)

for score in scores:
    if score < 0:
        continue               # 跳过本次循环剩余部分
    if score == 100:
        break                  # 结束当前这一层循环
    print(score)
```

- `range(start, stop, step)` 不包含 `stop`；步长不能为零。
- `zip()` 默认以最短输入为准，长度不一致可能丢掉尾部记录。
- `while` 必须有明确的停止机制；缺少更新条件可能形成无限循环。
- 遍历列表时直接删除其中元素可能漏处理记录，通常应构造新列表。
- 嵌套循环会增加处理次数，要警惕数据量增加后运行变慢。

### 补充：推导式与内置聚合

```python
scores = [85, 58, 92, 60]
passed_scores = [score for score in scores if score >= 60]
print(passed_scores)           # [85, 92, 60]
print(sum(scores))             # 295
print(min(scores), max(scores)) # 58 92
print(any(score < 60 for score in scores))  # True，至少一个
print(all(score >= 60 for score in scores)) # False，全部满足才为真
```

简单推导式可以压缩“遍历并生成结果”的代码。复杂逻辑先写普通循环。空列表不能直接用 `sum(scores) / len(scores)` 求均值；`min([])` 和 `max([])` 也会报错。

### 动手

输出所有不及格的学生姓名；再输出“第几条记录、姓名、分数”。解释为何零条记录时不能计算及格率。

## 07 · 函数：把步骤变成可复用的任务

### 主线：输入、处理、返回

```python
def get_level(score, pass_score=60):
    """根据分数返回等级。"""
    if score >= 90:
        return "优秀"
    if score >= pass_score:
        return "及格"
    return "待提高"


level = get_level(85)
print(level)                    # 及格
print(get_level(70, pass_score=75)) # 待提高
```

函数定义不会立即执行函数体；调用时才执行。`return` 返回结果并结束本次调用。函数应当有清楚的职责和输入约定，例如上例默认传入合法分数，并约定及格线不高于优秀线。

### 补充：参数与返回值

```python
def summarize(scores):
    if not scores:
        return {"count": 0, "average": None}
    return {"count": len(scores), "average": sum(scores) / len(scores)}


result = summarize([85, 58, 92])
print(result["count"])
print(result["average"])
```

- 参数是定义中的名字，实参是调用时传入的值。可按位置或关键字传参，默认参数可省略。
- `print()` 把内容显示出来；`return` 把值交给调用者。只有打印没有返回值的函数，调用结果是 `None`。
- `return count, average` 实际上返回一个元组，调用者可用 `count, average = ...` 解包。
- 函数内部赋值的名字通常是局部变量。优先通过参数传入数据、通过返回值交付结果，减少对全局变量的依赖。
- 函数可以修改传入的列表或字典，是否允许修改需要明确约定。
- `*args` 可接收额外的位置参数，`**kwargs` 可接收额外的关键字参数，第一遍能识别即可。
- `lambda x: x["score"]` 是一个简短匿名函数，例如 `sorted(students, key=lambda x: x["score"])`。

### 补充：两个重要习惯

避免把可变对象作为默认参数：

```python
def add_score(score, scores=None):
    if scores is None:
        scores = []
    scores.append(score)
    return scores
```

写成 `scores=[]` 时，默认列表会在多次调用间共享，可能产生意外结果。

类型提示表达约定，通常不会自动检查运行时输入：

```python
def is_passed(score: float) -> bool:
    return score >= 60
```

### 动手

写或让 AI 协助写一个 `calculate_pass_rate(scores)`。先约定：返回 0～1 的小数还是百分数？空列表返回什么？随后才实现代码。

## 08 · 对象与类：看懂点号后面的含义

### 主线：先会使用对象

在 Python 中，数字、字符串、列表、函数等都是对象。对象有类型，有些对象具有属性和方法。

```python
name = " 小林 "
print(name.strip())             # 调用字符串对象的方法

scores = [85, 58]
scores.append(92)               # 调用列表对象的方法
```

`对象.属性` 通常读取信息；`对象.方法(...)` 调用对象提供的操作。具体名称由类型决定。

### 补充：类描述一类对象

```python
class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def is_passed(self):
        return self.score >= 60


student = Student("小林", 85)
print(student.name)             # 属性
print(student.is_passed())      # 方法，True
```

- 类是创建某类对象的定义；实例是根据类创建的具体对象。
- `__init__` 在实例初始化时执行；`self` 按惯例表示当前实例。
- 字典也能表达学生记录；需要把状态和行为统一管理时，可以考虑定义类。小程序无需为了“面向对象”而强行建类。
- 封装、继承和多态属于后续主题。本章保留认识：封装组织状态与操作，继承扩展已有类，多态允许不同对象响应相同操作。
- `_name` 是内部使用的惯例；`__name` 涉及名称改写，不代表真正的安全隔离。
- `@property`、`@classmethod`、`@staticmethod`、`__slots__` 能在参考资料中继续学习，不影响阅读本章主线程序。

### 动手

比较 `student["name"]` 和 `student.name`：它们分别要求 `student` 是什么样的数据？

## 09 · 模块、包与运行环境

### 主线：复用已有能力

```python
import statistics
from pathlib import Path

scores = [85, 58, 92]
print(statistics.mean(scores))
print(Path.cwd())               # 当前工作目录
```

- 模块通常对应一个 `.py` 文件；包组织多个模块；库是对一组可复用能力的通称。
- 标准库随 Python 提供；第三方库通常需要额外安装。
- `import` 导入已可用的模块，不负责安装。安装分发包的名字与导入名有时不同。

### 补充：最小环境操作

以下是**终端命令，不是 Python 语句**。假设本机 Python 命令为 `python`：

```bash
python --version
python -m venv .venv
```

macOS / Linux 激活：

```bash
source .venv/bin/activate
```

Windows PowerShell 激活：

```powershell
.venv\Scripts\Activate.ps1
```

激活后安装、检查和记录依赖：

```bash
python -m pip install pandas openpyxl
python -m pip show pandas
python -m pip freeze > requirements.txt
python -m pip install -r requirements.txt
```

- 虚拟环境隔离不同项目的依赖。编辑器选择的解释器应与安装依赖时使用的解释器一致。
- `python -m pip` 有助于明确为哪个解释器安装；课程发放教师测试过的依赖清单，学生无需自行追逐最新版本。
- `requirements.txt` 记录依赖版本不代表在所有系统上都必然复现，还需要记录 Python 版本等条件。
- 不要把自己的文件命名为 `json.py`、`csv.py`、`statistics.py` 等，以免遮蔽要导入的模块。
- 自己的函数可保存到 `helpers.py`，再用 `from helpers import get_level` 导入。
- `if __name__ == "__main__":` 下的代码只在当前文件直接运行时执行，适合放程序入口，避免被导入时意外执行。

### 动手

出现 `ModuleNotFoundError` 时，先检查什么？让 AI 帮助区分“未安装”“装在另一个环境”“文件命名冲突”。

## 10 · 文件、路径与数据格式

### 主线：把内存中的结果保存下来

```python
from pathlib import Path

folder = Path("output")
folder.mkdir(parents=True, exist_ok=True)
report_path = folder / "report.txt"

report_path.write_text("小林：85 分，及格\n", encoding="utf-8")
content = report_path.read_text(encoding="utf-8")
print(content)
```

这段代码会在**当前工作目录**下创建 `output` 文件夹，并写入或覆盖 `report.txt`。

### 补充：打开文件与关闭文件

```python
with open("output/report.txt", "r", encoding="utf-8") as file:
    content = file.read()
print(content)
```

`with` 管理资源，离开代码块后自动关闭文件。常见模式：`r` 读取，`w` 写入并覆盖，`a` 追加，`rb` 读取二进制。

相对路径相对于当前工作目录，不一定相对于代码文件。普通脚本可用 `Path(__file__).resolve().parent` 定位脚本目录，Notebook 通常没有 `__file__`。

### 补充：CSV 与 JSON

CSV 适合二维表格；JSON 适合列表、字典等嵌套数据，也常见于 API。

```python
import csv
from pathlib import Path

Path("output").mkdir(exist_ok=True)
students = [{"name": "小林", "score": 85}, {"name": "小陈", "score": 58}]

with open("output/students.csv", "w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["name", "score"])
    writer.writeheader()
    writer.writerows(students)

with open("output/students.csv", encoding="utf-8-sig", newline="") as file:
    records = list(csv.DictReader(file))

print(records[0]["score"])       # '85'，CSV 读取后通常需要转换类型
```

```python
import json

student = {"name": "小林", "score": 85, "comment": None}
text = json.dumps(student, ensure_ascii=False, indent=2)
print(text)
restored = json.loads(text)
print(restored["name"])
```

JSON 的对象键是字符串，`true / false / null` 对应 Python 的 `True / False / None`。`dumps / loads` 处理字符串，`dump / load` 面向文件对象。JSON 与 Python 字典的写法相似，但不是同一种语言格式。

读取、覆盖、移动、删除文件之前，确认路径和作用范围；练习使用副本与专用输出目录，不覆盖原始数据。

### 动手

把及格学生保存成新 CSV；再次读入，核对人数与分数类型。为什么不能把 CSV 内容直接按逗号拆分？考虑字段内部含逗号的情况。

## 11 · 错误、异常与调试

### 主线：报错是定位线索

| 类型 | 例子 | 处理思路 |
|---|---|---|
| 语法错误 | 少了冒号、括号不匹配 | 先让代码符合语法 |
| 运行异常 | 除以零、文件不存在、类型不匹配 | 检查输入、环境与调用 |
| 逻辑错误 | 60 分被判为不及格 | 用明确的预期验证规则 |

读 Traceback 时，先看最后的异常类型和消息，再找自己代码中的文件名、行号，查看有关变量的值和类型。

```python
raw = "缺考"

try:
    score = float(raw)
except ValueError:
    print("分数不是有效数字，请检查输入")
else:
    print(f"转换成功：{score}")
finally:
    print("本次检查结束")
```

### 补充：主动拒绝错误输入

```python
import math


def parse_score(raw):
    if isinstance(raw, bool):
        raise ValueError("布尔值不能作为分数")
    score = float(raw)
    if not math.isfinite(score) or not 0 <= score <= 100:
        raise ValueError("分数必须是 0～100 之间的有限数")
    return score
```

- 常见异常：`NameError` 未定义名字，`TypeError` 类型不匹配，`ValueError` 值不合要求，`IndexError` 索引越界，`KeyError` 键不存在，`FileNotFoundError` 文件不存在。
- `raise` 主动抛出异常；`except` 处理预期异常。不要用宽泛捕获后 `pass` 来隐藏问题。
- `else` 在没有异常时执行；`finally` 通常用于无论成功失败都需执行的清理。
- `float("nan")` 和 `float("inf")` 可以转换成功，但不适合作为正常分数，因此校验不应止于“能转为数字”。
- 调试可以从打印 `repr(value)` 和 `type(value)` 开始，再逐步学习断点与调试器。

### 动手

把 `""`、`"85"`、`"缺考"`、`"101"`、`"nan"` 分别传入 `parse_score()`，预测并核对结果。不要为了让程序继续运行，偷偷把缺考改成零分。

## 12 · 验证：能运行不等于做对了

### 主线：先写预期，再检验结果

```python
def get_level(score):
    if score >= 90:
        return "优秀"
    if score >= 60:
        return "及格"
    return "待提高"


assert get_level(59) == "待提高"
assert get_level(60) == "及格"
assert get_level(90) == "优秀"
print("检查通过")
```

测试不是证明程序永远正确，而是用有代表性的样例检查重要行为，降低修改后出错的可能。

### 补充：一份最小验证清单

| 检查方向 | 成绩场景中的例子 |
|---|---|
| 正常情况 | 三名学生，分数分别为 85、58、92 |
| 边界情况 | 0、60、90、100 分 |
| 空数据 | 零条记录，均值和及格率如何表达 |
| 非法数据 | 缺失、文字、负数、超过 100、无穷与非数 |
| 口径 | 缺考是否进入分母；一名学生多条成绩如何处理 |
| 输出核对 | 有效条数加无效条数是否等于总条数 |
| 修改回归 | 改及格线后，其他规则是否仍然成立 |

- 浮点近似比较可用 `math.isclose()`，不要总是依赖 `==`。
- `assert` 适合教学检查与开发期断言；优化模式可能移除断言，正式输入校验应使用明确判断和异常。
- 保存小型测试数据与人工预期，之后再接入完整数据。
- AI 可以提出测试，但也可能与实现一起误解需求。验收标准应由人先确认。

### 动手

给“平均分”准备一份能手算的小样本，再向 AI 要一段故意写错的平均分程序，尝试用你的样例发现错误。

## 13 · 表格与图表：基础能力的应用入口

### 主线：用已有工具操作一整张表

以下为扩展示例，需要在当前环境安装 `pandas`。绘图另需 `matplotlib`，读写 `.xlsx` 常需 `openpyxl`。这些是终端安装任务，不应混入 Python 代码中。

```python
import pandas as pd

students = [
    {"name": "小林", "class": "一班", "score": 85},
    {"name": "小陈", "class": "一班", "score": 58},
    {"name": "小周", "class": "二班", "score": 92},
]
df = pd.DataFrame(students)
print(df.head())
print(df[df["score"] >= 60])
print(df.groupby("class")["score"].mean())
```

### 补充：看懂常见调用

- `pd.read_csv(...)`、`pd.read_excel(...)`：读取表格。
- `df["score"]`：选择一列；`df[条件]`：筛选行。
- `pd.to_numeric(..., errors="coerce")`：转换数字，无法转换的变为缺失值，需要后续明确处理。
- `dropna()`、`fillna()`、`drop_duplicates()`：处理缺失与重复，策略取决于业务含义。
- `groupby()`：按类别分组；`sum()`、`mean()`、`count()`：计算汇总。
- `to_csv(..., index=False)`：导出，通常不附带行索引。
- pandas 多条件筛选通常使用带括号的 `&`、`|`，不能直接照搬标量条件中的 `and`、`or`。

图表可以理解为“把数据传给绘图函数”：

```python
import matplotlib.pyplot as plt

plt.bar(["A", "B", "C"], [85, 58, 92])
plt.title("Student scores")
plt.xlabel("Student")
plt.ylabel("Score")
plt.ylim(0, 100)
plt.tight_layout()
plt.show()
```

条形图适合类别比较，折线图适合有序时间趋势。图表应有标题、单位、周期或样本说明。中文字体配置和具体分析操作放到后续练习展开。

### 动手

让 AI 解释 `df[df["score"] >= 60]` 的两层方括号各自做了什么，再用基础列表和循环表达同一个任务。

## 14 · API 与 AI：连接外部能力

### 主线：AI 调用仍然是输入、处理、输出

```text
学生的问题 + 当前示例代码
        ↓
页面组织请求
        ↓
服务端调用百炼 Agent
        ↓
得到响应并提取解释文字
        ↓
页面显示，学生继续追问
```

API 是程序之间约定的交互接口。HTTP API 常由请求地址、请求方法、请求头和请求体构成；响应通常包含状态码及数据。

### 补充：必须区分的几个概念

| 概念 | 含义 |
|---|---|
| API Key | 调用凭据，类似钥匙，不是模型本身 |
| Agent / 应用标识 | 决定调用哪个已配置的应用 |
| 请求输入 | 问题、代码、上下文等 |
| 响应数据 | 返回文字、标识、错误或其他结构 |
| 会话 | 多轮对话的上下文或会话标识，具体规则依平台接口 |
| 超时与限流 | 网络失败或服务限制，需要明确提示与处理 |

下面是**接口流程伪代码，不是可运行的百炼调用代码**。具体接入需要确认应用类型、区域、接口及官方协议：

```text
读取调用配置
检查问题与代码
按平台协议构造请求
设置认证与超时
发送请求
若失败：显示可理解的错误
若成功：解析响应并展示
```

- 模型返回的解释可能出错；格式正确也不代表内容正确。
- 数值统计与确定规则优先由代码执行，模型用于解释、归纳等任务，并配合核验。
- 模型输出作为外部数据处理，不直接执行其中的代码或命令。
- 教学页面可提供 KEY 输入，但共享页面中不应把教师长期密钥写死在前端或提交到仓库。正式部署需要设计服务端调用与访问控制。
- 本地教学也需说明 KEY 的传输和保存方式；不要默认把 KEY 长期存在浏览器或日志中。
- 成绩等数据使用虚构样例；调用外部服务时只发送完成任务所需的内容。

### 动手

假设网络断开，页面应该显示什么？如果 AI 说“60 分不及格”，你准备用什么证据判断对错？

## 15 · 与 AI 协作：从想法到可靠代码

### 主线：人负责目标与验收，AI 协助实现

推荐流程：

```text
描述问题 → 明确规则 → 给出样例 → 拆成步骤
       → 生成或修改一小段 → 运行 → 核对 → 再扩展
```

向 AI 提问时说明：任务目标、输入结构、处理规则、输出格式、限制条件、验收样例。

示例：

> 我在学习 Python，输入是学生字典组成的列表，每条包含 name 和 score。请先帮我拆解处理步骤，不要直接写完整程序。有效分数是 0～100 的有限数字，60 分及格。缺失或非法记录单独列出，不按零分参与平均数。没有有效记录时平均分为 None。请先给出三个输入输出样例让我确认。

### 补充：根据问题选择求助方式

- 读不懂：“解释这几个变量在每一步的值，用一个具体输入走一遍。”
- 不会拆解：“先列函数职责、输入输出和依赖关系。”
- 程序报错：“这是最小复现代码、完整报错、运行方式、预期和实际结果。”
- 程序不报错但结果不对：“请检查这条规则，用边界样例找反例。”
- 希望修改：“仅调整及格线规则，解释改动位置，重新核对已有样例。”
- 希望练习：“出一道类似问题，先给提示，等我回答后再反馈。”

AI 生成后，至少检查：能否解释关键代码；依赖是否确实存在；输入输出是否符合约定；是否读写了预期范围之外的文件；测试是否覆盖边界；凭据是否泄露。不能理解的代码，先缩小范围再运行。

### 动手

请 AI 实现及格率函数。你负责提前给出两个正常样例和一个空输入样例，并记录一次“AI 的实现与我的规则不一致”的修正过程。

## 16 · 串起来：一个完整、可验证的小程序

### 主线：一份数据经过哪些步骤

下面程序只使用标准库，完整源码另存于 `examples/grade_report.py`。运行后在指定输出目录生成报告与无效记录文件，不覆盖原始数据。

```text
准备原始记录
  → 校验并转换
  → 分离有效与无效记录
  → 计算汇总
  → 检查结果
  → 保存报告
```

关键口径：每条记录按一次成绩计数；姓名不能为空；布尔值不作为分数；分数必须为 0～100 的有限数；无效记录不进入均值和及格率分母；没有有效成绩时二者均为 `None`；及格率返回 0～1 的小数。

```python
# 节选：完整程序见配套源码

def summarize(students):
    scores = [student["score"] for student in students]
    count = len(scores)
    passed = sum(score >= 60 for score in scores)
    return {
        "valid_count": count,
        "passed_count": passed,
        "average": sum(scores) / count if count else None,
        "pass_rate": passed / count if count else None,
    }
```

为什么先校验再汇总？因为计算函数可以围绕明确的有效数据工作，输入问题也能单独保留下来，便于追溯。

### 动手：三层练习

1. **读懂：**画出数据流，解释每个函数的输入、输出与调用顺序。
2. **修改：**把及格线改为参数，允许使用 70 分，并补一个检查样例。
3. **扩展：**增加班级字段，按班级生成汇总；先写预期输出，再让 AI 协助实现。

验收时请回答：空数据怎样处理？非法数据去了哪里？报告保存在何处？哪些规则由你决定，哪些代码由 AI 协助编写？

## 17 · 基础地图与课后索引

### 学完本章，需要能说明这些关系

```text
数据：值 → 类型 → 变量 → 容器 → 多条记录
规则：表达式 → 条件 → 循环
组织：函数 → 模块 → 包；对象与类
连接：文件 → CSV / JSON → 第三方库 → API
质量：报错 → 调试 → 输入校验 → 测试 → 可复查的交付
协作：明确需求 → AI 辅助 → 人工理解与验证
```

### 基础覆盖核对

| 领域 | 本章保留的内容 | 阅读位置 |
|---|---|---|
| 执行模型 | 解释器、脚本、Notebook、顺序、缩进、注释 | 01 |
| 数据 | 变量、基本类型、转换、真假、None、浮点误差 | 02～03 |
| 表达式 | 算术、比较、逻辑、成员、身份、格式化、索引切片 | 03 |
| 容器 | 列表、元组、字典、集合、嵌套、修改、复制 | 04 |
| 控制流 | 条件、循环、range、break、continue、pass、推导式 | 05～06 |
| 函数 | 定义、调用、参数、返回、作用域、默认值、类型提示 | 07 |
| 对象 | 属性、方法、类、实例、self；面向对象后续入口 | 08 |
| 环境 | 模块、包、标准库、第三方库、安装、虚拟环境、入口 | 09 |
| 输入输出 | 路径、读写、with、编码、CSV、JSON | 10 |
| 质量 | 异常、主动抛错、调试、边界、测试、口径 | 11～12 |
| 应用 | 表格、图表、API、AI 调用与凭据 | 13～14 |
| 完整实践 | 需求、协作、校验、汇总、输出、修改与验收 | 15～16 |

### 后续主题：保留入口，避免首课失焦

以下内容有用，但不要求第一节课掌握：正则表达式、日期时区、生成器与迭代器、装饰器、上下文管理器实现、递归、继承与多态进阶、异步并发、数据库、Web 开发、打包发布、Git、专业测试框架与性能分析。它们应在后续任务需要时展开，不能把“看过一篇概览”当作已经掌握。

### 自测：能否脱离讲义解释

1. `=` 与 `==`、`==` 与 `is` 有什么区别？
2. 为什么 CSV 的分数需要转换类型？
3. 列表、字典分别如何表达学生数据？
4. 条件顺序为什么会改变结果？
5. `for` 和 `while` 如何选择？
6. `print` 与 `return` 有什么区别？
7. 为什么赋值一个列表不等于复制它？
8. 导入库和安装库分别发生在哪里？
9. 相对路径相对于什么位置？
10. 不报错的程序为什么仍可能错误？
11. 平均分与及格率的分母如何确定？
12. AI 生成代码之后，你如何决定它可以交付？

> 首课的完成标准：面对一个小程序，能够找到数据、规则、步骤、外部依赖与验证方法；允许查资料和求助 AI，但能够解释关键行为，并完成一次经过核对的修改。
