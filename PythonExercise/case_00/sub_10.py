'''
题目：格式化输出当前时间。
'''

import time

format = '%Y-%m-%d %H:%M:%S'

local = time.localtime(time.time())

print(local)

print(time.strftime(format, local))

# ---------------------
from datetime import datetime, timedelta

# 获取当前日期和时间
now = datetime.now()
print("当前日期和时间:", now)

# 获取当前日期
today = datetime.today()
print("今天的日期:", today)

# 创建一个指定日期和时间的 datetime 对象
specific_date = datetime(2023, 6, 29, 15, 30, 45)
print("指定日期和时间:", specific_date)

# 日期格式化为字符串
formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
print("格式化后的日期和时间:", formatted_date)

# 将字符串解析为 datetime 对象
date_string = "2024-06-29 14:45:30"
parsed_date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
print("解析后的日期和时间:", parsed_date)

# 日期加减操作
future_date = now + timedelta(days=10)
print("10天后的日期和时间:", future_date)

past_date = now - timedelta(days=10)
print("10天前的日期和时间:", past_date)

# 获取日期的各个部分
year = now.year
month = now.month
day = now.day
hour = now.hour
minute = now.minute
second = now.second
print(f"年: {year}, 月: {month}, 日: {day}, 时: {hour}, 分: {minute}, 秒: {second}")