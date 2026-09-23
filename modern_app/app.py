"""
Modernized Inventory & Order REST API
Transformed by IBM Bob 2.0 Subagent (Code Modernizer Engine)
Features:
- RESTful Flask Architecture
- Parameterized safe SQLite database queries
- Structured JSON error handling and HTTP status codes
"""

from flask import Flask, request, jsonify
from models import DatabaseManager

app = Flask(__name__)
db = DatabaseManager("modern_store.db")

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "engine": "IBM Bob 2.0 Modernized"}), 200

@app.route("/api/inventory", methods=["POST"])
def add_item():
    data = request.get_json() or {}
    name = data.get("name")
    quantity = data.get("quantity")
    price = data.get("unit_price")

    if not name or quantity is None or price is None:
        return jsonify({"error": "Missing required fields"}), 400

    item_id = db.add_item(name, int(quantity), float(price))
    return jsonify({"message": "Item created successfully", "id": item_id}), 201

@app.route("/api/inventory/search", methods=["GET"])
def search_inventory():
    query = request.args.get("q", "")
    results = db.search_items(query)
    return jsonify({"count": len(results), "items": results}), 200

@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json() or {}
    customer = data.get("customer_name")
    item_id = data.get("item_id")
    qty = data.get("qty")

    if not customer or not item_id or not qty:
        return jsonify({"error": "Invalid order payload"}), 400

    success, message = db.process_order(customer, int(item_id), int(qty))
    if not success:
        return jsonify({"error": message}), 400

    return jsonify({"message": message}), 201

if __name__ == "__main__":
    db.init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
