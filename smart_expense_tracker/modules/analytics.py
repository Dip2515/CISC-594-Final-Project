import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def monthly_trend_chart(df, symbol="$"):
    if df.empty:
        return None
    df = df.copy()
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    monthly = df.groupby("month")["amount"].sum().reset_index()
    fig = px.bar(
        monthly, x="month", y="amount",
        title="Monthly Spending Trend",
        labels={"amount": f"Amount ({symbol})", "month": "Month"},
        color="amount",
        color_continuous_scale="Blues"
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    return fig


def category_pie_chart(df, symbol="$"):
    if df.empty:
        return None
    by_cat = df.groupby("category")["amount"].sum().reset_index()
    fig = px.pie(
        by_cat, values="amount", names="category",
        title="Spending by Category",
        hole=0.4
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig


def category_bar_chart(df, symbol="$"):
    if df.empty:
        return None
    by_cat = df.groupby("category")["amount"].sum().reset_index().sort_values("amount", ascending=True)
    fig = px.bar(
        by_cat, x="amount", y="category",
        orientation="h",
        title="Total Spending by Category",
        labels={"amount": f"Amount ({symbol})", "category": "Category"},
        color="amount",
        color_continuous_scale="Reds"
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    return fig


def daily_spending_chart(df, symbol="$"):
    if df.empty:
        return None
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    daily = df.groupby("date")["amount"].sum().reset_index()
    fig = px.line(
        daily, x="date", y="amount",
        title="Daily Spending",
        labels={"amount": f"Amount ({symbol})", "date": "Date"},
        markers=True
    )
    return fig


def budget_comparison_chart(expenses_df, budgets_df, month_str, symbol="$"):
    if budgets_df.empty:
        return None
    spent_by_cat = {}
    if not expenses_df.empty:
        monthly = expenses_df[expenses_df["date"].str.startswith(month_str)]
        spent_by_cat = monthly.groupby("category")["amount"].sum().to_dict()

    categories = budgets_df["category"].tolist()
    limits = budgets_df["monthly_limit"].tolist()
    spent = [spent_by_cat.get(cat, 0) for cat in categories]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Budget Limit", x=categories, y=limits,
                         marker_color="lightblue"))
    fig.add_trace(go.Bar(name="Spent", x=categories, y=spent,
                         marker_color=["red" if s > l else "green"
                                       for s, l in zip(spent, limits)]))
    fig.update_layout(
        barmode="group",
        title=f"Budget vs Actual Spending — {month_str}",
        yaxis_title=f"Amount ({symbol})"
    )
    return fig


def spending_heatmap(df):
    if df.empty:
        return None
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["weekday"] = df["date"].dt.day_name()
    df["week"] = df["date"].dt.isocalendar().week.astype(str)
    pivot = df.pivot_table(values="amount", index="weekday", columns="week",
                           aggfunc="sum", fill_value=0)
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = pivot.reindex([d for d in days_order if d in pivot.index])
    fig = px.imshow(
        pivot,
        title="Spending Heatmap (by Day of Week)",
        color_continuous_scale="YlOrRd",
        aspect="auto"
    )
    fig.update_layout(xaxis_title="Week Number", yaxis_title="Day of Week")
    return fig


def yearly_summary_chart(df, symbol="$"):
    if df.empty:
        return None
    df = df.copy()
    df["year"] = pd.to_datetime(df["date"]).dt.year
    df["month_name"] = pd.to_datetime(df["date"]).dt.strftime("%b")
    df["month_num"] = pd.to_datetime(df["date"]).dt.month
    monthly = (df.groupby(["year", "month_num", "month_name"])["amount"]
               .sum().reset_index().sort_values(["year", "month_num"]))
    fig = px.line(
        monthly, x="month_name", y="amount", color="year",
        title="Year-over-Year Monthly Comparison",
        labels={"amount": f"Amount ({symbol})", "month_name": "Month"},
        markers=True
    )
    return fig
