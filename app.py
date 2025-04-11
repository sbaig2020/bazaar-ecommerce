from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import csv
import json
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'bazaar_secret_key'  # For session management

# Configuration
DATA_DIR = Path(__file__).parent / "data"
PRODUCTS_FILE = DATA_DIR / "bazaar_products.csv"

# Helper functions
def load_products():
    """Load product data from CSV file"""
    products = []
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert string representations back to lists
                row['images'] = row['images'].split('|') if row['images'] else []
                row['sizes'] = row['sizes'].split('|') if row['sizes'] else []
                # Convert price strings to float
                row['original_price'] = float(row['original_price']) if row['original_price'] else 0
                row['bazaar_price'] = float(row['bazaar_price']) if row['bazaar_price'] else 0
                products.append(row)
    return products

def get_product_by_id(product_id):
    """Get a specific product by ID"""
    products = load_products()
    for product in products:
        if product['id'] == product_id:
            return product
    return None

def get_products_by_category(category):
    """Get products filtered by category"""
    products = load_products()
    return [p for p in products if p['category'] == category]

# Initialize shopping cart
def init_cart():
    """Initialize an empty shopping cart in the session if it doesn't exist"""
    if 'cart' not in session:
        session['cart'] = []

# Routes
@app.route('/')
def home():
    """Homepage route"""
    products = load_products()
    # Get featured products (first 6)
    featured_products = products[:6] if products else []
    # Group products by category
    categories = {}
    for product in products:
        category = product['category']
        if category not in categories:
            categories[category] = []
        if len(categories[category]) < 4:  # Limit to 4 products per category
            categories[category].append(product)
    
    return render_template('index.html', 
                          featured_products=featured_products,
                          categories=categories)

@app.route('/products')
def products():
    """All products page"""
    category = request.args.get('category', None)
    if category:
        product_list = get_products_by_category(category)
    else:
        product_list = load_products()
    
    # Pagination
    page = int(request.args.get('page', 1))
    per_page = 12
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_products = product_list[start_idx:end_idx]
    total_pages = (len(product_list) + per_page - 1) // per_page
    
    return render_template('products.html', 
                          products=paginated_products,
                          category=category,
                          page=page,
                          total_pages=total_pages)

@app.route('/product/<product_id>')
def product_detail(product_id):
    """Product detail page"""
    product = get_product_by_id(product_id)
    if not product:
        return redirect(url_for('products'))
    
    # Get related products (same category, up to 4)
    related = get_products_by_category(product['category'])
    related = [p for p in related if p['id'] != product_id][:4]
    
    return render_template('product_detail.html', 
                          product=product,
                          related=related)

@app.route('/cart')
def cart():
    """Shopping cart page"""
    init_cart()
    cart_items = []
    cart_total = 0
    
    # Get full product details for cart items
    for item in session['cart']:
        product = get_product_by_id(item['product_id'])
        if product:
            cart_item = {
                'product': product,
                'quantity': item['quantity'],
                'size': item['size'],
                'subtotal': float(product['bazaar_price']) * item['quantity']
            }
            cart_items.append(cart_item)
            cart_total += cart_item['subtotal']
    
    return render_template('cart.html', 
                          cart_items=cart_items,
                          cart_total=cart_total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    init_cart()
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    size = request.form.get('size', '')
    
    # Check if product exists
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'})
    
    # Check if item already in cart, update quantity if so
    for item in session['cart']:
        if item['product_id'] == product_id and item['size'] == size:
            item['quantity'] += quantity
            session.modified = True
            return jsonify({'success': True, 'message': 'Updated quantity in cart'})
    
    # Otherwise add new item to cart
    session['cart'].append({
        'product_id': product_id,
        'quantity': quantity,
        'size': size
    })
    session.modified = True
    
    return jsonify({'success': True, 'message': 'Added to cart'})

@app.route('/update_cart', methods=['POST'])
def update_cart():
    """Update cart item quantities"""
    init_cart()
    item_index = int(request.form.get('index'))
    quantity = int(request.form.get('quantity'))
    
    if 0 <= item_index < len(session['cart']):
        if quantity > 0:
            session['cart'][item_index]['quantity'] = quantity
        else:
            session['cart'].pop(item_index)
        session.modified = True
        
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    """Checkout page"""
    init_cart()
    cart_items = []
    cart_total = 0
    
    # Get full product details for cart items
    for item in session['cart']:
        product = get_product_by_id(item['product_id'])
        if product:
            cart_item = {
                'product': product,
                'quantity': item['quantity'],
                'size': item['size'],
                'subtotal': float(product['bazaar_price']) * item['quantity']
            }
            cart_items.append(cart_item)
            cart_total += cart_item['subtotal']
    
    return render_template('checkout.html', 
                          cart_items=cart_items,
                          cart_total=cart_total)

@app.route('/search')
def search():
    """Search products"""
    query = request.args.get('q', '').lower()
    products = load_products()
    
    # Filter products based on search query
    if query:
        results = [p for p in products if 
                  query in p['title'].lower() or 
                  query in p['brand'].lower() or 
                  query in p['description'].lower()]
    else:
        results = []
    
    return render_template('search_results.html', 
                          results=results, 
                          query=query)

@app.route('/api/products')
def api_products():
    """API endpoint for products"""
    products = load_products()
    return jsonify(products)

@app.route('/api/product/<product_id>')
def api_product(product_id):
    """API endpoint for a specific product"""
    product = get_product_by_id(product_id)
    if product:
        return jsonify(product)
    return jsonify({'error': 'Product not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)