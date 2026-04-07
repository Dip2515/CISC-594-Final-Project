import streamlit as st
import pandas as pd
import io
from datetime import datetime, date
from modules import database as db
from modules import analytics

# ─── PAGE CONFIG ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── INIT DB ────────────────────────────────────────────────────────
db.init_db()

CATEGORIES = [
    "Food & Dining", "Transportation", "Shopping", "Entertainment",
    "Healthcare", "Housing", "Utilities", "Education", "Travel",
    "Personal Care", "Business", "Other"
]

CURRENCY_SYMBOLS = {"USD": "$", "EUR": "€", "GBP": "£", "INR": "₹", "CAD": "CA$"}

# ─── SESSION STATE ───────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = "default"
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# ─── AUTH ────────────────────────────────────────────────────────────
def login_page():
    st.title("💰 Smart Expense Tracker")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            if db.authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password.")
        st.caption("Default account: username `default` / password `default`")

    with tab2:
        st.subheader("Create Account")
        new_user = st.text_input("Username", key="reg_user")
        new_pass = st.text_input("Password", type="password", key="reg_pass")
        currency = st.selectbox("Preferred Currency", list(CURRENCY_SYMBOLS.keys()), key="reg_cur")
        if st.button("Register", use_container_width=True):
            if not new_user or not new_pass:
                st.error("Username and password are required.")
            elif db.register_user(new_user, new_pass, currency):
                st.success("Account created! Please log in.")
            else:
                st.error("Username already taken.")


# ─── HELPER ──────────────────────────────────────────────────────────
def get_symbol():
    currency = db.get_currency(st.session_state.username)
    return CURRENCY_SYMBOLS.get(currency, "$")


def current_month():
    return datetime.now().strftime("%Y-%m")


# ─── SIDEBAR ────────────────────────────────────────────────────────
def sidebar():
    st.sidebar.title("💰 Expense Tracker")
    st.sidebar.caption(f"Logged in as **{st.session_state.username}**")
    st.sidebar.divider()
    pages = ["Dashboard", "Add Expense", "Expense History",
             "Budgets", "Analytics", "Import / Export", "Settings"]
    choice = st.sidebar.radio("Navigate", pages)
    st.sidebar.divider()
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = "default"
        st.rerun()
    return choice


# ─── DASHBOARD ───────────────────────────────────────────────────────
def page_dashboard(user, symbol):
    st.title("Dashboard")
    expenses = db.get_expenses(user)
    budgets = db.get_budgets(user)
    mon = current_month()

    if expenses.empty:
        st.info("No expenses recorded yet. Go to **Add Expense** to get started.")
        return

    monthly = expenses[expenses["date"].str.startswith(mon)]
    total_month = monthly["amount"].sum()
    total_all = expenses["amount"].sum()
    num_tx = len(monthly)
    avg_tx = monthly["amount"].mean() if not monthly.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("This Month", f"{symbol}{total_month:,.2f}")
    c2.metric("All Time Total", f"{symbol}{total_all:,.2f}")
    c3.metric("Transactions (Month)", num_tx)
    c4.metric("Avg Transaction", f"{symbol}{avg_tx:,.2f}")

    st.divider()

    # Budget alerts
    if not budgets.empty:
        st.subheader("Budget Status")
        for _, b in budgets.iterrows():
            spent = monthly[monthly["category"] == b["category"]]["amount"].sum()
            limit = b["monthly_limit"]
            pct = (spent / limit * 100) if limit > 0 else 0
            label = f"{b['category']}: {symbol}{spent:,.2f} / {symbol}{limit:,.2f}"
            if pct >= 100:
                st.error(f"🚨 OVER BUDGET — {label}")
            elif pct >= 80:
                st.warning(f"⚠️ Near limit ({pct:.0f}%) — {label}")
            else:
                st.success(f"✅ {label} ({pct:.0f}%)")

        st.divider()

    col1, col2 = st.columns(2)
    with col1:
        fig = analytics.monthly_trend_chart(expenses, symbol)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = analytics.category_pie_chart(expenses, symbol)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent Expenses")
    show = expenses.head(10)[["date", "amount", "category", "description"]].copy()
    show["amount"] = show["amount"].apply(lambda x: f"{symbol}{x:,.2f}")
    st.dataframe(show, use_container_width=True, hide_index=True)


# ─── ADD EXPENSE ─────────────────────────────────────────────────────
def page_add_expense(user, symbol):
    st.title("Add Expense")
    with st.form("add_expense_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            exp_date = st.date_input("Date", value=date.today())
            amount = st.number_input(f"Amount ({symbol})", min_value=0.01,
                                     format="%.2f", step=0.01)
        with c2:
            category = st.selectbox("Category", CATEGORIES)
            description = st.text_input("Description (optional)")

        submitted = st.form_submit_button("Add Expense", use_container_width=True)
        if submitted:
            if amount <= 0:
                st.error("Amount must be greater than zero.")
            else:
                db.add_expense(str(exp_date), amount, category, description, user)
                st.success(f"Expense of {symbol}{amount:.2f} added under **{category}**!")

    # Quick stats hint
    expenses = db.get_expenses(user)
    if not expenses.empty:
        mon = current_month()
        monthly = expenses[expenses["date"].str.startswith(mon)]
        if not monthly.empty:
            top_cat = monthly.groupby("category")["amount"].sum().idxmax()
            st.info(f"Top spending category this month: **{top_cat}**")


# ─── EXPENSE HISTORY ─────────────────────────────────────────────────
def page_history(user, symbol):
    st.title("Expense History")
    expenses = db.get_expenses(user)

    if expenses.empty:
        st.info("No expenses recorded yet.")
        return

    # Filters
    with st.expander("Filters", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            search = st.text_input("Search description")
        with c2:
            cats = ["All"] + CATEGORIES
            filter_cat = st.selectbox("Category", cats)
        with c3:
            months = ["All"] + sorted(
                expenses["date"].str[:7].unique().tolist(), reverse=True
            )
            filter_month = st.selectbox("Month", months)

    df = expenses.copy()
    if search:
        df = df[df["description"].str.contains(search, case=False, na=False)]
    if filter_cat != "All":
        df = df[df["category"] == filter_cat]
    if filter_month != "All":
        df = df[df["date"].str.startswith(filter_month)]

    st.caption(f"Showing {len(df)} of {len(expenses)} expenses | "
               f"Total: {symbol}{df['amount'].sum():,.2f}")

    if df.empty:
        st.warning("No expenses match the filters.")
        return

    # Display + edit/delete
    for _, row in df.head(100).iterrows():
        with st.expander(
            f"{row['date']}  |  {symbol}{row['amount']:.2f}  |  "
            f"{row['category']}  —  {row['description'] or '(no description)'}"
        ):
            c1, c2 = st.columns(2)
            with c1:
                new_date = st.date_input("Date", value=pd.to_datetime(row["date"]).date(),
                                         key=f"d_{row['id']}")
                new_amt = st.number_input(f"Amount ({symbol})", value=float(row["amount"]),
                                          min_value=0.01, format="%.2f", key=f"a_{row['id']}")
            with c2:
                new_cat = st.selectbox("Category", CATEGORIES,
                                       index=CATEGORIES.index(row["category"])
                                       if row["category"] in CATEGORIES else 0,
                                       key=f"c_{row['id']}")
                new_desc = st.text_input("Description", value=row["description"] or "",
                                         key=f"desc_{row['id']}")
            bc1, bc2 = st.columns(2)
            if bc1.button("Save", key=f"save_{row['id']}", use_container_width=True):
                db.update_expense(row["id"], str(new_date), new_amt, new_cat, new_desc)
                st.success("Updated!")
                st.rerun()
            if bc2.button("Delete", key=f"del_{row['id']}", use_container_width=True,
                          type="secondary"):
                db.delete_expense(row["id"])
                st.warning("Deleted.")
                st.rerun()


# ─── BUDGETS ─────────────────────────────────────────────────────────
def page_budgets(user, symbol):
    st.title("Budgets")
    budgets = db.get_budgets(user)
    expenses = db.get_expenses(user)
    mon = current_month()
    monthly = expenses[expenses["date"].str.startswith(mon)] if not expenses.empty else pd.DataFrame()

    # Set / update budget
    st.subheader("Set Monthly Budget")
    with st.form("budget_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            cat = st.selectbox("Category", CATEGORIES)
        with c2:
            limit = st.number_input(f"Monthly Limit ({symbol})", min_value=1.0,
                                    format="%.2f", step=10.0)
        if st.form_submit_button("Save Budget", use_container_width=True):
            db.set_budget(cat, limit, user)
            st.success(f"Budget set: {symbol}{limit:.2f} / month for {cat}")
            st.rerun()

    # Show budgets
    if budgets.empty:
        st.info("No budgets set yet.")
        return

    st.subheader("Current Budgets")
    for _, b in budgets.iterrows():
        spent = monthly[monthly["category"] == b["category"]]["amount"].sum() \
            if not monthly.empty else 0
        limit = b["monthly_limit"]
        pct = min(spent / limit, 1.0) if limit > 0 else 0
        c1, c2, c3 = st.columns([4, 2, 1])
        with c1:
            st.progress(pct, text=f"{b['category']}: {symbol}{spent:.2f} / {symbol}{limit:.2f}")
        with c2:
            remaining = limit - spent
            if remaining < 0:
                st.error(f"Over by {symbol}{abs(remaining):.2f}")
            else:
                st.success(f"{symbol}{remaining:.2f} left")
        with c3:
            if st.button("Remove", key=f"delbud_{b['id']}"):
                db.delete_budget(b["id"])
                st.rerun()

    st.divider()
    fig = analytics.budget_comparison_chart(expenses, budgets, mon, symbol)
    if fig:
        st.plotly_chart(fig, use_container_width=True)


# ─── ANALYTICS ────────────────────────────────────────────────────────
def page_analytics(user, symbol):
    st.title("Analytics")
    expenses = db.get_expenses(user)

    if expenses.empty:
        st.info("No expense data to analyze yet.")
        return

    # Month filter
    months = sorted(expenses["date"].str[:7].unique().tolist(), reverse=True)
    selected_month = st.selectbox("Filter by month (for summaries)", ["All"] + months)

    if selected_month == "All":
        df = expenses
    else:
        df = expenses[expenses["date"].str.startswith(selected_month)]

    if df.empty:
        st.warning("No data for this month.")
        return

    # Summary table
    st.subheader("Category Summary")
    summary = df.groupby("category")["amount"].agg(["sum", "count", "mean"]).reset_index()
    summary.columns = ["Category", "Total", "# Transactions", "Average"]
    summary["Total"] = summary["Total"].apply(lambda x: f"{symbol}{x:,.2f}")
    summary["Average"] = summary["Average"].apply(lambda x: f"{symbol}{x:,.2f}")
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["Monthly Trend", "By Category", "Daily", "Heatmap"])

    with tab1:
        fig = analytics.monthly_trend_chart(expenses, symbol)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        fig2 = analytics.yearly_summary_chart(expenses, symbol)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            fig = analytics.category_pie_chart(df, symbol)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = analytics.category_bar_chart(df, symbol)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

    with tab3:
        fig = analytics.daily_spending_chart(df, symbol)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        fig = analytics.spending_heatmap(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    # Monthly report
    st.divider()
    st.subheader("Monthly Summary Report")
    expenses_copy = expenses.copy()
    expenses_copy["month"] = expenses_copy["date"].str[:7]
    monthly_report = (
        expenses_copy.groupby(["month", "category"])["amount"]
        .sum().reset_index()
        .pivot(index="month", columns="category", values="amount")
        .fillna(0)
    )
    monthly_report["TOTAL"] = monthly_report.sum(axis=1)
    st.dataframe(
        monthly_report.style.format(lambda x: f"{symbol}{x:,.2f}"),
        use_container_width=True
    )


# ─── IMPORT / EXPORT ──────────────────────────────────────────────────
def page_import_export(user, symbol):
    st.title("Import / Export")
    expenses = db.get_expenses(user)

    st.subheader("Export Expenses")
    if not expenses.empty:
        csv = expenses[["date", "amount", "category", "description"]].to_csv(index=False)
        st.download_button(
            "Download as CSV",
            data=csv,
            file_name=f"expenses_{user}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No expenses to export.")

    st.divider()
    st.subheader("Import Expenses from CSV")
    st.caption("CSV must have columns: `date`, `amount`, `category`, `description` (description is optional)")

    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        try:
            df = pd.read_csv(uploaded)
            required = {"date", "amount", "category"}
            if not required.issubset(set(df.columns)):
                st.error(f"Missing required columns: {required - set(df.columns)}")
            else:
                # Preview
                st.write("Preview (first 5 rows):")
                st.dataframe(df.head(), use_container_width=True, hide_index=True)
                if "description" not in df.columns:
                    df["description"] = ""
                if st.button("Confirm Import", use_container_width=True):
                    db.import_expenses_csv(df[["date", "amount", "category", "description"]], user)
                    st.success(f"Imported {len(df)} expenses!")
                    st.rerun()
        except Exception as e:
            st.error(f"Error reading CSV: {e}")


# ─── SETTINGS ────────────────────────────────────────────────────────
def page_settings(user, symbol):
    st.title("Settings")

    # Currency
    st.subheader("Currency")
    current_currency = db.get_currency(user)
    new_currency = st.selectbox("Select Currency", list(CURRENCY_SYMBOLS.keys()),
                                index=list(CURRENCY_SYMBOLS.keys()).index(current_currency))
    if st.button("Save Currency"):
        db.update_currency(user, new_currency)
        st.success(f"Currency updated to {new_currency}")
        st.rerun()

    st.divider()

    # Change password
    st.subheader("Change Password")
    with st.form("change_pass"):
        old_pass = st.text_input("Current Password", type="password")
        new_pass = st.text_input("New Password", type="password")
        confirm = st.text_input("Confirm New Password", type="password")
        if st.form_submit_button("Update Password"):
            if not db.authenticate_user(user, old_pass):
                st.error("Current password is incorrect.")
            elif new_pass != confirm:
                st.error("New passwords do not match.")
            elif len(new_pass) < 4:
                st.error("Password must be at least 4 characters.")
            else:
                import sqlite3
                conn = db.get_connection()
                conn.execute("UPDATE users SET password=? WHERE username=?", (new_pass, user))
                conn.commit()
                conn.close()
                st.success("Password updated!")

    st.divider()

    # Spending summary
    st.subheader("Account Summary")
    expenses = db.get_expenses(user)
    budgets = db.get_budgets(user)
    col1, col2 = st.columns(2)
    col1.metric("Total Expenses Recorded", len(expenses))
    col2.metric("Budgets Configured", len(budgets))
    if not expenses.empty:
        col1.metric("All-Time Spending", f"{symbol}{expenses['amount'].sum():,.2f}")
        col2.metric("Date Range",
                    f"{expenses['date'].min()} to {expenses['date'].max()}")

    st.divider()

    # Danger zone
    st.subheader("Danger Zone")
    with st.expander("Delete all my expenses"):
        st.warning("This will permanently delete ALL your expenses. This cannot be undone.")
        confirm_del = st.text_input("Type DELETE to confirm")
        if st.button("Delete All Expenses", type="primary"):
            if confirm_del == "DELETE":
                conn = db.get_connection()
                conn.execute("DELETE FROM expenses WHERE user=?", (user,))
                conn.commit()
                conn.close()
                st.success("All expenses deleted.")
                st.rerun()
            else:
                st.error('You must type DELETE to confirm.')


# ─── MAIN ────────────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        login_page()
        return

    user = st.session_state.username
    symbol = get_symbol()
    page = sidebar()

    if page == "Dashboard":
        page_dashboard(user, symbol)
    elif page == "Add Expense":
        page_add_expense(user, symbol)
    elif page == "Expense History":
        page_history(user, symbol)
    elif page == "Budgets":
        page_budgets(user, symbol)
    elif page == "Analytics":
        page_analytics(user, symbol)
    elif page == "Import / Export":
        page_import_export(user, symbol)
    elif page == "Settings":
        page_settings(user, symbol)


if __name__ == "__main__":
    main()
