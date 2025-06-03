import pandas as pd
from models import Transaction, Account, Budget
from typing import List
import datetime

def load_transactions(file_path: str) -> List[Transaction]:
    """
    Loads transactions from a CSV file.

    Args:
        file_path: The path to the CSV file containing transaction data.
                   Expected columns: 'Date', 'Description', 'Amount', 'Category', 'AccountName'

    Returns:
        A list of Transaction objects.
        Returns an empty list if the file is not found or if there's an error parsing the file.
    """
    transactions: List[Transaction] = []
    try:
        df = pd.read_csv(file_path)

        # Check for required columns
        required_columns = ['Date', 'Description', 'Amount', 'Category', 'AccountName']
        if not all(col in df.columns for col in required_columns):
            print(f"Error: Missing one or more required columns in {file_path}. Required: {required_columns}")
            return []

        for index, row in df.iterrows():
            try:
                # Convert date, attempting common formats
                try:
                    transaction_date = pd.to_datetime(row['Date']).date()
                except ValueError:
                    print(f"Warning: Could not parse date '{row['Date']}' at row {index+2} in {file_path}. Skipping this transaction.")
                    continue

                description = str(row['Description'])
                amount = float(row['Amount'])
                category = str(row['Category'])
                account_name = str(row['AccountName'])

                transactions.append(
                    Transaction(
                        date=transaction_date,
                        description=description,
                        amount=amount,
                        category=category,
                        account_affected=account_name,
                    )
                )
            except (ValueError, TypeError) as e:
                print(f"Warning: Error processing row {index+2} in {file_path}: {e}. Skipping this transaction.")
            except KeyError as e:
                print(f"Warning: Missing expected column '{e}' in row {index+2} of {file_path}. Skipping this transaction.")

    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except pd.errors.EmptyDataError:
        print(f"Error: The file {file_path} is empty.")
    except Exception as e:
        print(f"An unexpected error occurred while loading transactions from {file_path}: {e}")
    return transactions

def load_accounts(file_path: str) -> List[Account]:
    """
    Loads accounts from a CSV file.

    Args:
        file_path: The path to the CSV file containing account data.
                   Expected columns: 'AccountName', 'AccountType', 'InitialBalance'
                   Optional columns: 'Limit_or_OriginalAmount', 'InterestRate'

    Returns:
        A list of Account objects.
        Returns an empty list if the file is not found or if there's an error parsing the file.
    """
    accounts: List[Account] = []
    try:
        df = pd.read_csv(file_path)

        required_columns = ['AccountName', 'AccountType', 'InitialBalance']
        if not all(col in df.columns for col in required_columns):
            print(f"Error: Missing one or more required columns in {file_path}. Required: {required_columns}")
            return []

        for index, row in df.iterrows():
            try:
                account_name = str(row['AccountName'])
                account_type = str(row['AccountType'])
                initial_balance = float(row['InitialBalance'])

                # Handle optional fields
                limit_or_original = row.get('Limit_or_OriginalAmount')
                limit = float(limit_or_original) if pd.notna(limit_or_original) and limit_or_original != '' else None

                interest_rate_val = row.get('InterestRate')
                interest_rate = float(interest_rate_val) if pd.notna(interest_rate_val) and interest_rate_val != '' else None

                accounts.append(
                    Account(
                        account_name=account_name,
                        account_type=account_type,
                        current_balance=initial_balance,  # Assuming InitialBalance is the current balance at load time
                        limit=limit,
                        original_amount=limit if account_type.lower() == 'loan' else None, # Assuming limit is original for loan
                        interest_rate=interest_rate,
                    )
                )
            except (ValueError, TypeError) as e:
                print(f"Warning: Error processing row {index+2} in {file_path}: {e}. Skipping this account.")
            except KeyError as e:
                print(f"Warning: Missing expected column '{e}' in row {index+2} of {file_path}. Skipping this account.")


    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except pd.errors.EmptyDataError:
        print(f"Error: The file {file_path} is empty.")
    except Exception as e:
        print(f"An unexpected error occurred while loading accounts from {file_path}: {e}")
    return accounts

def load_budgets(file_path: str) -> List[Budget]:
    """
    Loads budgets from a CSV file.

    Args:
        file_path: The path to the CSV file containing budget data.
                   Expected columns: 'Category', 'MonthlyAmount'

    Returns:
        A list of Budget objects.
        Returns an empty list if the file is not found or if there's an error parsing the file.
    """
    budgets: List[Budget] = []
    try:
        df = pd.read_csv(file_path)

        required_columns = ['Category', 'MonthlyAmount']
        if not all(col in df.columns for col in required_columns):
            print(f"Error: Missing one or more required columns in {file_path}. Required: {required_columns}")
            return []

        for index, row in df.iterrows():
            try:
                category = str(row['Category'])
                monthly_amount = float(row['MonthlyAmount'])

                budgets.append(
                    Budget(category_name=category, budgeted_amount_monthly=monthly_amount)
                )
            except (ValueError, TypeError) as e:
                print(f"Warning: Error processing row {index+2} in {file_path}: {e}. Skipping this budget item.")
            except KeyError as e:
                print(f"Warning: Missing expected column '{e}' in row {index+2} of {file_path}. Skipping this budget item.")

    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except pd.errors.EmptyDataError:
        print(f"Error: The file {file_path} is empty.")
    except Exception as e:
        print(f"An unexpected error occurred while loading budgets from {file_path}: {e}")
    return budgets
