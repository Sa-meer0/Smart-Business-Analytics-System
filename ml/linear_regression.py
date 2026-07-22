import numpy as np


class LinearRegression:

    def __init__(self, learning_rate=0.001, epochs=1000, tolerance=1e-6):

        self.learning_rate = learning_rate
        self.epochs = epochs
        self.tolerance = tolerance

        self.weights = None
        self.bias = 0

        self.mean = None
        self.std = None

        self.cost_history = []

    # ==========================================================
    # Normalize Features
    # ==========================================================
    def normalize(self, X):

        self.mean = np.mean(X, axis=0)
        self.std = np.std(X, axis=0)

        self.std[self.std == 0] = 1

        return (X - self.mean) / self.std

    # ==========================================================
    # Initialize Parameters
    # ==========================================================
    def initialize_parameters(self, n_features):

        self.weights = np.zeros(n_features)
        self.bias = 0

    # ==========================================================
    # Hypothesis
    # ==========================================================
    def hypothesis(self, X):

        return np.dot(X, self.weights) + self.bias

    # ==========================================================
    # Cost
    # ==========================================================
    def compute_cost(self, y_true, y_pred):

        m = len(y_true)

        return (1 / (2 * m)) * np.sum((y_pred - y_true) ** 2)

    # ==========================================================
    # Train
    # ==========================================================
    def fit(self, X, y):

        if hasattr(X, "values"):
            X = X.values

        if hasattr(y, "values"):
            y = y.values

        X = X.astype(float)
        y = y.astype(float)

        X = self.normalize(X)

        m, n = X.shape

        self.initialize_parameters(n)

        previous_cost = float("inf")

        for epoch in range(self.epochs):

            prediction = self.hypothesis(X)

            cost = self.compute_cost(y, prediction)

            self.cost_history.append(cost)

            dw = (1 / m) * np.dot(X.T, (prediction - y))
            db = (1 / m) * np.sum(prediction - y)

            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db

            if abs(previous_cost - cost) < self.tolerance:
                print(f"Training converged at Epoch {epoch}")
                break

            previous_cost = cost

    # ==========================================================
    # Predict
    # ==========================================================
    def predict(self, X):

        print("\n========== PREDICT DEBUG ==========")

        print("Input:")
        print(X)

        print("\nMean:")
        print(self.mean)

        print("\nStd:")
        print(self.std)

        X_scaled = (X - self.mean) / self.std

        print("\nScaled Input:")
        print(X_scaled)

        y_pred = self.hypothesis(X_scaled)

        print("\nPrediction Before Clipping:")
        print(y_pred)

        print("===================================\n")

        return np.maximum(y_pred, 0)

    # ==========================================================
    # Revenue
    # ==========================================================
    def predict_revenue(self, X, unit_price):

        quantity = self.predict(X)

        return quantity * unit_price

    # ==========================================================
    # R² Score
    # ==========================================================
    def score(self, X, y):

        if hasattr(X, "values"):
            X = X.values

        if hasattr(y, "values"):
            y = y.values

        prediction = self.predict(X)

        ss_total = np.sum((y - np.mean(y)) ** 2)
        ss_residual = np.sum((y - prediction) ** 2)

        return 1 - (ss_residual / ss_total)

    # ==========================================================
    # Save Model
    # ==========================================================
    def save(self, feature_names=None):

        np.save(
            "trained_models/linear_weights.npy",
            self.weights
        )

        np.save(
            "trained_models/linear_bias.npy",
            np.array([self.bias])
        )

        np.save(
            "trained_models/linear_mean.npy",
            self.mean
        )

        np.save(
            "trained_models/linear_std.npy",
            self.std
        )

        if feature_names is not None:

            np.save(
                "trained_models/linear_features.npy",
                np.array(feature_names, dtype=object)
            )

    # ==========================================================
    # Load Model
    # ==========================================================
    def load(self):

        self.weights = np.load(
            "trained_models/linear_weights.npy"
        )

        self.bias = np.load(
            "trained_models/linear_bias.npy"
        )[0]

        self.mean = np.load(
            "trained_models/linear_mean.npy"
        )

        self.std = np.load(
            "trained_models/linear_std.npy"
        )

    # ==========================================================
    # Load Feature Names
    # ==========================================================
    def load_feature_names(self):

        return np.load(
            "trained_models/linear_features.npy",
            allow_pickle=True
        ).tolist()
