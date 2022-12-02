import json
from flask import Blueprint, jsonify, request
from sigs.ext import db
from flask_login import login_required, current_user

#MODEL

"""
Pair :
    label str
    trend = Long | Short
    confirmation = Long | Short
    trig = Long | Short

"""

class Pair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(12), unique=True, nullable=False)
    exchange = db.Column(db.String(28))
    trend = db.Column(db.String(8))
    confirmation = db.Column(db.String(8))
    trig = db.Column(db.String(8))

    @property
    def agreed(self):
       return((self.trend == self.confirmation) and (self.confirmation == self.trig) and (self.trend == self.trig))

def addPair(label: str, exchange: str, trend="", confirmation="", trig=""):
    p = Pair(label=label, exchange=exchange, trend=trend, confirmation=confirmation, trig=trig)
    db.session.add(p)
    db.session.commit()

pairs = Blueprint("pairs", __name__)

@pairs.route("/pairs/")
@login_required
def index():
    import time
    time.sleep(1)
    if not current_user.hasRole("admin"):
        return(jsonify("FUCK OFF"), 403)
    data = [
        {
            "label": p.label,
            "exchange": p.exchange,
            "trend": p.trend,
            "confirmation" : p.confirmation,
            "trig" : p.trig,
        }
        for p in Pair.query.all()
    ]
    return jsonify(data)

@pairs.route("/pairs/", methods=["POST"])
@login_required
def createPair():
    import time
    time.sleep(1)
    pairData = request.get_json()
    if not Pair.query.filter_by(label=pairData["label"]).first():
        addPair(
            pairData["label"],
            pairData["exchange"],
            pairData["trend"],
            pairData["confirmation"],
            pairData["trig"]
            )
    return jsonify("OK")

@pairs.route("/pairs/", methods=["PUT"])
@login_required
def updatePair():
    import time
    time.sleep(1)
    pairData = request.get_json()
    pair = Pair.query.filter_by(label=pairData["label"]).first()
    pair.exchange = pairData["exchange"]
    pair.trend = pairData["trend"]
    pair.confirmation = pairData["confirmation"]
    pair.trig = pairData["trig"]
    db.session.commit()
    return jsonify("OK")
