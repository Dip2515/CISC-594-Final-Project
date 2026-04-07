# 💰 Smart Expense Tracker

A multi-user personal finance web application built with **Streamlit**, **SQLite**, and **Plotly**. Track expenses, set budgets, and visualize spending patterns — all from your browser.

---

## Features

- User registration & login with per-account data isolation
- Add, edit, and delete expense entries
- Category-based monthly budgets with alerts
- Rich analytics: monthly trend, category breakdown, daily spending, heatmap, year-over-year comparison
- CSV import & export
- Multi-currency support (USD, EUR, GBP, INR, CAD)

---

## Project Structure

```
smart_expense_tracker/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── sample_expenses.csv     # Sample data for import
├── data/
│   └── expenses.db         # SQLite database (auto-created on first run)
└── modules/
    ├── __init__.py
    ├── database.py         # DB schema, CRUD operations, user management
    └── analytics.py        # Plotly chart generation
```

---

## Setup — macOS

### 1. Prerequisites

- Python 3.9 or higher
- `pip` (comes with Python)

Check your version:
```bash
python3 --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/) or use Homebrew:
```bash
brew install python
```

### 2. Clone / Download the Project

```bash
cd ~/Desktop
# If using git:
git clone <your-repo-url> smart_expense_tracker
cd smart_expense_tracker

# Or unzip downloaded folder and navigate into it
```

### 3. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the App

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

### 6. Stop the App

Press `Ctrl + C` in the terminal.

### 7. Deactivate Virtual Environment (optional)

```bash
deactivate
```

---

## Setup — Windows

### 1. Prerequisites

- Python 3.9 or higher (download from [python.org](https://www.python.org/downloads/))
- During installation, **check "Add Python to PATH"**

Verify installation in Command Prompt or PowerShell:
```cmd
python --version
```

### 2. Clone / Download the Project

```cmd
cd %USERPROFILE%\Desktop
:: If using git:
git clone <your-repo-url> smart_expense_tracker
cd smart_expense_tracker

:: Or unzip downloaded folder and navigate into it
```

### 3. Create a Virtual Environment

**Command Prompt:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> If PowerShell blocks activation with an execution policy error, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then retry the activate command.

You should see `(venv)` in your prompt.

### 4. Install Dependencies

```cmd
pip install -r requirements.txt
```

### 5. Run the App

```cmd
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

### 6. Stop the App

Press `Ctrl + C` in the terminal window.

### 7. Deactivate Virtual Environment (optional)

```cmd
deactivate
```

---

## First-Time Login

A default account is pre-created:

| Field    | Value     |
|----------|-----------|
| Username | `default` |
| Password | `default` |

You can also register a new account from the **Register** tab on the login screen.

---

## Importing Sample Data

1. Log in and navigate to **Import / Export** in the sidebar.
2. Upload `sample_expenses.csv` from the project root.
3. Preview the data and click **Confirm Import**.

---

## Dependencies

| Package         | Version   | Purpose                    |
|-----------------|-----------|----------------------------|
| streamlit       | ≥ 1.28.0  | Web UI framework           |
| pandas          | ≥ 2.0.0   | Data manipulation          |
| plotly          | ≥ 5.17.0  | Interactive charts         |
| python-dotenv   | ≥ 1.0.0   | Environment variable support |

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `streamlit: command not found` | Make sure your virtual environment is activated |
| Port 8501 already in use | Run `streamlit run app.py --server.port 8502` |
| `ModuleNotFoundError` | Re-run `pip install -r requirements.txt` |
| Database errors | Delete `data/expenses.db` to reset (all data will be lost) |
| PowerShell activation blocked | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
