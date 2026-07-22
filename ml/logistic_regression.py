import numpy as np
import os


class LogisticRegression:

    def __init__(self, learning_rate=0.01, epochs=3000, tolerance=1e-6):

        self.learning_rate = learning_rate
        self.epochs = epochs
        self.tolerance = tolerance

        # Model Parameters
        self.weights = None
        self.bias = None

        # Feature Scaling Parameters
        self.mean = None
        self.std = None

        # Class Labels
        self.classes = None

        # Store Cost History
        self.cost_history = {}

    # ==========================================================
    # Step 1 : Feature Scaling
    # x_scaled = (x - μ) / σ
    # ==========================================================
    def normalize(self, X):

        self.mean = np.mean(X, axis=0)
        self.std = np.std(X, axis=0)

        self.std[self.std == 0] = 1

        return (X - self.mean) / self.std

    # ==========================================================
    # Step 4 : Sigmoid Function
    # σ(z) = 1 / (1 + e^-z)
    # ==========================================================
    def sigmoid(self, z):

        z = np.clip(z, -500, 500)

        return 1 / (1 + np.exp(-z))

    # ==========================================================
    # Step 3 : Weighted Sum
    # z = w1x1 + w2x2 + w3x3 + b
    # ==========================================================
    def weighted_sum(self, X, w, b):

        return np.dot(X, w) + b

    # ==========================================================
    # Step 5 : Binary Cross Entropy Cost
    # ==========================================================
    def compute_cost(self, y_true, probability):

        m = len(y_true)

        epsilon = 1e-10

        probability = np.clip(probability, epsilon, 1 - epsilon)

        cost = -(1 / m) * np.sum(
            y_true * np.log(probability) +
            (1 - y_true) * np.log(1 - probability)
        )

        return cost

    # ==========================================================
    # Step 6 : Train using Gradient Descent
    # ==========================================================
    def fit(self, X, y):

        # Step 1
        X = self.normalize(X)

        m, n = X.shape

        self.classes = np.unique(y)

        self.weights = np.zeros((len(self.classes), n))
        self.bias = np.zeros(len(self.classes))

        # Train One-vs-Rest Classifiers
        for class_index, current_class in enumerate(self.classes):

            # =============================================
            # Step 2 : Create Binary Labels
            # =============================================
            y_binary = (y == current_class).astype(float)

            w = np.zeros(n)
            b = 0

            previous_cost = float("inf")

            self.cost_history[current_class] = []

            for epoch in range(self.epochs):

                # =============================================
                # Step 3 : Weighted Sum
                # =============================================
                z = self.weighted_sum(X, w, b)

                # =============================================
                # Step 4 : Sigmoid Probability
                # =============================================
                probability = self.sigmoid(z)

                # =============================================
                # Step 5 : Binary Cross Entropy Cost
                # =============================================
                cost = self.compute_cost(y_binary, probability)

                self.cost_history[current_class].append(cost)

                # =============================================
                # Step 6 : Compute Gradients
                # =============================================
                dw = (1 / m) * np.dot(X.T, (probability - y_binary))

                db = (1 / m) * np.sum(probability - y_binary)

                # Update Parameters
                w -= self.learning_rate * dw

                b -= self.learning_rate * db

                # Convergence Check
                if abs(previous_cost - cost) < self.tolerance:
                    break

                previous_cost = cost

            self.weights[class_index] = w
            self.bias[class_index] = b

    # ==========================================================
    # Step 7 : Predict Probabilities
    # ==========================================================
    def predict_probabilities(self, X):

        X = (X - self.mean) / self.std

        probabilities = []

        for i in range(len(self.classes)):

            z = self.weighted_sum(
                X,
                self.weights[i],
                self.bias[i]
            )

            probabilities.append(self.sigmoid(z))

        return np.array(probabilities)

    # ==========================================================
    # Step 8 : Final Classification
    # Class = argmax(PHigh, PMedium, PLow)
    # ==========================================================
    def predict(self, X):

        probabilities = self.predict_probabilities(X)

        prediction = np.argmax(probabilities, axis=0)

        return prediction

    # ==========================================================
    # Accuracy
    # ==========================================================
    def score(self, X, y):

        prediction = self.predict(X)

        return np.mean(prediction == y)

    # ==========================================================
    # Save Model
    # ==========================================================
    def save(self):

        os.makedirs("trained_models", exist_ok=True)

        np.save(
            "trained_models/logistic_weights.npy",
            self.weights
        )

        np.save(
            "trained_models/logistic_bias.npy",
            self.bias
        )

        np.save(
            "trained_models/logistic_mean.npy",
            self.mean
        )

        np.save(
            "trained_models/logistic_std.npy",
            self.std
        )

    # ==========================================================
    # Load Model
    # ==========================================================
    def load(self):

        self.weights = np.load(
            "trained_models/logistic_weights.npy"
        )

        self.bias = np.load(
            "trained_models/logistic_bias.npy"
        )

        self.mean = np.load(
            "trained_models/logistic_mean.npy"
        )

        self.std = np.load(
            "trained_models/logistic_std.npy"
        )

        self.classes = np.arange(len(self.weights))
