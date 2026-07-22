from database import get_connection


def get_dashboard_summary():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Total Sales
    cursor.execute("SELECT IFNULL(SUM(total),0) AS total_sales FROM sales")
    total_sales = cursor.fetchone()["total_sales"]

    # Units Sold
    cursor.execute("SELECT IFNULL(SUM(quantity),0) AS units_sold FROM sales")
    units_sold = cursor.fetchone()["units_sold"]

    # Total Customers
    cursor.execute("SELECT COUNT(*) AS customers FROM customers")
    customers = cursor.fetchone()["customers"]

    # Total Products
    cursor.execute("SELECT COUNT(*) AS products FROM products")
    products = cursor.fetchone()["products"]

    # Low Stock Products
    cursor.execute("""
        SELECT COUNT(*) AS low_stock
        FROM inventory
        WHERE stock_quantity <= reorder_level
    """)
    low_stock = cursor.fetchone()["low_stock"]

    cursor.close()
    conn.close()

    return {
        "total_sales": total_sales,
        "units_sold": units_sold,
        "customers": customers,
        "products": products,
        "low_stock": low_stock
    }
