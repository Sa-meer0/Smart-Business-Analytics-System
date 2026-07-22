from ml.logistic_regression import LogisticRegression
from ml.linear_regression import LinearRegression
from ml.preprocess import DataPreprocessor
from flask import Blueprint, redirect, session, flash
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


train = Blueprint("train", __name__, url_prefix="/train")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@train.route("/")
def train_models():

    if "admin" not in session:
        return redirect("/")

    # ==========================================================
    # Load ALL CSV files from dataset folder
    # ==========================================================
    dataset_path = os.path.join(BASE_DIR, "dataset")

    print("BASE_DIR:", BASE_DIR)
    print("DATASET PATH:", dataset_path)
    print("Exists:", os.path.exists(dataset_path))

    if not os.path.exists(dataset_path):
        flash("Dataset folder not found!", "danger")
        return redirect("/dashboard")

    try:

        processor = DataPreprocessor(dataset_path)

        processor.load_data()
        processor.clean_data()
        processor.encode_columns()

        models_dir = os.path.join(BASE_DIR, "trained_models")
        os.makedirs(models_dir, exist_ok=True)

        np.save(
            os.path.join(models_dir, "city_map.npy"),
            processor.city_mapping
        )

        np.save(
            os.path.join(models_dir, "product_map.npy"),
            processor.product_mapping
        )

        # ======================================================
        # Train Linear Regression
        # ======================================================
        X_sales, y_sales = processor.get_sales_data()

        y_mean = y_sales.mean()
        y_std = y_sales.std()

        if y_std == 0:
            y_std = 1

        y_sales_scaled = (y_sales - y_mean) / y_std

        np.save(
            os.path.join(models_dir, "y_mean.npy"),
            y_mean
        )

        np.save(
            os.path.join(models_dir, "y_std.npy"),
            y_std
        )

        linear = LinearRegression(
            learning_rate=0.01,
            epochs=5000
        )

        linear.fit(
            X_sales,
            y_sales_scaled
        )

        linear.save(
            feature_names=X_sales.columns.tolist()
        )

        print(
            f"Linear Regression R²: {linear.score(X_sales, y_sales_scaled)}"
        )

        # ======================================================
        # Train Logistic Regression
        # ======================================================
        X_customer, y_customer = processor.get_customer_data()

        if len(X_customer) == 0:
            flash("Customer dataset empty!", "warning")
            return redirect("/dashboard")

        logistic = LogisticRegression(
            learning_rate=0.01,
            epochs=3000
        )

        logistic.fit(
            X_customer,
            y_customer
        )

        logistic.save()

        flash("Models trained successfully!", "success")

    except Exception as e:

        flash(f"Training error: {str(e)}", "danger")
        print(f"Training error: {e}")

    return redirect("/dashboard")
