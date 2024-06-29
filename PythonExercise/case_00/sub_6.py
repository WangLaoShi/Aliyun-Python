'''
题目：斐波那契数列。
'''

arr = [0, 1]

tmp, num = 0, 1

dep = 20  # 数列长度

for i in range(dep - 2):
    tmp, num = num, tmp + num
    arr.append(num)

print(arr)


# 递归实现

def fib(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fib(n - 1) + fib(n - 2)

print(fib(20))