本笔记为阿里云天池龙珠计划Python训练营的学习内容，链接为：https://tianchi.aliyun.com/specials/promotion/aicamppython
# 阿里云天池 Python 训练营 [国际人学校 - 林肯老师 22 年情人节版本] - Part4

![rhtKQR](https://upiclw.oss-cn-beijing.aliyuncs.com/uPic/rhtKQR.png)

* 2022 年 02 月 14 日版本
* 本文档是以 CC 开源的模式的发布，你能且将获得本文档的 PDF 版本已经 Jupyter Notebook 版本
* 本文档并不申明自己的版权信息，为了更好的知识传播，我们授权你使用本文档，你可以使用它，进行二次创作，进行分发，进行修改，并可以以此为蓝本进行授课。
* 请保留本文档的原始来源。
* 本文档首先在国际人学校组织的“阿里云天池 Python 训练营课程”中使用。
* 本文档由林肯老师首次组织和编辑。你可以通过网址 [数据大咖](https://www.shujudaka.com) 找到他。

![TWy9b7](https://upiclw.oss-cn-beijing.aliyuncs.com/uPic/TWy9b7.jpg)

## Excel函数 | 相信这些也是你最常用这几个！

![maoDFp](https://upiclw.oss-cn-beijing.aliyuncs.com/uPic/maoDFp.jpg)

### 01. MID函数

函数定义：从一个文本字符串的指定位置开始,截取指定数目的字符

使用格式：MID(text, start_num, num_chars)

例子：

![rmzOuk](https://upiclw.oss-cn-beijing.aliyuncs.com/uPic/rmzOuk.jpg)

### 02. CONCATENATE函数

函数定义：将多个字符文本或单元格中的数据连接在一起,显示在一个单元格中

使用格式：CONCATENATE(text1,text2,……)

重点：也可以用&（和号）运算符代替函数CONCATENATE实现文本项的合并

例子：

![qLkAEU](https://upiclw.oss-cn-beijing.aliyuncs.com/uPic/qLkAEU.jpg)

### 03. AND函数

函数定义：检测所有的条件是否为真

使用格式：AND(logical1,logical2,……logical30)

注意事项：
如果指定的区域中不包含逻辑值或数值时,函数AND返回错误值#VALUE!.
Logical1,logical2,……logical30表示待检测的1到30个条件值,各条件值可为TRUE或FALSE

例子：

![qTpsbP](https://upiclw.oss-cn-beijing.aliyuncs.com/uPic/qTpsbP.jpg)

可以与IF函数连用

![53P0NO](https://upiclw.oss-cn-beijing.aliyuncs.com/uPic/53P0NO.jpg)

### 04. IF函数

函数定义：根据条件满足与否返回不同的值
使用格式：
IF(logical_test,value_if_true,value_if_false)
白话：IF(条件,与条件一样时运算这个,与条件不同时运算这个)
例子：

![dieC9s](https://upiclw.oss-cn-beijing.aliyuncs.com/uPic/dieC9s.jpg)

![4Znhla](https://upiclw.oss-cn-beijing.aliyuncs.com/uPic/4Znhla.jpg)

公式如下：

'=IF(C13>=$H$10,$I$10,IF(C13>=$H$9,$I$9,IF(C13>=$H$8,$I$8,IF(C13>=$H$7,$I$7,IF(C13>=$H$6,$I$6,IF(C13>=$H$5,$I$5,0))))))

### 05. DATEDIF函数

函数定义：计算期间内的年数、月数、天数

使用格式：

* =DATEDIF(start_date,end_date,"y")
* =DATEDIF(start_date,end_date,"m")
* =DATEDIF(start_date,end_date,"d")
* =DATEDIF(start_date,end_date,"ym")
* =DATEDIF(start_date,end_date,"yd")
* =DATEDIF(date1,date2,"md")

白话：DATEDIF(开始日期,结束日期,要计算的单位)

注意：

* y:计算满年数,返回值为0以上的整数
* m:计算满月数,返回值为0以上的整数;d:计算满日数,返回值为0以上的整数
* ym:计算不满一年的月数,返回值为1~11之间的整数
* yd计算不满一年的天数,返回值为0~365之间的整数
* md:计算不满意一个月的天数,返回值为0~30之间的整数

例子：

![UGACYk](https://upiclw.oss-cn-beijing.aliyuncs.com/uPic/UGACYk.jpg)

### 06. COUNTIF函数

函数定义：计算满足条件的单元格计数
使用格式：COUNTIF(range,criteria)

白话：COUNTIF(要找的内容所在的区域,要找的内容)

注意事项：

指定的条件必须用 " " (双引号括起来),如 ">=100、"男" 等.但,当指定条件为引用单元格时无需双引号括住.通配符使用参看SUMIF函数中的通配符说明

例子：

![bRX6ra](https://upiclw.oss-cn-beijing.aliyuncs.com/uPic/bRX6ra.jpg)

COUNTIF函数几种用法：

* 求包含值139的单元格数量 '=COUNTIF($D$4:$D$14,139)
* 求包含负值的单元格数量 '=COUNTIF($C$4:$C$14,"<0")
* 求不等于0 的单元格数量 '=COUNTIF($C$4:$C$14,"<>0")
* 求大于等于5的单元格数量 '=COUNTIF($C$4:$C$14,">=5")
* 求等于单元格B45中内容的单元格数量 '=COUNTIF($B$4:$B$14,B4)
* 求大于单元格E45中内容的单元格数量 '=COUNTIF($E$4:$E$14,">"&E4)
* 求包含文本内容的单元格数量 '=COUNTIF($B$4:$B$14,"*")
* 求包含六个字符内容的单元格数量 '=COUNTIF($B$4:$B$14,"??????")
* 求在文本中任何位置包含单词"文胸"字符内容的单元格数量 '=COUNTIF($B$4:$B$14,"*文胸*")
* 求包含以英文"D"(不分大小写)开头内容的单元格数量 '=COUNTIF($B$4:$B$14,"D*")
* 求包含当前日期的单元格数量 '=COUNTIF($E$4:$E$14,TODAY())
* 求大于平均值的单元格数量 '=COUNTIF($D$4:$D$14,">"&AVERAGE($D$5:$D$14))

![nrLoTJ](https://upiclw.oss-cn-beijing.aliyuncs.com/uPic/nrLoTJ.jpg)

统计区域内不重复数据数

![Dea4CU](https://upiclw.oss-cn-beijing.aliyuncs.com/uPic/Dea4CU.jpg)

公式：'{=SUM(1/COUNTIF(D5:D14,D5:D14))}

这里其实输入的是=SUM(1/COUNTIF(D5:D14,D5:D14))，然后按ctrl+shift+enter三键结束。

下面公式加了IF判断是否是空格的嵌套,避免出现#DIV/0!错误.

'{{=SUM(IF(D5:D14<>"",1/COUNTIF(D5:D14,D5:D14)))}}

或者可以用

=SUM(IF(ISBLANK(D5:D14),"",1/COUNTIF(D5:D14,D5:D14))),然后按ctrl+shift+enter三键结束。

### 07. SUMIF函数

函数定义：对满足条件的单元格的数值求和

使用格式：SUMIF(range,criteria,sum_range)

参数解释：

range：为用于条件判断的单元格区域.指定作为搜索对象的单元格区域
Criteria：为确定哪些单元格将被相加求和的条件,其形式可以为数字、表达式、文本或通配符
Sum_range：是需要求和的实际单元格

几种基本用法：

![cBdHhX](https://upiclw.oss-cn-beijing.aliyuncs.com/uPic/cBdHhX.jpg)

1. 以“文胸”开头的任意文本的销量

    =SUMIF($B$4:$B$14,"文胸*",$C$4:$C$14)

    注意：如果是“文胸~*”，则此时的“*”就是字符，不是通配符，需要准确查找文本为“文胸*”的销量合计

2. “文胸”后面一定是三个字符的文本的销量

    =SUMIF($B$4:$B$4,"文胸???",$C$4:$C$4)

    注意：如果是“文胸~???”，则此时的“?”就是字符，不是通配符，需要准确查找文本为“文胸???”的销量合计

3. 销售大于等于5件的销售合计

    =SUMIF($C$4:$C$14,">=5",$C$4:$C$14)

4. 查找内容为c20的销售合计

    =SUMIF($B$4:$B$14,C20,$C$4:$C$14)

### 08. DCOUNT函数

函数定义：计算满足条件的数值的个数

使用格式：DCOUNT(database,field,criteria)

参数定义：

* database: 构成列表或数据库的单元格区域.数据库是包含一组相关数据的列表,其中包含相关信息的行为记录,而包含数据的列为字段.列表的第一行包含着每一列的标志项.

* Field: 指定函数所使用的数据列.列表中的数据列必须在第一行具有标志项.Field可以是文本,即两端带引号的标志项,如"使用年数"或"产量"；此外,Field也可以是代表列表中数据列位置的数字：1表示第一列,2表示第二列,等等.

* Criteria: 为一组包含给定条件的单元格区域.可以为参数criteria指定任意区域,只要它至少包含一个列标志和列标志下方用于设定条件的单元格.

注意：

参数field为可选项,如果省略,函数DCOUNT返回数据库中满足条件criteria的所有记录数

例子：

![r5lurW](https://upiclw.oss-cn-beijing.aliyuncs.com/uPic/r5lurW.jpg)

公式：

1. 指定项目的有效支出

    =DCOUNT(B3:E9,E3,G3:G4)

    这里的结果是2，返回的是10月8日和10月10日的值。

2. 指定项目的支出

    =DCOUNT(B3:E9,,G3:G4)

    参数field为可选项,如果省略,函数DCOUNT返回数据库中满足条件criteria的所有记录数

    这里的结果是3，返回的是10月8日，10月10日和10月15日的值。
