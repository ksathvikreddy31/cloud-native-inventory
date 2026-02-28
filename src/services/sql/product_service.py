from models.product import Product
from database.mysql import db

def add(data):
    db.session.add(Product(name=data["name"],price=data["price"]))
    db.session.commit()
    return {"msg":"Product added SQL"}

def view():
    return [{"id":p.id,"name":p.name,"price":p.price}
            for p in Product.query.all()]