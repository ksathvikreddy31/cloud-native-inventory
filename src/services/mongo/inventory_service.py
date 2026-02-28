from database.mongo import mongo_db

def add(data):
    mongo_db.inventory.insert_one(data)
    return {"msg":"Inventory added Mongo"}

def view():
    return list(mongo_db.inventory.find({},{"_id":0}))