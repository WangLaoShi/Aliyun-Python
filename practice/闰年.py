# 编写一个判断是否是闰年

# 1. 得到用户输入
# 2. 判断是否是合法的年份
# 3. 如果不是合法年份，直接输出“非法年份”
# 4. 如果是合法年份，那么进行闰年的判断
# 5. 如果是闰年，输出，是闰年
# 6. 如果不是闰年，就输出，不是闰年
# 7. 程序结束。
try:
    year = int(input('请输入一个年份：'))
    print('合法年份')
except ValueError:
    print('非法年份')
    exit()
    
    
# 判断是否是闰年

if ((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)):
    print('是闰年')
else:
    print('不是闰年')

# if year >= 1900 and year <= 2099:
#     print('合法年份')
# else:
#     print('非法年份')

