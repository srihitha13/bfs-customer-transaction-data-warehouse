import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


# --------------------------------------------------
# Load all three days
# --------------------------------------------------

day1_customers = pd.read_csv(
    DATA_DIR / "day_1" / "customers.csv"
)

day2_customers = pd.read_csv(
    DATA_DIR / "day_2" / "customers.csv"
)

day3_customers = pd.read_csv(
    DATA_DIR / "day_3" / "customers.csv"
)

day1_accounts = pd.read_csv(
    DATA_DIR / "day_1" / "accounts.csv"
)

day2_accounts = pd.read_csv(
    DATA_DIR / "day_2" / "accounts.csv"
)

day3_accounts = pd.read_csv(
    DATA_DIR / "day_3" / "accounts.csv"
)

day1_transactions = pd.read_csv(
    DATA_DIR / "day_1" / "transactions.csv"
)

day2_transactions = pd.read_csv(
    DATA_DIR / "day_2" / "transactions.csv"
)

day3_transactions = pd.read_csv(
    DATA_DIR / "day_3" / "transactions.csv"
)


# --------------------------------------------------
# Helper: detect changed customers
# --------------------------------------------------

def find_customer_changes(old_df, new_df):

    compare_columns = [
        "address",
        "city",
        "state",
        "postal_code",
        "kyc_status"
    ]

    old_data = old_df.set_index("customer_id")
    new_data = new_df.set_index("customer_id")

    changed_mask = (
        old_data[compare_columns]
        != new_data[compare_columns]
    ).any(axis=1)

    return old_data[changed_mask].index.tolist()


# --------------------------------------------------
# Basic row counts
# --------------------------------------------------

print("=" * 65)
print("THREE-DAY SNAPSHOT VALIDATION")
print("=" * 65)

for day, customers, accounts, transactions in [
    (1, day1_customers, day1_accounts, day1_transactions),
    (2, day2_customers, day2_accounts, day2_transactions),
    (3, day3_customers, day3_accounts, day3_transactions),
]:

    print(f"\nDAY {day}")
    print("Customers:", len(customers))
    print("Accounts:", len(accounts))
    print("Transactions:", len(transactions))


# --------------------------------------------------
# Customer change validation
# --------------------------------------------------

day1_to_day2_changes = find_customer_changes(
    day1_customers,
    day2_customers
)

day2_to_day3_changes = find_customer_changes(
    day2_customers,
    day3_customers
)

print("\n" + "=" * 65)
print("CUSTOMER CHANGE VALIDATION")
print("=" * 65)

print(
    "\nDay 1 -> Day 2 changed customers:",
    len(day1_to_day2_changes)
)

print(
    "Day 2 -> Day 3 changed customers:",
    len(day2_to_day3_changes)
)


# --------------------------------------------------
# Customer ID stability
# --------------------------------------------------

print("\n" + "=" * 65)
print("CUSTOMER BUSINESS KEY VALIDATION")
print("=" * 65)

print(
    "\nDay 1 vs Day 2 customer IDs identical:",
    set(day1_customers["customer_id"])
    == set(day2_customers["customer_id"])
)

print(
    "Day 2 vs Day 3 customer IDs identical:",
    set(day2_customers["customer_id"])
    == set(day3_customers["customer_id"])
)


# --------------------------------------------------
# Transaction uniqueness across all days
# --------------------------------------------------

all_transactions = pd.concat(
    [
        day1_transactions,
        day2_transactions,
        day3_transactions
    ],
    ignore_index=True
)

print("\n" + "=" * 65)
print("TRANSACTION VALIDATION")
print("=" * 65)

print(
    "\nTotal transaction rows:",
    len(all_transactions)
)

print(
    "Unique transaction IDs:",
    all_transactions["transaction_id"].nunique()
)

print(
    "Duplicate transaction IDs:",
    all_transactions.duplicated(
        subset=["transaction_id"]
    ).sum()
)


# --------------------------------------------------
# Account -> transaction validation
# --------------------------------------------------

valid_accounts = set(
    day1_accounts["account_id"]
)

invalid_transactions = all_transactions[
    ~all_transactions["account_id"].isin(
        valid_accounts
    )
]

print(
    "Transactions with missing account:",
    len(invalid_transactions)
)


# --------------------------------------------------
# Validate account snapshots remain stable
# --------------------------------------------------

print("\n" + "=" * 65)
print("ACCOUNT SNAPSHOT VALIDATION")
print("=" * 65)

print(
    "\nDay 1 accounts equal Day 2:",
    day1_accounts.equals(day2_accounts)
)

print(
    "Day 2 accounts equal Day 3:",
    day2_accounts.equals(day3_accounts)
)


# --------------------------------------------------
# Show example SCD candidate
# --------------------------------------------------

if day1_to_day2_changes:

    sample_customer_id = (
        day1_to_day2_changes[0]
    )

    print("\n" + "=" * 65)
    print("SAMPLE SCD TYPE 2 CANDIDATE")
    print("=" * 65)

    columns = [
        "customer_id",
        "address",
        "city",
        "state",
        "postal_code",
        "kyc_status"
    ]

    print("\nDAY 1:")

    print(
        day1_customers[
            day1_customers["customer_id"]
            == sample_customer_id
        ][columns].to_string(index=False)
    )

    print("\nDAY 2:")

    print(
        day2_customers[
            day2_customers["customer_id"]
            == sample_customer_id
        ][columns].to_string(index=False)
    )

    print("\nDAY 3:")

    print(
        day3_customers[
            day3_customers["customer_id"]
            == sample_customer_id
        ][columns].to_string(index=False)
    )