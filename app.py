import dash
from dash import html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd # Keep for potential use in layouts or if any CSV processing remains
import datetime

# Updated imports for new data loaders
from data_loader import (
    load_accounts_from_json,
    load_budgets_from_json,
    load_all_transactions_from_directory
)
from core_logic import (
    process_transactions,
    calculate_monthly_spending, # Will be used by layouts
    calculate_account_summaries, # Will be used by layouts
    CATEGORIZATION_RULES
)
from models import Transaction, Account, Budget # Keep models
import layouts # Import the layouts module

# --- 1. Define File Paths ---
# Adjusted paths to be relative to the app's root directory, typically where Dockerfile is.
# Assuming JSON setup files are in the 'data' directory alongside transactions.
ACCOUNTS_JSON_PATH = 'data/accounts_setup.json'
BUDGETS_JSON_PATH = 'data/budget_setup.json'
TRANSACTIONS_DIR_PATH = 'data/transactions_data/' # Directory for multiple transaction CSVs

# --- 2. Load Data Globally (Initial Approach) ---
GLOBAL_TRANSACTIONS: List[Transaction] = []
GLOBAL_ACCOUNTS: List[Account] = []
GLOBAL_BUDGETS: List[Budget] = []

def load_and_process_data():
    """Loads all data from sources and processes transactions."""
    global GLOBAL_TRANSACTIONS, GLOBAL_ACCOUNTS, GLOBAL_BUDGETS

    print("Loading accounts...")
    loaded_accounts = load_accounts_from_json(ACCOUNTS_JSON_PATH)
    if not loaded_accounts:
        print("Warning: No accounts loaded. Check accounts_setup.json and logs.")

    print("Loading budgets...")
    loaded_budgets = load_budgets_from_json(BUDGETS_JSON_PATH)
    if not loaded_budgets:
        print("Warning: No budgets loaded. Check budget_setup.json and logs.")

    print("Loading transactions...")
    loaded_transactions = load_all_transactions_from_directory(TRANSACTIONS_DIR_PATH)
    if not loaded_transactions:
        print("Warning: No transactions loaded. Check the transactions directory and logs.")

    # Assign to globals after all individual loads, to ensure partial loads don't mix states easily
    GLOBAL_ACCOUNTS = loaded_accounts
    GLOBAL_BUDGETS = loaded_budgets
    GLOBAL_TRANSACTIONS = loaded_transactions

    # Process transactions (categorizes them and updates account balances)
    # Note: process_transactions modifies GLOBAL_ACCOUNTS in-place.
    if GLOBAL_TRANSACTIONS and GLOBAL_ACCOUNTS:
        print("Processing transactions...")
        process_transactions(GLOBAL_TRANSACTIONS, GLOBAL_ACCOUNTS, CATEGORIZATION_RULES)
        print("Transaction processing complete.")
    else:
        print("Skipping transaction processing due to missing transactions or accounts.")

try:
    print("Initial data load sequence started...")
    load_and_process_data()
    print("Initial data load sequence complete.")
except Exception as e: # Catch any unexpected error during the initial load
    print(f"FATAL: An unexpected error occurred during initial data loading: {e}")
    # Initialize with empty data to allow app to run but show an error or empty state.
    GLOBAL_TRANSACTIONS = []
    GLOBAL_ACCOUNTS = []
    GLOBAL_BUDGETS = []


# --- 3. Initialize Dash App ---
app = dash.Dash(__name__, suppress_callback_exceptions=True, title="Personal Finance Dashboard")
server = app.server  # For Gunicorn/deployment

# --- 4. App Layout ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Nav([
        dcc.Link('Dashboard', href='/', className="nav-link"),
        dcc.Link('Expenses Analysis', href='/expenses', className="nav-link"),
        dcc.Link('Account Details', href='/accounts', className="nav-link"),
        dcc.Link('Budget Management', href='/budgets', className="nav-link"),
        dcc.Link('Net Worth Tracker', href='/net-worth', className="nav-link"),
        html.Button('Refresh Data', id='refresh-button', n_clicks=0, className="nav-button"),
    ], className="navbar"),
    html.Div(id='page-content', className="page-content-container"),
    html.Div(id='refresh-notification-output', style={'display': 'none'}),
    html.Footer("© 2024 Personal Finance Dashboard", className="footer")
])

# --- 5. Callback for Page Routing ---
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname: str):
    if pathname == '/':
        return layouts.create_main_dashboard_layout(GLOBAL_ACCOUNTS, GLOBAL_TRANSACTIONS, GLOBAL_BUDGETS)
    elif pathname == '/expenses':
        return layouts.create_expenses_page_layout(GLOBAL_TRANSACTIONS)
    elif pathname == '/accounts':
        return layouts.create_accounts_page_layout(GLOBAL_ACCOUNTS)
    elif pathname == '/budgets':
        return layouts.create_budgets_page_layout(GLOBAL_BUDGETS, GLOBAL_TRANSACTIONS)
    elif pathname == '/net-worth':
        return layouts.create_net_worth_page_layout(GLOBAL_TRANSACTIONS, GLOBAL_ACCOUNTS) # transactions might not be needed
    else:
        return html.Div([
            html.H1("404: Page Not Found"),
            html.P(f"The pathname {pathname} was not recognised.")
        ], className="text-center page")

# --- 6. Callback for Refresh Button ---
@app.callback(
    Output('refresh-notification-output', 'children'),
    [Input('refresh-button', 'n_clicks')],
    prevent_initial_call=True
)
def refresh_data_globally(n_clicks: int):
    if n_clicks > 0:
        print(f"Refresh button clicked {n_clicks} times. Re-loading and processing data...")
        try:
            load_and_process_data() # Call the consolidated loading function
            print("Data reloaded and processed successfully via refresh button.")
            return f"Data refreshed at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
        except Exception as e:
            print(f"An error occurred during data refresh: {e}")
            return f"Refresh failed: An error occurred. {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    return ""

# --- 7. Main Execution Block ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
