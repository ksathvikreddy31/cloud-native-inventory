import unittest
import requests
import uuid

# Configuration
BASE_URL = "http://localhost:5000/api"

class TestInventoryAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a unique username for each test run to prevent 'User already exists' conflicts
        cls.username = f"testuser_{uuid.uuid4().hex[:8]}"
        cls.password = "securepassword"
        cls.user_id = None
        cls.godown_item_id = None

    def test_01_register_user(self):
        """Test user registration"""
        payload = {
            "username": self.username,
            "password": self.password,
            "db": "sql"
        }
        res = requests.post(f"{BASE_URL}/auth/register", json=payload)
        data = res.json()
        self.assertTrue(data.get("success"), f"Registration failed: {data.get('msg')}")
        self.assertIn("user_id", data)
        TestInventoryAPI.user_id = data["user_id"]
        print(f"Registered user: {self.username} with ID {TestInventoryAPI.user_id}")

    def test_02_login_user(self):
        """Test user login"""
        payload = {
            "username": self.username,
            "password": self.password,
            "db": "sql"
        }
        res = requests.post(f"{BASE_URL}/auth/login", json=payload)
        data = res.json()
        self.assertTrue(data.get("success"), "Login failed")
        self.assertEqual(data.get("user_id"), self.user_id)

    def test_03_admin_add_to_godown(self):
        """Test admin adding an item to the global godown"""
        payload = {
            "name": f"Test Gadget {uuid.uuid4().hex[:4]}",
            "description": "A wonderful test gadget",
            "master_stock": 500,
            "db": "sql" # Admin always uses SQL
        }
        res = requests.post(f"{BASE_URL}/godown/add", json=payload)
        self.assertTrue(res.json().get("success"), "Failed to add to Godown")

    def test_04_user_view_godown(self):
        """Test user viewing godown and capturing an item ID to pick"""
        res = requests.post(f"{BASE_URL}/godown/view", json={"db": "sql"})
        data = res.json()
        self.assertTrue(data.get("success"), "Failed to view Godown")
        items = data.get("data", [])
        self.assertGreater(len(items), 0, "No items found in Godown")
        
        # Save the last item's ID for the next tests
        TestInventoryAPI.godown_item_id = items[-1]["id"]
        print(f"Captured Godown Item ID: {TestInventoryAPI.godown_item_id}")

    def test_05_user_pick_item(self):
        """Test user picking an item from the godown to their private storefront"""
        payload = {
            "user_id": self.user_id,
            "godown_product_id": self.godown_item_id,
            "qty": 50,
            "price": 99.99,
            "db": "sql"
        }
        res = requests.post(f"{BASE_URL}/storefront/pick", json=payload)
        self.assertTrue(res.json().get("success"), "Failed to pick item to storefront")

    def test_06_user_add_to_cart(self):
        """Test user adding a private item to their shopping cart"""
        payload = {
            "store_owner_id": self.user_id,
            "godown_product_id": self.godown_item_id,
            "qty": 2,
            "db": "sql"
        }
        res = requests.post(f"{BASE_URL}/cart/add", json=payload)
        self.assertTrue(res.json().get("success"), "Failed to add item to cart")

    def test_07_user_view_cart(self):
        """Test user viewing their isolated cart"""
        payload = {
            "user_id": self.user_id,
            "db": "sql"
        }
        res = requests.post(f"{BASE_URL}/cart/view", json=payload)
        data = res.json()
        self.assertTrue(data.get("success"), "Failed to view cart")
        items = data.get("data", [])
        self.assertGreater(len(items), 0, "Cart is unexpectedly empty")
        
        # Verify calculation accuracy mapping
        self.assertEqual(items[0]["qty"], 2)

    def test_08_user_checkout_cart(self):
        """Test user checking out, reducing stock, and clearing cart"""
        payload = {
            "user_id": self.user_id,
            "db": "sql"
        }
        res = requests.post(f"{BASE_URL}/cart/checkout", json=payload)
        self.assertTrue(res.json().get("success"), "Checkout transaction failed")

    def test_09_verify_cart_cleared(self):
        """Test that the cart is completely empty after a successful checkout"""
        payload = {
            "user_id": self.user_id,
            "db": "sql"
        }
        res = requests.post(f"{BASE_URL}/cart/view", json=payload)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(len(data.get("data", [])), 0, "Cart was not cleared after checkout!")

if __name__ == "__main__":
    print("Running Integration Tests against Live Backend...")
    unittest.main()
