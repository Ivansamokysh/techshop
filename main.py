from flask import Flask, render_template, request, redirect, url_for
from database import get_db_connection

app = Flask(__name__, static_url_path="/src", static_folder="src")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/catalog", methods=["GET"])
def catalog():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template("catalog.html", catalog=products)

@app.route("/add_item", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        category = request.form.get("category")

        image_url = ""
        if category == "Смартфон":
            image_url = "/src/smartphone.png"
        elif category == "Ноутбук":
            image_url = "/src/laptop.png"
        elif category == "Холодильник":
            image_url = "/src/fridge.png"

        try:
            price = float(request.form.get("price"))
        except (ValueError, TypeError):
            return "Неправильний формат ціни", 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (title, description, price, image_url, category)
            VALUES (?, ?, ?, ?, ?)
        """, (title, description, price, image_url, category))
        conn.commit()
        conn.close()

        return redirect(url_for("catalog"))

    return render_template("add_item.html")

@app.route("/sort_by_category", methods=["GET"])
def sort_by_category():
    category = request.args.get("category")
    conn = get_db_connection()
    cursor = conn.cursor()
    if category:
        cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
    else:
        cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template("catalog.html", catalog=products)

@app.route("/sort_by_price", methods=["GET"])
def sort_by_price():
    order = request.args.get("order", "ASC").upper()
    if order not in ("ASC", "DESC"):
        order = "ASC"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM products ORDER BY price {order}")
    products = cursor.fetchall()
    conn.close()
    return render_template("catalog.html", catalog=products)

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
