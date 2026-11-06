# 编写一个程序，来获取本地的 IP，并且使用 dict 进行读取

# https://ipinfo.io/json

import requests
import json

from rich import print

response = requests.get("https://ipinfo.io/json")
# {'ip': '123.185.16.128', 'hostname': '128.16.185.123.broad.dl.ln.dynamic.163data.com.cn', 'city': 'Dalianwan', 'region': 'Liaoning', 'country': 'CN', 'loc': '39.0286,121.6950', 'org': 'AS134762 CHINANET Liaoning province Dalian MAN network', 'postal': '121000', 'timezone': 'Asia/Shanghai', 'readme': 'https://ipinfo.io/missingauth'}
# print(response.json())

# 将结果转换为 dict 类型
ip_info = json.loads(response.content.decode("utf-8"))
print(ip_info['region'])


