from database.mongo import mongo_db

def add(data):
    mongo_db.products.insert_one(data)
    return {"msg":"Product added Mongo"}

def view():
    return list(mongo_db.products.find({},{"_id":0}))