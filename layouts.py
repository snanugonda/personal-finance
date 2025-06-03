import dash.html as html
import dash.dcc as dcc
import dash.dash_table as dash_table
import plotly.express as px
import pandas as pd
from typing import List, Dict, Optional # Added Optional
import datetime

from models import Account, Transaction, Budget
from core_logic import calculate_account_summaries, calculate_monthly_spending, calculate_credit_card_utilization

def create_main_dashboard_layout(accounts: List[Account], transactions: List[Transaction], budgets: List[Budget]) -> html.Div:
    """
    Generates the layout for the main dashboard.
    (Content from previous step, assumed to be correct and complete)
    """
    summaries = calculate_account_summaries(accounts)
    key_metrics_div = html.Div([
        html.H2("Financial Overview"),
        html.H3(f"Current Net Worth: ${summaries.get('net_worth', 0.0):.2f}", className="metric"),
        html.P(f"Total Assets: ${summaries.get('total_assets', 0.0):.2f}", className="metric-detail"),
        html.P(f"Total Liabilities: ${summaries.get('total_liabilities', 0.0):.2f}", className="metric-detail"),
    ], className="metrics-container section-container")

    now = datetime.datetime.now()
    current_month = now.month
    current_year = now.year

    income_vs_expense_fig = create_income_expense_chart(transactions, current_month, current_year)
    income_expense_graph = dcc.Graph(
        id='income-expense-graph',
        figure=income_vs_expense_fig
    ) if income_vs_expense_fig else html.P("No transaction data for the current month to display income vs expense.")

    monthly_spending_data = calculate_monthly_spending(transactions, current_month, current_year)
    budget_overview_items = [html.H4("Current Month's Budget Progress")]
    if budgets:
        budget_cards = []
        for budget_item in budgets:
            category = budget_item.category_name
            budgeted = budget_item.budgeted_amount_monthly
            spent = monthly_spending_data.get(category, 0.0)
            remaining = budgeted - spent
            progress_percentage = (spent / budgeted * 100) if budgeted > 0 else 0

            color = "success" # Green for on track
            if budgeted > 0:
                if progress_percentage > 100:
                    color = "danger" # Red for overspent
                elif progress_percentage > 75:
                    color = "warning" # Yellow for approaching limit
            elif spent > 0 : # Budget is 0 or less, but spent money
                 color = "danger"


            budget_cards.append(
                html.Div([
                    html.H5(category, className="budget-card-title"),
                    html.P(f"Budgeted: ${budgeted:,.2f}"),
                    html.P(f"Spent: ${spent:,.2f}"),
                    html.P(f"Remaining: ${remaining:,.2f}", className=f"budget-remaining-{color}"),
                    (html.Div(dcc.Graph( # Mini progress bar
                        figure=px.bar(
                            y=['Progress'],
                            x=[progress_percentage if budgeted > 0 else 0],
                            orientation='h',
                            height=50,
                            range_x=[0,100],
                            color_discrete_sequence=[f'var(--bs-{color})'] if color else ['#1f77b4']
                        ).update_layout(
                            xaxis=dict(showticklabels=False, title=None, showgrid=False, zeroline=False),
                            yaxis=dict(showticklabels=False, title=None, showgrid=False, zeroline=False),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=0, r=0, t=5, b=5),
                            showlegend=False,
                            bargap=0.05
                        ),
                        config={'displayModeBar': False}
                    ), className="budget-progress-bar-container") if budgeted > 0 else html.P("Budget not set or zero.", className="text-muted"))
                ], className=f"budget-card card-body border-{color}")
            )
        budget_overview_div = html.Div(budget_cards, className="budget-cards-container")
    else:
        budget_overview_div = html.Div(html.P("No budget items defined."), className="section-container")

    return html.Div([
        key_metrics_div,
        html.Div([
            html.Div(income_expense_graph, className="chart-container card-body"),
            budget_overview_div
        ], className="dashboard-flex-container")
    ], className="dashboard-container page")

def create_income_expense_chart(transactions: List[Transaction], month: int, year: int) -> Optional[px.bar]:
    """ Helper function to create an income vs. expense bar chart. """
    current_month_transactions = [
        t for t in transactions
        if isinstance(t.date, datetime.date) and t.date.month == month and t.date.year == year
    ]
    if not current_month_transactions: return None
    total_income = sum(t.amount for t in current_month_transactions if t.amount > 0)
    total_expenses = sum(abs(t.amount) for t in current_month_transactions if t.amount < 0)
    df = pd.DataFrame({'Category': ['Income', 'Expenses'], 'Amount': [total_income, total_expenses]})
    fig = px.bar(df, x='Category', y='Amount', color='Category', title=f"Income vs. Expenses - {datetime.date(year, month, 1).strftime('%B %Y')}",
                 color_discrete_map={'Income': 'var(--bs-success)', 'Expenses': 'var(--bs-danger)'})
    fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

# --- Expenses Page ---
def create_expenses_page_layout(transactions: List[Transaction]) -> html.Div:
    """ Generates the layout for the Expenses Analysis page. """
    if not transactions:
        return html.Div([html.H2("Expenses Analysis"), html.P("No transaction data available.")], className="page")

    # Convert transactions to DataFrame for table and chart
    transaction_data = [{
        'Date': t.date.strftime('%Y-%m-%d') if isinstance(t.date, datetime.date) else str(t.date),
        'Description': t.description,
        'Category': t.category,
        'Amount': t.amount,
        'Account': t.account_affected
    } for t in transactions]
    df_transactions = pd.DataFrame(transaction_data)

    # Transactions Table
    transactions_table = dash_table.DataTable(
        id='transactions-table',
        columns=[{"name": i, "id": i} for i in df_transactions.columns],
        data=df_transactions.to_dict('records'),
        page_size=15,
        sort_action="native",
        filter_action="native",
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': 'var(--bs-light)', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'left', 'padding': '5px', 'minWidth': '100px', 'width': '150px', 'maxWidth': '200px'},
    )

    # Expenses by Category Chart (Pie Chart)
    df_expenses = df_transactions[df_transactions['Amount'] < 0].copy()
    df_expenses['Amount'] = df_expenses['Amount'].abs() # Use absolute values for chart

    expenses_by_category_fig = px.pie(
        df_expenses,
        names='Category',
        values='Amount',
        title='Expenses by Category (All Time)',
        hole=0.3,
    )
    expenses_by_category_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')


    return html.Div([
        html.H2("Expenses Analysis", className="page-title"),
        html.Div([
            html.Div(dcc.Graph(id='expenses-by-category-chart', figure=expenses_by_category_fig), className="chart-container card-body"),
        ], className="chart-row"),
        html.Div(transactions_table, className="table-container card-body"),
    ], className="page")

# --- Accounts Page ---
def create_accounts_page_layout(accounts: List[Account]) -> html.Div:
    """ Generates the layout for the Accounts Details page. """
    if not accounts:
        return html.Div([html.H2("Account Details"), html.P("No account data available.")], className="page")

    account_data = []
    for acc in accounts:
        utilization = None
        if acc.account_type.lower() == 'credit_card':
            utilization = calculate_credit_card_utilization(acc)

        limit_or_orig = acc.limit if acc.account_type.lower() == 'credit_card' else acc.original_amount

        account_data.append({
            'Account Name': acc.account_name,
            'Type': acc.account_type,
            'Balance': f"${acc.current_balance:,.2f}",
            'Limit/Original Amt': f"${limit_or_orig:,.2f}" if limit_or_orig is not None else "N/A",
            'Interest Rate': f"{acc.interest_rate*100:.2f}%" if acc.interest_rate is not None else "N/A",
            'Utilization %': f"{utilization:.2f}%" if utilization is not None else "N/A"
        })

    df_accounts = pd.DataFrame(account_data)

    accounts_table = dash_table.DataTable(
        id='accounts-table',
        columns=[{"name": i, "id": i} for i in df_accounts.columns],
        data=df_accounts.to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': 'var(--bs-light)', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
    )

    return html.Div([
        html.H2("Account Details", className="page-title"),
        html.Div(accounts_table, className="table-container card-body")
    ], className="page")

# --- Budgets Page ---
def create_budgets_page_layout(budgets: List[Budget], transactions: List[Transaction]) -> html.Div:
    """ Generates the layout for the Budget Management page. """
    if not budgets:
        return html.Div([html.H2("Budget Management"), html.P("No budget data available.")], className="page")

    now = datetime.datetime.now()
    current_month, current_year = now.month, now.year
    actual_spending_monthly = calculate_monthly_spending(transactions, current_month, current_year)

    budget_details_data = []
    for budget_item in budgets:
        spent = actual_spending_monthly.get(budget_item.category_name, 0.0)
        remaining = budget_item.budgeted_amount_monthly - spent
        budget_details_data.append({
            'Category': budget_item.category_name,
            'Budgeted Amount': f"${budget_item.budgeted_amount_monthly:,.2f}",
            'Spent Amount': f"${spent:,.2f}",
            'Remaining/Overspent': f"${remaining:,.2f}"
        })

    df_budget_details = pd.DataFrame(budget_details_data)

    budgets_table = dash_table.DataTable(
        id='budgets-table',
        columns=[{"name": i, "id": i} for i in df_budget_details.columns],
        data=df_budget_details.to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': 'var(--bs-light)', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
        # Conditional styling for 'Remaining/Overspent' can be added here later
    )

    # Chart for Budget vs Actual
    df_chart_data = []
    for item in budget_details_data:
        df_chart_data.append({'Category': item['Category'], 'Type': 'Budgeted', 'Amount': float(item['Budgeted Amount'].replace('$', '').replace(',', ''))})
        df_chart_data.append({'Category': item['Category'], 'Type': 'Spent', 'Amount': float(item['Spent Amount'].replace('$', '').replace(',', ''))})

    df_budget_chart = pd.DataFrame(df_chart_data)
    budget_vs_actual_fig = px.bar(
        df_budget_chart,
        x="Category",
        y="Amount",
        color="Type",
        barmode="group",
        title=f"Budget vs. Actual Spending - {datetime.date(current_year, current_month, 1).strftime('%B %Y')}"
    )
    budget_vs_actual_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')


    return html.Div([
        html.H2(f"Budget Management - {datetime.date(current_year, current_month, 1).strftime('%B %Y')}", className="page-title"),
        html.Div(dcc.Graph(id='budget-vs-actual-chart', figure=budget_vs_actual_fig), className="chart-container card-body"),
        html.Div(budgets_table, className="table-container card-body")
    ], className="page")

# --- Net Worth Page ---
def create_net_worth_page_layout(transactions: List[Transaction], accounts: List[Account]) -> html.Div:
    """ Generates the layout for the Net Worth Tracker page. """
    # For now, displays current net worth and a placeholder for historical tracking.
    # A true historical net worth requires more complex data processing.

    current_summaries = calculate_account_summaries(accounts)
    current_net_worth = current_summaries.get('net_worth', 0.0)

    # Placeholder for historical data - This is a simplified example
    # A real implementation would need to reconstruct balances over time.
    # For this example, let's assume we have snapshots or can derive them.
    # This is very basic and likely not accurate without proper historical balance snapshots.

    # Simplified: Show net worth changes if transactions span multiple months.
    # This is NOT a true historical net worth.
    # It's more like "Net worth after transactions up to this month's end".

    # For a simple placeholder:
    net_worth_display = [
        html.H2("Net Worth Tracker", className="page-title"),
        html.Div([
            html.H3(f"Current Net Worth: ${current_net_worth:,.2f}"),
            html.P("Detailed historical net worth tracking is a feature planned for future development."),
            html.P("To accurately track net worth over time, the application would need to:"),
            html.Ul([
                html.Li("Store or reconstruct historical account balances at regular intervals (e.g., daily or monthly)."),
                html.Li("Consider asset value changes (e.g., investments) over time, which requires external data integration or manual input."),
            ]),
            html.P("The current calculation reflects net worth based on the latest processed transaction data and account balances.")
        ], className="card-body")
    ]

    # If we want to try a very basic trend based on available data (highly simplified):
    # This is just illustrative of what might be done, not a robust solution.
    if transactions:
        df_transactions_temp = pd.DataFrame([{
            'Date': t.date if isinstance(t.date, datetime.date) else pd.to_datetime(t.date).date(),
        } for t in transactions])
        df_transactions_temp['Date'] = pd.to_datetime(df_transactions_temp['Date'])

        if not df_transactions_temp.empty and pd.api.types.is_datetime64_any_dtype(df_transactions_temp['Date']):
            # This is a very rough approximation and doesn't reflect true daily/monthly net worth.
            # It just shows the current net worth plotted at different transaction dates.
            # A real historical net worth would involve recalculating balances at each point.

            # For now, we will just show the placeholder text.
            # A proper historical chart requires significant backend logic.
            pass # Keep placeholder for now

    return html.Div(net_worth_display, className="page")
