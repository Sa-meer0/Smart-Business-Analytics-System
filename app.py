from flask import Flask, session
from database import Database
import os
import sys
from config import Config
from datetime import timedelta

# Add the routes folder to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'routes'))

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Import blueprints from routes folder
try:
    from routes.auth import auth
    from routes.dashboard import dashboard
    from routes.history import history
    from routes.prediction import prediction
    from routes.train import train
    from routes.add_customer import add_customer
    print("✓ All modules imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(history)
app.register_blueprint(prediction)
app.register_blueprint(train)
app.register_blueprint(add_customer)
print("✓ All blueprints registered")

# Initialize database tables
def init_db():
    try:
        with Database() as db:
            # Admin table
            db.execute_query("""
                CREATE TABLE IF NOT EXISTS admin (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
                )
            """)
            
            # Customers table
            db.execute_query("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_name VARCHAR(255) UNIQUE NOT NULL,
                    gender VARCHAR(50),
                    customer_type VARCHAR(50),
                    phone VARCHAR(20),
                    email VARCHAR(255),
                    registration_date DATE,
                    customer_segment VARCHAR(50) DEFAULT 'Low Value',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Sales table - Fixed schema
            db.execute_query("""
                CREATE TABLE IF NOT EXISTS sales (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    invoice_id VARCHAR(50) UNIQUE,
                    customer_id INT,
                    customer_name VARCHAR(255),
                    gender VARCHAR(50),
                    customer_type VARCHAR(50),
                    branch VARCHAR(50),
                    city VARCHAR(100),
                    unit_price DECIMAL(10,2),
                    quantity INT,
                    tax DECIMAL(10,2),
                    discount DECIMAL(10,2),
                    subtotal DECIMAL(10,2),
                    total DECIMAL(10,2),
                    payment_method VARCHAR(100),
                    product_line VARCHAR(255),
                    sale_date DATE,
                    sale_time TIME,
                    cogs DECIMAL(10,2),
                    gross_income DECIMAL(10,2),
                    gross_margin DECIMAL(10,2),
                    rating DECIMAL(3,1),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
                )
            """)
            
            # Prediction history table
            db.execute_query("""
                CREATE TABLE IF NOT EXISTS prediction_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    prediction_type VARCHAR(255),
                    input_data TEXT,
                    result VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert default admin if not exists
            admin = db.fetch_one("SELECT * FROM admin WHERE username = 'admin'")
            if not admin:
                db.execute_query(
                    "INSERT INTO admin (username, password) VALUES (%s, %s)",
                    ('admin', 'admin123')
                )
                print("✓ Default admin created: admin/admin123")
            
            print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database error: {e}")


# ============================================
# Request Context Processor for Session Validation
# ============================================
@app.context_processor
def inject_user():
    """Inject user info into all templates"""
    return {
        'session_user': session.get('admin', None),
        'is_logged_in': 'admin' in session
    }

# ============================================
# Session Cleanup for Fresh Dashboard Data
# ============================================
@app.after_request
def clear_dashboard_cache(response):
    """Clear any cached dashboard data from session"""
    if 'dashboard_cache' in session:
        del session['dashboard_cache']
    return response

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🚀 SMART BUSINESS ANALYTICS SYSTEM")
    print("📍 http://localhost:5000")
    print("🔑 admin / admin123")
    print("=" * 50 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)