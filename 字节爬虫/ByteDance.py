import requests
import json

url = "https://jobs.bytedance.com/api/v1/search/job/posts?limit=3&offset=NaN&job_category_id_list=&tag_id_list=&location_code_list=&subject_id_list=&recruitment_id_list=&portal_type=2&job_function_id_list=&storefront_id_list=&portal_entrance=2&_signature=KwX3zgAAAABhRNBR0nsM2ysF99AAEOe"

payload = json.dumps({
  "limit": 3,
  "offset": None,
  "job_category_id_list": [],
  "tag_id_list": [],
  "location_code_list": [],
  "subject_id_list": [],
  "recruitment_id_list": [],
  "portal_type": 2,
  "job_function_id_list": [],
  "storefront_id_list": [],
  "portal_entrance": 2
})
headers = {
  'Accept': 'application/json, text/plain, */*',
  'Connection': 'keep-alive',
  'Content-Type': 'application/json',
  'Origin': 'https://jobs.bytedance.com',
  'Portal-Channel': 'office',
  'Portal-Platform': 'h5',
  'Referer': 'https://jobs.bytedance.com/experienced/m/position/list?keywords=',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
  'accept-language': 'zh-CN',
  'env': 'undefined',
  'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'website-path': 'society',
  'x-csrf-token': '8kY1HkybjFiCgwLOm2FG3ah-7iEoPgHShxWA4Qzl8pg=',
  'Cookie': 'locale=zh-CN; device-id=7490094212570973697; channel=office; s_v_web_id=verify_mecs3t2t_FfMXdXb6_GK61_4whE_B0Xi_sdvRhIXUWh4b; platform=h5; atsx-csrf-token=8kY1HkybjFiCgwLOm2FG3ah-7iEoPgHShxWA4Qzl8pg%3D'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
