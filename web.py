from flask import Flask, render_template, request
from datetime import datetime
import requests
import os
import json
import firebase_admin
import time
from firebase_admin import credentials, firestore
from bs4 import BeautifulSoup

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>許旆慈Python網頁20260326</h1>"
    link += "<a href=/mis>MIS</a><hr>"
    link += "<a href=/today>顯示日期時間</a><hr>"
    link += "<a href=/welcome?u=旆慈&d=靜宜資管&c=資訊管理導論>Get傳值</a><hr>"
    link += "<a href=/account>Post傳值</a><hr>"
    link += "<a href=/about>關於我</a><hr>"
    link += "<a href=/calc>次方與根號計算</a><hr>"
    link += "<a href=/read2>讀取姓名</a><hr>"
    link += "<a href=/read1>讀取Firestore資料</a><hr>"
    link += "<a href=/spider>爬取子青老師本學習課程</a><hr>"
    link += "<a href=/movie>搜尋即將上映的電影(網頁爬蟲)</a><hr>"
    link += "<a href=/spidermo>爬取即將上映的電影存入資料庫</a><hr>"
    link += "<a href=/searchMovie>查詢資料庫符合的電影</a><hr>"
    link += "<a href=/road>台中市十大肇事路口</a><hr>"
    link += "<a href=/Weather>台中市天氣概況</a><hr>"
    return link

# ==========================================
# 這是你要求的 (2)searchMovie 功能
# ==========================================



@app.route("/Weather")
def weather():
    # 1. 標題 (記得名字改為你的)
    R = "<h1>台中市天氣概況</h1><br>"
    
    # 2. 設定參數 (Web 版不建議用 input，我們先寫死臺中市)
    city = "臺中市"
    token = "rdec-key-123-45678-011121314" # 請確認這是正確的 Authorization Key
    
    # 修正後的 URL (不要重複拼接)
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={token}&format=JSON&locationName={city}"

    try:
        # 3. 抓取資料
        data = requests.get(url, verify=False)
        json_data = json.loads(data.text)
        
        # 4. 解析資料 (照老師給的層次抓取)
        # 這裡要確認 API 回傳的結構是否符合
        location_data = json_data["records"]["location"][0]
        weather_state = location_data["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
        rain_chance = location_data["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
        
        # 5. 把結果組合進 R，網頁才看得到
        R += f"目前城市：{city}<br>"
        R += f"天氣狀況：{weather_state}<br>"
        R += f"降雨機率：{rain_chance}%<br>"
        
    except Exception as e:
        R += f"天氣資料讀取失敗，原因：{e}"

    # 6. 回傳結果
    return R

if __name__ == "__main__":
    app.run(debug=True)






@app.route("/road")
def opendata():
    # 所有的內容都要縮排在 def 裡面
    R = "<h1>台中市十大肇事路口(113年10月)許旆慈</h1><br>"
    requests.packages.urllib3.disable_warnings()

    url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Connection': 'close'
    }

    # 抓取資料
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        data_list = response.json()
        
        for item in data_list:
            area = item.get("區序", "")
            location = item.get("路口名稱", "")
            count = item.get("總件數", "0")
            reason = item.get("主要肇因", "")
            # 把每一行結果加進 R 字串中，網頁才會顯示
            R += f"{area}{location}：發生{count}件，主因是{reason}<br>"
            
    except Exception as e:
        R += f"暫時無法取得資料，錯誤原因：{e}"

    # 最後把組合好的 R 回傳給瀏覽器
    return R





@app.route("/searchMovie", methods=["GET", "POST"])
def searchMovie():
    # 建立符合圖片格式的表單 (外框、文字、按鈕)
    Result = """
    <div style="border: 1px solid #ccc; padding: 10px; display: inline-block; margin-bottom: 20px;">
        <form action="/searchMovie" method="post" style="margin: 0;">
            <label>請輸入欲查詢的片名：</label>
            <input type="text" name="keyword" required>
            <button type="submit">確定送出</button>
        </form>
    </div>
    """

    if request.method == "POST":
        keyword = request.form.get("keyword")
        Result += f"<h3>您查詢的關鍵字為：<span style='color:red;'>{keyword}</span></h3><hr>"
        
        # 連線至資料庫
        db = firestore.client()
        collection_ref = db.collection("電影2B")
        docs = collection_ref.stream()
        
        found = False
        for doc in docs:
            movie_data = doc.to_dict()
            title = movie_data.get("title", "")
            
            # 判斷關鍵字是否在片名中
            if keyword in title:
                found = True
                movie_id = doc.id
                picture = movie_data.get("picture", "")
                hyperlink = movie_data.get("hyperlink", "")
                showDate = movie_data.get("showDate", "")
                
                # 依序印出：編號,片名,海報,介紹頁及上映日期
                Result += f"<b>編號：</b> {movie_id}<br>"
                Result += f"<b>片名：</b> {title}<br>"
                Result += f"<b>海報：</b><br><img src='{picture}' width='150'><br>"
                Result += f"<b>介紹頁：</b> <a href='{hyperlink}' target='_blank'>點此查看介紹頁</a><br>"
                Result += f"<b>上映日期：</b> {showDate}<br>"
                Result += "<hr>"
                
        if not found:
            Result += f"目前資料庫中找不到片名包含「{keyword}」的電影。<br>"

    Result += "<br><a href='/'>返回首頁</a>"
    return Result

# ==========================================
# 以下為原有的功能
# ==========================================
@app.route("/spidermo")
def spitermo():
    R = ""
    db = firestore.client()

    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    lastUpdate = sp.find(class_="smaller09").text.replace("更新時間:","")
    result = sp.select(".filmListAllX li")
    
    total = 0
    for item in result:
        total += 1
        movie_id = item.find("a").get("href").replace("/movie/","").replace("/","")
        title = item.find(class_="filmtitle").text
        picture = "http://www.atmovies.com.tw" + item.find("img").get("src")
        hyperlink = "http://www.atmovies.com.tw" + item.find("a").get("href")
        showDate = item.find(class_="runtime").text[5:15]

        doc = {
            "title": title,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "lastUpdate": lastUpdate
        }

        doc_ref = db.collection("電影2B").document(movie_id)
        doc_ref.set(doc)

    R += "網站最近更新日期:" + lastUpdate + "<br>"
    R += "總共爬取" + str(total) + "部電影到資料庫<br>"
    R += "<br><a href='/'>返回首頁</a>"
    return R

@app.route("/movie")
def movie():
    keyword = request.args.get("keyword", "")

    R = f"""
    <form action="/movie" method="get">
        <label>請輸入電影關鍵字：</label>
        <input type="text" name="keyword" value="{keyword}">
        <button type="submit">搜尋</button>
    </form>
    <hr>
    """
    
    if keyword:
        R += f"您搜尋的關鍵字是：<b>{keyword}</b><br><br>"
    
    url = "https://www.atmovies.com.tw/movie/next"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result = sp.select(".filmListAllX li")
    
    found_count = 0
    for item in result:
        try:
            img_tag = item.find("img")
            title = img_tag.get("alt") if img_tag else "無標題"
            
            if not keyword or keyword in title:
                introduce = "https://www.atmovies.com.tw" + item.find("a").get("href")
                img_url = "https://www.atmovies.com.tw" + img_tag.get("src")
                
                R += f"<b>{title}</b><br>"
                R += f'<a href="{introduce}" target="_blank">介紹頁超鏈結</a><br>'
                R += f'<img src="{img_url}" width="200"><br><br>'
                found_count += 1
        except:
            continue
            
    if keyword and found_count == 0:
        R += f"找不到包含「{keyword}」的即將上映電影。"
            
    return R

@app.route("/spider")
def spider():
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url) 
    Data.encoding = "utf-8"
    
    sp = BeautifulSoup(Data.text, "html.parser")
    items = sp.select(".team-box a") 
    
    info = "" 
    for i in items:
        info += i.text + "：" + i.get("href") + "<br>"
        
    return info

@app.route("/read2", methods=["GET", "POST"])
def read2():
    Result = "<h1>靜宜資管老師查詢</h1>"
    Result += '<form action="/read2" method="post">'
    Result += '請輸入老師姓名關鍵字：<input type="text" name="keyword">'
    Result += '<button type="submit">查詢</button></form><br>'

    if request.method == "POST":
        keyword = request.form.get("keyword") 
        Result += f"<h3>查詢結果 (關鍵字: {keyword}):</h3>"
        
        db = firestore.client()
        collection_ref = db.collection("資管2B 2026")
        docs = collection_ref.get()
        
        found = False
        for doc in docs:
            teacher_data = doc.to_dict()
            name = teacher_data.get('name')
            
            if name and keyword in name: 
                found = True
                lab = teacher_data.get('lab', '未知')
                Result += f"<span style='color:blue; font-weight:bold'>{name}</span> 老師的研究室是在 <b>{lab}</b><br>"
        
        if not found:
            Result += f"找不到姓名包含「{keyword}」的老師。<br>"

    Result += "<br><a href=/>返回首頁</a>"
    return Result

@app.route("/read1")
def read1():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("資管2B 2026")
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).get()
    for doc in docs:
        Result += str(doc.to_dict()) + "<br>"
    return Result 

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>返回首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html", datetime=str(now))

@app.route("/about")
def me():
    return render_template("about.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    u = request.values.get("u")
    d = request.values.get("d")
    c = request.values.get("c")
    return render_template("welcome.html", name=u, dep=d, course=c)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/calc", methods=["GET", "POST"])
def calc():
    if request.method == "POST":
        x = float(request.form["x"])
        y = float(request.form["y"])
        opt = request.form["opt"]

        if opt == "∧":
            result = x ** y
        elif opt == "√":
            if y == 0:
                result = "數學不能開0次根號"
            else:
                result = x ** (1/y)
        else:
            result = "請輸入∧或√"

        return render_template("calc.html", result=result)
    return render_template("calc.html")

if __name__ == "__main__":
    app.run(debug=True)