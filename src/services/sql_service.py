import json
from database.mysql import get_db_connection

def execute_action(module, action, data):
    conn = get_db_connection()
    if not conn:
        return {"success": False, "msg": "Failed to connect to MySQL database."}
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        if module == "auth":
            if action == "register":
                cursor.execute("SELECT id FROM users WHERE username = %s", (data["username"],))
                if cursor.fetchone():
                    return {"success": False, "msg": "User already exists"}
                cursor.execute("INSERT INTO users (username, password, role, db_type) VALUES (%s, %s, %s, %s)", 
                               (data["username"], data["password"], data.get("role", "user"), data.get("db", "sql")))
                conn.commit()
                return {"success": True, "msg": "Registered successfully", "user_id": cursor.lastrowid, "role": data.get("role", "user")}
            
            elif action == "login":
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (data["username"], data["password"]))
                user = cursor.fetchone()
                if user:
                    if user["db_type"] != data.get("db", "sql"):
                        cursor.execute("UPDATE users SET db_type = %s WHERE id = %s", (data.get("db", "sql"), user["id"]))
                        conn.commit()
                    return {"success": True, "msg": "Login successful", "user_id": user["id"], "role": user["role"]}
                return {"success": False, "msg": "Invalid credentials"}
        
        elif module == "godown":
            if action == "add":
                cursor.execute("INSERT INTO godown_products (name, description, category, master_stock) VALUES (%s, %s, %s, %s)", 
                               (data["name"], data["description"], data.get("category", "Uncategorized"), data["master_stock"]))
                conn.commit()
                return {"success": True, "msg": "Product added to godown"}
                
            elif action == "view":
                cursor.execute("SELECT id, name, description, category, master_stock FROM godown_products")
                prods = cursor.fetchall()
                # Ensure backward compatibility with UI sku expectation
                for p in prods:
                    p["sku"] = f"SKU-{p['id']}"
                return {"success": True, "data": prods}
                
            elif action == "update":
                cursor.execute("UPDATE godown_products SET master_stock = %s WHERE id = %s", (data["master_stock"], data["id"]))
                conn.commit()
                return {"success": True}
        
        elif module == "storefront":
            if action == "pick":
                cursor.execute("SELECT master_stock FROM godown_products WHERE id = %s", (data["godown_product_id"],))
                godown_prod = cursor.fetchone()
                qty_to_pick = int(data["qty"])
                
                if not godown_prod or godown_prod["master_stock"] < qty_to_pick:
                    return {"success": False, "msg": "Not enough stock in Godown"}
                
                # Logic per requirements: reduce Godown stock
                cursor.execute("UPDATE godown_products SET master_stock = master_stock - %s WHERE id = %s", (qty_to_pick, data["godown_product_id"]))
                
                # User Private Products 
                cursor.execute("SELECT id, qty, price FROM user_products WHERE user_id = %s AND godown_product_id = %s", (data["user_id"], data["godown_product_id"]))
                priv = cursor.fetchone()
                
                if priv:
                    cursor.execute("UPDATE user_products SET qty = qty + %s, price = %s WHERE id = %s", (qty_to_pick, float(data.get("price", priv["price"])), priv["id"]))
                else:
                    cursor.execute("INSERT INTO user_products (user_id, godown_product_id, price, qty) VALUES (%s, %s, %s, %s)", 
                                   (data["user_id"], data["godown_product_id"], float(data["price"]), qty_to_pick))
                
                conn.commit()
                return {"success": True, "msg": "Picked item to storefront"}
                
            elif action == "view":
                cursor.execute("""
                    SELECT up.id, up.godown_product_id, gp.name, up.price, up.qty as stock 
                    FROM user_products up
                    JOIN godown_products gp ON up.godown_product_id = gp.id
                    WHERE up.user_id = %s
                """, (data["user_id"],))
                res = cursor.fetchall()
                for p in res:
                    p["sku"] = f"SKU-{p['godown_product_id']}"
                    if "price" in p and p["price"] is not None:
                        p["price"] = float(p["price"])
                return {"success": True, "data": res}
        
        elif module == "cart":
            if action == "add":
                cursor.execute("SELECT id, qty FROM user_products WHERE user_id = %s AND godown_product_id = %s", (data["store_owner_id"], data["godown_product_id"]))
                priv = cursor.fetchone()
                qty = int(data["qty"])
                
                if not priv or priv["qty"] < qty:
                    return {"success": False, "msg": "Product not available in your store. Please add from Godown."}
                
                cursor.execute("SELECT id, qty FROM cart WHERE user_id = %s AND user_product_id = %s", (data["store_owner_id"], priv["id"]))
                cart_item = cursor.fetchone()
                
                if cart_item:
                    if priv["qty"] < (cart_item["qty"] + qty):
                        return {"success": False, "msg": "Insufficient stock in your store to add more to cart."}
                    cursor.execute("UPDATE cart SET qty = qty + %s WHERE id = %s", (qty, cart_item["id"]))
                else:
                    cursor.execute("INSERT INTO cart (user_id, user_product_id, qty) VALUES (%s, %s, %s)", (data["store_owner_id"], priv["id"], qty))
                
                conn.commit()
                return {"success": True, "msg": "Added to Cart!"}

            elif action == "view":
                cursor.execute("""
                    SELECT c.id, gp.name, up.price, c.qty, (up.price * c.qty) as total
                    FROM cart c
                    JOIN user_products up ON c.user_product_id = up.id
                    JOIN godown_products gp ON up.godown_product_id = gp.id
                    WHERE c.user_id = %s
                """, (data["user_id"],))
                res = cursor.fetchall()
                for p in res:
                    if "price" in p and p["price"] is not None:
                        p["price"] = float(p["price"])
                    if "total" in p and p["total"] is not None:
                        p["total"] = float(p["total"])
                return {"success": True, "data": res}

            elif action == "remove":
                cursor.execute("DELETE FROM cart WHERE id = %s AND user_id = %s", (data["cart_item_id"], data["user_id"]))
                conn.commit()
                return {"success": True, "msg": "Removed from cart."}
                
            elif action == "checkout":
                cursor.execute("""
                    SELECT c.id as cart_id, c.qty, c.user_product_id, up.qty as stock, up.price
                    FROM cart c
                    JOIN user_products up ON c.user_product_id = up.id
                    WHERE c.user_id = %s
                """, (data["user_id"],))
                items = cursor.fetchall()
                if not items:
                    return {"success": False, "msg": "Cart is empty."}
                    
                for item in items:
                    if item["stock"] < item["qty"]:
                        return {"success": False, "msg": "Insufficient stock."}
                
                items_list = []
                total = 0
                
                for item in items:
                    # Update personal user_products stock directly (no ORM tracking logic)
                    cursor.execute("UPDATE user_products SET qty = qty - %s WHERE id = %s", (item["qty"], item["user_product_id"]))
                    items_list.append({"product_id": item["user_product_id"], "qty": item["qty"], "price": float(item["price"])})
                    total += (item["qty"] * item["price"])
                    cursor.execute("DELETE FROM cart WHERE id = %s", (item["cart_id"],))
                    
                cursor.execute("INSERT INTO orders (user_id, items_list, total) VALUES (%s, %s, %s)", (data["user_id"], json.dumps(items_list), total))
                conn.commit()
                return {"success": True, "msg": "Order placed successfully! Cart cleared and stock reduced."}
    
    except Exception as e:
        conn.rollback()
        return {"success": False, "msg": str(e)}
    finally:
        cursor.close()
        conn.close()
    
    return {"success": False, "msg": "Invalid action"}
