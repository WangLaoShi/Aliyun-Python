# 平均函数
def average(lst): 
    num=sum(lst)/len(lst) # 平均处理。
    avg=float('{:.2f}'.format(num)) # 格式化平均值。
    return avg # 返回平均值。

# 分段函数
def intercept(s,num,delimiter): 
    s1=str(s) # 将要分段的对象转换为字符串类型。
    lst=[s1[n:n+num] for n in range(0,len(s1),num)] # 对数据进行分段处理。
    s2=delimiter.join(lst) # 合并分段的列表。
    return s2 # 将合并结果返回函数。

# 模仿vlookup   
def vlookup(val,lst,num=1): 
    r=lst[0].index(val) # 对lst列表第1个元素使用index函数进行查找。得到返回值赋值给r变量。
    v=lst[num][r] # 再使用num和r变量确定截取位置。
    return v # 将截取的值返回给函数

# 分类合并字符串
def combine(range,join_range,delimiter=' '): 
    dic={} # 初始化dic变量为空字典。
    for x,y in zip(range,join_range): # 将range和join_range接收的值使用zip函数做组合转换，并赋值给x,y变量。
        if not x in dic: # 如果x在dic字典中不存在。
            dic[x]=[y] # 则以x为键，y为值，创建键值，注意y是写在列表中的。
        else: # 否则。
            dic[x].append(y) # 如果x键存在，则将y添加到对应的值列表中。
        l=[(k,delimiter.join([str(i) for i in dict.fromkeys(i)])) for k,i in dic.items()] # 将键对应值列表去重合并。
    return l # l变量是列表，列表中的元素是元组类型，元组中分别存储是dic字典的键，及dic字典对应值合并后的字符串。