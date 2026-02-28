from database.mongo import mongo_db

def add(data):
    mongo_db.orders.insert_one(data)
    return {"msg":"Order created Mongo"}

def view():
    return list(mongo_db.orders.find({},{"_id":0}))