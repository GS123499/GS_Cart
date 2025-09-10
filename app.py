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
