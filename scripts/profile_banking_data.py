import pandas as pd
from pathlib import Path


# --------------------------------------------------
# File paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DAY_1_DIR = BASE_DIR / "data" / "day_1"


# --------------------------------------------------
# Load Day 1 datasets
# --------------------------------------------------

customers = pd.read_csv(
    DAY_1_DIR / "customers.csv"
)

accounts = pd.read_csv(
    DAY_1_DIR / "accounts.csv"
)

transactions = pd.read_csv(
    DAY_1_DIR / "transactions.csv"
)


# ==================================================
# CUSTOMER PROFILING
# ==================================================

print("\n" + "=" * 60)
print("DAY 1 CUSTOMER PROFILE")
print("=" * 60)

print("\nRows:", len(customers))
print("Columns:", len(customers.columns))

print("\nNull Counts:")
print(customers.isnull().sum())

print("\nDuplicate customer_id:")
print(
    customers.duplicated(
        subset=["customer_id"]
    ).sum()
)

print("\nKYC Distribution:")
print(
    customers["kyc_status"].value_counts()
)


# ==================================================
# ACCOUNT PROFILING
# ==================================================

print("\n" + "=" * 60)
print("DAY 1 ACCOUNT PROFILE")
print("=" * 60)

print("\nRows:", len(accounts))
print("Columns:", len(accounts.columns))

print("\nNull Counts:")
print(accounts.isnull().sum())

print("\nDuplicate account_id:")
print(
    accounts.duplicated(
        subset=["account_id"]
    ).sum()
)

print("\nAccount Type Distribution:")
print(
    accounts["account_type"].value_counts()
)

print("\nAccount Status Distribution:")
print(
    accounts["account_status"].value_counts()
)


# ==================================================
# TRANSACTION PROFILING
# ==================================================

print("\n" + "=" * 60)
print("DAY 1 TRANSACTION PROFILE")
print("=" * 60)

print("\nRows:", len(transactions))
print("Columns:", len(transactions.columns))

print("\nColumn Names:")
print(transactions.columns.tolist())

print("\nNull Counts:")
print(transactions.isnull().sum())

print("\nDuplicate transaction_id:")
print(
    transactions.duplicated(
        subset=["transaction_id"]
    ).sum()
)

print("\nTransaction Type Distribution:")
print(
    transactions["transaction_type"].value_counts()
)

print("\nTransaction Status Distribution:")
print(
    transactions["transaction_status"].value_counts()
)

print("\nMerchant Category Distribution:")
print(
    transactions["merchant_category"].value_counts()
)

print("\nTransaction Amount Statistics:")
print(
    transactions["amount"].describe()
)


# ==================================================
# BUSINESS RULE VALIDATION
# ==================================================

print("\n" + "=" * 60)
print("BUSINESS RULE VALIDATION")
print("=" * 60)


# --------------------------------------------------
# Validate customer -> account relationship
# --------------------------------------------------

invalid_accounts = accounts[
    ~accounts["customer_id"].isin(
        customers["customer_id"]
    )
]

print(
    "\nAccounts with missing customer:",
    len(invalid_accounts)
)


# --------------------------------------------------
# Validate account -> transaction relationship
# --------------------------------------------------

invalid_transactions = transactions[
    ~transactions["account_id"].isin(
        accounts["account_id"]
    )
]

print(
    "Transactions with missing account:",
    len(invalid_transactions)
)


# --------------------------------------------------
# Validate transaction types
# --------------------------------------------------

valid_transaction_types = {
    "CREDIT",
    "DEBIT"
}

invalid_transaction_types = transactions[
    ~transactions["transaction_type"].isin(
        valid_transaction_types
    )
]

print(
    "Transactions with invalid type:",
    len(invalid_transaction_types)
)


# --------------------------------------------------
# Validate transaction statuses
# --------------------------------------------------

valid_transaction_statuses = {
    "SUCCESS",
    "FAILED",
    "PENDING"
}

invalid_transaction_statuses = transactions[
    ~transactions["transaction_status"].isin(
        valid_transaction_statuses
    )
]

print(
    "Transactions with invalid status:",
    len(invalid_transaction_statuses)
)


# --------------------------------------------------
# Validate amounts
# --------------------------------------------------

invalid_amounts = transactions[
    transactions["amount"] <= 0
]

print(
    "Transactions with amount <= 0:",
    len(invalid_amounts)
)


# --------------------------------------------------
# Accounts per customer
# --------------------------------------------------

accounts_per_customer = (
    accounts
    .groupby("customer_id")
    .size()
)

print(
    "\nMinimum accounts per customer:",
    accounts_per_customer.min()
)

print(
    "Maximum accounts per customer:",
    accounts_per_customer.max()
)

print(
    "Customers represented in accounts:",
    accounts["customer_id"].nunique()
)


# --------------------------------------------------
# Transaction timestamp validation
# --------------------------------------------------

parsed_timestamps = pd.to_datetime(
    transactions["transaction_timestamp"],
    errors="coerce"
)

invalid_timestamps = (
    parsed_timestamps.isna().sum()
)

print(
    "\nInvalid transaction timestamps:",
    invalid_timestamps
)


# ==================================================
# SAMPLE RECORDS
# ==================================================

print("\n" + "=" * 60)
print("SAMPLE RECORDS")
print("=" * 60)

print("\nFirst 5 Customers:")
print(customers.head())

print("\nFirst 5 Accounts:")
print(accounts.head())

print("\nFirst 5 Transactions:")
print(transactions.head())