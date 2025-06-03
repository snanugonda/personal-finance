import datetime
from typing import Dict # Added Dict

class Transaction:
    """
    Represents a single financial transaction.
    """
    def __init__(self, date: datetime.date | str, description: str, category: str,
                 amount: float, account_affected: str, currency: str): # Added currency
        """
        Initializes a Transaction object.

        Args:
            date: The date of the transaction (datetime.date object or string).
            description: A description of the transaction.
            category: The category of the transaction (e.g., 'Groceries', 'Salary').
            amount: The amount of the transaction (positive for income, negative for expense).
            account_affected: The name of the account affected by this transaction.
            currency: The currency code for the transaction amount (e.g., "USD", "EUR").
        """
        self.date: datetime.date | str = date
        self.description: str = description
        self.category: str = category
        self.amount: float = amount
        self.account_affected: str = account_affected
        self.currency: str = currency # Added currency

    def __repr__(self) -> str:
        return (f"Transaction(date={self.date!r}, description={self.description!r}, "
                f"category={self.category!r}, amount={self.amount:.2f}, "
                f"currency={self.currency!r}, account_affected={self.account_affected!r})") # Added currency

class Account:
    """
    Represents a financial account.
    """
    def __init__(self, account_name: str, account_type: str, current_balance: float, currency: str, # Added currency
                 limit: float | None = None, original_amount: float | None = None,
                 interest_rate: float | None = None):
        """
        Initializes an Account object.

        Args:
            account_name: The name of the account (e.g., 'Chase Checking').
            account_type: The type of account (e.g., 'checking', 'savings', 'credit_card').
            current_balance: The current balance of the account in its specified currency.
            currency: The currency code for the account's balance (e.g., "USD", "EUR").
            limit: The credit limit (for credit cards), in the account's currency. Defaults to None.
            original_amount: The original loan amount (for loans), in the account's currency. Defaults to None.
            interest_rate: The interest rate (for credit cards/loans). Defaults to None.
        """
        self.account_name: str = account_name
        self.account_type: str = account_type
        self.current_balance: float = current_balance
        self.currency: str = currency # Added currency
        self.limit: float | None = limit
        self.original_amount: float | None = original_amount
        self.interest_rate: float | None = interest_rate

    def __repr__(self) -> str:
        return (f"Account(account_name={self.account_name!r}, account_type={self.account_type!r}, "
                f"current_balance={self.current_balance:.2f}, currency={self.currency!r}, " # Added currency
                f"limit={self.limit}, original_amount={self.original_amount}, "
                f"interest_rate={self.interest_rate})")

class Budget:
    """
    Represents a budget category and its associated spending, supporting multiple currencies.
    """
    def __init__(self, category_name: str, budgeted_amount_monthly: Dict[str, float]): # Changed type
        """
        Initializes a Budget object.

        Args:
            category_name: The name of the budget category (e.g., 'Dining Out').
            budgeted_amount_monthly: A dictionary where keys are currency codes (e.g., "USD")
                                     and values are the allocated monthly budget amounts for this category
                                     in that currency. Example: {"USD": 500.00, "EUR": 50.00}
        """
        self.category_name: str = category_name
        self.budgeted_amount_monthly: Dict[str, float] = budgeted_amount_monthly # Changed type
        self.actual_spending_monthly: Dict[str, float] = {}  # Changed type, initialized to empty dict

    def __repr__(self) -> str:
        return (f"Budget(category_name={self.category_name!r}, "
                f"budgeted_amount_monthly={self.budgeted_amount_monthly!r}, " # Changed type
                f"actual_spending_monthly={self.actual_spending_monthly!r})") # Changed type
