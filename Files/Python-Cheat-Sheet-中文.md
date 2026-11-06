# Python 速查表（中文版）

> 原文：*Python Cheat Sheet* — Mosh Hamedani（Code with Mosh）第 1 版  
> 来源：`Files/Python-Cheat-Sheet.pdf`  
> 说明：本文件为中文翻译。原文中的弯引号（`‘’“”`）等**不能直接当 Python 代码运行**；文中示例已改为合法写法，并对不能连续执行的片段做了拆分与注释。

---

## 目录

1. [关于本速查表](#关于本速查表)
2. [关于作者](#关于作者)
3. [变量](#变量)
4. [注释](#注释)
5. [接收输入](#接收输入)
6. [字符串](#字符串)
7. [算术运算](#算术运算)
8. [if 语句](#if-语句)
9. [比较运算符](#比较运算符)
10. [while 循环](#while-循环)
11. [for 循环](#for-循环)
12. [列表](#列表)
13. [元组](#元组)
14. [字典](#字典)
15. [函数](#函数)
16. [异常](#异常)
17. [类](#类)
18. [继承](#继承)
19. [模块](#模块)
20. [包](#包)
21. [Python 标准库](#python-标准库)
22. [PyPI](#pypi)

---

## 关于本速查表

本速查表整理了作者在 YouTube《Python 初学者教程》中讲过的内容。教程与本速查表都覆盖了语言的**核心结构**，但**并非面面俱到**。

若希望系统学习 Python、成为更熟练的开发者，可参考作者的完整课程：  
<http://bit.ly/complete-python-course>

---

## 关于作者

你好！我是 **Mosh Hamedani**。我是一名有约二十年经验的软件工程师，已帮助超过三百万人学习编程或走上职业软件工程师之路。我的目标是让软件工程变得简单、人人可及。

- <https://codewithmosh.com>
- <https://youtube.com/user/programmingwithmosh>
- <https://twitter.com/moshhamedani>
- <https://facebook.com/programmingwithmosh/>

---

## 变量

变量用来在计算机内存中**临时存放数据**。

```python
price = 10
rating = 4.9
course_name = "Python for Beginners"
is_published = True
```

在上面的例子中：

- `price` 是**整数**（integer，没有小数点的整数）
- `rating` 是**浮点数**（float，带小数点）
- `course_name` 是**字符串**（string，一串字符）
- `is_published` 是**布尔值**（boolean）。布尔值只能是 `True` 或 `False`（注意首字母大写）

---

## 注释

注释用来给代码加说明。好的注释解释**怎么做、为什么这样做**，而不是复述代码字面在干什么——后者应尽量由代码本身表达清楚。可用注释提醒自己或同事，或说明假设与设计原因。

```python
# 这是注释，不会被执行。
# 注释可以写多行。
```

---

## 接收输入

可用内置函数 `input()` 接收用户输入。

```python
birth_year = int(input("Birth year: "))
```

`input()` **总是返回字符串**。若要按整数使用，需用内置函数 `int()` 转换（如上所示）。用户若输入非数字，`int(...)` 会抛出 `ValueError`（见后文「异常」）。

---

## 字符串

可用单引号 `'...'` 或双引号 `"..."` 定义字符串。  
多行字符串用**三引号**包围（`'''...'''` 或 `"""..."""`）。  
可用方括号 `[]` 取单个字符。

```python
course = "Python for Beginners"
course[0]   # 第一个字符 → 'P'
course[1]   # 第二个字符 → 'y'
course[-1]  # 从末尾数第一个 → 's'
course[-2]  # 从末尾数第二个 → 'r'
```

切片写法类似：

```python
course[1:5]  # 从下标 1 取到 5（不含 5）→ 'ytho'
```

- 省略起始下标时，默认从 `0` 开始。
- 省略结束下标时，默认取到字符串末尾。

可用**格式化字符串（f-string）**动态插入值：

```python
name = "Mosh"
message = f"Hi, my name is {name}"
```

常用字符串方法：

```python
message = "Hi, my name is Mosh"

message.upper()              # 全大写
message.lower()              # 全小写
message.title()              # 每个单词首字母大写
message.find("p")            # 第一次出现 'p' 的下标；找不到返回 -1
message.replace("p", "q")    # 把 'p' 替换成 'q'（不修改原字符串，返回新串）
```

检查字符串是否包含某字符（或子串），用 `in` 运算符：

```python
course = "Python for Beginners"
contains = "Python" in course  # True
```

---

## 算术运算

| 运算符 | 含义 |
|--------|------|
| `+` | 加 |
| `-` | 减 |
| `*` | 乘 |
| `/` | 除，结果为 **float** |
| `//` | 整除，结果为 **int**（向负无穷取整） |
| `%` | 取余（余数） |
| `**` | 幂：`x ** y` 表示 x 的 y 次方 |

增强赋值：

```python
x = 0
x = x + 10
x += 10  # 等价于上一行的写法
```

运算符优先级（从高到低）：

1. 括号 `()`
2. 幂 `**`
3. 乘 / 除（`*`、`/`、`//`、`%`）
4. 加 / 减（`+`、`-`）

---

## if 语句

```python
is_hot = True
is_cold = False

if is_hot:
    print("hot day")
elif is_cold:
    print("cold day")
else:
    print("beautiful day")
```

逻辑运算符：

```python
has_high_income = True
has_good_credit = True

if has_high_income and has_good_credit:
    ...  # 两个条件都为真

if has_high_income or has_good_credit:
    ...  # 至少一个为真

is_day = True
is_night = not is_day  # 取反
```

---

## 比较运算符

```python
a, b = 3, 5

a > b    # 大于
a >= b   # 大于或等于
a < b    # 小于
a <= b   # 小于或等于
a == b   # 等于（注意是两个等号）
a != b   # 不等于
```

---

## while 循环

```python
i = 1
while i < 5:
    print(i)
    i += 1
# 输出：1 2 3 4
```

注意循环体内要能让条件最终变为假，否则会变成**死循环**。

---

## for 循环

```python
for i in range(1, 5):
    print(i)
# 输出：1 2 3 4
```

关于 `range`：

- `range(5)`：生成 `0, 1, 2, 3, 4`
- `range(1, 5)`：生成 `1, 2, 3, 4`
- `range(1, 5, 2)`：生成 `1, 3`（步长为 2）

---

## 列表

列表是可变的有序序列。下面按**主题**给出示例（不要把所有方法当成对同一列表一气跑完的脚本；例如 `clear()` 之后列表为空，再 `index(...)` 会出错）。

```python
numbers = [1, 2, 3, 4, 5]

numbers[0]    # 第一项 → 1
numbers[1]    # 第二项 → 2
numbers[-1]   # 从末尾数第一项 → 5
numbers[-2]   # 从末尾数第二项 → 4
```

常用方法：

```python
numbers = [1, 2, 3, 4, 5]

numbers.append(6)     # 末尾追加 6 → [1, 2, 3, 4, 5, 6]
numbers.insert(0, 6)  # 在下标 0 插入 6
numbers.remove(6)     # 删除**第一次出现**的 6；没有该值会 ValueError
numbers.pop()         # 删除并返回最后一项
numbers.clear()       # 清空列表

numbers = [1, 2, 3, 4, 5]
numbers.index(3)      # 第一次出现 3 的下标 → 2；找不到会 ValueError
numbers.sort()        # 原地排序（默认升序）
numbers.reverse()     # 原地反转
copy_of_numbers = numbers.copy()  # 浅拷贝一份新列表
```

> **校对说明（相对 PDF）：** 原文在同一段里写了 `numbers.index(8)`，而示例列表是 `[1, 2, 3, 4, 5]`，连续执行会 `ValueError`。上表改为对存在的元素取下标，并注明找不到时的行为。

---

## 元组

元组类似「只读列表」：用来存放一组项；一旦定义，**不能增删改**其中的元素。

```python
coordinates = (1, 2, 3)
```

可以把列表或元组**解包**到多个变量：

```python
coordinates = (1, 2, 3)
x, y, z = coordinates  # x=1, y=2, z=3
```

---

## 字典

字典用来存储**键 / 值**对。

```python
customer = {
    "name": "John Smith",
    "age": 30,
    "is_verified": True,
}
```

键通常用字符串或数字，且应唯一；值可以是任意类型。

```python
customer["name"]                 # → "John Smith"
# customer["type"]               # 键不存在 → KeyError
customer.get("type", "silver")   # 找不到键时返回默认值 "silver"
customer["name"] = "new name"    # 修改已有键，或新增键
```

---

## 函数

函数把程序拆成小块，便于阅读、理解和维护；出 bug 时也更容易在小范围内定位，并且可以复用。

```python
def greet_user(name):
    print(f"Hi {name}")


greet_user("John")
```

- **参数（parameter）**：函数定义里的占位符（如上例的 `name`）
- **实参（argument）**：调用时传入的实际值（如上例的 `"John"`）

实参有两类：

- **位置实参**：顺序有意义
- **关键字实参**：顺序不重要，写成 `参数名=值`

```python
def greet_user(first_name, last_name):
    print(f"Hi {first_name} {last_name}")


# 两个位置实参（顺序要对应参数定义）
greet_user("John", "Smith")


def calculate_total(order, shipping, tax):
    return order + shipping + order * tax


# 关键字实参（顺序可调整）
total = calculate_total(order=50, shipping=5, tax=0.1)
```

函数可用 `return` 返回值。若没有 `return`，默认返回 `None`（表示「没有值」）。

```python
def square(number):
    return number * number


result = square(2)
print(result)  # 4
```

> **校对说明：** PDF 中「两个位置实参」示例仍写 `greet_user("John", "Smith")`，但前文函数只有一个参数 `name`，直接运行会 `TypeError`。中文版改为两参数的 `greet_user`，与「位置实参」说明一致。

---

## 异常

异常是会导致程序崩溃的错误，常因不良输入或编程失误引起。应预判并处理它们，避免程序异常退出。

```python
try:
    age = int(input("Age: "))
    income = 20000
    risk = income / age
    print(age)
except ValueError:
    print("Not a valid number")
except ZeroDivisionError:
    print("Age cannot be 0")
```

> **校对说明：** PDF 原文将 “crashing” 误写为 “cashing”，翻译按正确含义处理。

---

## 类

用类定义新的类型。

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        print("move")
```

类中的函数称为**方法（method）**。  
类是创建对象的模板；**对象**是类的一个**实例**。每次 `Point(...)` 都会按类的结构新建一个实例。

```python
point1 = Point(10, 5)
point2 = Point(2, 4)
```

`__init__` 是特殊的**构造方法**，在创建对象时自动调用，用来初始化对象。

---

## 继承

继承可减少重复代码：在基类中定义公共方法，其他类再继承这些方法。

```python
class Mammal:
    def walk(self):
        print("walk")


class Dog(Mammal):
    def bark(self):
        print("bark")


dog = Dog()
dog.walk()  # 继承自 Mammal
dog.bark()  # 定义在 Dog 中
```

---

## 模块

模块就是包含 Python 代码的文件。用模块把程序拆成多个文件，结构更清晰，避免单文件膨胀到成千上万行。

导入模块有两种常见方式：导入整个模块，或只导入模块中的某个对象。

```python
# 导入整个 converters 模块（假设项目中有 converters.py）
import converters

converters.kg_to_lbs(5)

# 只导入 converters 中的一个函数
from converters import kg_to_lbs

kg_to_lbs(5)
```

> 上例中的 `converters` / `kg_to_lbs` 为教学示意模块名；运行前需自备对应文件。

---

## 包

**包**是包含 `__init__.py` 的目录，其中可放一个或多个模块。

```python
# 导入 ecommerce 包中的 sales 模块（示意）
from ecommerce import sales

sales.calc_shipping()

# 只导入 sales 模块中的一个函数
from ecommerce.sales import calc_shipping

calc_shipping()
```

---

## Python 标准库

Python 自带大量模块，用于常见任务，例如发邮件、处理日期时间、生成随机数等。

### random 模块

```python
import random

random.random()       # [0.0, 1.0) 之间的 float
random.randint(1, 6)  # 1 到 6（含两端）的 int

members = ["John", "Bob", "Mary"]
leader = random.choice(members)  # 随机选一项
```

---

## PyPI

[Python Package Index](https://pypi.org)（PyPI）是全球开发者发布的 Python 包目录。用 **pip** 安装或卸载这些包：

```bash
pip install openpyxl
pip uninstall openpyxl
```

---

## 想成为 Python 高手？

若认真学习 Python 并希望从事相关工作，作者建议学习其 Complete Python Course（营销内容，按原文保留要点）：

- 约 12 小时高清视频  
- 无限次回看  
- 可按自己节奏学习  
- 可在线或下载离线观看  
- 结业证书  
- 30 天无理由退款  

课程原价等促销信息以作者页面为准：  
<http://bit.ly/complete-python-course>

---

## 附录：相对 PDF 原文的代码核对摘要

| 问题 | 处理 |
|------|------|
| 全文使用弯引号 `‘’“”` | 全部改为标准 `'...'` / `"..."` |
| 「tripe quotes」笔误 | 译为「三引号」 |
| 「cashing」笔误 | 按 crashing 译为「崩溃 / 异常退出」 |
| `numbers.index(8)` 与列表内容不符 | 改为 `index(3)`，并注明找不到会 `ValueError` |
| 列表方法若连写会互相影响 | 拆成独立示例，并说明 `clear()` 后果 |
| 单参数 `greet_user` 却传入两个位置实参 | 补充两参数版本与关键字实参示例 |
| `converters` / `ecommerce` | 保留为示意，注明需自备模块 |

---

*本中文版仅供学习参考；版权归原作者 Mosh Hamedani / Code with Mosh 所有。*
