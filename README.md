# Personal Financial Data Visualizer

## Overview/Description

This application provides a web-based user interface for visualizing personal financial data. It helps users understand their spending habits, track account balances, monitor budgets, and view their overall net worth across multiple currencies. The application is built using Python, with Dash and Plotly for the interactive web interface and data visualizations. Account and budget configurations are loaded from JSON files, while transaction data is loaded from a directory of CSV files.

## Features

-   **Data Loading:**
    -   Imports account configurations from `accounts_setup.json` (supports multiple currencies per account).
    -   Imports budget configurations from `budget_setup.json` (supports multi-currency monthly budget amounts per category).
    -   Loads all transactions from CSV files within the `data/transactions_data/` directory.
-   **Multi-Currency Support:** Core data models, calculations, and UI elements are designed to handle and display financial data in multiple currencies.
-   **Automated Transaction Categorization:** Automatically categorizes transactions based on keywords found in their descriptions.
-   **Main Dashboard:**
    -   Displays current net worth, summarized per currency.
    -   Summarizes total assets and liabilities, per currency.
    -   Shows a monthly income vs. expense bar chart, grouped by currency for the current month.
    -   Provides an overview of budget progress for the current month, detailed per currency for each budget category.
-   **Expenses Page:**
    -   Presents a detailed, sortable, and filterable table of all transactions, including their currency.
    -   Visualizes expenses by category using separate pie charts for each currency.
-   **Accounts Page:**
    -   Lists all financial accounts with their types, current balances, and currency.
    -   For credit cards, displays credit limit, interest rate, and utilization percentage (calculated within the account's currency).
    -   For loans, shows the original loan amount and interest rate (in the account's currency).
-   **Budgets Page:**
    -   Compares budgeted monthly amounts against actual spending for each category, detailed per currency.
    -   Shows remaining or overspent amounts per currency.
    -   Includes a bar chart visualizing budgeted vs. actual spending, faceted by currency.
-   **Net Worth Page:**
    -   Displays the current calculated net worth, summarized per currency.
    -   (Note: Historical net worth tracking is a planned future enhancement).
-   **Docker Support:** Includes a `Dockerfile` for easy building and running the application in a containerized environment.

## Directory Structure

-   `app.py`: The main Dash application file. It defines the app instance, overall UI layout (including navigation), and manages callbacks for interactivity and page routing.
-   `models.py`: Contains Python class definitions for core data structures: `Transaction`, `Account`, and `Budget`, all supporting multi-currency.
-   `data_loader.py`: Includes functions responsible for reading and parsing data from JSON configuration files and the directory of transaction CSVs.
-   `core_logic.py`: Houses the business logic of the application. This includes functions for processing transactions (like updating account balances with currency matching), transaction categorization rules, and multi-currency financial calculations.
-   `layouts.py`: Defines the Dash layout components for each distinct page of the application, adapted for multi-currency display.
-   `data/`: This directory holds user-supplied data:
    -   `accounts_setup.json`: JSON file for defining all financial accounts.
    -   `budget_setup.json`: JSON file for defining monthly budgets per category.
    -   `transactions_data/`: A subdirectory containing individual CSV files for transactions, where each CSV's filename links to an account.
-   `Dockerfile`: Instructions for building a Docker image of the application.
-   `requirements.txt`: Lists all Python package dependencies.

## Setup and Installation

### Prerequisites

-   Python 3.9+
-   `uv` (or `pip`) for Python package management. `uv` is recommended for faster dependency resolution.
-   Docker (recommended for the easiest setup and deployment).

### Installation Steps

1.  **Clone the Repository** (or download the source code):
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a Virtual Environment** (Optional, but highly recommended if not using Docker):
    ```bash
    python -m venv venv
    ```
    Activate the virtual environment:
    -   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    -   On Windows:
        ```bash
        venv\Scripts\activate
        ```

3.  **Install Dependencies:**
    If you don't have `uv` installed: `pip install uv`
    Then, install the project dependencies:
    ```bash
    uv pip install -r requirements.txt
    ```
    (If using `pip` directly: `pip install -r requirements.txt`)

## Data Input

Data for the application is provided through JSON configuration files and a directory of CSV transaction files, all located within the `data/` directory.

### Configuration Files (in `data/` directory)

1.  **`data/accounts_setup.json`**:
    *   **Purpose:** Defines all your financial accounts.
    *   **Format:** A JSON array of account objects.
    *   **Account Object Fields:**
        *   `AccountName` (string): A unique name for the account (e.g., "Main Checking USD").
        *   `AccountType` (string): Type of account (e.g., 'checking', 'savings', 'credit_card', 'loan', 'investment').
        *   `InitialBalance` (number): The starting balance of the account.
        *   `Currency` (string): The currency code for this account (e.g., "USD", "EUR", "GBP").
        *   `Limit_or_OriginalAmount` (number, optional): For 'credit_card' types, this is the credit limit. For 'loan' types, this is the original loan amount. In the account's currency.
        *   `InterestRate` (number, optional): Annual interest rate as a decimal (e.g., `0.05` for 5%).

2.  **`data/budget_setup.json`**:
    *   **Purpose:** Defines your monthly budgets for various spending categories.
    *   **Format:** A JSON object where each key is a category name (e.g., "Groceries").
    *   **Category Structure:** The value for each category key is an object containing:
        *   `budgeted_amount_monthly` (object): A dictionary mapping currency codes to budgeted amounts for that category.
            *   Example: `"Groceries": { "budgeted_amount_monthly": {"USD": 500, "EUR": 450} }`

### Transactional Data (in `data/transactions_data/` directory)

*   **Purpose:** This directory holds all your transaction data, with each account's transactions typically in a separate CSV file.
*   **File Processing:** The application processes all `*.csv` files found directly within this subdirectory.
*   **Filename Convention for Account Linking:** The base filename (without the `.csv` extension) of each transaction file is used as the `AccountName` to link those transactions to an account defined in `accounts_setup.json`.
    *   Example: Transactions in `my_checking_usd.csv` will be associated with the account named "my_checking_usd". Ensure this matches an `AccountName` in your accounts setup.
*   **CSV Columns per File:** Each CSV file in this directory should contain the following columns:
    *   `Date` (string): The date of the transaction (format: `YYYY-MM-DD`).
    *   `Description` (string): A textual description of the transaction.
    *   `Amount` (number): The monetary value. Negative for expenses (e.g., `-50.25`), positive for income (e.g., `2000.00`).
    *   `Currency` (string): The currency code for this transaction's amount (e.g., "USD", "EUR"). This should match the currency of the account it belongs to for balance updates.
    *   `Category` (string, optional): An initial category for the transaction. The application may re-categorize it based on rules in `core_logic.py`. If omitted, it defaults to 'Uncategorized'.

## Running the Application

### Locally (using Python directly)

1.  **Prepare Data:**
    *   Create and place your `accounts_setup.json` and `budget_setup.json` files into the `data/` directory.
    *   Create the `data/transactions_data/` subdirectory.
    *   Place your transaction CSV files (following the filename convention) into the `data/transactions_data/` subdirectory.
2.  **Run the App:** Navigate to the project's root directory in your terminal and execute:
    ```bash
    python app.py
    ```
3.  **Access in Browser:** Open your web browser and go to `http://127.0.0.1:8050` (or `http://0.0.0.0:8050` as indicated in the terminal output).

### With Docker (Recommended)

1.  **Prepare Data:** As above, ensure your `accounts_setup.json`, `budget_setup.json` are in `data/`, and your transaction CSVs are in `data/transactions_data/` on your host machine.
2.  **Build the Docker Image:** From the project's root directory, run:
    ```bash
    docker build -t financial-visualizer .
    ```
3.  **Run the Docker Container:**
    This command runs the container and mounts your entire local `data` directory (including `transactions_data/` and JSON files) into the container's `/app/data` directory.
    -   For macOS/Linux:
        ```bash
        docker run -p 8050:8050 -v "$(pwd)/data:/app/data" financial-visualizer
        ```
    -   For Windows (Command Prompt/PowerShell):
        ```bash
        docker run -p 8050:8050 -v "%cd%/data:/app/data" financial-visualizer
        ```
    *(Note: Ensure Docker Desktop has permission to access the specified directory if using Windows/macOS.)*
4.  **Access in Browser:** Open your web browser and go to `http://localhost:8050`.

## Transaction Categorization

The application automatically attempts to categorize transactions based on a predefined set of rules. These rules are defined as a Python dictionary named `CATEGORIZATION_RULES` within the `core_logic.py` file.

The categorization works by performing a case-insensitive search for keywords (defined as keys in the `CATEGORIZATION_RULES` dictionary) within the transaction's description. If a keyword is found, the transaction is assigned the corresponding category (the value associated with that keyword). If no rule matches, or if the transaction's initial category is empty or generic (like 'Uncategorized'), it will be labeled as 'Uncategorized'.

You can customize these rules by editing the `CATEGORIZATION_RULES` dictionary in `core_logic.py` to better suit your spending patterns.

## Future Enhancements

This application provides a solid foundation for personal finance visualization. Potential future enhancements could include:

-   **Database Integration:** Replace file-based data loading with a database for more robust data storage and querying.
-   **User Authentication & Management:** Secure access, potentially supporting multiple users.
-   **User-Editable Categories & Rules:** Allow users to manage categorization rules and categories directly through the UI.
-   **Currency Conversion:** Option to view reports in a single preferred currency, with exchange rate handling.
-   **Advanced Charting & Reporting:** More sophisticated visualizations, custom date range filtering, and downloadable reports.
-   **Historical Net Worth Tracking:** Develop robust logic to accurately calculate and display net worth changes over time.
-   **Investment Tracking:** More detailed tracking of investment performance.
-   **Recurring Transactions:** Ability to define and manage recurring transactions.
-   **Data Import/Export:** More flexible data import options and the ability to export processed data or reports.
-   **Improved UI/UX:** Further theme customization and enhanced user experience features.