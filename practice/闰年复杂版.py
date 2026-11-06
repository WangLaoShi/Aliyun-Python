def is_leap_year(year):
    if ((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)):
        print('是闰年')
    else:
        print('不是闰年')
        
try:
    year = int(input('请输入一个年份：'))
    print('合法年份')
    is_leap_year(year)
except ValueError:
    print('非法年份')
    exit()
    