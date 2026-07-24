import streamlit as st
import os
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

# --- Session State Management ---
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Check login status
user_id = st.session_state.user_id
user = None
if user_id:
    user = uc.get_user_by_id(user_id)

if user:
    # User is logged in, show the Dashboard
    st.sidebar.header(f"Logged in as: {user.username}")
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.rerun()

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
        if not category.strip():
            st.error("Please provide a category.")
        else:
            tc.add_transaction(user.id, t_type, category, amount, description)
            st.success(f"{t_type.capitalize()} added successfully!")
            st.rerun()

    # --- Analytics Charts ---
    st.subheader("📈 Analytics")
    st.markdown("### Income vs Expense")
    fig1 = ac.plot_expense_vs_income(user.id)
    if fig1 is not None:
        st.pyplot(fig1)

    st.markdown("### Expense by Category")
    fig2 = ac.plot_expense_by_category(user.id)
    if fig2 is not None:
        st.pyplot(fig2)

    st.markdown("### Monthly Trend")
    fig3 = ac.monthly_trend(user.id)
    if fig3 is not None:
        st.pyplot(fig3)

    # --- AI Insights ---
    st.subheader("🤖 AI Predictions & Insights")
    forecast = ai.forecast_next_month_expense(user.id)
    anomalies = ai.detect_expense_anomalies(user.id)
    advice = ai.budget_recommendations(user.id, user.monthly_budget)
    st.metric("Predicted Next Month Expense", f"${forecast}" if forecast is not None else "$0.00")
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
        if not category_r.strip():
            st.error("Please provide a category.")
        else:
            recurring_ctrl.add_recurring(user.id, t_type_r, category_r, amount_r, description_r, interval_r)
            st.success("Recurring transaction added successfully!")
            st.rerun()

    # --- Export Reports ---
    st.subheader("📄 Export Reports")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export CSV"):
            path = report_ctrl.export_csv(user.id)
            if path:
                st.success(f"CSV exported at {path}")
                with open(path, "rb") as f:
                    st.download_button("Download CSV", f, file_name=os.path.basename(path), key="dl_csv")
            else:
                st.warning("No transactions to export.")
    with col2:
        if st.button("Export Excel"):
            path = report_ctrl.export_excel(user.id)
            if path:
                st.success(f"Excel exported at {path}")
                with open(path, "rb") as f:
                    st.download_button("Download Excel", f, file_name=os.path.basename(path), key="dl_xlsx")
            else:
                st.warning("No transactions to export.")

else:
    # User is not logged in, show User Access: Login or Create Account
    st.sidebar.header("User Access")
    action = st.sidebar.selectbox("Action", ["Login", "Create Account"])

    if action == "Create Account":
        username = st.sidebar.text_input("Username")
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type="password")
        monthly_budget = st.sidebar.number_input("Monthly Budget", min_value=0.0, value=3000.0)
        if st.sidebar.button("Sign Up"):
            if not username.strip() or not email.strip() or not password.strip():
                st.sidebar.error("All fields are required!")
            elif uc.get_user_by_email(email):
                st.sidebar.error("Email already exists!")
            else:
                user = uc.create_user(username, email, password, monthly_budget)
                st.session_state.user_id = user.id
                st.rerun()

    else:  # Login
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if uc.verify_password(email, password):
                user = uc.get_user_by_email(email)
                st.session_state.user_id = user.id
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials.")
