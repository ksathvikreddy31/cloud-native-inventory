from models.order import Order
from models.order_item import OrderItem
from models.inventory import Inventory
from database.mysql import db

def add(data):

    order = Order(user_id=data["user_id"],status="created")
    db.session.add(order)
    db.session.commit()

    for item in data["products"]:

        inv = Inventory.query.filter_by(
            user_id=data["user_id"],
            product_id=item["product_id"]
        ).first()

        if inv.stock < item["qty"]:
            return {"msg":"Not enough stock"}

        inv.stock -= item["qty"]

        db.session.add(OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            qty=item["qty"]
        ))

    db.session.commit()
    return {"msg":"Order created SQL"}

def view():
    return [{"id":o.id,"user_id":o.user_id} for o in Order.query.all()]