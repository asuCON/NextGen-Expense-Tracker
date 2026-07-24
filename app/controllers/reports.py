import pandas as pd
from app.controllers.transactions import TransactionController
from datetime import datetime
import os
from sqlalchemy.orm import Session
from typing import Optional

class ReportController:
    """
    Export transactions and analytics reports as CSV, Excel, or PDF (basic).
    """

    def __init__(self, db: Optional[Session] = None):
        self.tc = TransactionController(db=db)
        # Folder to save reports
        self.report_dir = "reports"
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

    def close(self):
        if hasattr(self, "tc") and self.tc:
            self.tc.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def export_csv(self, user_id: int, filename: str = None):
        transactions = self.tc.list_transactions(user_id)
        if not transactions:
            print("No transactions to export.")
            return None

        df = pd.DataFrame([
            {
                "id": t.id,
                "type": t.type,
                "category": t.category,
                "amount": t.amount,
                "description": t.description,
                "date": t.date
            }
            for t in transactions
        ])

        if not filename:
            filename = f"report_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(self.report_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"CSV report saved at: {filepath}")
        return filepath

    def export_excel(self, user_id: int, filename: str = None):
        transactions = self.tc.list_transactions(user_id)
        if not transactions:
            print("No transactions to export.")
            return None

        df = pd.DataFrame([
            {
                "id": t.id,
                "type": t.type,
                "category": t.category,
                "amount": t.amount,
                "description": t.description,
                "date": t.date
            }
            for t in transactions
        ])

        if not filename:
            filename = f"report_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(self.report_dir, filename)
        df.to_excel(filepath, index=False)
        print(f"Excel report saved at: {filepath}")
        return filepath
