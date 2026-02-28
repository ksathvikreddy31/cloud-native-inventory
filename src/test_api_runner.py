import requests
import time
import sys

def run_tests():
    base = "http://localhost:5000/api"
    print("Testing Backend...")
    db = "sql"
    
    print("Register")
    res = requests.post(f"{base}/auth/register", json={"db": db, "username": "cartuser", "password": "abc"}).json()
    if not res.get("success") and res.get("msg") != "User already exists":
        print("Register failed:", res)
        sys.exit(1)
        
    print("Login")
    res = requests.post(f"{base}/auth/login", json={"db": db, "username": "cartuser", "password": "abc"}).json()
    if not res.get("success"):
        print("Login failed:", res)
        sys.exit(1)
    user_id = res["user_id"]

    print("Add to Godown")
    res = requests.post(f"{base}/godown/add", json={"db": db, "sku": "CART-123", "name": "Cart Item", "description": "Cart", "master_stock": 100}).json()
    if not res.get("success") and "UNIQUE constraint failed" not in res.get("msg", ""):
        print("Godown Add failed:", res)
    
    # Needs to get gp_id properly in case it already existed
    res = requests.post(f"{base}/godown/view", json={"db": db}).json()
    gp_id = None
    for item in res["data"]:
        if item["sku"] == "CART-123":
            gp_id = item["id"]
            break

    print("Pick item to storefront")
    res = requests.post(f"{base}/storefront/pick", json={"db": db, "user_id": user_id, "godown_product_id": gp_id, "qty": 10, "price": 5.99}).json()
    if not res.get("success"):
        print("Pick failed:", res)
        sys.exit(1)

    print("Add to cart")
    res = requests.post(f"{base}/cart/add", json={"db": db, "store_owner_id": user_id, "godown_product_id": gp_id, "qty": 2}).json()
    if not res.get("success"):
        print("Add to Cart failed:", res)
        sys.exit(1)
        
    print("Add to cart again")
    res = requests.post(f"{base}/cart/add", json={"db": db, "store_owner_id": user_id, "godown_product_id": gp_id, "qty": 2}).json()
    if not res.get("success"):
        print("Add to Cart again failed:", res)

    print("View cart")
    res = requests.post(f"{base}/cart/view", json={"db": db, "user_id": user_id}).json()
    if not res.get("success") or len(res["data"]) == 0:
        print("View cart failed:", res)
        sys.exit(1)
        
    print("Checkout Cart")
    res = requests.post(f"{base}/cart/checkout", json={"db": db, "user_id": user_id}).json()
    if not res.get("success"):
        print("Checkout Cart failed:", res)
        sys.exit(1)

    print("All cart tests passed successfully.")

if __name__ == "__main__":
    run_tests()
