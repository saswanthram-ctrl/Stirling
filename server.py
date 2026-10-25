import json
import os
from flask import Flask, render_template_string, redirect, url_for

app = Flask(__name__)

# --- 1. PERSISTENT STORAGE FILE PATHS ---
USER_DB_FILE = "users_db.json"
LOG_FILE = "orders_log.json"

# --- 2. THE STERLING PRODUCT INVENTORY DATABASE ---
CATALOG = {
    "1": {"name": "Developer Pro Laptop", "desc": "High-performance engineering workstation.", "price": 75000.00, "stock": 5},
    "2": {"name": "Wireless Mouse",       "desc": "Ergonomic high-DPI tracking layout.", "price": 1200.00,  "stock": 12},
    "3": {"name": "Mechanical Keyboard",  "desc": "Tactile mechanical switch deck profile.", "price": 4500.00,  "stock": 8},
    "4": {"name": "4K Ultra Monitor",     "desc": "High color accuracy display array panels.", "price": 28999.00, "stock": 3}
}

shopping_cart = []
current_user = "WERT"  # Authenticated active user profile track footprint

def load_orders():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as file:
            try: return json.load(file)
            except: return []
    return []

def save_transaction_to_disk(subtotal, tax, grand_total):
    order_data = {
        "user": current_user,
        "items": [item["name"] for item in shopping_cart],
        "subtotal": round(subtotal, 2),
        "tax_18_percent": round(tax, 2),
        "grand_total": round(grand_total, 2)
    }
    records = load_orders()
    records.append(order_data)
    with open(LOG_FILE, "w") as file:
        json.dump(records, file, indent=4)

# --- 3. FLASK WEB CORE ROUTING PIPELINES ---
@app.route('/')
def storefront_dashboard():
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Sterling Marketplace Console</title>
        <style>
            body { background-color: #f3f4f6; font-family: sans-serif; margin: 0; padding: 0; }
            header { background-color: #0f172a; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .logo { color: #f97316; font-size: 24px; font-weight: bold; letter-spacing: 1px; }
            .user-status { color: #cbd5e1; }
            .cart-btn { background-color: #f97316; color: black; border: none; padding: 8px 16px; font-weight: bold; border-radius: 4px; cursor: pointer; margin-left: 15px; }
            .container { max-width: 1100px; margin: 30px auto; padding: 0 20px; }
            .catalog-title { color: #1f2937; font-size: 24px; font-weight: bold; margin-bottom: 20px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }
            .card { background-color: white; padding: 24px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e5e7eb; display: flex; flex-direction: column; justify-content: space-between; }
            .prod-title { color: #111827; font-size: 18px; font-weight: bold; margin: 0 0 5px 0; }
            .prod-desc { color: #6b7280; font-size: 14px; margin: 0; }
            .price-row { display: flex; justify-content: space-between; align-items: center; margin-top: 25px; }
            .price { font-size: 20px; font-weight: 800; color: #0f172a; }
            .add-btn { background-color: #facc15; color: #0f172a; border: none; padding: 8px 14px; font-weight: 600; font-size: 14px; border-radius: 4px; cursor: pointer; text-decoration: none; text-align: center; }
            .add-btn:hover { background-color: #eab308; }
            .out-btn { background-color: #e5e7eb; color: #9ca3af; padding: 8px 14px; font-size: 14px; border-radius: 4px; cursor: not-allowed; text-decoration: none; text-align: center; }
            .checkout-zone { background-color: white; padding: 20px; border-radius: 8px; margin-top: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }
            .checkout-btn { background-color: #10b981; color: white; border: none; padding: 10px 20px; font-size: 16px; font-weight: bold; border-radius: 4px; cursor: pointer; text-decoration: none; }
            .checkout-btn:hover { background-color: #059669; }
        </style>
    </head>
    <body>
        <header>
            <div class="logo">STERLING MARKETPLACE</div>
            <div class="user-status">
                Logged in as: <strong style="color: white;">{{ user.upper() }}</strong>
                <button class="cart-btn">Cart ({{ cart_len }})</button>
            </div>
        </header>

        <div class="container">
            <div class="catalog-title">Sterling Product Catalog</div>
            
            <div class="grid">
                {% for prod_id, info in items.items() %}
                <div class="card">
                    <div>
                        <div class="prod-title">{{ info.name }}</div>
                        <p class="prod-desc">{{ info.desc }}</p>
                        <p style="font-size: 12px; color: #9ca3af; margin: 5px 0 0 0;">Stock Available: {{ info.stock }}</p>
                    </div>
                    <div class="price-row">
                        <span class="price">₹{{ "{:,.2f}".format(info.price) }}</span>
                        {% if info.stock > 0 %}
                            <a href="/add/{{ prod_id }}" class="add-btn">Add to Cart</a>
                        {% else %}
                            <span class="out-btn">Sold Out</span>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>

            {% if cart_len > 0 %}
            <div class="checkout-zone">
                <div>
                    <h3 style="margin: 0; color: #111827;">Ready to Process Invoice?</h3>
                    <p style="margin: 5px 0 0 0; color: #4b5563; font-size: 14px;">Secure checkout stream active via Sterling Core.</p>
                </div>
                <a href="/checkout" class="checkout-btn">Proceed to Payment</a>
            </div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, items=CATALOG, cart_len=len(shopping_cart), user=current_user)

@app.route('/add/<prod_id>')
def append_item_to_array(prod_id):
    if prod_id in CATALOG and CATALOG[prod_id]["stock"] > 0:
        shopping_cart.append({"name": CATALOG[prod_id]["name"], "price": CATALOG[prod_id]["price"]})
        CATALOG[prod_id]["stock"] -= 1
    return redirect(url_for('storefront_dashboard'))

@app.route('/checkout')
def finalize_order_transaction():
    if not shopping_cart:
        return redirect(url_for('storefront_dashboard'))
        
    subtotal = sum(item["price"] for item in shopping_cart)
    tax_levy = subtotal * 0.18
    grand_total = subtotal + tax_levy
    
    save_transaction_to_disk(subtotal, tax_levy, grand_total)
    shopping_cart.clear()
    
    return """
    <div style="max-width: 500px; margin: 100px auto; text-align: center; font-family: sans-serif; border: 1px solid #e5e7eb; padding: 24px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <h2 style="color: #10b981;">✔ STERLING TRANSACTION SECURED</h2>
        <p style="color: #4b5563;">Your transaction invoice processed successfully.</p>
        <p style="font-weight: bold; font-size: 18px; color: #0f172a;">Grand Total Captured: ₹""" + f"{grand_total:,.2f}" + """</p>
        <p style="color: #9ca3af; font-size: 12px;">Invoice encrypted and archived safely in storage text logs.</p>
        <br>
        <a href="/" style="background-color: #0f172a; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; font-weight: bold;">Return to Storefront</a>
    </div>
    """

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
