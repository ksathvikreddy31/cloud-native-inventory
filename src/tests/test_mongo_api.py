import unittest
import requests
import uuid

# Configuration
BASE_URL = "http://localhost:5000/api"

class TestInventoryMongoAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a unique username for each test run to prevent 'User already exists' conflicts
        cls.username = f"mongo_user_{uuid.uuid4().hex[:8]}"
        cls.password = "securepassword"
        cls.user_id = None
        cls.godown_item_id = None

    def test_01_register_mongo_user(self):
        """Test user registration for a Mongo-based storefront user"""
        payload = {
            "username": self.username,
            "password": self.password,
            "db": "mongo"
        }
        res = requests.post(f"{BASE_URL}/auth/register", json=payload)
        data = res.json()
        self.assertTrue(data.get("success"), f"Registration failed: {data.get('msg')}")
        self.assertIn("user_id", data)
        TestInventoryMongoAPI.user_id = data["user_id"]
        print(f"Registered Mongo user: {self.username} with ID {TestInventoryMongoAPI.user_id}")

    def test_02_login_mongo_user(self):
        """Test user login"""
        payload = {
            "username": self.username,
            "password": self.password,
            "db": "mongo"
        }
        res = requests.post(f"{BASE_URL}/auth/login", json=payload)
        data = res.json()
        self.assertTrue(data.get("success"), "Login failed")
        self.assertEqual(data.get("user_id"), self.user_id)

    def test_03_admin_add_to_godown(self):
        """Test admin adding an item to the global godown (this still goes to MySQL physically)"""
        payload = {
            "name": f"Mongo Test Item {uuid.uuid4().hex[:4]}",
            "description": "An item to be picked via MongoDB",
            "master_stock": 300,
            "db": "mongo" # Sent from Mongo client, but backend routes godown modules to SQL
        }
        res = requests.post(f"{BASE_URL}/godown/add", json=payload)
        self.assertTrue(res.json().get("success"), "Failed to add to Godown")

    def test_04_user_view_godown(self):
        """Test user viewing godown to get latest Item ID"""
        res = requests.post(f"{BASE_URL}/godown/view", json={"db": "mongo"})
        data = res.json()
        self.assertTrue(data.get("success"), "Failed to view Godown")
        items = data.get("data", [])
        self.assertGreater(len(items), 0, "No items found in Godown")
        
        # Save the last item's ID for the next tests
        TestInventoryMongoAPI.godown_item_id = items[-1]["id"]
        print(f"Captured Godown Item ID for Mongo: {TestInventoryMongoAPI.godown_item_id}")

    def test_05_mongo_user_pick_item(self):
        """Test user picking an item from the godown to their Mongo private collection"""
        payload = {
            "user_id": self.user_id,
            "godown_product_id": self.godown_item_id,
            "qty": 30,
            "price": 120.00,
            "db": "mongo"
        }
        res = requests.post(f"{BASE_URL}/storefront/pick", json=payload)
        self.assertTrue(res.json().get("success"), "Failed to pick item to MongoDB storefront")

    def test_06_mongo_user_add_to_cart(self):
        """Test MongoDB user adding an item to their isolated Mongo cart collection"""
        payload = {
            "store_owner_id": self.user_id,
            "godown_product_id": self.godown_item_id,
            "qty": 5,
            "db": "mongo"
        }
        res = requests.post(f"{BASE_URL}/cart/add", json=payload)
        self.assertTrue(res.json().get("success"), "Failed to add item to Mongo cart")

    def test_07_mongo_user_view_cart(self):
        """Test viewing the MongoDB cart and validating metrics"""
        payload = {
            "user_id": self.user_id,
            "db": "mongo"
        }
        res = requests.post(f"{BASE_URL}/cart/view", json=payload)
        data = res.json()
        self.assertTrue(data.get("success"), "Failed to view cart")
        items = data.get("data", [])
        self.assertGreater(len(items), 0, "Cart is unexpectedly empty")
        # Validate quantity matches
        self.assertEqual(items[0]["qty"], 5)

    def test_08_mongo_user_checkout_cart(self):
        """Test user checking out via MongoDB, reducing NoSQL stock, logging Order, and clearing Cart collection"""
        payload = {
            "user_id": self.user_id,
            "db": "mongo"
        }
        res = requests.post(f"{BASE_URL}/cart/checkout", json=payload)
        self.assertTrue(res.json().get("success"), "Mongo Checkout transaction failed")

    def test_09_verify_mongo_cart_cleared(self):
        """Test that the MongoDB Cart document was properly deleted after checkout"""
        payload = {
            "user_id": self.user_id,
            "db": "mongo"
        }
        res = requests.post(f"{BASE_URL}/cart/view", json=payload)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(len(data.get("data", [])), 0, "Mongo Cart was not cleared after checkout!")

if __name__ == "__main__":
    print("Running Integration Tests against MongoDB Backend...")
    unittest.main()
