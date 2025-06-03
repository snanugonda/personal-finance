import pandas as pd
from models import Transaction, Account, Budget # Account, Budget might be used by other functions if kept
from typing import List, Dict
import datetime
import json
import os # Added
import glob # Added

# --- JSON Loaders (from previous step) ---

def load_accounts_from_json(file_path: str) -> List[Account]:
    """
    Loads account setup data from a JSON file.
    (Implementation from previous step - assumed correct)
    """
    accounts: List[Account] = []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        if not isinstance(data, list):
            print(f"Error: JSON data in {file_path} is not a list as expected.")
            return []
        for acc_data in data:
            if not isinstance(acc_data, dict):
                print(f"Warning: Found non-object item in account list in {file_path}. Skipping.")
                continue
            try:
                account_name = acc_data['AccountName']
                account_type = acc_data['AccountType']
                initial_balance = float(acc_data['InitialBalance'])
                currency = acc_data['Currency']
                limit_or_original = acc_data.get('Limit_or_OriginalAmount')
                limit = None
                original_amount = None
                if account_type.lower() == 'credit_card' and limit_or_original is not None:
                    limit = float(limit_or_original)
                elif account_type.lower() == 'loan' and limit_or_original is not None:
                    original_amount = float(limit_or_original)
                interest_rate_val = acc_data.get('InterestRate')
                interest_rate = float(interest_rate_val) if interest_rate_val is not None else None
                accounts.append(Account(account_name=account_name, account_type=account_type, current_balance=initial_balance, currency=currency, limit=limit, original_amount=original_amount, interest_rate=interest_rate))
            except KeyError as e:
                print(f"Warning: Missing expected key '{e}' in an account object in {file_path}. Skipping this account.")
            except (ValueError, TypeError) as e:
                print(f"Warning: Error processing an account object in {file_path}: {e}. Skipping this account.")
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from {file_path}. Details: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while loading accounts from {file_path}: {e}")
    return accounts

def load_budgets_from_json(file_path: str) -> List[Budget]:
    """
    Loads budget setup data from a JSON file.
    (Implementation from previous step - assumed correct)
    """
    budgets: List[Budget] = []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            print(f"Error: JSON data in {file_path} is not an object/dictionary as expected.")
            return []
        for category_name, budget_data in data.items():
            if not isinstance(budget_data, dict):
                print(f"Warning: Budget data for category '{category_name}' in {file_path} is not an object. Skipping.")
                continue
            try:
                budgeted_amount_monthly = budget_data.get('budgeted_amount_monthly')
                if not isinstance(budgeted_amount_monthly, dict):
                    print(f"Warning: 'budgeted_amount_monthly' for category '{category_name}' in {file_path} is not a dictionary. Skipping.")
                    continue
                valid_budget_amounts = {}
                for currency, amount in budgeted_amount_monthly.items():
                    if not isinstance(currency, str) or not isinstance(amount, (int, float)):
                        print(f"Warning: Invalid currency ('{currency}') or amount ('{amount}') in 'budgeted_amount_monthly' for '{category_name}'. Skipping this currency.")
                        continue
                    valid_budget_amounts[currency] = float(amount)
                if not valid_budget_amounts:
                    print(f"Warning: No valid budget amounts found for category '{category_name}' in {file_path} after validation. Skipping.")
                    continue
                budgets.append(Budget(category_name=category_name, budgeted_amount_monthly=valid_budget_amounts))
            except KeyError as e:
                print(f"Warning: Missing expected key '{e}' in budget data for category '{category_name}' in {file_path}. Skipping this budget item.")
            except (ValueError, TypeError) as e:
                print(f"Warning: Error processing budget data for '{category_name}' in {file_path}: {e}. Skipping this budget item.")
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from {file_path}. Details: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while loading budgets from {file_path}: {e}")
    return budgets

# --- New Transaction Loader for Directory ---

def load_all_transactions_from_directory(directory_path: str) -> List[Transaction]:
    """
    Loads all transactions from CSV files within a specified directory.
    The AccountName for transactions in each file is derived from the filename.

    Args:
        directory_path: The path to the directory containing transaction CSV files.

    Returns:
        A list of all Transaction objects found and processed from the CSV files.
        Returns an empty list if the directory doesn't exist, contains no CSVs,
        or if critical errors occur during processing.
    """
    all_transactions: List[Transaction] = []

    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return all_transactions

    csv_files = glob.glob(os.path.join(directory_path, '*.csv'))

    if not csv_files:
        print(f"Info: No CSV files found in directory '{directory_path}'.")
        return all_transactions

    # Expected columns in each transaction CSV
    # Category is optional at this stage, will be set by core_logic
    required_csv_columns = ['Date', 'Description', 'Amount', 'Currency']

    for file_path in csv_files:
        try:
            # Derive AccountName from filename (without extension)
            account_name_from_file = os.path.splitext(os.path.basename(file_path))[0]

            print(f"Info: Processing transaction file: '{file_path}' for account '{account_name_from_file}'")

            df = pd.read_csv(file_path)

            if df.empty:
                print(f"Warning: File '{file_path}' is empty. Skipping.")
                continue

            # Check for required columns in this specific CSV
            if not all(col in df.columns for col in required_csv_columns):
                missing_cols = [col for col in required_csv_columns if col not in df.columns]
                print(f"Warning: File '{file_path}' is missing required columns: {missing_cols}. Skipping this file.")
                continue

            for index, row in df.iterrows():
                try:
                    # Date parsing
                    try:
                        transaction_date = pd.to_datetime(row['Date']).date()
                    except ValueError:
                        print(f"Warning: Could not parse date '{row['Date']}' in '{file_path}' at row {index+2}. Skipping this transaction.")
                        continue

                    description = str(row['Description'])
                    amount = float(row['Amount'])
                    currency = str(row['Currency'])

                    # Category can be initially empty or a default, to be set by core_logic
                    # If CSV has a category column, it can be used as an initial hint
                    initial_category = str(row.get('Category', 'Uncategorized'))

                    all_transactions.append(
                        Transaction(
                            date=transaction_date,
                            description=description,
                            amount=amount,
                            currency=currency,
                            account_affected=account_name_from_file, # Derived from filename
                            category=initial_category
                        )
                    )
                except (ValueError, TypeError) as e:
                    print(f"Warning: Error processing row {index+2} in '{file_path}': {e}. Skipping this transaction.")
                except KeyError as e: # Should be caught by column check, but good for safety
                    print(f"Warning: Missing expected data column '{e}' in row {index+2} of '{file_path}'. Skipping this transaction.")

        except pd.errors.EmptyDataError:
            print(f"Warning: File '{file_path}' is empty (pandas error). Skipping.")
        except FileNotFoundError: # Should not happen if glob works correctly, but for safety
            print(f"Error: File '{file_path}' not found during processing (should have been caught earlier). Skipping.")
        except Exception as e:
            print(f"An unexpected error occurred while processing file '{file_path}': {e}. Skipping this file.")

    print(f"Info: Successfully loaded {len(all_transactions)} transactions from {len(csv_files)} files in '{directory_path}'.")
    return all_transactions

# The old load_transactions_from_csv function is now removed.
