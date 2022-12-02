from sigs import makeApp
from sigs.ext import db
from sigs.users import User, addUser
from sigs.pairs import Pair, addPair

app = makeApp("dev")


with app.app_context():
    users = User.query.all()
    for user in users:
        userData = user.data
        for pair in userData["forex"]["pairs"]:
            pair["isAverse"] = False
        for pair in userData["oanda"]["pairs"]:
            pair["isAverse"] = False
        user.data = userData
        db.session.commit()
