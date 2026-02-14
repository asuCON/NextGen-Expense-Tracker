from .. import SessionLocal
from app.controllers.analytics import AnalyticsController
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

class AIInsightsController:
    """
    Provides AI-powered insights:
    - Expense prediction
    - Anomaly detection
    - Budget recommendations
    """

    def __init__(self):
        self.ac = AnalyticsController()

    def forecast_next_month_expense(self, user_id: int):
        """
        Predict next month's total expense based on historical monthly data.
        Uses simple linear regression on past months.
        """
        df = self.ac.get_transaction_df(user_id)
        df = df[df['type'] == 'expense']
        if df.empty:
            print("No expenses to forecast.")
            return None

        # Group by month
        df['month'] = df['date'].dt.to_period('M')
        monthly_expense = df.groupby('month')['amount'].sum().reset_index()

        # Prepare data for linear regression
        X = np.arange(len(monthly_expense)).reshape(-1, 1)
        y = monthly_expense['amount'].values

        model = LinearRegression()
        model.fit(X, y)

        # Predict next month
        next_month_index = np.array([[len(monthly_expense)]])
        prediction = model.predict(next_month_index)[0]

        return round(prediction, 2)

    def detect_expense_anomalies(self, user_id: int):
        """
        Detect categories with unusually high spending compared to average.
        Returns a dict {category: amount}
        """
        df = self.ac.get_transaction_df(user_id)
        df = df[df['type'] == 'expense']
        if df.empty:
            print("No expenses to analyze for anomalies.")
            return {}

        category_sum = df.groupby('category')['amount'].sum()
        mean = category_sum.mean()
        threshold = mean * 1.5  # anomaly threshold = 1.5x average
        anomalies = category_sum[category_sum > threshold].to_dict()

        return anomalies

    def budget_recommendations(self, user_id: int, monthly_budget: float):
        """
        Provide simple recommendations based on current spending vs budget.
        """
        df = self.ac.get_transaction_df(user_id)
        total_expense = df[df['type'] == 'expense']['amount'].sum()
        remaining_budget = monthly_budget - total_expense

        if remaining_budget < 0:
            advice = f"You are over budget by ${abs(remaining_budget):.2f}! Consider reducing expenses."
        else:
            advice = f"You have ${remaining_budget:.2f} remaining in your budget. Keep it up!"

        return advice