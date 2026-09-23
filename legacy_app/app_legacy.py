#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LEGACY SYSTEM: Inventory & Billing Dispatcher v1.2 (Circa 2012)
Issues:
- Deprecated procedural architecture
- High vulnerability to SQL Injection (Raw string formatting)
- Hardcoded database connections without connection pooling
- No automated unit tests or input schema validation
- Python 2 string handling & outdated print syntax
"""

import sqlite3
import time

DB_PATH = "legacy_store.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            quantity INTEGER,
            unit_price REAL,
            updated_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            item_id INTEGER,
            qty INTEGER,
            total_price REAL,
            order_date TEXT
        )
    """)
    conn.commit()
    conn.close()

# VULNERABLE: Direct SQL string interpolation
def add_inventory_item(name, quantity, unit_price):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    timestamp = str(time.time())
    query = "INSERT INTO inventory (item_name, quantity, unit_price, updated_at) VALUES ('%s', %s, %s, '%s')" % (name, quantity, unit_price, timestamp)
    cur.execute(query)
    conn.commit()
    conn.close()
    return True

# VULNERABLE: SQL Injection vector in search
def search_items(search_term):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    query = "SELECT * FROM inventory WHERE item_name LIKE '%%" + search_term + "%%'"
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return rows

# UNHANDLED EDGE CASES: Race conditions, negative stock, lack of transaction rollback
def process_order(customer_name, item_id, order_qty):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Check stock
    cur.execute("SELECT quantity, unit_price FROM inventory WHERE id = " + str(item_id))
    item = cur.fetchone()
    if not item:
        conn.close()
        return "ERROR: Item not found"
    
    current_qty, price = item[0], item[1]
    if current_qty < order_qty:
        conn.close()
        return "ERROR: Insufficient stock"
    
    new_qty = current_qty - order_qty
    total = order_qty * price
    date_str = str(time.time())
    
    # Deduct stock and insert order
    cur.execute("UPDATE inventory SET quantity = " + str(new_qty) + " WHERE id = " + str(item_id))
    cur.execute("INSERT INTO orders (customer_name, item_id, qty, total_price, order_date) VALUES ('" + customer_name + "', " + str(item_id) + ", " + str(order_qty) + ", " + str(total) + ", '" + date_str + "')")
    
    conn.commit()
    conn.close()
    return "SUCCESS: Order processed"

if __name__ == "__main__":
    init_db()
    print("Legacy System Initialized. Ready for IBM Bob 2.0 Modernization.")
