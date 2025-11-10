import requests
import json

def bytedance_jobs(offset=0):
    # balabala
    # return #
    # pass # 我还不知道该干点什么，先过！
    url = "https://jobs.bytedance.com/api/v1/search/job/posts?keyword=&limit=2&job_category_id_list=&tag_id_list=&location_code_list=&subject_id_list=&recruitment_id_list=&portal_type=2&job_function_id_list=&storefront_id_list=&portal_entrance=1"

    payload = json.dumps({
        "keyword": "",
        "limit": 10,
        "offset": offset,
        "job_category_id_list": [],
        "tag_id_list": [],
        "location_code_list": [],
        "subject_id_list": [],
        "recruitment_id_list": [],
        "portal_type": 2,
        "job_function_id_list": [],
        "storefront_id_list": [],
        "portal_entrance": 1
    })
    
    headers = {
        
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://jobs.bytedance.com',
        'Portal-Channel': 'office',
        'Portal-Platform': 'pc',
        'Referer': 'https://jobs.bytedance.com/experienced/position/list?keywords=&category=&location=&project=&type=&job_hot_flag=&current=6&limit=10&functionCategory=&tag=',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'accept-language': 'zh-CN',
        'env': 'undefined',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'website-path': 'society'
    
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    get_jobs_info(response.text)

def get_jobs_info(response_text):
    
    jobs_info = json.loads(response_text) # 将json字符串转换成字典
    
    if int(jobs_info['code']) == 0:
        # 遍历
        jobs_list = jobs_info['data']['job_post_list']
        
        length = len(jobs_list)
        
        for i in range(length):
            job_info = jobs_list[i]
            # print("*"*60)
            # print("第 ",i," 个职位信息：")
            print(job_info['id'])
            # print(job_info['title'])
            # print(job_info['description'])
            # print(job_info['requirement'])
            # print("*"*60)
            save_jobs_info(job_info['id'],description=job_info['description'],requirement=job_info['requirement'],title=job_info['title'])
            
def save_jobs_info(id,title="默认",description="默认描述",requirement="默认需求"):
    # 保存职位信息到 csv 中，csv 文件名为：jobs.csv
    # 采用的是追加的方式
    
    with open('jobs.csv', 'a', encoding='utf-8') as f:
        f.write(id+","+title+","+description.replace("\n","")+","+requirement.replace("\n","")+"\n")