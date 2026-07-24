from app.controllers.transactions import TransactionController
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional

class RecurringTransactionController:
    """
    Automatically handles recurring transactions like monthly bills or income.
    """

    def __init__(self, db: Optional[Session] = None):
        self.tc = TransactionController(db=db)
        # For streamlit, persist recurring_transactions in session_state so they are not lost on rerun.
        # Fall back to a standard in-memory list if Streamlit is not available or outside session context.
        try:
            import streamlit as st
            if hasattr(st, "session_state"):
                if "recurring_transactions" not in st.session_state:
                    st.session_state.recurring_transactions = []
                self.recurring_transactions = st.session_state.recurring_transactions
            else:
                self.recurring_transactions = []
        except (ImportError, RuntimeError):
            self.recurring_transactions = []

    def close(self):
        if hasattr(self, "tc") and self.tc:
            self.tc.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

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
