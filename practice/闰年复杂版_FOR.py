def is_leap_year(year):
    if ((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)):
        print(f'{year} 是闰年')
    else:
        print(f'{year} 不是闰年')
        
try:
    year_start = int(input('请输入一个开始年份：'))
    year_end = int(input('请输入一个结束年份：'))
    
    for year in range(year_start, year_end + 1):
        is_leap_year(year)
except ValueError:
    print('非法年份')
    exit()
    