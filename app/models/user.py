from sqlalchemy import Column, Integer, String, Float
from app import Base

class User(Base):
    """
    Represents a user in the NextGen Expense Platform.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)  # store hashed password
    monthly_budget = Column(Float, default=0.0)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"