# Personal Financial Data Visualizer

## Overview/Description

This application provides a web-based user interface for visualizing personal financial data. It helps users understand their spending habits, track account balances, monitor budgets, and view their overall net worth. The application is built using Python, with Dash and Plotly for the interactive web interface and data visualizations. All data is loaded from user-provided CSV files.

## Features

-   **Data Loading:** Imports financial data from CSV files for transactions, accounts, and budgets.
-   **Automated Transaction Categorization:** Automatically categorizes transactions based on keywords found in their descriptions.
-   **Main Dashboard:**
    -   Displays current net worth.
    -   Summarizes total assets and liabilities.
    -   Shows a monthly income vs. expense bar chart for the current month.
    -   Provides an overview of budget progress for the current month.
-   **Expenses Page:**
    -   Presents a detailed, sortable, and filterable table of all transactions.
    -   Visualizes expenses by category using a pie chart.
-   **Accounts Page:**
    -   Lists all financial accounts with their types and current balances.
    -   For credit cards, displays credit limit, interest rate, and utilization percentage.
    -   For loans, shows the original loan amount and interest rate.
-   **Budgets Page:**
    -   Compares budgeted monthly amounts against actual spending for each category for the current month.
    -   Shows remaining or overspent amounts.
    -   Includes a bar chart visualizing budgeted vs. actual spending.
-   **Net Worth Page:**
    -   Displays the current calculated net worth.
    -   (Note: Historical net worth tracking is a planned future enhancement).
-   **Docker Support:** Includes a `Dockerfile` for easy building and running the application in a containerized environment.

## Directory Structure

-   `app.py`: The main Dash application file. It defines the app instance, overall UI layout (including navigation), and manages callbacks for interactivity and page routing.
-   `models.py`: Contains Python class definitions for core data structures: `Transaction`, `Account`, and `Budget`.
-   `data_loader.py`: Includes functions responsible for reading and parsing data from the input CSV files (`transactions.csv`, `accounts.csv`, `budget.csv`) into the data model objects.
-   `core_logic.py`: Houses the business logic of the application. This includes functions for processing transactions (like updating account balances), transaction categorization rules, and financial calculations (e.g., monthly spending, account summaries, credit card utilization).
-   `layouts.py`: Defines the Dash layout components for each distinct page of the application (e.g., Main Dashboard, Expenses, Accounts).
-   `data/`: This directory is where the user must place their input CSV files. Example files might be provided, but actual financial data is user-supplied.
-   `Dockerfile`: Instructions for building a Docker image of the application, allowing for easy deployment and consistent runtime environments.
-   `requirements.txt`: Lists all Python package dependencies required to run the application (e.g., Dash, Pandas, Plotly).

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

### CSV File Location

All financial data must be provided in CSV files placed directly within the `data/` directory at the root of the project.

### File Formats

Ensure your CSV files adhere to the following column structures:

**1. `data/transactions.csv`**
   -   `Date`: The date of the transaction (format: `YYYY-MM-DD`).
   -   `Description`: A textual description of the transaction.
   -   `Amount`: The monetary value of the transaction. Use negative numbers for expenses (e.g., `-50.25`) and positive numbers for income (e.g., `2000.00`).
   -   `Category`: (Optional initial category) The category of the transaction (e.g., 'Groceries', 'Salary'). The application will attempt to re-categorize based on rules in `core_logic.py`.
   -   `AccountName`: The name of the account affected by this transaction. This name must correspond to an `AccountName` in `accounts.csv`.

**2. `data/accounts.csv`**
   -   `AccountName`: A unique name for the account (e.g., 'Chase Checking', 'Visa Credit Card'). This is used to link transactions.
   -   `AccountType`: The type of account. Supported types include: 'checking', 'savings', 'credit_card', 'loan', 'investment'.
   -   `InitialBalance`: The starting balance of the account. For credit cards, a positive balance usually means you owe money (liability). For loans, this is typically the principal amount owed.
   -   `Limit_or_OriginalAmount`: (Optional) For 'credit_card' types, this is the credit limit. For 'loan' types, this is the original loan amount. Can be left blank or 0 if not applicable.
   -   `InterestRate`: (Optional) The annual interest rate for the account, if applicable (e.g., for savings, credit cards, loans). Enter as a decimal (e.g., `0.05` for 5%, `0.18` for 18%).

**3. `data/budget.csv`**
   -   `Category`: The name of the budget category (e.g., 'Groceries', 'Entertainment'). This should ideally match categories used in transactions.
   -   `MonthlyAmount`: The total amount budgeted for this category per month.

## Running the Application

### Locally (using Python directly)

1.  **Prepare Data:** Ensure your `transactions.csv`, `accounts.csv`, and `budget.csv` files are correctly formatted and placed in the `data/` directory.
2.  **Run the App:** Navigate to the project's root directory in your terminal and execute:
    ```bash
    python app.py
    ```
3.  **Access in Browser:** Open your web browser and go to `http://127.0.0.1:8050` (or `http://0.0.0.0:8050` as indicated in the terminal output).

### With Docker (Recommended)

1.  **Prepare Data:** Ensure your `transactions.csv`, `accounts.csv`, and `budget.csv` files are correctly formatted and placed in the `data/` directory on your host machine.
2.  **Build the Docker Image:** From the project's root directory, run:
    ```bash
    docker build -t financial-visualizer .
    ```
3.  **Run the Docker Container:**
    This command runs the container and mounts your local `data` directory into the container's `/app/data` directory, allowing the application to access your CSV files.
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

-   **Database Integration:** Replace CSV file loading with a database (e.g., SQLite, PostgreSQL) for more robust data storage, querying, and persistence.
-   **User Authentication & Management:** Allow multiple users or secure access.
-   **User-Editable Categories & Rules:** Allow users to manage categorization rules and categories directly through the UI.
-   **Advanced Charting & Reporting:** Implement more sophisticated visualizations, custom date range filtering for all reports, and downloadable reports.
-   **Historical Net Worth Tracking:** Develop robust logic to accurately calculate and display net worth changes over time.
-   **Investment Tracking:** More detailed tracking of investment performance.
-   **Recurring Transactions:** Ability to define and manage recurring transactions.
-   **Data Import/Export:** More flexible data import options and the ability to export processed data or reports.
-   **Improved UI/UX:** Further theme customization and enhanced user experience features.