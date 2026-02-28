from models.user import User
from database.mysql import db

def add(data):
    db.session.add(User(name=data["name"]))
    db.session.commit()
    return {"msg":"User added SQL"}

def view():
    return [{"id":u.id,"name":u.name} for u in User.query.all()]