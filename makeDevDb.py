from sigs import makeApp
from sigs.ext import db
from sigs.users import User, addUser
from sigs.pairs import Pair, addPair

app = makeApp("dev")


with app.app_context():
    db.create_all()
    addUser("username", "password", True)
