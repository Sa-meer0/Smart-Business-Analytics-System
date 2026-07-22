from flask import Blueprint, render_template, request, session, redirect, flash, jsonify
from database import Database
from datetime import date, datetime
import sys
import os
import re
import random
import string

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

add_customer = Blueprint("add_customer", __name__, url_prefix="/customer")


def generate_invoice_id():
    """Generate a unique invoice ID"""
    prefix = "INV"
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}-{timestamp}-{random_suffix}"


def upgrade_segment(current_segment):
    """Upgrade customer segment: Low → Medium → High"""
    if current_segment == "Low Value":
        return "Medium Value"
    elif current_segment == "Medium Value":
        return "High Value"
    else:
        return "High Value"  # High Value stays High Value


def calculate_cogs(unit_price, quantity):
    """Calculate Cost of Goods Sold"""
    return unit_price * quantity * 0.65  # Assuming 65% cost ratio


def calculate_gross_income(total, cogs):
    """Calculate Gross Income"""
    return total - cogs


@add_customer.route("/add", methods=["GET", "POST"])
def add_customer_page():
    """Handle customer addition and sales transaction"""
    if "admin" not in session:
        return redirect("/")

    customer_data = None
    is_existing = False
    segment_upgraded = False
    new_segment = None
    operation_message = None
    operation_type = None  # 'existing_upgraded', 'new_customer', 'error'
    transaction_saved = False
    invoice_id = None

    if request.method == "POST":
        # Get customer form data
        customer_name = request.form.get("customer_name", "").strip()
        gender = request.form.get("gender", "Male")
        customer_type = request.form.get("customer_type", "Normal")
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()

        # Get sales form data
        product_line = request.form.get(
            "product_line", "Electronic accessories")
        product_id = request.form.get("product_id")

        if not product_id:
            flash("Please select a product.", "danger")
            return render_template("add_customer.html", today=date.today().isoformat())

        product_id = int(product_id)

        unit_price = float(request.form.get("unit_price", 0) or 0)
        quantity = int(request.form.get("quantity", 0) or 0)
        tax = float(request.form.get("tax", 0) or 0)
        discount = float(request.form.get("discount", 0) or 0)
        total = float(request.form.get("total", 0) or 0)
        payment_method = request.form.get("payment_method", "Cash")
        city = request.form.get("city", "Yangon")
        branch = request.form.get("branch", "A")
        sale_date = request.form.get("date", date.today().isoformat())

        # Validate required fields
        if not customer_name:
            flash("Customer name is required!", "danger")
            return render_template("add_customer.html", today=date.today().isoformat())

        if not phone:
            flash("Phone number is required!", "danger")
            return render_template("add_customer.html", today=date.today().isoformat())

        if not email:
            flash("Email address is required!", "danger")
            return render_template("add_customer.html", today=date.today().isoformat())

        if unit_price <= 0:
            flash("Unit price must be greater than 0!", "danger")
            return render_template("add_customer.html", today=date.today().isoformat())

        if quantity <= 0:
            flash("Quantity must be greater than 0!", "danger")
            return render_template("add_customer.html", today=date.today().isoformat())

        if total <= 0:
            flash("Total amount must be greater than 0!", "danger")
            return render_template("add_customer.html", today=date.today().isoformat())

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format!", "warning")
            return render_template("add_customer.html", today=date.today().isoformat())

        # Validate phone (basic)
        if not re.match(r"^[\d\s\+\-\(\)]{7,20}$", phone):
            flash("Invalid phone number format!", "warning")
            return render_template("add_customer.html", today=date.today().isoformat())

        try:
            with Database() as db:
                # ============================================================
                # STEP 1: Check if customer exists by Name, Phone, AND Email
                # ============================================================
                existing_customer = db.fetch_one(
                    """SELECT * FROM customers 
                       WHERE customer_name = %s 
                       AND phone = %s 
                       AND email = %s""",
                    (customer_name, phone, email)
                )

                if existing_customer:
                    # ============================================================
                    # CASE 1: Customer exists - Update customer_segment
                    # ============================================================
                    is_existing = True
                    customer_id = existing_customer['customer_id']
                    current_segment = existing_customer.get(
                        'customer_segment', 'Low Value')

                    # Determine new segment (upgrade logic)
                    new_segment = upgrade_segment(current_segment)
                    segment_upgraded = (new_segment != current_segment)

                    if segment_upgraded:
                        # Update only the customer_segment field
                        db.execute_query(
                            "UPDATE customers SET customer_segment = %s WHERE customer_id = %s",
                            (new_segment, customer_id)
                        )
                        operation_type = 'existing_upgraded'
                        operation_message = f"Existing customer found. Segment upgraded from '{current_segment}' to '{new_segment}'!"
                        flash(operation_message, "success")
                    else:
                        operation_type = 'existing_no_change'
                        operation_message = f"Existing customer found. Segment remains '{current_segment}' (already at highest level)."
                        flash(operation_message, "info")

                    # Get updated customer data
                    customer_data = db.fetch_one(
                        "SELECT * FROM customers WHERE customer_id = %s",
                        (customer_id,)
                    )

                else:
                    # ============================================================
                    # CASE 2: Customer does NOT exist - Insert new customer
                    # ============================================================

                    # Check if phone is used by another customer (different name)
                    phone_conflict = db.fetch_one(
                        "SELECT * FROM customers WHERE phone = %s AND customer_name != %s",
                        (phone, customer_name)
                    )
                    if phone_conflict:
                        flash(
                            f"Phone number '{phone}' is already registered to '{phone_conflict['customer_name']}'!", "warning")
                        return render_template("add_customer.html", today=date.today().isoformat())

                    # Check if email is used by another customer (different name)
                    email_conflict = db.fetch_one(
                        "SELECT * FROM customers WHERE email = %s AND customer_name != %s",
                        (email, customer_name)
                    )
                    if email_conflict:
                        flash(
                            f"Email '{email}' is already registered to '{email_conflict['customer_name']}'!", "warning")
                        return render_template("add_customer.html", today=date.today().isoformat())

                    # Insert new customer
                    initial_segment = "Low Value"
                    registration_date = date.today().isoformat()

                    db.execute_query("""
                        INSERT INTO customers 
                        (customer_name, gender, customer_type, phone, email, registration_date, customer_segment) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        customer_name,
                        gender,
                        customer_type,
                        phone,
                        email,
                        registration_date,
                        initial_segment
                    ))

                    customer_id = db.cursor.lastrowid
                    operation_type = 'new_customer'
                    operation_message = f"New customer '{customer_name}' added successfully with '{initial_segment}' segment!"
                    flash(operation_message, "success")

                    # Get the new customer data
                    customer_data = db.fetch_one(
                        "SELECT * FROM customers WHERE customer_id = %s",
                        (customer_id,)
                    )

                # ============================================================
                # STEP 2: Insert Sales Record
                # ============================================================

                # Generate invoice ID
                invoice_id = generate_invoice_id()

                # Calculate derived values
                subtotal = unit_price * quantity  # Calculated but not stored in DB
                cogs = calculate_cogs(unit_price, quantity)
                gross_income = calculate_gross_income(total, cogs)
                gross_margin = (gross_income / total * 100) if total > 0 else 0
                sale_time = datetime.now().strftime("%H:%M:%S")

                # Insert into sales table - REMOVED subtotal column (doesn't exist in table)
                db.execute_query("""
                    INSERT INTO sales 
                    (invoice_id, customer_id, product_id, branch, city,
                     unit_price, quantity, tax, discount, total,
                     payment_method, sale_date, sale_time,
                     cogs, gross_income)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    invoice_id,
                    customer_id,
                    product_id,
                    branch,
                    city,
                    unit_price,
                    quantity,
                    tax,
                    discount,
                    total,
                    payment_method,
                    sale_date,
                    sale_time,
                    cogs,
                    gross_income,
                ))

                transaction_saved = True
                flash(
                    f"Transaction #{invoice_id} saved successfully!", "success")

                # Get updated sales stats
                sales_stats = db.fetch_one(
                    """SELECT 
                        COUNT(*) as frequency,
                        COALESCE(SUM(total), 0) as total_spent
                    FROM sales 
                    WHERE customer_id = %s""",
                    (customer_id,)
                )
                frequency = sales_stats['frequency'] if sales_stats else 0
                total_spent = sales_stats['total_spent'] if sales_stats else 0

                return render_template(
                    "add_customer.html",
                    customer_exists=is_existing,
                    customer_name=customer_name,
                    customer_data=customer_data,
                    frequency=frequency,
                    total_spent=total_spent,
                    transaction_saved=transaction_saved,
                    invoice_id=invoice_id,
                    segment_upgraded=segment_upgraded,
                    new_segment=new_segment,
                    operation_type=operation_type,
                    operation_message=operation_message,
                    today=date.today().isoformat()
                )

        except Exception as e:
            flash(f"Database error: {str(e)}", "danger")
            print(f"Error in add_customer_page: {e}")
            return render_template("add_customer.html", today=date.today().isoformat())

    return render_template("add_customer.html", today=date.today().isoformat())


@add_customer.route("/check_customer", methods=["POST"])
def check_customer():
    """AJAX endpoint to check if customer exists by Name, Phone, AND Email"""
    try:
        customer_name = request.json.get("customer_name", "").strip()
        phone = request.json.get("phone", "").strip()
        email = request.json.get("email", "").strip()

        if not customer_name:
            return jsonify({"exists": False, "error": "Customer name is required"})

        if not phone or not email:
            return jsonify({
                "exists": False,
                "error": "Phone and email are required to check",
                "partial": True
            })

        with Database() as db:
            # ============================================================
            # Check EXACT match: Name + Phone + Email
            # ============================================================
            existing_customer = db.fetch_one(
                """SELECT * FROM customers 
                   WHERE customer_name = %s 
                   AND phone = %s 
                   AND email = %s""",
                (customer_name, phone, email)
            )

            if existing_customer:
                customer_id = existing_customer['customer_id']
                current_segment = existing_customer.get(
                    'customer_segment', 'Low Value')

                # Determine if upgrade is possible
                new_segment = upgrade_segment(current_segment)
                can_upgrade = (new_segment != current_segment)

                response = {
                    "exists": True,
                    "exact_match": True,
                    "customer": existing_customer,
                    "customer_id": customer_id,
                    "current_segment": current_segment,
                    "new_segment": new_segment if can_upgrade else current_segment,
                    "can_upgrade": can_upgrade,
                    "status": "existing_customer",
                    "message": f"Customer found with exact match. Segment: {current_segment}"
                }
                return jsonify(response)

            # ============================================================
            # Check for partial matches (conflicts)
            # ============================================================

            # Check if name exists with different phone/email
            name_exists = db.fetch_one(
                "SELECT * FROM customers WHERE customer_name = %s",
                (customer_name,)
            )
            if name_exists:
                return jsonify({
                    "exists": False,
                    "exact_match": False,
                    "status": "name_exists",
                    "message": f"Customer name '{customer_name}' exists but with different contact details.",
                    "existing_phone": name_exists.get('phone'),
                    "existing_email": name_exists.get('email')
                })

            # Check if phone is used by another customer
            phone_exists = db.fetch_one(
                "SELECT * FROM customers WHERE phone = %s",
                (phone,)
            )
            if phone_exists:
                return jsonify({
                    "exists": False,
                    "exact_match": False,
                    "status": "phone_exists",
                    "message": f"Phone number '{phone}' is already registered to '{phone_exists['customer_name']}'."
                })

            # Check if email is used by another customer
            email_exists = db.fetch_one(
                "SELECT * FROM customers WHERE email = %s",
                (email,)
            )
            if email_exists:
                return jsonify({
                    "exists": False,
                    "exact_match": False,
                    "status": "email_exists",
                    "message": f"Email '{email}' is already registered to '{email_exists['customer_name']}'."
                })

            # ============================================================
            # Completely new customer
            # ============================================================
            return jsonify({
                "exists": False,
                "exact_match": False,
                "status": "new_customer",
                "message": "New customer. Will be added with Low Value segment.",
                "new_segment": "Low Value"
            })

    except Exception as e:
        print(f"Error in check_customer: {e}")
        return jsonify({"error": str(e)}), 500


@add_customer.route("/calculate_total", methods=["POST"])
def calculate_total():
    """AJAX endpoint to calculate total with tax and discount"""
    try:
        unit_price = float(request.json.get("unit_price", 0))
        quantity = int(request.json.get("quantity", 0))
        tax = float(request.json.get("tax", 0))
        discount = float(request.json.get("discount", 0))

        subtotal = unit_price * quantity
        total = subtotal + tax - discount

        return jsonify({
            "subtotal": round(subtotal, 2),
            "total": round(total, 2)
        })
    except Exception as e:
        print(f"Error in calculate_total: {e}")
        return jsonify({"error": str(e)}), 500


@add_customer.route("/get_products/<category_name>")
def get_products(category_name):
    """Get all products of the selected category"""

    try:
        with Database() as db:

            products = db.fetch_all("""
                SELECT
                    p.product_id,
                    p.product_name
                FROM products p
                INNER JOIN categories c
                    ON p.category_id = c.category_id
                WHERE c.category_name = %s
                ORDER BY p.product_name
            """, (category_name,))

            return jsonify(products)

    except Exception as e:
        print(e)
        return jsonify([])
