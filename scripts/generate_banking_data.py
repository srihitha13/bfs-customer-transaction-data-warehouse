import random
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker


# --------------------------------------------------
# Configuration
# --------------------------------------------------

fake = Faker("en_IN")

Faker.seed(42)
random.seed(42)

NUM_CUSTOMERS = 1000
TRANSACTIONS_PER_DAY = 5000
CUSTOMERS_CHANGED_PER_DAY = 75

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DAY_DATES = {
    1: datetime(2026, 11, 20),
    2: datetime(2026, 11, 21),
    3: datetime(2026, 11, 22),
}


# --------------------------------------------------
# Generate baseline customers
# --------------------------------------------------

def generate_customers():

    customers = []

    for i in range(1, NUM_CUSTOMERS + 1):

        customer_id = f"C{i:05d}"

        customer = {
            "customer_id": customer_id,
            "customer_name": fake.name(),

            "date_of_birth": fake.date_of_birth(
                minimum_age=18,
                maximum_age=75
            ),

            "email": fake.email(),
            "phone": fake.phone_number(),
            "address": fake.street_address(),
            "city": fake.city(),
            "state": fake.state(),
            "postal_code": fake.postcode(),

            "kyc_status": random.choice(
                ["VERIFIED", "PENDING", "REJECTED"]
            ),

            "customer_since": fake.date_between(
                start_date="-10y",
                end_date="-1d"
            )
        }

        customers.append(customer)

    return pd.DataFrame(customers)


# --------------------------------------------------
# Generate accounts
# --------------------------------------------------

def generate_accounts(customers):

    accounts = []
    account_counter = 1

    for customer_id in customers["customer_id"]:

        # Most customers get one account.
        # Some customers get two accounts.
        num_accounts = random.choice(
            [1, 1, 1, 2]
        )

        for _ in range(num_accounts):

            account_id = f"A{account_counter:06d}"

            account = {
                "account_id": account_id,
                "customer_id": customer_id,

                "account_type": random.choice(
                    ["SAVINGS", "CURRENT"]
                ),

                "account_status": random.choice(
                    [
                        "ACTIVE",
                        "ACTIVE",
                        "ACTIVE",
                        "INACTIVE"
                    ]
                ),

                "branch_code": (
                    f"BR{random.randint(1, 50):03d}"
                ),

                "balance": round(
                    random.uniform(1000, 500000),
                    2
                ),

                "opened_date": fake.date_between(
                    start_date="-10y",
                    end_date="-1d"
                )
            }

            accounts.append(account)
            account_counter += 1

    return pd.DataFrame(accounts)


# --------------------------------------------------
# Generate transactions for one day
# --------------------------------------------------

def generate_transactions(
    accounts,
    day_number,
    starting_transaction_number
):

    transactions = []

    account_ids = accounts["account_id"].tolist()
    base_date = DAY_DATES[day_number]

    merchant_categories = [
        "GROCERY",
        "ECOMMERCE",
        "FUEL",
        "RESTAURANT",
        "UTILITIES",
        "TRAVEL",
        "TRANSFER",
        "ATM"
    ]

    for offset in range(TRANSACTIONS_PER_DAY):

        transaction_number = (
            starting_transaction_number + offset
        )

        transaction_id = (
            f"T{transaction_number:08d}"
        )

        random_seconds = random.randint(
            0,
            86399
        )

        transaction_timestamp = (
            base_date
            + timedelta(seconds=random_seconds)
        )

        transaction = {
            "transaction_id": transaction_id,

            "account_id": random.choice(
                account_ids
            ),

            "transaction_timestamp":
                transaction_timestamp.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "transaction_type": random.choice(
                ["CREDIT", "DEBIT"]
            ),

            "amount": round(
                random.uniform(10, 100000),
                2
            ),

            "transaction_status": random.choice(
                [
                    "SUCCESS",
                    "SUCCESS",
                    "SUCCESS",
                    "FAILED",
                    "PENDING"
                ]
            ),

            "merchant_category": random.choice(
                merchant_categories
            )
        }

        transactions.append(transaction)

    return pd.DataFrame(transactions)


# --------------------------------------------------
# Create changed customer snapshot
# --------------------------------------------------

def create_changed_customer_snapshot(
    previous_customers,
    day_number
):

    updated_customers = (
        previous_customers.copy(deep=True)
    )

    selected_indexes = random.sample(
        list(updated_customers.index),
        CUSTOMERS_CHANGED_PER_DAY
    )

    change_records = []

    possible_kyc_statuses = [
        "VERIFIED",
        "PENDING",
        "REJECTED"
    ]

    for index in selected_indexes:

        customer_id = updated_customers.at[
            index,
            "customer_id"
        ]

        old_address = updated_customers.at[
            index,
            "address"
        ]

        old_city = updated_customers.at[
            index,
            "city"
        ]

        old_state = updated_customers.at[
            index,
            "state"
        ]

        old_postal_code = updated_customers.at[
            index,
            "postal_code"
        ]

        old_kyc_status = updated_customers.at[
            index,
            "kyc_status"
        ]

        # Generate a new address.
        new_address = fake.street_address()
        new_city = fake.city()
        new_state = fake.state()
        new_postal_code = fake.postcode()

        # Ensure the new KYC status differs from the old one.
        new_kyc_options = [
            status
            for status in possible_kyc_statuses
            if status != old_kyc_status
        ]

        new_kyc_status = random.choice(
            new_kyc_options
        )

        updated_customers.at[
            index,
            "address"
        ] = new_address

        updated_customers.at[
            index,
            "city"
        ] = new_city

        updated_customers.at[
            index,
            "state"
        ] = new_state

        updated_customers.at[
            index,
            "postal_code"
        ] = new_postal_code

        updated_customers.at[
            index,
            "kyc_status"
        ] = new_kyc_status

        change_records.append(
            {
                "day_number": day_number,
                "customer_id": customer_id,
                "old_address": old_address,
                "new_address": new_address,
                "old_city": old_city,
                "new_city": new_city,
                "old_state": old_state,
                "new_state": new_state,
                "old_postal_code": old_postal_code,
                "new_postal_code": new_postal_code,
                "old_kyc_status": old_kyc_status,
                "new_kyc_status": new_kyc_status
            }
        )

    change_log = pd.DataFrame(change_records)

    return updated_customers, change_log


# --------------------------------------------------
# Save one day's snapshot
# --------------------------------------------------

def save_daily_snapshot(
    day_number,
    customers,
    accounts,
    transactions,
    change_log=None
):

    day_directory = (
        DATA_DIR / f"day_{day_number}"
    )

    day_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    customers.to_csv(
        day_directory / "customers.csv",
        index=False
    )

    accounts.to_csv(
        day_directory / "accounts.csv",
        index=False
    )

    transactions.to_csv(
        day_directory / "transactions.csv",
        index=False
    )

    if change_log is not None:

        change_log.to_csv(
            day_directory / "customer_changes.csv",
            index=False
        )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    # Day 1 baseline data
    day_1_customers = generate_customers()

    accounts = generate_accounts(
        day_1_customers
    )

    day_1_transactions = generate_transactions(
        accounts=accounts,
        day_number=1,
        starting_transaction_number=1
    )

    save_daily_snapshot(
        day_number=1,
        customers=day_1_customers,
        accounts=accounts,
        transactions=day_1_transactions
    )

    # Day 2 customer changes and new transactions
    (
        day_2_customers,
        day_2_change_log
    ) = create_changed_customer_snapshot(
        previous_customers=day_1_customers,
        day_number=2
    )

    day_2_transactions = generate_transactions(
        accounts=accounts,
        day_number=2,
        starting_transaction_number=5001
    )

    save_daily_snapshot(
        day_number=2,
        customers=day_2_customers,
        accounts=accounts,
        transactions=day_2_transactions,
        change_log=day_2_change_log
    )

    # Day 3 starts from the Day 2 customer snapshot
    (
        day_3_customers,
        day_3_change_log
    ) = create_changed_customer_snapshot(
        previous_customers=day_2_customers,
        day_number=3
    )

    day_3_transactions = generate_transactions(
        accounts=accounts,
        day_number=3,
        starting_transaction_number=10001
    )

    save_daily_snapshot(
        day_number=3,
        customers=day_3_customers,
        accounts=accounts,
        transactions=day_3_transactions,
        change_log=day_3_change_log
    )

    print("=" * 60)
    print("THREE-DAY BANKING DATA GENERATION COMPLETE")
    print("=" * 60)

    print("\nDay 1:")
    print(f"Customers: {len(day_1_customers)}")
    print(f"Accounts: {len(accounts)}")
    print(f"Transactions: {len(day_1_transactions)}")
    print("Customer changes: 0")

    print("\nDay 2:")
    print(f"Customers: {len(day_2_customers)}")
    print(f"Accounts: {len(accounts)}")
    print(f"Transactions: {len(day_2_transactions)}")
    print(
        "Customer changes:",
        len(day_2_change_log)
    )

    print("\nDay 3:")
    print(f"Customers: {len(day_3_customers)}")
    print(f"Accounts: {len(accounts)}")
    print(f"Transactions: {len(day_3_transactions)}")
    print(
        "Customer changes:",
        len(day_3_change_log)
    )

    print("\nExpected total daily transactions:")
    print(
        len(day_1_transactions)
        + len(day_2_transactions)
        + len(day_3_transactions)
    )


# --------------------------------------------------
# Run program
# --------------------------------------------------

if __name__ == "__main__":
    main()