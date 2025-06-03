from typing import List, Dict, Optional
from models import Transaction, Account, Budget # Budget is not used yet, but good to have for future
import datetime

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

    # If no rule matches and transaction has no pre-assigned category or it's empty/generic
    if not transaction.category or transaction.category.lower() in ['uncategorized', '', 'other']:
        transaction.category = 'Uncategorized'
    return transaction.category

def process_transactions(transactions: List[Transaction], accounts: List[Account], categorization_rules: Dict[str, str] = CATEGORIZATION_RULES) -> None:
    """
    Processes a list of transactions: categorizes them and updates account balances.

    Args:
        transactions: A list of Transaction objects.
        accounts: A list of Account objects. Balances will be updated in place.
        categorization_rules: Rules for categorizing transactions.
    """
    for transaction in transactions:
        # Categorize the transaction
        categorize_transaction(transaction, categorization_rules)

        # Update account balance
        account_found = False
        for acc in accounts:
            if acc.account_name == transaction.account_affected:
                acc.current_balance += transaction.amount
                account_found = True
                break

        if not account_found:
            print(f"Warning: Account '{transaction.account_affected}' for transaction '{transaction.description}' not found. Balance not updated.")

# --- Part 2: Budget Management (Initial Implementation) ---

def calculate_monthly_spending(transactions: List[Transaction], target_month: int, target_year: int) -> Dict[str, float]:
    """
    Calculates total spending per category for a specific month and year.

    Args:
        transactions: A list of Transaction objects.
        target_month: The month (1-12) to filter transactions for.
        target_year: The year to filter transactions for.

    Returns:
        A dictionary where keys are category names and values are total positive
        spending amounts for that category in the specified month/year.
    """
    monthly_spending: Dict[str, float] = {}

    for transaction in transactions:
        # Ensure transaction date is a datetime.date object
        if not isinstance(transaction.date, datetime.date):
            try:
                # Attempt to parse if it's a string (e.g., "YYYY-MM-DD")
                transaction_date = datetime.datetime.strptime(str(transaction.date), "%Y-%m-%d").date()
            except ValueError:
                print(f"Warning: Could not parse date '{transaction.date}' for transaction '{transaction.description}'. Skipping for monthly spending.")
                continue
        else:
            transaction_date = transaction.date

        if transaction.amount < 0 and transaction_date.month == target_month and transaction_date.year == target_year:
            category = transaction.category if transaction.category else 'Uncategorized'
            # Store spending as a positive value
            monthly_spending[category] = monthly_spending.get(category, 0.0) + abs(transaction.amount)

    return monthly_spending

# --- Part 3: Account Summaries (Initial Implementation) ---

def calculate_account_summaries(accounts: List[Account]) -> Dict[str, float]:
    """
    Calculates total assets, total liabilities, and net worth from a list of accounts.

    Args:
        accounts: A list of Account objects.

    Returns:
        A dictionary with keys 'total_assets', 'total_liabilities', and 'net_worth'.
    """
    total_assets: float = 0.0
    total_liabilities: float = 0.0

    asset_types = ['checking', 'savings', 'investment']
    liability_types = ['credit_card', 'loan']

    for account in accounts:
        if account.account_type.lower() in asset_types:
            total_assets += account.current_balance
        elif account.account_type.lower() in liability_types:
            # Assuming credit card balances are positive if they represent debt owed
            # and loan balances are also positive representing debt owed.
            # If a convention of negative balances for liabilities is used, this needs adjustment.
            # For now, we sum current_balance directly for liabilities.
            # If current_balance for a credit card is -200 (meaning $200 owed),
            # and for a loan is 10000 (meaning $10000 owed),
            # this logic needs to be consistent with how balances are stored in Account objects.
            # Let's assume positive balances for credit cards and loans mean amount owed.
            if account.account_type.lower() == 'credit_card':
                 # If balance is positive, it's debt. If it's negative (e.g. a refund/credit), it reduces liability.
                total_liabilities += account.current_balance
            elif account.account_type.lower() == 'loan':
                # Loans are typically positive representing the outstanding amount owed.
                total_liabilities += account.current_balance


    net_worth: float = total_assets - total_liabilities

    return {
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'net_worth': net_worth,
    }

def calculate_credit_card_utilization(account: Account) -> float:
    """
    Calculates the credit utilization for a single credit card account.

    Args:
        account: An Account object.

    Returns:
        The credit utilization percentage (0-100), or 0.0 if not applicable,
        limit is zero, or an error occurs.
    """
    if account.account_type.lower() == 'credit_card':
        # Assuming current_balance on a credit card is positive when money is owed.
        current_debt = account.current_balance
        limit = account.limit if account.limit is not None else 0.0

        if limit > 0:
            if current_debt < 0: # If account has a positive credit (e.g. overpayment)
                return 0.0
            utilization = (current_debt / limit) * 100
            return max(0.0, min(utilization, 100.0)) # Cap at 0-100%
        else:
            # No limit or zero limit, utilization is not meaningfully calculable or is undefined.
            # Could also return None or raise an error if current_debt > 0 and limit is 0.
            return 0.0
    return 0.0

# Placeholder for future functions if needed
# def advanced_budget_analysis(...) -> ...:
#     pass

# def investment_performance(...) -> ...:
#     pass
