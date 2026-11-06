WINDOW_WITTH = 1020
WINDOW_HEIGHT = 720

for i in range(10):
    for j in range(10):
        print(i, j)
        
def add(a, b):
    return a + b

print(add(1, 2))

def say_hello():
    print("Hello, World!")

say_hello()

def say_hello_to(name):
    for wk in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        print(wk)
    print(f"Hello, {name}!")

say_hello_to("John")


# 阶乘
# 5! = 5 * 4 * 3 * 2 * 1
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)

print(factorial(5))

import os

# 通过递归函数来访问整个电脑 C 盘的文件
def visit_file(path):
    for file in os.listdir(path):
        print(file)
        if os.path.isdir(os.path.join(path, file)):
            visit_file(os.path.join(path, file))

visit_file("C:\\")

import pandas as pd

df = pd.read_csv("data.csv")

df = pd.read_csv("data.csv", encoding="utf-8", delimiter=",", header=0, index_col=0)
df = pd.read_csv("data.csv",  delimiter=",", header=0,encoding="utf-8", index_col=0)