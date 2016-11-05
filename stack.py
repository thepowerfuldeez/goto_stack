from flask import Flask, render_template, request
from Gadalka import Gadalka
app = Flask(__name__)

g = Gadalka()

@app.route("/", methods=["POST", "GET"])
def index():
    result = ""
    if request.method == "POST":
        link = request.form["film"]
        if link:
            try:
                if link.split("//")[1][:2] == "ru":
                    g.switch = "ru"
                    result = g.predict(link)
                else:
                    g.switch = "en"
                    result = g.predict(link)
            except:
                pass
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
