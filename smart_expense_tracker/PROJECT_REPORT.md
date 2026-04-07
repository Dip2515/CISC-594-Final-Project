# Smart Expense Tracker — Project Report

**Date:** April 2026
**Technology Stack:** Python · Streamlit · SQLite · Pandas · Plotly

---

## 1. Project Overview

Smart Expense Tracker is a locally hosted personal finance web application that allows individuals to record, categorize, and analyze their daily expenses. The application is designed for personal use with multi-user support, meaning multiple people can maintain isolated expense records on the same installation. The entire stack runs locally with no external API dependencies, making it suitable for privacy-conscious users.

---

## 2. Objectives

- Provide an intuitive interface for logging daily expenses without spreadsheet overhead.
- Allow users to set monthly spending budgets per category and receive visual alerts.
- Deliver meaningful analytics (trends, category breakdowns, heatmaps) to help users understand their spending behavior.
- Support CSV import and export for data portability.
- Enable multi-user access with isolated data per account.

---

## 3. Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| Frontend / UI | Streamlit ≥ 1.28.0 | Rapid Python-native web UI; no HTML/JS required |
| Database | SQLite (via Python `sqlite3`) | Zero-config, file-based, sufficient for personal use |
| Data Processing | Pandas ≥ 2.0.0 | DataFrame-based querying and aggregation |
| Visualization | Plotly ≥ 5.17.0 | Interactive, browser-rendered charts |
| Configuration | python-dotenv ≥ 1.0.0 | Environment variable management |
| Language | Python 3.9+ | Broad library support, cross-platform |

---

## 4. System Architecture

```
┌─────────────────────────────────────────────┐
│                  Browser UI                  │
│            (Streamlit on port 8501)          │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│                   app.py                     │
│  - Session state management                  │
│  - Authentication flow                       │
│  - Page routing (7 pages)                    │
│  - UI rendering                              │
└──────────┬─────────────────┬────────────────┘
           │                 │
┌──────────▼──────┐  ┌───────▼────────────────┐
│  database.py    │  │     analytics.py        │
│  - SQLite CRUD  │  │  - Plotly chart funcs   │
│  - User auth    │  │  - Monthly trend        │
│  - CSV import   │  │  - Category pie/bar     │
└──────────┬──────┘  │  - Daily line chart     │
           │         │  - Spending heatmap     │
┌──────────▼──────┐  │  - Year-over-year       │
│  data/          │  │  - Budget comparison    │
│  expenses.db    │  └─────────────────────────┘
│  (SQLite file)  │
└─────────────────┘
```

### Data Flow

1. User interacts with the browser UI (Streamlit).
2. `app.py` handles session state, routing, and form logic.
3. `database.py` performs all reads and writes to `data/expenses.db`.
4. Query results are returned as Pandas DataFrames.
5. `analytics.py` consumes DataFrames and returns Plotly figure objects.
6. Plotly figures are rendered back in the browser via Streamlit.

---

## 5. Database Design

The application uses three SQLite tables:

### `expenses`

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment primary key |
| date | TEXT | Expense date (YYYY-MM-DD) |
| amount | REAL | Expense amount |
| category | TEXT | Spending category |
| description | TEXT | Optional free-text description |
| user | TEXT | Owner username (default: `default`) |
| created_at | TEXT | Row creation timestamp |

### `budgets`

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment primary key |
| category | TEXT | Budget category |
| monthly_limit | REAL | Spending cap per month |
| user | TEXT | Owner username |

Unique constraint on `(category, user)` — one budget per category per user.

### `users`

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment primary key |
| username | TEXT UNIQUE | Login username |
| password | TEXT | Plain-text password |
| currency | TEXT | Preferred display currency (default: USD) |
| created_at | TEXT | Account creation timestamp |

> **Security Note:** Passwords are stored in plain text in the current implementation. For production deployments, passwords should be hashed using `bcrypt` or `hashlib`.

---

## 6. Application Pages

### 6.1 Login / Register

Entry point for the application. Provides a tabbed interface for existing users to log in and new users to register. A pre-seeded `default/default` account is created on first run via `init_db()`.

### 6.2 Dashboard

The home page after login. Displays:
- Four KPI metrics: current month total, all-time total, transaction count, average transaction.
- Budget status cards with color-coded alerts (green / yellow warning at 80% / red at 100%).
- Monthly spending trend bar chart.
- Category spending pie chart.
- Last 10 expenses table.

### 6.3 Add Expense

A validated form for creating new expense records. Fields: date, amount, category (dropdown from 12 preset categories), description. Displays the top spending category for the current month as a contextual hint.

### 6.4 Expense History

Paginated, filterable list of all expenses with inline edit and delete. Supports filtering by keyword, category, and month. Shows a running count and filtered total.

### 6.5 Budgets

Set and manage monthly category budgets. Displays progress bars showing spent vs. limit per category with remaining balance. Over-budget categories are highlighted in red. Includes a grouped bar chart comparing budget vs. actual spend.

### 6.6 Analytics

Multi-tab analytics dashboard:
- **Monthly Trend** — bar chart of total spending per month + year-over-year line chart.
- **By Category** — pie chart and horizontal bar chart for the selected period.
- **Daily** — line chart of day-by-day spending.
- **Heatmap** — spending intensity by day-of-week and week number.
- **Monthly Summary Report** — pivot table of spending by category and month.

### 6.7 Import / Export

- **Export:** One-click CSV download of all expenses (columns: date, amount, category, description).
- **Import:** Upload a CSV file, preview the first 5 rows, and confirm bulk insert. Required columns: `date`, `amount`, `category`.

### 6.8 Settings

- Change preferred display currency.
- Change account password.
- View account summary (total records, all-time spending, date range).
- Danger zone: permanently delete all expenses (requires typing `DELETE` to confirm).

---

## 7. Analytics Module

`analytics.py` contains seven chart-generating functions, each accepting a Pandas DataFrame and returning a Plotly figure (or `None` if data is empty).

| Function | Chart Type | Description |
|---|---|---|
| `monthly_trend_chart` | Bar | Total spending grouped by calendar month |
| `category_pie_chart` | Donut Pie | Spending proportion per category |
| `category_bar_chart` | Horizontal Bar | Total per category, sorted ascending |
| `daily_spending_chart` | Line + Markers | Day-by-day spending for a given period |
| `budget_comparison_chart` | Grouped Bar | Budget limit vs. actual spend per category |
| `spending_heatmap` | Heatmap | Spending by day-of-week × week number |
| `yearly_summary_chart` | Multi-line | Monthly totals overlaid per year |

---

## 8. Key Design Decisions

### Local-first Architecture
The app stores all data in a local SQLite file (`data/expenses.db`). This eliminates server costs, keeps user data private, and removes network dependency.

### Streamlit for UI
Streamlit was chosen to keep the codebase Python-only. All UI, state management, and routing is handled in `app.py` without HTML, CSS, or JavaScript.

### DataFrame-centric Data Layer
`database.py` returns query results as Pandas DataFrames. This keeps the analytics and display logic consistent — Plotly and Streamlit both integrate natively with DataFrames.

### Multi-user via User Column
Instead of separate databases per user, all tables include a `user` column. All queries are filtered by the logged-in username, providing logical data isolation within a single SQLite file.

### 12 Preset Categories
Categories are hardcoded in `app.py` (`CATEGORIES` list) to ensure consistency in budget mapping and chart grouping:
Food & Dining, Transportation, Shopping, Entertainment, Healthcare, Housing, Utilities, Education, Travel, Personal Care, Business, Other.

---

## 9. Limitations & Future Improvements

| Limitation | Suggested Improvement |
|---|---|
| Plain-text passwords | Hash with `bcrypt` or `hashlib.sha256` |
| No recurring expense support | Add recurring transaction scheduler |
| No data backup mechanism | Add automated SQLite backup / export on startup |
| Single-file SQLite | Migrate to PostgreSQL for concurrent multi-user deployments |
| No mobile responsiveness | Use Streamlit's column layout tuning or build a React frontend |
| Categories are hardcoded | Allow users to create and manage custom categories |
| No spending forecast | Add simple linear regression for next-month prediction |
| No notifications | Integrate email/push alerts when budgets reach 80%/100% |

---

## 10. File Summary

| File | Lines | Purpose |
|---|---|---|
| `app.py` | 527 | Main app: auth, routing, all 7 page UIs |
| `modules/database.py` | 186 | SQLite schema, CRUD, user management |
| `modules/analytics.py` | 131 | 7 Plotly chart functions |
| `modules/__init__.py` | — | Package marker |
| `requirements.txt` | 4 | Python dependency declarations |
| `sample_expenses.csv` | 31 | 30-row sample dataset for import testing |

**Total application code: ~844 lines of Python**

---

## 11. Running the Application

```bash
# macOS / Linux
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py

# Windows
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Access at: `http://localhost:8501`
Default credentials: `default` / `default`
