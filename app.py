import dash
from dash import html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd
import datetime

from data_loader import load_transactions, load_accounts, load_budgets
from core_logic import process_transactions, calculate_monthly_spending, calculate_account_summaries, CATEGORIZATION_RULES
from models import Transaction, Account, Budget
import layouts # Import the layouts module

# --- 1. Define File Paths ---
TRANSACTIONS_CSV = 'data/transactions.csv'
ACCOUNTS_CSV = 'data/accounts.csv'
BUDGETS_CSV = 'data/budget.csv'

# --- 2. Load Data Globally (Initial Approach) ---
# This data is loaded once when the app starts.
try:
    all_transactions_raw = load_transactions(TRANSACTIONS_CSV)
    all_accounts_raw = load_accounts(ACCOUNTS_CSV)
    all_budgets_raw = load_budgets(BUDGETS_CSV)

    # Process transactions: categorizes them and updates account balances
    # Create copies to avoid modifying the raw loaded data if we need to reset
    # For now, we'll work with these copies globally.
    # A more robust solution for refresh might involve dcc.Store or re-triggering this block.
    processed_transactions = [t for t in all_transactions_raw] # Shallow copy for now
    current_accounts_state = [a for a in all_accounts_raw] # Shallow copy

    process_transactions(processed_transactions, current_accounts_state, CATEGORIZATION_RULES)

    # Make these available globally for callbacks
    # In a multi-user or more complex scenario, this global state needs careful management.
    GLOBAL_TRANSACTIONS = processed_transactions
    GLOBAL_ACCOUNTS = current_accounts_state
    GLOBAL_BUDGETS = all_budgets_raw

except FileNotFoundError as e:
    print(f"Error: One or more data files not found. Please ensure CSV files exist at specified paths: {e}")
    # Initialize with empty data to allow app to run and show an error or empty state.
    GLOBAL_TRANSACTIONS = []
    GLOBAL_ACCOUNTS = []
    GLOBAL_BUDGETS = []
except Exception as e:
    print(f"An error occurred during initial data loading: {e}")
    GLOBAL_TRANSACTIONS = []
    GLOBAL_ACCOUNTS = []
    GLOBAL_BUDGETS = []


# --- 3. Initialize Dash App ---
app = dash.Dash(__name__, suppress_callback_exceptions=True, title="Personal Finance Dashboard")
server = app.server  # For Gunicorn/deployment

# --- 4. App Layout ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False), # Handles URL changes

    # Navigation Bar
    html.Nav([
        dcc.Link('Dashboard', href='/', className="nav-link"),
        dcc.Link('Expenses Analysis', href='/expenses', className="nav-link"),
        dcc.Link('Account Details', href='/accounts', className="nav-link"),
        dcc.Link('Budget Management', href='/budgets', className="nav-link"),
        dcc.Link('Net Worth Tracker', href='/net-worth', className="nav-link"),
        html.Button('Refresh Data', id='refresh-button', n_clicks=0, className="nav-button"),
    ], className="navbar"),

    # Page Content Area
    html.Div(id='page-content', className="page-content-container"),

    # Hidden div for refresh notifications (or could be a dcc.Store for more complex state)
    html.Div(id='refresh-notification-output', style={'display': 'none'}),

    # Footer (optional)
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
        # Pass necessary data to the layout function
        return layouts.create_expenses_page_layout(GLOBAL_TRANSACTIONS)
    elif pathname == '/accounts':
        return layouts.create_accounts_page_layout(GLOBAL_ACCOUNTS)
    elif pathname == '/budgets':
        return layouts.create_budgets_page_layout(GLOBAL_BUDGETS, GLOBAL_TRANSACTIONS)
    elif pathname == '/net-worth':
        # This might need both transactions and accounts
        return layouts.create_net_worth_page_layout(GLOBAL_TRANSACTIONS, GLOBAL_ACCOUNTS)
    else:
        return html.Div([
            html.H1("404: Page Not Found"),
            html.P(f"The pathname {pathname} was not recognised.")
        ], className="text-center")

# --- 6. Callback for Refresh Button (Placeholder/Initial Implementation) ---
@app.callback(
    Output('refresh-notification-output', 'children'), # Example output
    # Potentially, we might want to Output to multiple graphs/data displays to trigger their refresh
    # Or use dcc.Store to signal a refresh to other callbacks
    [Input('refresh-button', 'n_clicks')],
    prevent_initial_call=True
)
def refresh_data_globally(n_clicks: int):
    global GLOBAL_TRANSACTIONS, GLOBAL_ACCOUNTS, GLOBAL_BUDGETS

    if n_clicks > 0:
        print(f"Refresh button clicked {n_clicks} times. Re-loading and processing data...")
        try:
            # Re-load
            all_transactions_raw = load_transactions(TRANSACTIONS_CSV)
            all_accounts_raw = load_accounts(ACCOUNTS_CSV) # Load initial balances
            all_budgets_raw = load_budgets(BUDGETS_CSV)

            # Re-process (essential for account balances and categorization)
            # Create new lists for processing to ensure we're not mutating unexpectedly if load fails midway
            processed_transactions_new = [t for t in all_transactions_raw]
            current_accounts_state_new = [a for a in all_accounts_raw]

            process_transactions(processed_transactions_new, current_accounts_state_new, CATEGORIZATION_RULES)

            # Update global variables
            GLOBAL_TRANSACTIONS = processed_transactions_new
            GLOBAL_ACCOUNTS = current_accounts_state_new
            GLOBAL_BUDGETS = all_budgets_raw

            print("Data reloaded and processed successfully.")
            # This simple refresh won't automatically update the 'page-content'
            # The user would need to navigate away and back, or a more complex callback structure
            # involving dcc.Store and multiple Outputs would be needed to refresh the current page view.
            # For now, this reloads data for subsequent page navigations.
            return f"Data refreshed at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. Navigate to a page to see updates."
        except FileNotFoundError as e:
            print(f"Error during refresh: One or more data files not found: {e}")
            return f"Refresh failed: Data file not found. {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        except Exception as e:
            print(f"An error occurred during data refresh: {e}")
            return f"Refresh failed: An error occurred. {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    return "" # No refresh triggered initially


# --- 7. Main Execution Block ---
if __name__ == '__main__':
    # Note: Setting host='0.0.0.0' makes it accessible externally if run in a container/VM
    # app.run_server has been replaced by app.run in newer Dash versions
    app.run(debug=True, host='0.0.0.0', port=8050)
