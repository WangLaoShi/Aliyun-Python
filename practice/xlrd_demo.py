# XLRD 是 python 中用来进行 Excel 读取的一个外部库
# 使用 XLRD 库之前，需要先安装该库
# 安装方法：pip install xlrd -i https://mirrors.aliyun.com/pypi/simple/
# 使用方法：
# 1. 导入 XLRD 库
import xlrd
# 2. 读取 Excel 文件
wb = xlrd.open_workbook('有问题的薪资.xls')
# 3. 读取 Excel 文件中的数据
sheet = wb.sheet_by_index(0)
# 4. 读取 Excel 文件中的数据
print(sheet.cell_value(0, 0))
# 5. 读取 Excel 文件中的数据
print(sheet.cell_value(1, 0))
# 6. 读取 Excel 文件中一共有多少行
print(sheet.nrows)
# 7. 读取 Excel 文件中一共有多少列
print(sheet.ncols)

# 导入另一个文件里的函数

from salary import split_salary

# 遍历 [1,0] ..... [nrows,0]
# for i in range(1, sheet.nrows):
#     print(f"实际文本 {i} 行：",sheet.cell_value(i, 0))
#     print(split_salary(sheet.cell_value(i, 0)))
from salary import write_salary
salaries = list()
for i in range(1, sheet.nrows):
    item = list()
    item.append(sheet.cell_value(i, 0))
    item.append(split_salary(sheet.cell_value(i, 0))[0])
    item.append(split_salary(sheet.cell_value(i, 0))[1])
    item.append(split_salary(sheet.cell_value(i, 0))[2])
    salaries.append(item)
write_salary(salaries)