import json
from flask import Blueprint, jsonify, request
from sigs.ext import db
from flask_login import UserMixin, login_required, current_user
from gcapi import GCapiClient

# MODEL

"""
Forex :
    username Str
    passwd Str
    apikey Str
    pairs (List {label: Str, orderSize: Integer, position: Str})

Binance :
    apikey Str
    secretkey Str
    pairs (List {label: Str, orderSize: Float})

Oanda :
    acctId Str
    apikey Str
    pairs (List {label: Str, orderSize: Float})

User :
    id Int
    email Str
    passwd Str
    admin Bool
    forex Forex
    binance Binance
"""

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    passwd = db.Column(db.String(120))
    data_json = db.Column(db.Text)

    @property
    def data(self):
        return json.loads(self.data_json)

    @data.setter
    def data(self, newData):
        self.data_json = json.dumps(newData)

    def hasRole(self, role):
        # change everyone to isAdmin()... like later.. after awhile.. probably never
        return self.data["admin"]


# UPDATE


def addUser(
        email: str, passwd: str, admin = False,
        forexPairs=[],
        binancePairs=[],
        oandaPairs=[],
        ):
    u = User(email=email, passwd=passwd)
    u.data = {
            "admin": admin,
            "forex": {
                "username": "",
                "password": "",
                "apiKey": "",
                "tradingAcctId" : "",
                "pairs": [{"label": l, "orderSize": 0, "position": "NEUTRAL", "isAverse" : False} for l in forexPairs],
                },
            "binance": {
                "apiKey": "",
                "secretKey": "",
                "pairs": [{"label": l, "orderSize": 0.00, "isAverse" : False} for l in binancePairs],
                },
            "oanda": {
                "acctId": "",
                "apiKey": "",
                "pairs": [{"label": l, "orderSize": 0.00, "isAverse" : False} for l in oandaPairs],
            },
            }
    db.session.add(u)
    db.session.commit()


# SUBSCRIPTIONS


users = Blueprint("users", __name__)
@users.route("/user/")
@login_required
def user():
    import time
    time.sleep(1)
    userData = current_user.data
    return jsonify({
        "forexPairs": userData["forex"]["pairs"],
        "binancePairs": userData["binance"]["pairs"],
        "oandaPairs": userData["oanda"]["pairs"],
        })

@users.route("/users/")
@login_required
def index():
    import time
    time.sleep(1)
    if not current_user.hasRole("admin"):
        return (jsonify("FUCK OFF"), 403)
    data = [
            {
                "id": u.id,
                "email": u.email,
                "passwd": u.passwd,
                **u.data
                }
            for u in User.query.all()
            ]
    return jsonify(data)

def updatePairs(newPairs, oldPairs):
    newLabels = [p["label"] for p in newPairs]
    oldLabels = [p["label"] for p in oldPairs]
    pairs = [
            p for p in oldPairs
            if p["label"] in newLabels
            ]
    for label in newLabels:
        if label not in oldLabels:
            pairs.append({"label": label, "orderSize": 0, "position": "NEUTRAL", "isAverse": False})
    return pairs

@users.route("/users/adminAddNewUser", methods=["POST"])
@login_required
def adminSaveNewUser():
    if not current_user.hasRole("admin"):
        return(jsonify("FUCK OFF"), 403)
    newUser = request.get_json()
    addUser(newUser["email"], newUser["passwd"])
    return jsonify("OK")

@users.route("/users/adminUpdate", methods=["PUT"])
@login_required
def adminUpdate():
    if not current_user.hasRole("admin"):
        return (jsonify("FUCK OFF"), 403)
    stuff = request.get_json()
    u = User.query.get(stuff["id"])
    if stuff["passwd"] != "":
        newPass = stuff["passwd"]
    userData = u.data
    userData["admin"] = stuff["isAdmin"]
    userData["binance"]["pairs"] = updatePairs(
            stuff["binance"],
            userData["binance"]["pairs"]
            )
    userData["forex"]["pairs"] = updatePairs(
            stuff["forex"],
            userData["forex"]["pairs"]
            )
    userData["oanda"]["pairs"] = updatePairs(
            stuff["oanda"],
            userData["oanda"]["pairs"]
            )
    u.data = userData
    db.session.commit()
    return jsonify("OK")

@users.route("/users/passwd/", methods=["PUT"])
@login_required
def passwd():
    import time
    time.sleep(1)
    current_user.passwd = request.get_json()
    db.session.commit()
    return jsonify("OK")

@users.route("/users/binance/", methods=["PUT"])
@login_required
def binance():
    import time
    time.sleep(1)
    userData = current_user.data
    userData["binance"]["apiKey"] = request.get_json()["apiKey"]
    userData["binance"]["secretKey"] = request.get_json()["secretKey"]
    current_user.data = userData
    db.session.commit()
    return jsonify("OK")

@users.route("/users/forex/", methods=["PUT"])
@login_required
def forex():
    import time
    time.sleep(1)
    userData = current_user.data
    userData["forex"]["username"] = request.get_json()["username"]
    userData["forex"]["password"] = request.get_json()["password"]
    userData["forex"]["apiKey"] = request.get_json()["apiKey"]
    current_user.data = userData
    db.session.commit()
    return jsonify("OK")

@users.route("/users/oanda/", methods=["PUT"])
@login_required
def oanda():
    import time
    time.sleep(1)
    userData = current_user.data
    userData["oanda"]["acctId"] = request.get_json()["acctId"]
    userData["oanda"]["apiKey"] = request.get_json()["apiKey"]
    current_user.data = userData
    db.session.commit()
    return jsonify("OK")

@users.route("/users/pairs/", methods=["PUT"])
@login_required
def pairs():
    import time
    time.sleep(1)
    pairData = request.get_json()
    userData = current_user.data
    userData["forex"]["pairs"] = pairData["forexPairs"]
    userData["binance"]["pairs"] = pairData["binancePairs"]
    userData["oanda"]["pairs"] = pairData["oandaPairs"]
    current_user.data = userData
    db.session.commit()
    return jsonify("OK")
