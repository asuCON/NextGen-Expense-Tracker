import streamlit as st
from app.controllers.users import UserController
from app.controllers.transactions import TransactionController
from app.controllers.analytics import AnalyticsController
from app.controllers.ai_insights import AIInsightsController
from app.controllers.reports import ReportController
from app.controllers.recurring import RecurringTransactionController

# --- Initialize Controllers ---
uc = UserController()
tc = TransactionController()
ac = AnalyticsController()
ai = AIInsightsController()
report_ctrl = ReportController()
recurring_ctrl = RecurringTransactionController()

# --- Streamlit Page Setup ---
st.set_page_config(page_title="NextGen Expense Platform", layout="wide")
st.title("💰 NextGen Expense Management Dashboard")

# --- User Login / Signup ---
st.sidebar.header("User Access")
action = st.sidebar.selectbox("Action", ["Login", "Create Account"])

if action == "Create Account":
    username = st.sidebar.text_input("Username")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    monthly_budget = st.sidebar.number_input("Monthly Budget", min_value=0.0, value=3000.0)
    if st.sidebar.button("Sign Up"):
        user = uc.create_user(username, email, password, monthly_budget)
        st.success(f"Account created for {user.username}!")

else:  # Login
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if uc.verify_password(email, password):
            user = uc.get_user_by_email(email)
            st.success(f"Welcome back, {user.username}!")

            # --- Dashboard: Recurring Transactions Processing ---
            recurring_ctrl.process_recurring()

            # --- Transactions Overview ---
            st.subheader("📊 Transactions Overview")
            transactions = tc.list_transactions(user.id)
            st.write(transactions)

            # --- Add New Transaction ---
            st.subheader("➕ Add New Transaction")
            t_type = st.selectbox("Type", ["income", "expense"])
            category = st.text_input("Category")
            amount = st.number_input("Amount", min_value=0.0)
            description = st.text_input("Description")
            if st.button("Add Transaction"):
                tc.add_transaction(user.id, t_type, category, amount, description)
                st.success(f"{t_type.capitalize()} added successfully!")

            # --- Analytics Charts ---
            st.subheader("📈 Analytics")
            st.markdown("### Income vs Expense")
            ac.plot_expense_vs_income(user.id)

            st.markdown("### Expense by Category")
            ac.plot_expense_by_category(user.id)

            st.markdown("### Monthly Trend")
            ac.monthly_trend(user.id)

            # --- AI Insights ---
            st.subheader("🤖 AI Predictions & Insights")
            forecast = ai.forecast_next_month_expense(user.id)
            anomalies = ai.detect_expense_anomalies(user.id)
            advice = ai.budget_recommendations(user.id, user.monthly_budget)
            st.metric("Predicted Next Month Expense", f"${forecast}")
            st.write("Anomalies Detected:", anomalies if anomalies else "None")
            st.info(advice)

            # --- Recurring Transactions ---
            st.subheader("🔁 Add Recurring Transaction")
            t_type_r = st.selectbox("Type", ["income", "expense"], key="r_type")
            category_r = st.text_input("Category", key="r_category")
            amount_r = st.number_input("Amount", min_value=0.0, key="r_amount")
            interval_r = st.number_input("Interval (days)", min_value=1, value=30, key="r_interval")
            description_r = st.text_input("Description", key="r_desc")
            if st.button("Add Recurring Transaction"):
                recurring_ctrl.add_recurring(user.id, t_type_r, category_r, amount_r, description_r, interval_r)
                st.success("Recurring transaction added successfully!")

            # --- Export Reports ---
            st.subheader("📄 Export Reports")
            if st.button("Export CSV"):
                path = report_ctrl.export_csv(user.id)
                st.success(f"CSV exported at {path}")

            if st.button("Export Excel"):
                path = report_ctrl.export_excel(user.id)
                st.success(f"Excel exported at {path}")

        else:
            st.error("Invalid credentials.")