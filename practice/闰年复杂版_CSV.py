import csv

def is_leap_year(year):
    if ((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)):
        # print(f'{year} 是闰年')
        write_to_csv(year, '是闰年')
    else:
        # print(f'{year} 不是闰年')
        write_to_csv(year, '不是闰年')

def write_to_csv(year, is_leap_year):
    with open('leap_years.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([year, is_leap_year])
   
try:
    year_start = int(input('请输入一个开始年份：'))
    year_end = int(input('请输入一个结束年份：'))
    
    for year in range(year_start, year_end + 1):
        is_leap_year(year)
except ValueError:
    print('非法年份')
    exit()
    