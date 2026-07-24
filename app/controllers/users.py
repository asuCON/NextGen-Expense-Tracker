from .. import SessionLocal
from app.models.user import User
from sqlalchemy.orm import Session
from typing import List, Optional
from werkzeug.security import generate_password_hash, check_password_hash

class UserController:
    """
    Handles CRUD operations for users.
    """

    def __init__(self, db: Optional[Session] = None):
        self.db: Session = db if db is not None else SessionLocal()
        self._owns_db = db is None

    def close(self):
        if self._owns_db and self.db:
            try:
                self.db.close()
            except Exception:
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def create_user(self, username: str, email: str, password: str, monthly_budget: float = 0.0) -> User:
        """
        Create a new user with hashed password.
        """
        password_hash = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=password_hash, monthly_budget=monthly_budget)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def list_users(self) -> List[User]:
        return self.db.query(User).all()

    def verify_password(self, email: str, password: str) -> bool:
        user = self.get_user_by_email(email)
        if not user:
            return False
        return check_password_hash(user.password_hash, password)
