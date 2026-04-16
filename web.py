from flask import Flask, render_template, request
from datetime import datetime

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

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
    return link

@app.route("/spider")
def spider():
    import requests # 放在這裡或檔案最上方都可以
    from bs4 import BeautifulSoup
    
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url) # 確保是小寫 requests
    Data.encoding = "utf-8"
    
    sp = BeautifulSoup(Data.text, "html.parser")
    items = sp.select(".team-box a") # 換個變數名稱叫 items
    
    info = "" # 用來存結果的字串
    for i in items:
        info += i.text + "：" + i.get("href") + "<br>"
        
    return info



@app.route("/read2", methods=["GET", "POST"])
def read2():
    # 網頁標題與查詢表單
    Result = "<h1>靜宜資管老師查詢</h1>"
    Result += '<form action="/read2" method="post">'
    Result += '請輸入老師姓名關鍵字：<input type="text" name="keyword">'
    Result += '<button type="submit">查詢</button></form><br>'

    if request.method == "POST":
        keyword = request.form.get("keyword") # 取得使用者輸入的字，例如「楊」
        Result += f"<h3>查詢結果 (關鍵字: {keyword}):</h3>"
        
        db = firestore.client()
        collection_ref = db.collection("資管2B 2026")
        docs = collection_ref.get()
        
        found = False
        for doc in docs:
            teacher_data = doc.to_dict()
            name = teacher_data.get('name')
            
            # --- 關鍵修正：判斷關鍵字是否有在姓名裡面 ---
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
    db = firestore.client() # 這裡原本拼錯，已修正
    collection_ref = db.collection("資管2B 2026")
    # 這裡保留你原本的排序邏輯，但修正了 stream 和 return 縮排
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).get()
    for doc in docs:
        Result += str(doc.to_dict()) + "<br>"
    return Result # 縮排往左移，這樣才會顯示全部資料

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