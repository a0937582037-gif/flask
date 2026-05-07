import requests
import json
import time

# 忽略 SSL 警告
requests.packages.urllib3.disable_warnings()

url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"

# 模擬更完整的瀏覽器資訊
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Connection': 'close' # 告訴伺服器抓完就斷，不要占用連線，減少被踢的機率
}

def get_data(url):
    for i in range(3): # 最多嘗試 3 次
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"第 {i+1} 次連線失敗，正在重試...")
            time.sleep(2) # 休息 2 秒再試
    return None

# 開始抓取
data_list = get_data(url)

if data_list:
    for item in data_list:
        # 根據你的圖片格式組合字串
        area = item.get("區序", "")
        location = item.get("路口名稱", "")
        count = item.get("總件數", "0")
        reason = item.get("主要肇因", "")
        
        print(f"({area}){location}：發生{count}件，主因是{reason}")
else:
    print("伺服器連線失敗，請檢查網路或稍後再試。")