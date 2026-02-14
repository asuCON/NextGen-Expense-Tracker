from app.controllers.transactions import TransactionController
from datetime import datetime, timedelta

class RecurringTransactionController:
    """
    Automatically handles recurring transactions like monthly bills or income.
    """

    def __init__(self):
        self.tc = TransactionController()
        # Example storage for recurring rules (could be a DB table in future)
        self.recurring_transactions = []

    def add_recurring(self, user_id: int, t_type: str, category: str, amount: float, description: str, interval_days: int = 30):
        """
        Adds a recurring transaction rule
        """
        rule = {
            "user_id": user_id,
            "type": t_type,
            "category": category,
            "amount": amount,
            "description": description,
            "interval_days": interval_days,
            "last_added": datetime.now()
        }
        self.recurring_transactions.append(rule)

    def process_recurring(self):
        """
        Checks all recurring rules and adds transactions if interval passed
        """
        now = datetime.now()
        for rule in self.recurring_transactions:
            delta = now - rule['last_added']
            if delta.days >= rule['interval_days']:
                # Add transaction
                self.tc.add_transaction(
                    rule['user_id'],
                    rule['type'],
                    rule['category'],
                    rule['amount'],
                    rule['description']
                )
                rule['last_added'] = now  # Reset last added timestamp