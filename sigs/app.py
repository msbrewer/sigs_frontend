import time
import requests
from flask import Flask, render_template, request, jsonify
from flask_login import login_user, logout_user, login_required
from sigs.cfg import initCfg
from sigs.ext import db, lm
from sigs.users import users, User
from sigs.pairs import pairs, Pair, addPair

def initApp(cfg: dict) -> Flask:
    app = Flask(__name__)
    app.config = {**app.config, **cfg}
    return app

def initExt(app: Flask) -> Flask:
    db.init_app(app)
    lm.init_app(app)
    return app

def initRoutes(app: Flask) -> Flask:
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/login", methods=["POST"])
    def login():
        import time
        time.sleep(1)
        formData = request.get_json()
        u = User.query.filter(User.email == formData["email"]).first()
        if not u or u.passwd != formData["passwd"]:
            return jsonify({
                "ok": False,
                "data": "Invalid Username/Password"
                })
        login_user(u)
        db.session.commit()
        return jsonify({"ok": True, "isAdmin": u.hasRole("admin")})

    @app.route('/logout')
    @login_required
    def logout():
        import time
        time.sleep(1)
        logout_user()
        return jsonify('OK')

    app.register_blueprint(users, url_prefix="/api")
    app.register_blueprint(pairs, url_prefix="/api")
    @app.route("/positionUpdate", methods=["POST"])
    def positionUpdate():
        data = request.get_json()
        userEmail = data["userEmail"]
        tradeData = data["tradeData"]
        user = User.query.filter_by(email=userEmail).first()
        if not user:
            return jsonify("Not Found"), 404
        oldData = user.data
        for pair in oldData["forex"]["pairs"]:
            if pair["label"] == tradeData["label"]:
                pair["orderSize"] = tradeData["orderSize"]
                pair["position"] = tradeData["position"]
        user.data = oldData
        db.session.commit()
        return jsonify("OK")

    @app.route("/positionsUpdate", methods=["POST"])
    def positionsUpdate():
        import json
        data=request.get_json()
        userData = data["userData"]
        userEmail = data["userEmail"]
        user = User.query.filter_by(email=userEmail).first()
        if not user:
            return jsonify("Not Found"), 404 
        oldData = user.data
        oldData["forex"]["pairs"] = userData
        user.data = oldData
        db.session.commit()
        return jsonify("Ok")


    @app.route("/webhook", methods=["POST"])
    def webhook():
        import json
        data=request.get_json()
        pair = Pair.query.filter_by(label=data["pair"]).first()
        if pair == None:
            addPair(data["pair"], data["exchange"])
            db.session.commit()
        if data["term"] == "trend":
            pair.trend = data["direction"]
            db.session.commit()
            return jsonify("OK")
        if data["term"] == "confirmation":
            pair.confirmation = data["direction"]
            db.session.commit()
            return jsonify("OK")
        if data["term"] == "trig":
            pair.trig = data["direction"]
            db.session.commit()
        pair = Pair.query.filter_by(label=data["pair"]).first()
        pairDict = {
                    'label' : pair.label,
                    'exchange' : pair.exchange,
                    'trig' : pair.trig
                    }
        pairData = json.dumps(pairDict)
        for user in User.query.all():
            userData = user.data
            '''
            if userData["binance"]["apiKey"] != "":
            if data["exchange"] == "binance":
                dataToSend = {
                        "tradeData" : request.get_json(),
                        "userData" : userData["binance"],
                        "userEmail": user.email
                        }
                newHeaders = {
                        'Content-type': 'application/json',
                        'Accept': 'text/plain'
                        }
                requests.post(
                        "http://127.0.0.1:3000/" + data["exchange"],
                        headers=newHeaders,
                        json = dataToSend
                        )
            '''
            if userData["forex"]["username"] != "":
                if data["exchange"] == "forex":
                    dataToSend = {
                            "tradeData" : request.get_json(),
                            "pairData" : pairData,
                            "userData" : userData["forex"],
                            "userEmail" : user.email,
                            }
                    newHeaders = {
                            'Content-type': 'application/json',
                            'Accept': 'text/plain'
                            }
                    requests.post(
                            "http://127.0.0.1:5002/" + data["exchange"],
                            headers=newHeaders,
                            json = dataToSend
                            )
            if userData["oanda"]["acctId"] != "":
                if data["exchange"] == "oanda":
                    dataToSend = {
                            "tradeData" : request.get_json(),
                            "pairData" : pairData,
                            "userData" : userData["oanda"],
                            "userEmail" : user.email,
                            }
                    newHeaders = {
                            'Content-type': 'application/json',
                            'Accept': 'text/plain'
                            }
                    requests.post(
                            "http://127.0.0.1:5003/" + data["exchange"],
                            headers=newHeaders,
                            json = dataToSend
                            )
        return jsonify("OK")

    return app


def makeApp(env: str) -> Flask:
    return initRoutes(initExt(initApp(initCfg(env))))

@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)
