"""
E-Commerce Database System
"""

import sys
from datetime import datetime

import mysql.connector
from mysql.connector import Error

# Database connection settings (edit for your specific machine)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "mysqlpassword",
    "database": "ecommerce",
    # Autocommit for ordinary statements; make_purchase() opens an
    # explicit transaction where atomicity actually matters.
    "autocommit": True,
}

def get_connection():
    """Open a new connection to the ecommerce DB"""
    return mysql.connector.connect(**DB_CONFIG)

# Shared helpers
def print_table(rows, headers):
    """Print query results as a simple aligned text table"""
    if not rows:
        print("  (no results)")
        return
    str_rows = [[str(v) for v in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in str_rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(val))
    line = "  " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(line)
    print("  " + "-+-".join("-" * w for w in widths))
    for row in str_rows:
        print("  " + " | ".join(val.ljust(widths[i]) for i, val in enumerate(row)))

def ask_int(prompt):
    """Prompt until the user enters a valid integer"""
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("  Please enter a whole number.")

def ask_float(prompt):
    """Prompt until the user enters a valid non-negative number"""
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value < 0:
                print("  Value cannot be negative.")
                continue
            return value
        except ValueError:
            print("  Please enter a number.")

# Product browsing
def view_products(conn):
    cur = conn.cursor()
    cur.execute(
        """SELECT ProductId, Name, Category, Price, Stock
           FROM Product ORDER BY ProductId"""
    )
    rows = cur.fetchall()
    cur.close()
    print("\n  PRODUCT CATALOG")
    print_table(rows, ["ID", "Name", "Category", "Price", "In Stock"])

# Staff features
def staff_login(conn):
    """Identify a staff member by email. Returns (StaffId, name) or None"""
    email = input("  Staff email: ").strip()
    cur = conn.cursor()
    cur.execute(
        "SELECT StaffId, FirstName, LastName FROM Staff WHERE Email = %s",
        (email,),
    )
    row = cur.fetchone()
    cur.close()
    if row is None:
        print("  No staff member found with that email.")
        return None
    print(f"  Welcome, {row[1]} {row[2]}!")
    return row[0], f"{row[1]} {row[2]}"

def add_product(conn, staff_id):
    print("\n  ADD NEW PRODUCT")
    name = input("  Product name: ").strip()
    if not name:
        print("  Name cannot be empty.")
        return
    description = input("  Description: ").strip()
    category = input("  Category: ").strip()
    price = ask_float("  Price: ")
    stock = ask_int("  Starting stock quantity: ")
    if stock < 0:
        print("  Stock cannot be negative.")
        return
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO Product (Name, Description, Category, Price,
                                Stock, ManagedBy)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (name, description, category, price, stock, staff_id),
    )
    conn.commit()
    print(f"  Product '{name}' added with ID {cur.lastrowid}.")
    cur.close()

def update_stock(conn):
    print("\n  UPDATE STOCK")
    view_products(conn)
    product_id = ask_int("\n  Product ID to update: ")
    new_qty = ask_int("  New stock quantity: ")
    if new_qty < 0:
        print("  Stock cannot be negative.")
        return
    cur = conn.cursor()
    cur.execute(
        "UPDATE Product SET Stock = %s WHERE ProductId = %s",
        (new_qty, product_id),
    )
    conn.commit()
    if cur.rowcount == 0:
        print("  No product with that ID.")
    else:
        print("  Stock updated.")
    cur.close()

def view_transactions(conn):
    cur = conn.cursor()
    cur.execute(
        """SELECT pu.PurchaseId,
                  CONCAT(c.FirstName, ' ', c.LastName) AS Customer,
                  p.Name AS Product,
                  pu.Quantity,
                  pu.TotalPrice,
                  pu.DatePurchased
           FROM Purchase pu
           JOIN Customer c ON pu.CustomerId = c.CustomerId
           JOIN Product  p ON pu.ProductId  = p.ProductId
           ORDER BY pu.DatePurchased DESC"""
    )
    rows = cur.fetchall()
    cur.close()
    print("\n  ALL TRANSACTIONS")
    print_table(rows, ["ID", "Customer", "Product", "Qty", "Total", "Date"])

def staff_menu(conn):
    login = staff_login(conn)
    if login is None:
        return
    staff_id, _name = login
    while True:
        print(
            "\n  STAFF MENU\n"
            "  1) View products\n"
            "  2) Add product\n"
            "  3) Update stock\n"
            "  4) View all transactions\n"
            "  0) Back to main menu"
        )
        choice = input("  Choice: ").strip()
        if choice == "1":
            view_products(conn)
        elif choice == "2":
            add_product(conn, staff_id)
        elif choice == "3":
            update_stock(conn)
        elif choice == "4":
            view_transactions(conn)
        elif choice == "0":
            return
        else:
            print("  Invalid choice.")

# Customer features
def customer_login(conn):
    """Identify a customer by email. Returns (CustomerId, name) or None"""
    email = input("  Customer email: ").strip()
    cur = conn.cursor()
    cur.execute(
        "SELECT CustomerId, FirstName, LastName FROM Customer WHERE Email = %s",
        (email,),
    )
    row = cur.fetchone()
    cur.close()
    if row is None:
        print("  No customer found with that email.")
        return None
    print(f"  Welcome, {row[1]} {row[2]}!")
    return row[0], f"{row[1]} {row[2]}"

def add_credit_card(conn, customer_id):
    print("\n  ADD CREDIT CARD")
    number = input("  Card number: ").strip()
    if not (number.isdigit() and 13 <= len(number) <= 19):
        print("  Card number must be 13-19 digits.")
        return
    holder = input("  Cardholder name: ").strip()
    exp = input("  Expiration date (YYYY-MM-DD): ").strip()
    try:
        datetime.strptime(exp, "%Y-%m-%d")
    except ValueError:
        print("  Invalid date format.")
        return
    zipcode = input("  Billing ZIP: ").strip()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO CreditCard (CustomerId, card_number, cardholder_name,
                                   expiration_date, billing_zip)
           VALUES (%s, %s, %s, %s, %s)""",
        (customer_id, number, holder, exp, zipcode),
    )
    conn.commit()
    print(f"  Card ending in {number[-4:]} added.")
    cur.close()

def choose_card(conn, customer_id):
    """List the customer's cards and return the chosen CardId, or None"""
    cur = conn.cursor()
    cur.execute(
        """SELECT CardId, CONCAT('**** ', RIGHT(card_number, 4)), expiration_date
           FROM CreditCard WHERE CustomerId = %s""",
        (customer_id,),
    )
    cards = cur.fetchall()
    cur.close()
    if not cards:
        print("  You have no stored cards. Add one first.")
        return None
    print("\n  YOUR CARDS")
    print_table(cards, ["ID", "Card", "Expires"])
    card_id = ask_int("  Pay with card ID: ")
    if card_id not in [c[0] for c in cards]:
        print("  That is not one of your cards.")
        return None
    return card_id

def make_purchase(conn, customer_id):
    print("\n  MAKE A PURCHASE")
    view_products(conn)
    product_id = ask_int("\n  Product ID to buy: ")
    quantity = ask_int("  Quantity: ")
    if quantity <= 0:
        print("  Quantity must be at least 1.")
        return

    cur = conn.cursor()
    try:
        conn.start_transaction()
        cur.execute(
            """SELECT Name, Price, Stock FROM Product
               WHERE ProductId = %s FOR UPDATE""",
            (product_id,),
        )
        row = cur.fetchone()
        if row is None:
            print("  No product with that ID.")
            conn.rollback()
            return
        name, price, stock = row
        if stock < quantity:
            print(f"  Not enough stock: only {stock} unit(s) of '{name}' left.")
            conn.rollback()
            return

        card_id = choose_card(conn, customer_id)
        if card_id is None:
            conn.rollback()
            return

        total = price * quantity
        cur.execute(
            """INSERT INTO Purchase (CustomerId, ProductId, CardId,
                                     Quantity, TotalPrice)
               VALUES (%s, %s, %s, %s, %s)""",
            (customer_id, product_id, card_id, quantity, total),
        )
        cur.execute(
            """UPDATE Product SET Stock = Stock - %s
               WHERE ProductId = %s""",
            (quantity, product_id),
        )
        conn.commit()
        print(f"  Purchase complete: {quantity} x {name} for ${total:.2f}.")
    except Error as err:
        conn.rollback()
        print(f"  Purchase failed and was rolled back: {err}")
    finally:
        cur.close()

def view_my_history(conn, customer_id):
    cur = conn.cursor()
    cur.execute(
        """SELECT p.Name, pu.Quantity, pu.TotalPrice, pu.DatePurchased
           FROM Purchase pu
           JOIN Product p ON pu.ProductId = p.ProductId
           WHERE pu.CustomerId = %s
           ORDER BY pu.DatePurchased DESC""",
        (customer_id,),
    )
    rows = cur.fetchall()
    cur.close()
    print("\n  YOUR PURCHASE HISTORY")
    print_table(rows, ["Product", "Qty", "Total", "Date"])

def customer_menu(conn):
    login = customer_login(conn)
    if login is None:
        return
    customer_id, _name = login
    while True:
        print(
            "\n  CUSTOMER MENU\n"
            "  1) Browse products\n"
            "  2) Add credit card\n"
            "  3) Make a purchase\n"
            "  4) View my purchase history\n"
            "  0) Back to main menu"
        )
        choice = input("  Choice: ").strip()
        if choice == "1":
            view_products(conn)
        elif choice == "2":
            add_credit_card(conn, customer_id)
        elif choice == "3":
            make_purchase(conn, customer_id)
        elif choice == "4":
            view_my_history(conn, customer_id)
        elif choice == "0":
            return
        else:
            print("  Invalid choice.")

# Main
def main():
    try:
        conn = get_connection()
    except Error as err:
        print(f"Could not connect to database: {err}")
        print("Check DB_CONFIG at the top of this file.")
        sys.exit(1)

    print("=" * 50)
    print("  E-COMMERCE DATABASE SYSTEM")
    print("=" * 50)
    try:
        while True:
            print(
                "\n  MAIN MENU\n"
                "  1) Staff login\n"
                "  2) Customer login\n"
                "  0) Exit"
            )
            choice = input("  Choice: ").strip()
            if choice == "1":
                staff_menu(conn)
            elif choice == "2":
                customer_menu(conn)
            elif choice == "0":
                print("  Goodbye!")
                break
            else:
                print("  Invalid choice.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
