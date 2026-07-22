import os
import glob
import pandas as pd
import numpy as np


class DataPreprocessor:

    def __init__(self, filepath):

        self.filepath = filepath
        self.data = None

        # Mapping dictionaries (used by Logistic Regression)
        self.product_mapping = {}
        self.city_mapping = {}
        self.segment_mapping = {}

    # ==========================================================
    # Load Dataset
    # ==========================================================
    def load_data(self):

        # ------------------------------------------------------
        # If a directory is provided, load ALL CSV files
        # ------------------------------------------------------
        if os.path.isdir(self.filepath):

            csv_files = glob.glob(
                os.path.join(self.filepath, "*.csv")
            )

            if len(csv_files) == 0:
                raise FileNotFoundError(
                    f"No CSV files found in {self.filepath}"
                )

            dfs = []

            for file in csv_files:
                dfs.append(pd.read_csv(file))

            self.data = pd.concat(
                dfs,
                ignore_index=True
            )

        # ------------------------------------------------------
        # If a single CSV is provided
        # ------------------------------------------------------
        elif self.filepath.endswith(".csv"):

            self.data = pd.read_csv(self.filepath)

        # ------------------------------------------------------
        # Excel file
        # ------------------------------------------------------
        else:

            self.data = pd.read_excel(self.filepath)

        self.data.columns = self.data.columns.str.strip()
        

        return self.data

    # ==========================================================
    # Clean Dataset
    # ==========================================================
    def clean_data(self):

        self.data.drop_duplicates(inplace=True)

        self.data.dropna(inplace=True)

        self.data.reset_index(drop=True, inplace=True)

        return self.data

    # ==========================================================
    # Encode Columns
    #
    # Used ONLY for Logistic Regression
    # ==========================================================
    def encode_columns(self):

        categories = sorted(self.data["category"].unique())

        self.product_mapping = {
            value: index
            for index, value in enumerate(categories)
        }

        cities = sorted(self.data["city"].unique())

        self.city_mapping = {
            value: index
            for index, value in enumerate(cities)
        }

        return self.data

    # ==========================================================
    # Get Lists
    # ==========================================================
    def get_products(self):

        return sorted(self.data["category"].unique().tolist())

    def get_cities(self):

        return sorted(self.data["city"].unique().tolist())

    # ==========================================================
    # Linear Regression Dataset
    # ==========================================================
    def get_sales_data(self):

        df = self.data.copy()

        # -------------------------
        # Convert Date
        # -------------------------
        df["sale_date"] = pd.to_datetime(
            df["sale_date"],
            format="mixed",
            dayfirst=True,
            errors="coerce"
        )

        df = df.dropna(subset=["sale_date"])

        df["month"] = df["sale_date"].dt.month.astype(int)

        # -------------------------
        # One-Hot Encode
        # -------------------------
        df = pd.get_dummies(
            df,
            columns=["category", "city"],
            drop_first=True,
            dtype=int
        )

        # -------------------------
        # Target
        # -------------------------
        y = df["quantity"].astype(float)

        # -------------------------
        # Feature Columns
        # -------------------------
        feature_columns = [
            "unit_price",
            "month"
        ]

        feature_columns.extend(
            sorted(
                [col for col in df.columns if col.startswith("category_")]
            )
        )

        feature_columns.extend(
            sorted(
                [col for col in df.columns if col.startswith("city_")]
            )
        )

        X = df[feature_columns].astype(float)

        print("\n========== Linear Regression Features ==========")
        print(X.columns.tolist())
        print("Number of Features:", len(X.columns))
        print("===============================================\n")

        print("\n========== TRAINING DATA ==========")
        print(X.describe())

        print("\nQuantity")
        print(y.describe())

        print("\nUnit Price Range")
        print(df["unit_price"].describe())

        return X, y

    # ==========================================================
    # RFM Features
    # ==========================================================
    def create_rfm_features(self):

        df = self.data.copy()

        df["sale_date"] = pd.to_datetime(
            df["sale_date"],
            format="mixed",
            dayfirst=True,
            errors="coerce"
        )
        latest_date = df["sale_date"].max()

        rfm = (

            df.groupby("customer_name")

            .agg(

                total_amount=("total", "sum"),

                frequency=("invoice_id", "count"),

                last_purchase=("sale_date", "max")

            )

            .reset_index()

        )

        rfm["recency"] = (

            latest_date - rfm["last_purchase"]

        ).dt.days

        rfm.drop(columns=["last_purchase"], inplace=True)

        return rfm

    # ==========================================================
    # Customer Segmentation
    # ==========================================================
    def create_customer_segments(self, rfm):

        score = (

            rfm["total_amount"].rank(pct=True) * 0.5 +

            rfm["frequency"].rank(pct=True) * 0.3 +

            (1 - rfm["recency"].rank(pct=True)) * 0.2

        )

        rfm["customer_segment"] = np.where(

            score >= 0.70,

            "High Value",

            np.where(

                score >= 0.40,

                "Medium Value",

                "Low Value"

            )

        )

        return rfm

    # ==========================================================
    # Encode Customer Segment
    # ==========================================================
    def encode_customer_segment(self, rfm):

        self.segment_mapping = {

            "Low Value": 0,

            "Medium Value": 1,

            "High Value": 2

        }

        rfm["customer_segment"] = rfm[
            "customer_segment"
        ].map(self.segment_mapping)

        return rfm

    # ==========================================================
    # Logistic Regression Dataset
    # ==========================================================
    def get_customer_data(self):

        rfm = self.create_rfm_features()

        rfm = self.create_customer_segments(rfm)

        rfm = self.encode_customer_segment(rfm)

        X = rfm[
            [
                "total_amount",
                "frequency",
                "recency"
            ]
        ].astype(float)

        y = rfm["customer_segment"].astype(int)

        return X.values, y.values
