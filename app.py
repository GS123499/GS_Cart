import os
import uuid
from flask import Flask, render_template, jsonify, request, session


app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-please-change')


# Sample product catalog
PRODUCTS = [
    {'id': 'p1', 'title': 'Wireless Headphones', 'price': 2499, 'desc': 'Comfortable, long battery life', 'category': 'Electronics'},
    {'id': 'p2', 'title': 'Smart Watch', 'price': 3499, 'desc': 'Fitness tracking, notifications', 'category': 'Electronics'},
    {'id': 'p3', 'title': 'Portable Speaker', 'price': 1299, 'desc': 'Rich bass, compact size', 'category': 'Electronics'},
    {'id': 'p4', 'title': 'Mechanical Keyboard', 'price': 3999, 'desc': 'RGB, tactile switches', 'category': 'Peripherals'},
    {'id': 'p5', 'title': 'Gaming Mouse', 'price': 1799, 'desc': 'High DPI, ergonomic', 'category': 'Peripherals'},
    {'id': 'p6', 'title': 'USB-C Charger', 'price': 799, 'desc': 'Fast charging 65W', 'category': 'Accessories'},
]
# Helpers for session cart
def _get_cart():
    return session.get('cart', {})
def _save_cart(cart):
    session['cart'] = cart

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/products')
def api_products():
    q = request.args.get('q', '').strip().lower()
    category = request.args.get('category', '').strip().lower()
    items = PRODUCTS
    if q:
        items = [p for p in items if q in p['title'].lower() or q in p['desc'].lower()]
    if category:
        items = [p for p in items if category == p['category'].lower()]
    return jsonify(items)


@app.route('/api/product/<pid>')
def api_product(pid):
    p = next((x for x in PRODUCTS if x['id'] == pid), None)
    if not p:
        return jsonify({'error': 'not found'}), 404
    return jsonify(p)

@app.route('/api/cart', methods=['GET'])
def api_get_cart():
    cart = _get_cart()
    items = []
    total = 0
    for pid, qty in cart.items():
        p = next((x for x in PRODUCTS if x['id'] == pid), None)
        if not p:
            continue
        line = p['price'] * qty
        total += line
        items.append({'product': p, 'qty': qty, 'line': line})
    return jsonify({'items': items, 'total': total, 'count': sum(cart.values())})

@app.route('/api/cart', methods=['POST'])
def api_add_to_cart():
    data = request.get_json() or {}
    pid = data.get('product_id')
    qty = int(data.get('qty', 1))
    if not pid:
        return jsonify({'error': 'product_id required'}), 400
    p = next((x for x in PRODUCTS if x['id'] == pid), None)
    if not p:
        return jsonify({'error': 'product not found'}), 404
    cart = _get_cart()
    cart[pid] = cart.get(pid, 0) + qty
    _save_cart(cart)
    return api_get_cart()
  
@app.route('/api/cart', methods=['PUT'])
def api_set_cart_qty():
    data = request.get_json() or {}
    pid = data.get('product_id')
    qty = int(data.get('qty', 0))
    if not pid:
        return jsonify({'error': 'product_id required'}), 400
    cart = _get_cart()
    if qty <= 0:
        cart.pop(pid, None)
    else:
        cart[pid] = qty
    _save_cart(cart)
    return api_get_cart()


@app.route('/api/cart/<pid>', methods=['DELETE'])
def api_remove_from_cart(pid):
    cart = _get_cart()
    if pid in cart:
        cart.pop(pid)
        _save_cart(cart)
    return api_get_cart()

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    data = request.get_json() or {}
    name = data.get('name', 'Customer')
    address = data.get('address', '')
    cart = _get_cart()
    if not cart:
        return jsonify({'error': 'cart empty'}), 400
    items = []
    total = 0
    for pid, qty in cart.items():
        p = next((x for x in PRODUCTS if x['id'] == pid), None)
        if not p:
            continue
        line = p['price'] * qty
        total += line
        items.append({'id': pid, 'title': p['title'], 'price': p['price'], 'qty': qty, 'line': line})
    order = {
        'id': uuid.uuid4().hex[:8],
        'customer': name,
        'address': address,
        'items': items,
        'total': total,
    }
    orders = session.get('orders', [])
    orders.append(order)
    session['orders'] = orders
    session['cart'] = {}
    return jsonify({'success': True, 'order': order})


@app.route('/api/orders')
def api_orders():
    return jsonify(session.get('orders', []))


if __name__ == '__main__':
    app.run(debug=True)
