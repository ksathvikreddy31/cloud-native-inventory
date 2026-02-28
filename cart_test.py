import requests

# Set base URL
url = 'http://localhost:5000/api'

# Register
resp = requests.post(f'{url}/auth/register', json={'username':'sathvik_test', 'password':'pw', 'db':'sql'})
print('Register:', resp.json())

# Login
resp = requests.post(f'{url}/auth/login', json={'username':'sathvik_test', 'password':'pw', 'db':'sql'})
user_id = resp.json().get('user_id')
print('Login UserID:', user_id)

# Add Godown
resp = requests.post(f'{url}/godown/add', json={'name':'Item Test', 'description':'Desc', 'master_stock':100})
print('Add Godown:', resp.json())

# View Godown
resp = requests.post(f'{url}/godown/view', json={'db':'sql'})
godown_items = resp.json().get('data', [])
print('Godown Items:', godown_items)

if godown_items:
    g_id = godown_items[-1]['id']

    # Pick
    resp = requests.post(f'{url}/storefront/pick', json={'db':'sql', 'user_id': user_id, 'godown_product_id': g_id, 'qty': 10, 'price': 50})
    print('Pick Item:', resp.json())

    # Add to Cart
    resp = requests.post(f'{url}/cart/add', json={'db':'sql', 'store_owner_id': user_id, 'godown_product_id': g_id, 'qty': 2})
    print('Add to Cart:', resp.json())

    # View Cart
    resp = requests.post(f'{url}/cart/view', json={'db':'sql', 'user_id': user_id})
    print('View Cart:', resp.json())

    # Checkout
    resp = requests.post(f'{url}/cart/checkout', json={'db':'sql', 'user_id': user_id})
    print('Checkout:', resp.json())

    # View Cart After Checkout
    resp = requests.post(f'{url}/cart/view', json={'db':'sql', 'user_id': user_id})
    print('View Cart After Checkout:', resp.json())
