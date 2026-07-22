from platform import processor

from utils.history import save_prediction
from ml.preprocess import DataPreprocessor
from ml.logistic_regression import LogisticRegression
from ml.linear_regression import LinearRegression
from flask import Blueprint, render_template, request, session, redirect, flash
import numpy as np
import pandas as pd
import os
import sys
import glob

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

prediction = Blueprint("prediction", __name__, url_prefix="/prediction")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET = os.path.join(BASE_DIR, "dataset")


def load_dataset():

    csv_files = glob.glob(
        os.path.join(DATASET, "*.csv")
    )

    if len(csv_files) == 0:
        raise FileNotFoundError("No CSV files found in dataset folder.")

    dfs = []

    for file in csv_files:
        dfs.append(pd.read_csv(file))

    return pd.concat(
        dfs,
        ignore_index=True
    )


def get_products():
    df = load_dataset()
    return sorted(df["category"].dropna().unique().tolist())


def get_product_mapping():
    df = load_dataset()
    mapping = {}
    for category in sorted(df["category"].dropna().unique()):
        products = (df[df["category"] == category]["product_name"]
                    .dropna().sort_values().unique().tolist())
        mapping[category] = products
    return mapping


def get_all_products():
    df = load_dataset()
    return sorted(df["product_name"].dropna().unique().tolist())


def get_customers():
    df = load_dataset()
    return sorted(df["customer_name"].dropna().unique().tolist())


def get_cities():
    df = load_dataset()
    return sorted(df["city"].dropna().unique().tolist())


@prediction.route("/")
def prediction_page():
    if "admin" not in session:
        return redirect("/")

    return render_template(
        "prediction.html",
        products=get_products(),
        product_mapping=get_product_mapping(),
        customers=get_customers(),
        cities=get_cities()
    )


@prediction.route("/sales", methods=["POST"])
def sales_prediction():
    if "admin" not in session:
        return redirect("/")

    category = request.form.get("product_category", "")
    product_name = request.form.get("product_name", "")
    city = request.form.get("city", "")
    price = request.form.get("unit_price", "").strip()

    if not price:
        flash("Unit price is required!", "danger")
        return render_template(
            "prediction.html",
            products=get_products(),
            product_mapping=get_product_mapping(),
            customers=get_customers(),
            cities=get_cities()
        )

    try:
        unit_price = float(price)
    except ValueError:
        flash("Invalid unit price!", "danger")
        return render_template(
            "prediction.html",
            products=get_products(),
            product_mapping=get_product_mapping(),
            customers=get_customers(),
            cities=get_cities()
        )    
    month = int(request.form.get("month", 1))

    try:
        model = LinearRegression()
        model.load()
        feature_names = model.load_feature_names()

        row = pd.DataFrame(np.zeros((1, len(feature_names))),
                           columns=feature_names)

        if "unit_price" in row.columns:
            row.loc[0, "unit_price"] = unit_price
        if "month" in row.columns:
            row.loc[0, "month"] = month

        category_column = f"category_{category}"
        if category_column in row.columns:
            row.loc[0, category_column] = 1

        product_column = f"product_name_{product_name}"
        if product_column in row.columns:
            row.loc[0, product_column] = 1

        city_column = f"city_{city}"
        if city_column in row.columns:
            row.loc[0, city_column] = 1

        X = row.values.astype(float)

        models_dir = os.path.join(BASE_DIR, "trained_models")
        x_mean = np.load(os.path.join(models_dir, "linear_mean.npy"))
        x_std = np.load(os.path.join(models_dir, "linear_std.npy"))
        y_mean = np.load(os.path.join(models_dir, "y_mean.npy"))
        y_std = np.load(os.path.join(models_dir, "y_std.npy"))

        X = (X - x_mean) / x_std
        pred_scaled = model.predict(X)[0]
        raw_prediction = (pred_scaled * y_std) + y_mean
        prediction_value = round(float(raw_prediction), 2)

        # Save to database
        input_text = f"{category}, {product_name}, {city}, Price={unit_price}, Month={month}"
        save_prediction("Sales Prediction", input_text, prediction_value)

        flash(f"Prediction saved! Result: {prediction_value}", "success")

        return render_template(
            "prediction.html",
            products=get_products(),
            product_mapping=get_product_mapping(),
            product_names=get_all_products(),
            customers=get_customers(),
            cities=get_cities(),
            sales_result=prediction_value
        )
    except Exception as e:
        flash(f"Prediction error: {str(e)}", "danger")
        return render_template(
            "prediction.html",
            products=get_products(),
            product_mapping=get_product_mapping(),
            customers=get_customers(),
            cities=get_cities()
        )


@prediction.route("/customers", methods=["GET", "POST"])
def customer_segmentation():
    if "admin" not in session:
        return redirect("/")

    try:
        processor = DataPreprocessor(DATASET)
        processor.load_data()
        rfm = processor.create_rfm_features()

        model = LogisticRegression()
        try:
            model.load()
        except:
            flash("Model not trained yet. Please train first.", "warning")
            return render_template("customers.html", customers=[], selected_segment=None)

        X = rfm[["total_amount", "frequency", "recency"]].values
        rfm["segment_id"] = model.predict(X)

        label_map = {0: "Low Value", 1: "Medium Value", 2: "High Value"}
        rfm["segment"] = rfm["segment_id"].map(label_map)

        result = rfm
        selected_segment = None
        segment_count = 0
        recommendations = []

        if request.method == "POST":
            selected_segment = request.form.get("segment", "")
            result = rfm[rfm["segment"] == selected_segment]
            result = result.sort_values("total_amount", ascending=False)
            segment_count = len(result)

            # Generate recommendations based on segment
            recommendations = get_segment_recommendations(selected_segment)

        return render_template(
            "customers.html",
            customers=result.to_dict("records"),
            selected_segment=selected_segment,
            segment_count=segment_count,
            recommendations=recommendations
        )
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return render_template("customers.html", customers=[], selected_segment=None)


def get_segment_recommendations(segment):
    """Get business recommendations based on customer segment"""
    recommendations = {
        "High Value": [
            {"icon": "fa-crown", "title": "Reward Loyal Customers",
                "desc": "Offer exclusive discounts and VIP treatment to retain high-value customers."},
            {"icon": "fa-gem", "title": "Premium Membership",
                "desc": "Provide premium membership with special benefits and early access to new products."},
            {"icon": "fa-gift", "title": "Personalized Offers",
                "desc": "Send personalized recommendations and exclusive deals based on purchase history."},
            {"icon": "fa-star", "title": "Referral Program",
                "desc": "Create a referral program that rewards high-value customers for bringing new clients."},
        ],
        "Medium Value": [
            {"icon": "fa-arrow-up", "title": "Encourage Repeat Purchases",
                "desc": "Use loyalty points and rewards to encourage more frequent purchases."},
            {"icon": "fa-percent", "title": "Seasonal Discounts",
                "desc": "Offer seasonal promotions and bundle deals to increase order value."},
            {"icon": "fa-cart-plus", "title": "Cross-Sell Products",
                "desc": "Recommend complementary products to increase average order value."},
            {"icon": "fa-bullhorn", "title": "Targeted Promotions",
                "desc": "Run targeted email campaigns with products they're likely to buy."},
        ],
        "Low Value": [
            {"icon": "fa-rocket", "title": "Re-engagement Campaigns",
                "desc": "Launch re-engagement campaigns with special offers to win back customers."},
            {"icon": "fa-tags", "title": "Introductory Discounts",
                "desc": "Offer first-purchase discounts or free shipping to encourage buying."},
            {"icon": "fa-box", "title": "Promotional Bundles",
                "desc": "Create attractive bundles and starter packs at competitive prices."},
            {"icon": "fa-envelope", "title": "Email Marketing",
                "desc": "Send personalized product recommendations and brand storytelling emails."},
        ]
    }
    return recommendations.get(segment, [])
