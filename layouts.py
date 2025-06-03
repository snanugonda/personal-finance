import dash.html as html
import dash.dcc as dcc
import dash.dash_table as dash_table
import plotly.express as px
import pandas as pd
from typing import List, Dict, Optional
import datetime
from collections import defaultdict # Added for potential use in complex aggregations

from models import Account, Transaction, Budget
from core_logic import calculate_account_summaries, calculate_monthly_spending, calculate_credit_card_utilization

# --- Helper Function for Multi-Currency Display ---
def format_currency_dict(data: Dict[str, float], default_if_empty: str = "N/A") -> str:
    """
    Formats a dictionary of currency:amount pairs into a display string.
    Example: {'USD': 100.23, 'EUR': 50.76} -> "USD 100.23, EUR 50.76"
    """
    if not data or not isinstance(data, dict):
        return default_if_empty
    return ", ".join([f"{currency} {amount:,.2f}" for currency, amount in data.items()])

# --- Main Dashboard Layout ---
def create_main_dashboard_layout(accounts: List[Account], transactions: List[Transaction], budgets: List[Budget]) -> html.Div:
    """
    Generates the layout for the main dashboard, updated for multi-currency.
    """
    # 1. Key Metrics Display (Multi-Currency)
    account_summaries = calculate_account_summaries(accounts) # Returns {'metric': {'CUR': val}}

    net_worth_str = format_currency_dict(account_summaries.get('net_worth', {}))
    assets_str = format_currency_dict(account_summaries.get('total_assets', {}))
    liabilities_str = format_currency_dict(account_summaries.get('total_liabilities', {}))

    key_metrics_div = html.Div([
        html.H2("Financial Overview"),
        html.H3(f"Current Net Worth: {net_worth_str}", className="metric"),
        html.P(f"Total Assets: {assets_str}", className="metric-detail"),
        html.P(f"Total Liabilities: {liabilities_str}", className="metric-detail"),
    ], className="metrics-container section-container")

    # 2. Income vs. Expense Chart (Multi-Currency)
    now = datetime.datetime.now()
    current_month = now.month
    current_year = now.year

    # Aggregate income and expenses per currency for the current month
    monthly_income_by_currency = defaultdict(float)
    monthly_expenses_by_currency = defaultdict(float)

    for t in transactions:
        if isinstance(t.date, datetime.date) and t.date.month == current_month and t.date.year == current_year:
            if t.amount > 0:
                monthly_income_by_currency[t.currency] += t.amount
            else:
                monthly_expenses_by_currency[t.currency] += abs(t.amount)

    chart_data = []
    all_currencies_in_month = set(monthly_income_by_currency.keys()) | set(monthly_expenses_by_currency.keys())

    if not all_currencies_in_month:
        income_expense_graph = html.P("No transaction data for the current month to display income vs expense.")
    else:
        for currency in sorted(list(all_currencies_in_month)):
            chart_data.append({'Currency': currency, 'Type': 'Income', 'Amount': monthly_income_by_currency.get(currency, 0.0)})
            chart_data.append({'Currency': currency, 'Type': 'Expenses', 'Amount': monthly_expenses_by_currency.get(currency, 0.0)})

        df_income_expense = pd.DataFrame(chart_data)

        income_vs_expense_fig = px.bar(
            df_income_expense,
            x='Currency',
            y='Amount',
            color='Type',
            barmode='group',
            title=f"Income vs. Expenses - {datetime.date(current_year, current_month, 1).strftime('%B %Y')}",
            color_discrete_map={'Income': 'var(--bs-success)', 'Expenses': 'var(--bs-danger)'}
        )
        income_vs_expense_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        income_expense_graph = dcc.Graph(id='income-expense-graph', figure=income_vs_expense_fig)

    # 3. Budget Overview (Multi-Currency)
    # calculate_monthly_spending returns {category: {currency: amount}}
    monthly_spending_data = calculate_monthly_spending(transactions, current_month, current_year)
    budget_overview_items = [html.H4(f"Budget Progress - {datetime.date(current_year, current_month, 1).strftime('%B %Y')}")]

    if budgets:
        budget_cards = []
        for budget_item in budgets:
            category = budget_item.category_name
            # budget.budgeted_amount_monthly is Dict[str, float]
            budgeted_amounts_dict = budget_item.budgeted_amount_monthly
            spent_amounts_dict = monthly_spending_data.get(category, {})

            card_content = [html.H5(category, className="budget-card-title")]

            all_budget_currencies = set(budgeted_amounts_dict.keys()) | set(spent_amounts_dict.keys())
            if not all_budget_currencies:
                card_content.append(html.P("No budget defined or spending in any currency for this category."))

            for currency in sorted(list(all_budget_currencies)):
                budgeted = budgeted_amounts_dict.get(currency, 0.0)
                spent = spent_amounts_dict.get(currency, 0.0)
                remaining = budgeted - spent

                progress_percentage = (spent / budgeted * 100) if budgeted > 0 else 0
                color = "success"
                if budgeted > 0:
                    if progress_percentage > 100: color = "danger"
                    elif progress_percentage > 75: color = "warning"
                elif spent > 0 : color = "danger" # Spent with no budget or zero budget

                card_content.append(html.Strong(f"{currency}:"))
                card_content.append(html.P(f"  Budgeted: {budgeted:,.2f}"))
                card_content.append(html.P(f"  Spent: {spent:,.2f}"))
                card_content.append(html.P(f"  Remaining: {remaining:,.2f}", className=f"budget-remaining-{color}"))
                if budgeted > 0 :
                    card_content.append(html.Div(dcc.Graph(
                        figure=px.bar(y=['Progress'], x=[progress_percentage], orientation='h', height=30, range_x=[0,100],color_discrete_sequence=[f'var(--bs-{color})'])
                            .update_layout(xaxis=dict(showticklabels=False, title=None, showgrid=False, zeroline=False), yaxis=dict(showticklabels=False, title=None, showgrid=False, zeroline=False),
                                           plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=0, b=0), showlegend=False, bargap=0.05),
                        config={'displayModeBar': False}
                    ), className="budget-progress-bar-container-small"))
                card_content.append(html.Hr(style={'margin': '5px 0'}))

            budget_cards.append(html.Div(card_content, className=f"budget-card card-body border-{color if all_budget_currencies else 'secondary'}"))
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

# --- Accounts Page Layout ---
def create_accounts_page_layout(accounts: List[Account]) -> html.Div:
    """ Generates the layout for the Accounts Details page, updated for multi-currency. """
    if not accounts:
        return html.Div([html.H2("Account Details"), html.P("No account data available.")], className="page")

    account_data = []
    for acc in accounts:
        utilization = None
        if acc.account_type.lower() == 'credit_card' and acc.limit is not None and acc.limit > 0 :
            utilization = calculate_credit_card_utilization(acc)

        limit_or_orig_display = "N/A"
        if acc.account_type.lower() == 'credit_card' and acc.limit is not None:
            limit_or_orig_display = f"{acc.limit:,.2f}"
        elif acc.account_type.lower() == 'loan' and acc.original_amount is not None:
            limit_or_orig_display = f"{acc.original_amount:,.2f}"

        account_data.append({
            'Account Name': acc.account_name,
            'Type': acc.account_type,
            'Balance': f"{acc.current_balance:,.2f}",
            'Currency': acc.currency, # Added Currency column
            'Limit/Original Amt': limit_or_orig_display,
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

# --- Expenses Page Layout (Minimal Multi-Currency Adaptation) ---
def create_expenses_page_layout(transactions: List[Transaction]) -> html.Div:
    """ Generates the layout for the Expenses Analysis page, minimally adapted for multi-currency. """
    if not transactions:
        return html.Div([html.H2("Expenses Analysis"), html.P("No transaction data available.")], className="page")

    transaction_data = [{
        'Date': t.date.strftime('%Y-%m-%d') if isinstance(t.date, datetime.date) else str(t.date),
        'Description': t.description,
        'Category': t.category,
        'Amount': t.amount,
        'Currency': t.currency, # Added Currency column
        'Account': t.account_affected
    } for t in transactions]
    df_transactions = pd.DataFrame(transaction_data)

    transactions_table = dash_table.DataTable(
        id='transactions-table',
        columns=[{"name": i, "id": i} for i in df_transactions.columns],
        data=df_transactions.to_dict('records'),
        page_size=15, sort_action="native", filter_action="native",
        style_table={'overflowX': 'auto'}, style_header={'backgroundColor': 'var(--bs-light)', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'left', 'padding': '5px', 'minWidth': '100px', 'width': '150px', 'maxWidth': '200px'},
    )

    # Pie chart generation - create one per currency for expenses
    expense_charts_divs = [html.H3("Expenses by Category")]
    df_expenses = df_transactions[df_transactions['Amount'] < 0].copy()
    if df_expenses.empty:
        expense_charts_divs.append(html.P("No expense data to display."))
    else:
        df_expenses['Amount'] = df_expenses['Amount'].abs()
        available_currencies = df_expenses['Currency'].unique()
        for currency in available_currencies:
            df_currency_expenses = df_expenses[df_expenses['Currency'] == currency]
            if not df_currency_expenses.empty:
                fig = px.pie(df_currency_expenses, names='Category', values='Amount',
                             title=f'Expenses in {currency}', hole=0.3)
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                expense_charts_divs.append(dcc.Graph(figure=fig, className="chart-container-half card-body"))
            else:
                expense_charts_divs.append(html.P(f"No expense data for {currency}."))

    return html.Div([
        html.H2("Expenses Analysis", className="page-title"),
        html.Div(expense_charts_divs, className="chart-row-flex"), # Use flex for multiple charts
        html.Div(transactions_table, className="table-container card-body"),
    ], className="page")

# --- Budgets Page Layout (Minimal Multi-Currency Adaptation) ---
def create_budgets_page_layout(budgets: List[Budget], transactions: List[Transaction]) -> html.Div:
    """ Generates the layout for the Budget Management page, minimally adapted for multi-currency. """
    if not budgets:
        return html.Div([html.H2("Budget Management"), html.P("No budget data available.")], className="page")

    now = datetime.datetime.now()
    current_month, current_year = now.month, now.year
    # calculate_monthly_spending returns {category: {currency: amount}}
    actual_spending_monthly = calculate_monthly_spending(transactions, current_month, current_year)

    budget_table_data = []
    for budget_item in budgets:
        # budget_item.budgeted_amount_monthly is Dict[str, float] (e.g. {"USD": 100, "EUR": 50})
        # actual_spending_monthly[budget_item.category_name] is Dict[str, float]

        spent_for_category = actual_spending_monthly.get(budget_item.category_name, {})

        all_currencies_for_budget = set(budget_item.budgeted_amount_monthly.keys()) | set(spent_for_category.keys())
        if not all_currencies_for_budget: # No budget set, no spending
             budget_table_data.append({
                'Category': budget_item.category_name,
                'Currency': "N/A",
                'Budgeted Amount': "N/A",
                'Spent Amount': "N/A",
                'Remaining/Overspent': "N/A"
            })
        for currency in sorted(list(all_currencies_for_budget)):
            budgeted = budget_item.budgeted_amount_monthly.get(currency, 0.0)
            spent = spent_for_category.get(currency, 0.0)
            remaining = budgeted - spent
            budget_table_data.append({
                'Category': budget_item.category_name,
                'Currency': currency,
                'Budgeted Amount': f"{budgeted:,.2f}",
                'Spent Amount': f"{spent:,.2f}",
                'Remaining/Overspent': f"{remaining:,.2f}"
            })

    df_budget_details = pd.DataFrame(budget_table_data)
    budgets_table = dash_table.DataTable(
        id='budgets-table',
        columns=[{"name": i, "id": i} for i in df_budget_details.columns],
        data=df_budget_details.to_dict('records'), page_size=10,
        style_table={'overflowX': 'auto'}, style_header={'backgroundColor': 'var(--bs-light)', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
    )

    # Chart for Budget vs Actual - needs to be adapted for multi-currency (e.g. grouped bar chart by currency)
    # For this pass, let's create a grouped bar chart per category, with currency groups.
    # This might get busy if many currencies. Alternative: one chart per currency.
    # Let's try one chart, x=Category, y=Amount, color=Type, facet_col="Currency" (if few currencies)
    # Or, stick to the prompt's idea: Category | Currency | Type (Budgeted/Spent) | Amount

    chart_df_data = []
    for item in budget_table_data:
        if item['Currency'] != "N/A": # Avoid trying to float "N/A"
            chart_df_data.append({'Category': item['Category'], 'Currency': item['Currency'], 'Type': 'Budgeted', 'Amount': float(str(item['Budgeted Amount']).replace(',', ''))})
            chart_df_data.append({'Category': item['Category'], 'Currency': item['Currency'], 'Type': 'Spent', 'Amount': float(str(item['Spent Amount']).replace(',', ''))})

    budget_vs_actual_fig = html.P("Budget vs Actual chart needs refinement for multi-currency display.")
    if chart_df_data:
        df_budget_chart = pd.DataFrame(chart_df_data)
        if not df_budget_chart.empty:
            try:
                fig = px.bar(df_budget_chart, x="Category", y="Amount", color="Type", barmode="group",
                             facet_col="Currency", # Separate charts by currency
                             title=f"Budget vs. Actual Spending - {datetime.date(current_year, current_month, 1).strftime('%B %Y')}")
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                fig.update_xaxes(matches=None) # Allow x-axes to be independent for each facet
                budget_vs_actual_fig = dcc.Graph(id='budget-vs-actual-chart', figure=fig)
            except Exception as e:
                 budget_vs_actual_fig = html.P(f"Could not generate budget chart: {e}")


    return html.Div([
        html.H2(f"Budget Management - {datetime.date(current_year, current_month, 1).strftime('%B %Y')}", className="page-title"),
        budget_vs_actual_fig,
        html.Div(budgets_table, className="table-container card-body")
    ], className="page")

# --- Net Worth Page Layout ---
def create_net_worth_page_layout(transactions: List[Transaction], accounts: List[Account]) -> html.Div:
    """ Generates the layout for the Net Worth Tracker page, updated for multi-currency. """
    account_summaries = calculate_account_summaries(accounts)
    net_worth_data = account_summaries.get('net_worth', {})
    net_worth_str = format_currency_dict(net_worth_data) if net_worth_data else "N/A (No account data)"

    net_worth_display = [
        html.H2("Net Worth Tracker", className="page-title"),
        html.Div([
            html.H3(f"Current Net Worth: {net_worth_str}"),
            html.P("Detailed historical net worth tracking is a feature planned for future development."),
        ], className="card-body section-container")
    ]
    return html.Div(net_worth_display, className="page")
