from flask import Flask,render_template, request
from datetime import datetime
app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>許旆慈Python網頁20260409</h1>"
    link += "<a href=/mis>MIS</a><hr>"
    link += "<a href=/today>顯示日期時間</a><hr>"
    link += "<a href=/welcome?u=旆慈&d=靜宜資管&c=資訊管理導論>Get傳直</a><hr>"
    link += "<a href=/account>Poste傳值</a><hr>"
    link += "<a href=/about>關於我</a><hr>"
    link += "<a href=/calc>次方與根號計算</a><hr>"
    return link
@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>返回首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html",datetime=str(now))
@app.route("/about")
def me():
    return render_template("about.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    u = request.values.get("u")
    d = request.values.get("d")
    c = request.values.get("c")
    return render_template("welcome.html", name=u,dep=d,course = c)

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

