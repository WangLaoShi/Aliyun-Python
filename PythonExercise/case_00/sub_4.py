'''
题目：输入某年某月某日（yyyy-MM-dd），判断这一天是这一年的第几天？
'''

cal = input('日期：')

date = cal.split('-')  # 拆分日期

year = int(date[0])
month = int(date[1])
day = int(date[2])

# 1-12月每月的天数
# 1,3,5,7,8,10,12(腊)月是31天
# 4,6,9,11(冬)月是30天
# 2月平年28天，闰年29天
arr = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

num = 0

if ((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0):
    arr[2] = 29

la = len(arr)

for i in range(1, la):
    if month > i:
        num += arr[i]
    else:
        num += day
        break

print('天数：', num)


# 剩余多少天计算

print('剩余天数：', 366 - num if arr[2] == 29 else 365 - num)