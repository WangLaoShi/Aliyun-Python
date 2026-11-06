def split_salary(salary):
    
    # 如果原始文本为空，
    if salary == "" or salary.find("面议") != -1:
        return "", "", ""
    
    salary = salary.replace(" ", "").replace("\n", "").replace("万", "0k")
    
    if salary.find("及以下") != -1:
        salary = salary.replace("及以下", "")
        salary = "0k-" + salary
    
    parts = list()
    if salary.find("·") != -1: # 如果薪水中有 · 的话，要先进行分割
        parts = salary.split("·")
        if parts[0].find("-") != -1:
            start = parts[0].split("-")[0]
            end = parts[0].split("-")[1]
            
        return start.replace("k", "").replace("K", ""), end.replace("k", "").replace("K", ""),parts[1].replace("薪", "").replace(" ", "")
    else:
        parts = salary.split("-")
        start = parts[0].replace("k", "").replace("K", "")
        end = parts[1].replace("k", "").replace("K", "")
        return start, end, 12
    
print(split_salary("15k-22k·15薪"))


# 我们要定义一个新的数据结构，虽然在这里很简单

# [
# ["10k-20k",10,20,12],    
# [salary,start,end,months],    
# [salary,start,end,months],    
# [salary,start,end,months],    
# [salary,start,end,months],    
# [salary,start,end,months],    
#]

def write_salary(salaries):
    # 写入到新的 xls 文件中
    # 使用 XLWT 库
    # 安装方法：pip install xlwt -i https://mirrors.aliyun.com/pypi/simple/
    import xlwt
    # 新建工作簿
    wb = xlwt.Workbook()
    # 新建工作表
    ws = wb.add_sheet("工资表")
    
    # salaries 的大小
    # len(salaries) # 高度
    # 宽度 ： 4
    # 写入数据
    for i in range(len(salaries)):
        for j in range(4):
            ws.write(i, j, salaries[i][j])
    # 保存工作簿
    wb.save("工资表.xls")