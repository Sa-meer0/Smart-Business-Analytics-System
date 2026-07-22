from database import Database
from flask import Blueprint, render_template, session, redirect, flash
import pandas as pd
import os
import sys
import glob
import traceback
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


dashboard = Blueprint("dashboard", __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET = os.path.join(BASE_DIR, "dataset")


def load_dataset():

    csv_files = glob.glob(
        os.path.join(DATASET, "*.csv")
    )

    if len(csv_files) == 0:
        return None

    dfs = []

    for file in csv_files:
        dfs.append(pd.read_csv(file))

    return pd.concat(
        dfs,
        ignore_index=True
    )


@dashboard.route("/dashboard")
def home():
    if "admin" not in session:
        return redirect("/")

    defaults = {
        "total_sales": 0,
        "total_transactions": 0,
        "total_customers": 0,
        "total_categories": 0,
        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "monthly_sales": [0] * 12,
        "category_labels": [],
        "category_sales": [],
        "segment_labels": ["High", "Medium", "Low"],
        "segment_values": [0, 0, 0],
        "top_names": [],
        "top_sales": [],
        "sales_model": False,
        "customer_model": False,
        "prediction_history": [],  # Added for dashboard prediction history
        "prediction_count": 0      # Added for dashboard prediction count
    }

    # ============================================================
    # Fetch Prediction History from Database (Fresh every load)
    # ============================================================
    try:
        with Database() as db:
            # Get recent predictions (last 5)
            recent_predictions = db.fetch_all(
                """SELECT id, prediction_type, input_data, result, created_at 
                   FROM prediction_history 
                   ORDER BY created_at DESC 
                   LIMIT 5"""
            )

            # Get total prediction count
            total_predictions = db.fetch_one(
                "SELECT COUNT(*) as count FROM prediction_history"
            )

            if recent_predictions:
                defaults["prediction_history"] = recent_predictions
            if total_predictions:
                defaults["prediction_count"] = total_predictions['count']

    except Exception as e:
        print(f"Prediction history fetch error: {e}")
        # Continue with empty history, don't fail the dashboard

    # ============================================================
    # Fetch Dashboard Stats from Dataset
    # ============================================================
    try:
        df = load_dataset()

        if df is None:
            flash("No CSV files found in the dataset folder!", "warning")
            return render_template("dashboard.html", **defaults)

        col_map = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'date' in col_lower:
                col_map['date'] = col
            elif 'total' in col_lower or 'amount' in col_lower:
                col_map['total'] = col
            elif 'customer' in col_lower and 'name' in col_lower:
                col_map['customer'] = col
            elif 'category' in col_lower or 'product' in col_lower:
                col_map['category'] = col
            elif 'city' in col_lower:
                col_map['city'] = col

        if not col_map.get('total'):
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    col_map['total'] = col
                    break

        if 'total' in col_map:
            total_col = col_map['total']
            defaults['total_sales'] = round(df[total_col].sum(), 2)
            defaults['total_transactions'] = len(df)

            if 'date' in col_map:
                try:
                    df[col_map['date']] = pd.to_datetime(df[col_map['date']])
                    df['month_name'] = df[col_map['date']].dt.strftime("%b")
                    monthly = df.groupby('month_name')[total_col].sum()
                    month_order = ["Jan", "Feb", "Mar", "Apr", "May",
                                   "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                    monthly = monthly.reindex(month_order, fill_value=0)
                    defaults['months'] = monthly.index.tolist()
                    defaults['monthly_sales'] = [
                        float(x) for x in monthly.values.tolist()]
                except Exception as e:
                    print(f"Monthly sales error: {e}")

            if 'category' in col_map:
                try:
                    category = df.groupby(col_map['category'])[
                        total_col].sum().sort_values(ascending=False).head(10)
                    defaults['category_labels'] = category.index.tolist()
                    defaults['category_sales'] = [
                        float(x) for x in category.values.tolist()]
                except Exception as e:
                    print(f"Category error: {e}")

            if 'customer' in col_map:
                try:
                    top = df.groupby(col_map['customer'])[
                        total_col].sum().sort_values(ascending=False).head(10)
                    defaults['top_names'] = top.index.tolist()
                    defaults['top_sales'] = [
                        float(x) for x in top.values.tolist()]
                except Exception as e:
                    print(f"Top customers error: {e}")

                try:
                    customer_total = df.groupby(col_map['customer'])[
                        total_col].sum()
                    if len(customer_total) > 0:
                        high_threshold = customer_total.quantile(0.8)
                        medium_threshold = customer_total.quantile(0.4)
                        defaults['segment_values'] = [
                            int((customer_total >= high_threshold).sum()),
                            int(((customer_total >= medium_threshold) & (
                                customer_total < high_threshold)).sum()),
                            int((customer_total < medium_threshold).sum())
                        ]
                except Exception as e:
                    print(f"Segments error: {e}")

            if 'customer' in col_map:
                defaults['total_customers'] = df[col_map['customer']].nunique()

            if 'category' in col_map:
                defaults['total_categories'] = df[col_map['category']].nunique()

    except Exception as e:
        print(f"Dashboard Error: {e}")
        print(traceback.format_exc())
        flash(f"Error loading dashboard: {str(e)}", "danger")

    # Model status
    models_dir = os.path.join(BASE_DIR, "trained_models")
    defaults['sales_model'] = os.path.exists(
        os.path.join(models_dir, "linear_weights.npy"))
    defaults['customer_model'] = os.path.exists(
        os.path.join(models_dir, "logistic_weights.npy"))

    return render_template("dashboard.html", **defaults)
