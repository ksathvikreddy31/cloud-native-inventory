from models.inventory import Inventory
from database.mysql import db

def add(data):
    db.session.add(
        Inventory(
            user_id=data["user_id"],
            product_id=data["product_id"],
            stock=data["stock"]
        )
    )
    db.session.commit()
    return {"msg":"Inventory added SQL"}

def view():
    return [{"user":i.user_id,"product":i.product_id,"stock":i.stock}
            for i in Inventory.query.all()]