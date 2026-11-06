# 权威清单：约 100 个常用 Excel 函数

> **第一次看本仓库？** 建议先读 [beginner-guide.md](beginner-guide.md)（小白向），再查下表。  
> 下表是「产品清单+进度」，不解释 **Python 里怎么调**，那种说明在源码 docstring 与 `demo/` 里。

列 **状态**：`done` 已实现（含简化语义）、`partial` 部分场景或边缘与 Excel 不一致、`stub` 仅占位或未实现。


| #   | 函数           | 分类  | 状态      | 说明                           |
| --- | ------------ | --- | ------- | ---------------------------- |
| 1   | SUM          | 数学  | done    |                              |
| 2   | AVERAGE      | 数学  | done    |                              |
| 3   | AVERAGEA     | 数学  | done    |                              |
| 4   | COUNT        | 数学  | done    |                              |
| 5   | COUNTA       | 数学  | done    |                              |
| 6   | COUNTBLANK   | 数学  | done    |                              |
| 7   | MAX          | 数学  | done    |                              |
| 8   | MIN          | 数学  | done    |                              |
| 9   | MEDIAN       | 数学  | done    |                              |
| 10  | MODE.SNGL    | 统计  | done    | 多众数取最小；导出 ``MODE_SNGL`` |
| 11  | PRODUCT      | 数学  | done    |                              |
| 12  | SUMPRODUCT   | 数学  | partial | 等长一维                         |
| 13  | SUBTOTAL     | 数学  | partial | 含 7/8/10/11 标准差与方差；101–111 与 1–11 同映射 |
| 14  | AGGREGATE    | 数学  | partial | 忽略 options 精细语义              |
| 15  | ROUND        | 数学  | done    | 半舍远离 0                       |
| 16  | ROUNDDOWN    | 数学  | done    |                              |
| 17  | ROUNDUP      | 数学  | done    |                              |
| 18  | MROUND       | 数学  | done    |                              |
| 19  | CEILING.MATH | 数学  | done    | 以 `CEILING_MATH` 导出          |
| 20  | FLOOR.MATH   | 数学  | done    | 以 `FLOOR_MATH` 导出            |
| 21  | INT          | 数学  | done    |                              |
| 22  | TRUNC        | 数学  | done    |                              |
| 23  | ABS          | 数学  | done    |                              |
| 24  | SIGN         | 数学  | done    |                              |
| 25  | MOD          | 数学  | done    |                              |
| 26  | POWER        | 数学  | done    |                              |
| 27  | SQRT         | 数学  | done    |                              |
| 28  | EXP          | 数学  | done    |                              |
| 29  | LN           | 数学  | done    |                              |
| 30  | LOG          | 数学  | done    |                              |
| 31  | LOG10        | 数学  | done    |                              |
| 32  | PI           | 数学  | done    |                              |
| 33  | RAND         | 数学  | done    |                              |
| 34  | RANDBETWEEN  | 数学  | done    |                              |
| 35  | FACT         | 数学  | done    |                              |
| 36  | COMBIN       | 数学  | done    |                              |
| 37  | PERMUT       | 数学  | done    |                              |
| 38  | GCD          | 数学  | done    |                              |
| 39  | LCM          | 数学  | done    |                              |
| 40  | QUOTIENT     | 数学  | done    |                              |
| 41  | SUMIF        | 条件  | done    | 简单比较串                        |
| 42  | SUMIFS       | 条件  | done    |                              |
| 43  | COUNTIF      | 条件  | done    |                              |
| 44  | COUNTIFS     | 条件  | done    |                              |
| 45  | AVERAGEIF    | 条件  | done    |                              |
| 46  | AVERAGEIFS   | 条件  | done    |                              |
| 47  | MAXIFS       | 条件  | done    |                              |
| 48  | MINIFS       | 条件  | done    |                              |
| 49  | IF           | 逻辑  | done    | 无短路                          |
| 50  | IFS          | 逻辑  | done    |                              |
| 51  | SWITCH       | 逻辑  | done    |                              |
| 52  | AND          | 逻辑  | done    |                              |
| 53  | OR           | 逻辑  | done    |                              |
| 54  | NOT          | 逻辑  | done    |                              |
| 55  | XOR          | 逻辑  | done    |                              |
| 56  | TRUE         | 逻辑  | done    |                              |
| 57  | FALSE        | 逻辑  | done    |                              |
| 58  | IFERROR      | 逻辑  | done    |                              |
| 59  | IFNA         | 逻辑  | done    |                              |
| 60  | CONCAT       | 文本  | done    |                              |
| 61  | TEXTJOIN     | 文本  | partial |                              |
| 62  | LEFT         | 文本  | done    |                              |
| 63  | RIGHT        | 文本  | done    |                              |
| 64  | MID          | 文本  | done    |                              |
| 65  | LEN          | 文本  | done    |                              |
| 66  | LENB         | 文本  | partial | UTF-8 字节长度；与 Excel DBCS 可能不同   |
| 67  | TRIM         | 文本  | done    |                              |
| 68  | UPPER        | 文本  | done    |                              |
| 69  | LOWER        | 文本  | done    |                              |
| 70  | PROPER       | 文本  | done    |                              |
| 71  | SUBSTITUTE   | 文本  | done    |                              |
| 72  | REPLACE      | 文本  | done    |                              |
| 73  | REPT         | 文本  | done    |                              |
| 74  | FIND         | 文本  | done    |                              |
| 75  | SEARCH       | 文本  | partial | 无通配符                         |
| 76  | TEXT         | 文本  | partial | 格式子集                         |
| 77  | VALUE        | 文本  | done    | 实现名 `VALUE_FROM_TEXT`        |
| 78  | CHAR         | 文本  | done    |                              |
| 79  | CODE         | 文本  | done    |                              |
| 80  | T            | 文本  | done    | 文本返回自身，否则 `''`；错误原样返回      |
| 81  | EXACT        | 文本  | done    |                              |
| 82  | FIXED        | 文本  | partial |                              |
| 83  | CLEAN        | 文本  | done    |                              |
| 84  | VLOOKUP      | 查找  | partial | 近似匹配有限                       |
| 85  | HLOOKUP      | 查找  | partial |                              |
| 86  | INDEX        | 查找  | done    |                              |
| 87  | MATCH        | 查找  | partial |                              |
| 88  | XLOOKUP      | 查找  | partial | 精确/正向                        |
| 89  | XMATCH       | 查找  | partial |                              |
| 90  | CHOOSE       | 查找  | done    |                              |
| 91  | ADDRESS      | 查找  | partial |                              |
| 92  | INDIRECT     | 查找  | partial | 无 `workbook` 为 `#REF!`；可选关键字 `workbook=` 查地址 |
| 93  | OFFSET       | 查找  | done    | 二维 `list` 矩形切片                 |
| 94  | ROW          | 查找  | partial |                              |
| 95  | COLUMN       | 查找  | partial |                              |
| 96  | ROWS         | 查找  | done    |                              |
| 97  | COLUMNS      | 查找  | done    |                              |
| 98  | TRANSPOSE    | 查找  | done    |                              |
| 99  | LOOKUP       | 查找  | partial |                              |
| 100 | UNIQUE       | 数组  | partial | 一维；二维按行（或 ``by_col`` 按列）去重   |


## 扩展（第 101+，同仓库实现但未计入上表「100」）


| 函数                                            | 分类  | 状态      |
| --------------------------------------------- | --- | ------- |
| TODAY / NOW / DATE / TIME                     | 日期  | done    |
| YEAR / MONTH / DAY / HOUR / MINUTE / SECOND   | 日期  | done    |
| WEEKDAY / WEEKNUM / ISOWEEKNUM                | 日期  | partial |
| EDATE / EOMONTH                               | 日期  | done    |
| NETWORKDAYS / WORKDAY                         | 日期  | partial |
| DATEDIF                                       | 日期  | partial |
| DATEVALUE / TIMEVALUE                         | 日期  | done    |
| PV / FV / PMT / NPER / RATE                   | 财务  | partial |
| IPMT / PPMT                                   | 财务  | partial |
| NPV / IRR / XNPV / XIRR                       | 财务  | partial |
| ISBLANK / ISNUMBER / ISTEXT / ISLOGICAL       | 信息  | done    |
| ISERROR / ISERR / ISNA                        | 信息  | done    |
| ISFORMULA / ISREF                             | 信息  | partial |
| N / TYPE / ERROR.TYPE                         | 信息  | partial |
| SORT / SORTBY / FILTER / SEQUENCE / RANDARRAY | 数组  | partial |
| MAXA / MINA                                   | 数学  | done    |


