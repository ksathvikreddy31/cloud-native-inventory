from database.mysql import db

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    db_type = db.Column(db.String(20), default='sql')
    role = db.Column(db.String(20), default='user')

class MasterInventory(db.Model):
    __tablename__ = 'master_inventory'
    item_id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))
    master_stock = db.Column(db.Integer)

class UserProduct(db.Model):
    __tablename__ = 'user_products'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    master_item_id = db.Column(db.Integer)
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    items_list = db.Column(db.String(1000))
    total = db.Column(db.Float)

class CartItem(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    user_product_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
