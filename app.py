from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4

app = Flask(__name__)
app.secret_key = "local-demo-only-change-me"

PRODUCTS = [
    {"id": 1, "name": "Python Programming Book", "category": "Books", "price": 24.99},
    {"id": 2, "name": "Wireless Mouse", "category": "Electronics", "price": 18.50},
    {"id": 3, "name": "Mechanical Keyboard", "category": "Electronics", "price": 59.00},
    {"id": 4, "name": "Water Bottle", "category": "Accessories", "price": 12.00},
]
USERS = {}
ORDERS = {}

def current_user():
    email = session.get("email")
    return USERS.get(email) if email else None

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            return redirect(url_for("signin"))
        return view(*args, **kwargs)
    return wrapped

def cart_items():
    cart = session.get("cart", {})
    items = []
    for product_id, quantity in cart.items():
        product = next((p for p in PRODUCTS if str(p["id"]) == str(product_id)), None)
        if product:
            item = dict(product)
            item["quantity"] = int(quantity)
            item["subtotal"] = item["price"] * item["quantity"]
            items.append(item)
    return items

@app.context_processor
def inject_globals():
    return {"current_user": current_user(), "cart_count": sum(int(q) for q in session.get("cart", {}).values())}

@app.route("/")
def home():
    return redirect(url_for("products"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Enter a name, valid email, and password with at least 6 characters.", "error")
            return render_template("signup.html")
        if email in USERS:
            flash("An account with this email already exists.", "error")
            return render_template("signup.html")
        USERS[email] = {"name": name, "password_hash": generate_password_hash(password)}
        flash("Account created successfully. Please sign in.", "success")
        return redirect(url_for("signin"))
    return render_template("signup.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = USERS.get(email)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("signin.html")
        session.clear()
        session["email"] = email
        session["cart"] = {}
        return redirect(url_for("products"))
    return render_template("signin.html")

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("signin"))

@app.route("/products")
@login_required
def products():
    query = request.args.get("q", "").strip().lower()
    filtered = [p for p in PRODUCTS if query in p["name"].lower() or query in p["category"].lower()]
    return render_template("products.html", products=filtered, query=query)

@app.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    if not any(p["id"] == product_id for p in PRODUCTS):
        return "Product not found", 404
    cart = session.get("cart", {})
    key = str(product_id)
    cart[key] = int(cart.get(key, 0)) + 1
    session["cart"] = cart
    flash("Product added to cart.", "success")
    return redirect(url_for("products", q=request.form.get("q", "")))

@app.route("/cart")
@login_required
def cart():
    items = cart_items()
    total = sum(item["subtotal"] for item in items)
    return render_template("cart.html", items=items, total=total)

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items = cart_items()
    if not items:
        flash("Your cart is empty.", "error")
        return redirect(url_for("cart"))
    total = sum(item["subtotal"] for item in items)
    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "").strip()
        postal_code = request.form.get("postal_code", "").strip()
        if not all([name, address, city, postal_code]):
            flash("Please complete all shipping fields.", "error")
            return render_template("checkout.html", items=items, total=total)
        order_id = uuid4().hex[:8].upper()
        ORDERS[order_id] = {"id": order_id, "name": name, "items": items, "total": total}
        session["cart"] = {}
        return redirect(url_for("confirmation", order_id=order_id))
    return render_template("checkout.html", items=items, total=total)

@app.route("/confirmation/<order_id>")
@login_required
def confirmation(order_id):
    order = ORDERS.get(order_id)
    if not order:
        return "Order not found", 404
    return render_template("confirmation.html", order=order)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
