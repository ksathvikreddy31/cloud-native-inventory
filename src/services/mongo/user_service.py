from database.mongo import mongo_db

def add(data):
    mongo_db.users.insert_one(data)
    return {"msg":"User added Mongo"}

def view():
    return list(mongo_db.users.find({},{"_id":0}))