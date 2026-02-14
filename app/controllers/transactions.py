from .. import SessionLocal
from app.models.transaction import Transaction
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

class TransactionController:
    """
    Handles CRUD operations for transactions.
    """

    def __init__(self):
        self.db: Session = SessionLocal()

    def add_transaction(
        self,
        user_id: int,
        t_type: str,
        category: str,
        amount: float,
        description: str = ""
    ) -> Transaction:
        """
        Add a new income or expense transaction for a user.
        """
        if t_type not in ("income", "expense"):
            raise ValueError("Transaction type must be 'income' or 'expense'")

        transaction = Transaction(
            user_id=user_id,
            type=t_type,
            category=category,
            amount=amount,
            description=description
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()

    def list_transactions(self, user_id: int, t_type: Optional[str] = None) -> List[Transaction]:
        """
        List all transactions for a user. Can filter by type ('income' or 'expense').
        """
        query = self.db.query(Transaction).filter(Transaction.user_id == user_id)
        if t_type in ("income", "expense"):
            query = query.filter(Transaction.type == t_type)
        return query.order_by(Transaction.date.desc()).all()

    def delete_transaction(self, transaction_id: int) -> bool:
        transaction = self.get_transaction_by_id(transaction_id)
        if not transaction:
            return False
        self.db.delete(transaction)
        self.db.commit()
        return True

    def update_transaction(
        self,
        transaction_id: int,
        category: Optional[str] = None,
        amount: Optional[float] = None,
        description: Optional[str] = None,
        t_type: Optional[str] = None
    ) -> Optional[Transaction]:
        transaction = self.get_transaction_by_id(transaction_id)
        if not transaction:
            return None

        if t_type in ("income", "expense"):
            transaction.type = t_type
        if category:
            transaction.category = category
        if amount is not None:
            transaction.amount = amount
        if description is not None:
            transaction.description = description

        self.db.commit()
        self.db.refresh(transaction)
        return transaction