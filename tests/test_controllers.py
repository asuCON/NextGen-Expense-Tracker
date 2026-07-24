import pytest
import os
import tempfile
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import Base
from app.controllers.users import UserController
from app.controllers.transactions import TransactionController
from app.controllers.analytics import AnalyticsController
from app.controllers.ai_insights import AIInsightsController
from app.controllers.recurring import RecurringTransactionController
from app.controllers.reports import ReportController

@pytest.fixture(scope="function")
def db_session():
    # In-memory SQLite for complete isolation and performance
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_user_controller(db_session):
    with UserController(db=db_session) as uc:
        # Create user
        user = uc.create_user("testuser", "test@example.com", "password123", 2500.0)
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.monthly_budget == 2500.0

        # Get user by ID and email
        assert uc.get_user_by_id(user.id).username == "testuser"
        assert uc.get_user_by_email("test@example.com").id == user.id
        assert uc.get_user_by_email("nonexistent@example.com") is None

        # Verify credentials
        assert uc.verify_password("test@example.com", "password123") is True
        assert uc.verify_password("test@example.com", "wrongpassword") is False
        assert uc.verify_password("nonexistent@example.com", "password123") is False

        # List all users
        users = uc.list_users()
        assert len(users) == 1
        assert users[0].username == "testuser"

def test_transaction_controller(db_session):
    with UserController(db=db_session) as uc, TransactionController(db=db_session) as tc:
        user = uc.create_user("tuser", "t@example.com", "pass")

        # Add transactions
        t1 = tc.add_transaction(user.id, "income", "Salary", 5000.0, "Monthly salary")
        t2 = tc.add_transaction(user.id, "expense", "Rent", 1200.0, "Apartment rent")

        assert t1.id is not None
        assert t1.type == "income"
        assert t1.category == "Salary"
        assert t1.amount == 5000.0

        # List transactions
        all_tx = tc.list_transactions(user.id)
        assert len(all_tx) == 2

        incomes = tc.list_transactions(user.id, t_type="income")
        assert len(incomes) == 1
        assert incomes[0].category == "Salary"

        expenses = tc.list_transactions(user.id, t_type="expense")
        assert len(expenses) == 1
        assert expenses[0].category == "Rent"

        # Update transaction
        updated = tc.update_transaction(t2.id, category="Housing", amount=1300.0)
        assert updated.category == "Housing"
        assert updated.amount == 1300.0

        # Delete transaction
        assert tc.delete_transaction(t1.id) is True
        assert len(tc.list_transactions(user.id)) == 1

def test_analytics_controller(db_session):
    with UserController(db=db_session) as uc, TransactionController(db=db_session) as tc, AnalyticsController(db=db_session) as ac:
        user = uc.create_user("a_user", "a@example.com", "pass")

        # Empty state
        df_empty = ac.get_transaction_df(user.id)
        assert df_empty.empty
        assert "category" in df_empty.columns

        # Verify plotting on empty database returns None without crashing
        assert ac.plot_expense_vs_income(user.id) is None
        assert ac.plot_expense_by_category(user.id) is None
        assert ac.monthly_trend(user.id) is None

        # Add data
        tc.add_transaction(user.id, "income", "Salary", 4000.0)
        tc.add_transaction(user.id, "expense", "Food", 150.0)
        tc.add_transaction(user.id, "expense", "Utilities", 100.0)

        df = ac.get_transaction_df(user.id)
        assert len(df) == 3

        # Generate plots (returns Figure object)
        fig1 = ac.plot_expense_vs_income(user.id)
        assert fig1 is not None

        fig2 = ac.plot_expense_by_category(user.id)
        assert fig2 is not None

        fig3 = ac.monthly_trend(user.id)
        assert fig3 is not None

def test_ai_insights_controller(db_session):
    with UserController(db=db_session) as uc, TransactionController(db=db_session) as tc, AIInsightsController(db=db_session) as ai:
        user = uc.create_user("ai_user", "ai@example.com", "pass", monthly_budget=2000.0)

        # Basic budget recommendations
        advice = ai.budget_recommendations(user.id, user.monthly_budget)
        assert "remaining" in advice

        # Add transactions to trigger warnings
        tc.add_transaction(user.id, "expense", "Shopping", 2500.0)
        advice_over = ai.budget_recommendations(user.id, user.monthly_budget)
        assert "over budget" in advice_over

        # Test anomalies
        # Add some small expenses to lower the mean category average
        tc.add_transaction(user.id, "expense", "Rent", 100.0)
        tc.add_transaction(user.id, "expense", "Food", 50.0)
        tc.add_transaction(user.id, "expense", "Shopping", 150.0)
        tc.add_transaction(user.id, "expense", "Huge Expense", 5000.0)
        anomalies = ai.detect_expense_anomalies(user.id)
        assert "Huge Expense" in anomalies

        # Test prediction (needs at least some historical data)
        forecast_empty = ai.forecast_next_month_expense(user.id)
        assert forecast_empty >= 0.0

def test_recurring_transaction_controller(db_session):
    with UserController(db=db_session) as uc, RecurringTransactionController(db=db_session) as rc:
        user = uc.create_user("r_user", "r@example.com", "pass")

        # Add recurring rule
        rc.add_recurring(user.id, "expense", "Subscription", 15.0, "Netflix", interval_days=30)
        assert len(rc.recurring_transactions) == 1
        rule = rc.recurring_transactions[0]
        assert rule["category"] == "Subscription"
        assert rule["amount"] == 15.0

        # Process when interval has not passed (should not create transaction)
        rc.process_recurring()
        assert len(rc.tc.list_transactions(user.id)) == 0

        # Force simulate interval passing (set last_added to 31 days ago)
        rule["last_added"] = datetime.now() - timedelta(days=31)
        rc.process_recurring()

        txs = rc.tc.list_transactions(user.id)
        assert len(txs) == 1
        assert txs[0].category == "Subscription"
        assert txs[0].amount == 15.0

def test_report_controller(db_session):
    with UserController(db=db_session) as uc, TransactionController(db=db_session) as tc, ReportController(db=db_session) as rep:
        user = uc.create_user("rep_user", "rep@example.com", "pass")

        # Empty export returns None
        assert rep.export_csv(user.id) is None
        assert rep.export_excel(user.id) is None

        # Add data
        tc.add_transaction(user.id, "income", "Salary", 3000.0)

        # Export
        with tempfile.TemporaryDirectory() as tmpdir:
            # Overwrite directory path
            rep.report_dir = tmpdir

            csv_path = rep.export_csv(user.id, "test.csv")
            assert csv_path is not None
            assert os.path.exists(csv_path)

            xlsx_path = rep.export_excel(user.id, "test.xlsx")
            assert xlsx_path is not None
            assert os.path.exists(xlsx_path)
