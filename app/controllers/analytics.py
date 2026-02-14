from app.controllers.transactions import TransactionController
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

class AnalyticsController:
    """
    Provides analytics and visualization for user transactions.
    """

    def __init__(self):
        self.tc = TransactionController()

    def get_transaction_df(self, user_id: int):
        """
        Returns a pandas DataFrame of all transactions for the user.
        Ensures correct columns even if no transactions exist.
        """
        transactions = self.tc.list_transactions(user_id)

        if not transactions:  # Empty DataFrame for new users
            return pd.DataFrame(columns=["id", "type", "category", "amount", "description", "date", "user_id"])

        data = [
            {
                "id": t.id,
                "type": t.type,
                "category": t.category,
                "amount": t.amount,
                "description": t.description,
                "date": pd.to_datetime(t.date),  # Convert to datetime
                "user_id": t.user_id
            }
            for t in transactions
        ]
        df = pd.DataFrame(data)
        return df

    def plot_expense_vs_income(self, user_id: int):
        """
        Plot total income vs total expenses as a bar chart.
        """
        df = self.get_transaction_df(user_id)
        if df.empty:
            print("No transactions to plot.")
            return

        # Ensure 'type' column exists
        if 'type' not in df.columns or 'amount' not in df.columns:
            print("Transactions missing required columns.")
            return

        income = df[df['type'] == 'income']['amount'].sum()
        expense = df[df['type'] == 'expense']['amount'].sum()

        plt.figure(figsize=(6, 4))
        plt.bar(['Income', 'Expense'], [income, expense], color=['green', 'red'])
        plt.title('Income vs Expense')
        plt.ylabel('Amount ($)')
        plt.show()

    def plot_expense_by_category(self, user_id: int):
        """
        Plot expenses grouped by category as a pie chart.
        """
        df = self.get_transaction_df(user_id)
        expense_df = df[df['type'] == 'expense']

        if expense_df.empty:
            print("No expenses to plot.")
            return

        category_sums = expense_df.groupby('category')['amount'].sum()

        plt.figure(figsize=(7, 7))
        plt.pie(
            category_sums,
            labels=category_sums.index,
            autopct='%1.1f%%',
            startangle=140,
            shadow=True,
            explode=[0.05]*len(category_sums)
        )
        plt.title("Expense Distribution by Category")
        plt.show()

    def monthly_trend(self, user_id: int):
        """
        Plot monthly income vs expenses trend.
        """
        df = self.get_transaction_df(user_id)
        if df.empty:
            print("No transactions to analyze.")
            return

        # Ensure date is datetime
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'], errors='coerce')

        df['month'] = df['date'].dt.to_period('M')
        monthly = df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)

        if monthly.empty:
            print("No monthly data to plot.")
            return

        monthly.plot(kind='bar', figsize=(10, 5))
        plt.title('Monthly Income vs Expense Trend')
        plt.ylabel('Amount ($)')
        plt.xlabel('Month')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()