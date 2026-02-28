from database.mongo import mongo_db
from database.mysql import get_db_connection
import traceback
import json

def execute_action(module, action, data):
    try:
        mongo_db.command("ping")
    except Exception:
        return {"success": False, "msg": "MongoDB is not running or unreachable. Please check connection."}

    try:
        if module == "storefront":
            if action == "pick":
                # Connect to MySQL physically to cross-reference and apply master_stock updates
                conn = get_db_connection()
                if not conn:
                    return {"success": False, "msg": "MySQL Database connection failed over Mongo route"}
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute("SELECT master_stock FROM godown_products WHERE id = %s", (data["godown_product_id"],))
                godown_prod = cursor.fetchone()
                qty_to_pick = int(data["qty"])
                
                if not godown_prod or godown_prod["master_stock"] < qty_to_pick:
                    cursor.close()
                    conn.close()
                    return {"success": False, "msg": "Not enough stock in Godown"}
                
                # Deduct Stock using RAW SQL and hard-commit 
                cursor.execute("UPDATE godown_products SET master_stock = master_stock - %s WHERE id = %s", (qty_to_pick, data["godown_product_id"]))
                conn.commit()
                cursor.close()
                conn.close()
                
                # Now push into MongoDB Private Products Table
                priv = mongo_db.products.find_one({"user_id": data["user_id"], "id": data["godown_product_id"]})
                if priv:
                    mongo_db.products.update_one({"_id": priv["_id"]}, {"$inc": {"qty": qty_to_pick}, "$set": {"price": float(data.get("price", priv["price"]))}})
                else:
                    priv_id = mongo_db.products.count_documents({}) + 1
                    mongo_db.products.insert_one({
                        "_id": priv_id,
                        "id": data["godown_product_id"], # Link to Godown Product
                        "user_id": data["user_id"],
                        "price": float(data["price"]),
                        "qty": qty_to_pick
                    })
                    
                return {"success": True, "msg": "Picked item to storefront"}
                
            elif action == "view":
                privs = list(mongo_db.products.find({"user_id": data["user_id"]}))
                res = []
                
                # Cross-reference with MySQL to get names
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    for p in privs:
                        cursor.execute("SELECT name FROM godown_products WHERE id = %s", (p["id"],))
                        gp = cursor.fetchone()
                        if gp:
                            res.append({
                                "id": p["_id"],
                                "godown_product_id": p["id"],
                                "sku": f"SKU-{p['id']}",
                                "name": gp["name"],
                                "price": p["price"],
                                "stock": p["qty"]
                            })
                    cursor.close()
                    conn.close()
                return {"success": True, "data": res}
                
        elif module == "cart":
            if action == "add":
                priv = mongo_db.products.find_one({"user_id": data["store_owner_id"], "id": data["godown_product_id"]})
                qty = int(data["qty"])
                if not priv or priv["qty"] < qty:
                    return {"success": False, "msg": "Product not available. Please add from Godown first."}
                
                cart_item = mongo_db.cart.find_one({"user_id": data["store_owner_id"], "user_product_id": priv["_id"]})
                if cart_item:
                    if priv["qty"] < (cart_item["qty"] + qty):
                        return {"success": False, "msg": "Insufficient stock."}
                    mongo_db.cart.update_one({"_id": cart_item["_id"]}, {"$inc": {"qty": qty}})
                else:
                    cart_id = mongo_db.cart.count_documents({}) + 1
                    mongo_db.cart.insert_one({"_id": cart_id, "user_id": data["store_owner_id"], "user_product_id": priv["_id"], "qty": qty})
                return {"success": True, "msg": "Added to Cart!"}

            elif action == "view":
                items = list(mongo_db.cart.find({"user_id": data["user_id"]}))
                res = []
                
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    for item in items:
                        priv = mongo_db.products.find_one({"_id": item["user_product_id"]})
                        cursor.execute("SELECT name FROM godown_products WHERE id = %s", (priv["id"],))
                        gp = cursor.fetchone()
                        
                        res.append({
                            "id": item["_id"],
                            "name": gp["name"] if gp else "Unknown",
                            "price": priv["price"],
                            "qty": item["qty"],
                            "total": priv["price"] * item["qty"]
                        })
                    cursor.close()
                    conn.close()
                return {"success": True, "data": res}

            elif action == "remove":
                mongo_db.cart.delete_one({"_id": data["cart_item_id"], "user_id": data["user_id"]})
                return {"success": True, "msg": "Removed from cart."}
                
            elif action == "checkout":
                items = list(mongo_db.cart.find({"user_id": data["user_id"]}))
                if not items:
                    return {"success": False, "msg": "Cart is empty."}
                    
                for item in items:
                    priv = mongo_db.products.find_one({"_id": item["user_product_id"]})
                    if not priv or priv["qty"] < item["qty"]:
                        return {"success": False, "msg": "Insufficient stock."}
                
                items_list = []
                total = 0
                
                for item in items:
                    priv = mongo_db.products.find_one({"_id": item["user_product_id"]})
                    # Raw direct collection update
                    mongo_db.products.update_one({"_id": priv["_id"]}, {"$inc": {"qty": -item["qty"]}})
                    # Build summary
                    items_list.append({"product_id": priv["_id"], "qty": item["qty"], "price": priv["price"]})
                    total += (item["qty"] * priv["price"])
                    # Remove cart item
                    mongo_db.cart.delete_one({"_id": item["_id"]})
                    
                order_id = mongo_db.orders.count_documents({}) + 1
                mongo_db.orders.insert_one({"_id": order_id, "order_id": order_id, "user_id": data["user_id"], "items_list": json.dumps(items_list), "total": total})
                    
                return {"success": True, "msg": "Order placed successfully! Cart cleared and stock reduced."}
                
    except Exception as e:
        traceback.print_exc()
        return {"success": False, "msg": str(e)}
        
    return {"success": False, "msg": "Invalid action"}
