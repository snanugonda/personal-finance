from typing import List, Dict, Optional # Keep Optional if used elsewhere, ensure Dict
from models import Transaction, Account, Budget
import datetime
from collections import defaultdict # Added defaultdict

# --- Part 1: Transaction Processing and Categorization ---

CATEGORIZATION_RULES: Dict[str, str] = {
    'amazon': 'Shopping',
    'amzn': 'Shopping',
    'starbucks': 'Food/Drinks',
    'coffee': 'Food/Drinks',
    'salary': 'Income',
    'payroll': 'Income',
    'rent': 'Housing',
    'mortgage': 'Housing',
    'groceries': 'Groceries',
    'restaurant': 'Food/Drinks',
    'gas': 'Transportation',
    'uber': 'Transportation',
    'lyft': 'Transportation',
    'internet': 'Bills & Utilities',
    'spotify': 'Entertainment',
    'netflix': 'Entertainment',
    'pharmacy': 'Healthcare',
    'doctor': 'Healthcare',
}

def categorize_transaction(transaction: Transaction, rules: Dict[str, str]) -> str:
    """
    Categorizes a transaction based on keywords in its description.
    (This function remains largely unchanged as categorization is not currency-specific yet)

    Args:
        transaction: The Transaction object to categorize.
        rules: A dictionary where keys are keywords (lowercase) and values are categories.

    Returns:
        The assigned category. The transaction.category is updated in place.
    """
    description_lower = transaction.description.lower()
    for keyword, category in rules.items():
        if keyword in description_lower:
            transaction.category = category
            return category

    if not transaction.category or transaction.category.lower() in ['uncategorized', '', 'other']:
        transaction.category = 'Uncategorized'
    return transaction.category

def process_transactions(transactions: List[Transaction], accounts: List[Account], categorization_rules: Dict[str, str] = CATEGORIZATION_RULES) -> None:
    """
    Processes a list of transactions: categorizes them and updates account balances,
    checking for currency consistency.

    Args:
        transactions: A list of Transaction objects.
        accounts: A list of Account objects. Balances will be updated in place.
        categorization_rules: Rules for categorizing transactions.
    """
    for transaction in transactions:
        categorize_transaction(transaction, categorization_rules)

        account_found = False
        for acc in accounts:
            if acc.account_name == transaction.account_affected:
                account_found = True
                # Check for currency match before updating balance
                if acc.currency == transaction.currency:
                    acc.current_balance += transaction.amount
                else:
                    print(f"Warning: Currency mismatch for transaction '{transaction.description}' (ID: TBD if IDs are added) "
                          f"on account '{acc.account_name}'. Transaction currency: {transaction.currency}, "
                          f"Account currency: {acc.currency}. Skipping balance update for this transaction.")
                break

        if not account_found:
            print(f"Warning: Account '{transaction.account_affected}' for transaction '{transaction.description}' not found. Balance not updated.")

# --- Part 2: Budget Management (Multi-Currency) ---

def calculate_monthly_spending(transactions: List[Transaction], target_month: int, target_year: int) -> Dict[str, Dict[str, float]]:
    """
    Calculates total spending per category and currency for a specific month and year.

    Args:
        transactions: A list of Transaction objects.
        target_month: The month (1-12) to filter transactions for.
        target_year: The year to filter transactions for.

    Returns:
        A dictionary where keys are category names, and values are dictionaries
        mapping currency codes to total positive spending amounts for that category
        in that currency (e.g., {'Groceries': {'USD': 150.75, 'EUR': 50.20}}).
    """
    spending_by_category_currency: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for transaction in transactions:
        if not isinstance(transaction.date, datetime.date):
            try:
                transaction_date = datetime.datetime.strptime(str(transaction.date), "%Y-%m-%d").date()
            except ValueError:
                print(f"Warning: Could not parse date '{transaction.date}' for transaction '{transaction.description}'. Skipping for monthly spending.")
                continue
        else:
            transaction_date = transaction.date

        if transaction.amount < 0 and transaction_date.month == target_month and transaction_date.year == target_year:
            category = transaction.category if transaction.category else 'Uncategorized'
            # Accumulate spending by currency for the category
            spending_by_category_currency[category][transaction.currency] += abs(transaction.amount)

    return dict(spending_by_category_currency) # Convert back to dict for cleaner output if preferred

# --- Part 3: Account Summaries (Multi-Currency) ---

def calculate_account_summaries(accounts: List[Account]) -> Dict[str, Dict[str, float]]:
    """
    Calculates total assets, total liabilities, and net worth from a list of accounts,
    summed per currency.

    Args:
        accounts: A list of Account objects.

    Returns:
        A dictionary with keys 'total_assets', 'total_liabilities', and 'net_worth'.
        Each of these is a dictionary mapping currency codes to the summed amounts.
        Example: {'total_assets': {'USD': 5000.00, 'EUR': 200.00}, ...}
    """
    summaries: Dict[str, Dict[str, float]] = {
        "total_assets": defaultdict(float),
        "total_liabilities": defaultdict(float),
        "net_worth": defaultdict(float)
    }

    asset_types = ['checking', 'savings', 'investment']
    liability_types = ['credit_card', 'loan']

    for account in accounts:
        account_currency = account.currency
        if account.account_type.lower() in asset_types:
            summaries["total_assets"][account_currency] += account.current_balance
        elif account.account_type.lower() in liability_types:
            # Assuming positive current_balance for credit cards/loans means debt owed.
            # If a credit card has a negative balance (credit), it reduces liabilities for that currency.
            summaries["total_liabilities"][account_currency] += account.current_balance

    # Calculate net worth for each currency
    all_currencies = set(summaries["total_assets"].keys()) | set(summaries["total_liabilities"].keys())
    for curr in all_currencies:
        assets_in_curr = summaries["total_assets"].get(curr, 0.0)
        liabilities_in_curr = summaries["total_liabilities"].get(curr, 0.0)
        summaries["net_worth"][curr] = assets_in_curr - liabilities_in_curr

    # Convert defaultdicts to dicts for cleaner output if preferred
    summaries["total_assets"] = dict(summaries["total_assets"])
    summaries["total_liabilities"] = dict(summaries["total_liabilities"])
    summaries["net_worth"] = dict(summaries["net_worth"])

    return summaries

def calculate_credit_card_utilization(account: Account) -> float:
    """
    Calculates the credit utilization for a single credit card account.
    This calculation is currency-specific to the account (balance and limit are in account.currency).

    Args:
        account: An Account object (must be a credit card).

    Returns:
        The credit utilization percentage (0-100), or 0.0 if not applicable,
        limit is zero/None, account is not a credit card, or an error occurs.
    """
    if account.account_type.lower() == 'credit_card':
        current_debt = account.current_balance
        limit = account.limit if account.limit is not None else 0.0

        if limit > 0:
            if current_debt < 0:
                return 0.0
            utilization = (current_debt / limit) * 100
            return max(0.0, min(utilization, 100.0))
        else:
            return 0.0
    return 0.0
