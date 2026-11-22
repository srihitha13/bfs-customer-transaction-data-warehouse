BFS Customer & Transaction Data Warehouse
Project Overview
This project implements an end-to-end Banking and Financial Services (BFS) data warehouse using Google Cloud Platform, BigQuery, dbt Core, Python, and GitHub Actions.

The project demonstrates:

Medallion Architecture
Synthetic banking-data generation
Daily snapshot processing
Incremental transaction loading
Slowly Changing Dimension Type 2 (SCD Type 2)
Surrogate-key generation
Gold analytical models
dbt data-quality testing
dbt lineage
GitHub Actions Continuous Integration
Architecture
The pipeline follows this architecture:

Python + Faker
|
v
Synthetic Banking Data
Day 1 / Day 2 / Day 3
|
v
Google Cloud Storage
|
v
BigQuery Bronze
|
v
dbt Core
|
+-----------------------+
| |
v v
Silver Models dbt Snapshot
| |
| SCD Type 2
| |
+-----------+-----------+
|
v
Gold Layer
/ \
 v v
dim_customer fact_transactions
\ /
+--------------+
|
v
dbt Tests & Lineage
|
v
GitHub Actions CI
Technology Stack
Technology Purpose
Python Synthetic data generation and validation
Faker Synthetic customer data
pandas Data profiling and validation
Google Cloud Storage Raw Bronze landing layer
BigQuery Cloud data warehouse
dbt Core Transformation and modeling
dbt-bigquery BigQuery dbt adapter
dbt Snapshots SCD Type 2 history
Git Source control
GitHub Repository hosting
GitHub Actions CI automation
YAML dbt sources, snapshots, tests, and CI
Synthetic Banking Data
The project models three related entities:

CUSTOMERS
|
| customer_id
v
ACCOUNTS
|
| account_id
v
TRANSACTIONS
Customers
Customer attributes include:

customer_id
customer_name
date_of_birth
email
phone
address
city
state
postal_code
kyc_status
customer_since
KYC statuses:

VERIFIED
PENDING
REJECTED
Accounts
Account attributes include:

account_id
customer_id
account_type
account_status
branch_code
balance
opened_date
Account types:

SAVINGS
CURRENT
Transactions
Transaction attributes include:

transaction_id
account_id
transaction_timestamp
transaction_type
amount
transaction_status
merchant_category
Transaction types:

CREDIT
DEBIT
Transaction statuses:

SUCCESS
FAILED
PENDING
Three-Day Snapshot Simulation
Three daily BFS snapshots were generated.

Day Customers Accounts Transactions Customers Changed
Day 1 1,000 1,271 5,000 0
Day 2 1,000 1,271 5,000 75
Day 3 1,000 1,271 5,000 75
Total transactions:

15,000
On Day 2 and Day 3, exactly:

75 / 1000 = 7.5%
of customers were deliberately changed.

Tracked attributes included:

address
city
state
postal_code
kyc_status
These deliberate mutations provide a controlled test case for SCD Type 2.

Local Data Validation
Python and pandas were used to validate the generated data before cloud ingestion.

Validation included:

Row counts
NULL counts
Business-key uniqueness
Referential integrity
Transaction-type validation
Transaction-status validation
Positive transaction amounts
Timestamp validation
Cross-day customer comparisons
Cross-day transaction uniqueness
Validation Results
Customers: 1,000
Accounts: 1,271

Transactions per day: 5,000
Total transactions: 15,000
Unique transaction IDs: 15,000
Duplicate transaction IDs: 0

Accounts without customer: 0
Transactions without account: 0

Day 1 → Day 2 customer changes: 75
Day 2 → Day 3 customer changes: 75
Bronze Layer
The generated daily CSV files were uploaded to Google Cloud Storage using date-based paths:

bronze/
├── 2026-11-20/
│ ├── customers.csv
│ ├── accounts.csv
│ └── transactions.csv
│
├── 2026-11-21/
│ ├── customers.csv
│ ├── accounts.csv
│ └── transactions.csv
│
└── 2026-11-22/
├── customers.csv
├── accounts.csv
└── transactions.csv
The BigQuery Bronze dataset preserves each daily snapshot separately:

bfs_bronze
├── customers_day1
├── customers_day2
├── customers_day3
├── accounts_day1
├── accounts_day2
├── accounts_day3
├── transactions_day1
├── transactions_day2
└── transactions_day3
Bronze Layer Evidence
screenshots/bigquery_bronze_layer.png

dbt Core Setup
dbt Core was installed locally with the BigQuery adapter inside a Python virtual environment.

dbt Core
|
v
dbt-bigquery
|
v
GCP Service Account
|
v
BigQuery
A dedicated GCP service account is used by dbt.

The service-account JSON credential is stored outside the Git repository.

Connectivity was validated using:

dbt debug
dbt Sources
Bronze BigQuery tables are defined as dbt sources in:

models/bronze/sources.yml
For example:

{{ source('bfs_bronze', 'customers_day1') }}
Using source() allows dbt to understand upstream dependencies and include those relationships in lineage.

Silver Layer
The Silver layer performs cleaning, standardization, and incremental processing.

bfs_silver
├── current_customers
├── silver_customers
├── silver_accounts
└── silver_transactions
Silver Layer Evidence
screenshots/bigquery_silver_layer.png

Silver Customers
silver_customers standardizes customer information.

Transformations include:

Converting identifiers to strings
Trimming text
Lowercasing email addresses
Uppercasing KYC status
Converting dates with SAFE_CAST
Treating postal code as a string identifier
Silver Accounts
silver_accounts standardizes:

account_id
customer_id
account_type
account_status
branch_code
balance
opened_date
Types are normalized so that:

account_id → STRING
customer_id → STRING
balance → NUMERIC
opened_date → DATE
Incremental Transactions
silver_transactions is implemented as a dbt incremental model.

Configuration:

{{
    config(
        materialized='incremental',
        unique_key='transaction_id',
        incremental_strategy='merge'
    )
}}
The transaction IDs are non-overlapping across daily batches:

Day 1 → T00000001 - T00005000
Day 2 → T00005001 - T00010000
Day 3 → T00010001 - T00015000
The completed incremental model contains:

15,000 total rows
15,000 unique transaction IDs
Re-running the model does not duplicate the transactions already present.

Why Incremental Loads Matter
For growing transaction datasets, rebuilding all historical records on every run would repeatedly scan old data.

Incremental processing reduces unnecessary:

Data scanning
Query execution
Processing time
BigQuery compute consumption
Customer SCD Type 2
Historical customer tracking is implemented with a dbt snapshot.

The snapshot tracks changes to:

address
city
state
postal_code
kyc_status
The customer business key is:

customer_id
dbt adds validity metadata:

dbt_valid_from
dbt_valid_to
A row where:

dbt_valid_to IS NULL
represents the active version.

Snapshot Layer
The final customer snapshot is stored separately from the Silver and Gold layers:

bfs_snapshots
└── customer_snapshot
Snapshot Evidence
screenshots/bigquery_snapshot.png

SCD Type 2 Example
Customer C00441 demonstrates SCD Type 2 behavior.

An older customer version contained:

Address: 46/996, Kala Chowk
City: Salem
State: West Bengal
Postal: 677269
KYC Status: REJECTED
A later version contained:

Address: 11/06 Shankar Marg
City: Haldia
State: Jharkhand
Postal: 879397
KYC Status: PENDING
The old row received a populated:

dbt_valid_to
while the current row retains:

dbt_valid_to = NULL
The analytical dimension converts this into:

Historical row → is_current = FALSE
Current row → is_current = TRUE
SCD Type 2 Evidence
screenshots/scd_type2_customer_history.png

Gold Layer
The final analytical layer contains:

bfs_gold
├── dim_customer
└── fact_transactions
Gold Layer Evidence
screenshots/bigquery_gold_layer.png

Gold dim_customer
The customer dimension contains both current and historical customer versions.

Important fields include:

customer_sk
customer_id
customer_name
address
city
state
postal_code
kyc_status
dbt_valid_from
dbt_valid_to
is_current
Final results:

Total customer versions: 1,150
Current customer versions: 1,000
Historical versions: 150
Surrogate Key Design
A business key such as:

customer_id = C00441
can occur more than once in an SCD Type 2 dimension.

Therefore, each historical version requires its own unique warehouse key.

customer_sk is generated using an MD5 hash based on:

customer_id + dbt_valid_from
Conceptually:

C00441
├── historical version → customer_sk_1
└── current version → customer_sk_2
is_current
The Gold customer dimension includes:

is_current
derived using:

CASE
WHEN dbt_valid_to IS NULL THEN TRUE
ELSE FALSE
END
This allows simple current-state queries:

WHERE is_current = TRUE
while historical customer records remain preserved.

Gold fact_transactions
The transaction fact combines:

silver_transactions +
silver_accounts +
dim_customer
Final validation:

Total fact rows: 15,000
Distinct transaction IDs: 15,000
Missing customer surrogate keys: 0
The model includes fields such as:

transaction_id
account_id
customer_id
customer_sk
transaction_timestamp
transaction_type
amount
transaction_status
merchant_category
account_type
account_status
branch_code
Customer Dimension Join Decision
The transaction fact references the current customer dimension version.

This was an intentional design decision.

The dbt snapshot validity timestamps represent when dbt observed source states during snapshot execution.

The synthetic transaction timestamps represent simulated business-event timestamps.

These two timelines therefore do not have equivalent business-effective semantics.

Forcing a temporal join between transaction timestamps and snapshot execution timestamps caused valid transaction rows to be excluded.

The final implementation therefore:

Preserves complete SCD Type 2 history
↓
dim_customer

and

Links transaction facts
↓
to the current dimension version
For a production historical point-in-time fact join, a source-system effective timestamp or CDC event timestamp would be required.

dbt Data Quality Tests
Warehouse quality is validated using dbt tests.

The project implements:

not_null
unique
accepted_values
relationships
Examples
Customer KYC
VERIFIED
PENDING
REJECTED
Account Type
SAVINGS
CURRENT
Transaction Type
CREDIT
DEBIT
Transaction Status
SUCCESS
FAILED
PENDING
Referential Integrity
silver_accounts.customer_id
↓
silver_customers.customer_id
silver_transactions.account_id
↓
silver_accounts.account_id
fact_transactions.customer_sk
↓
dim_customer.customer_sk
Test Results
PASS=25
WARN=0
ERROR=0
SKIP=0
TOTAL=25
dbt Documentation and Lineage
Documentation was generated with:

dbt docs generate
and viewed locally with:

dbt docs serve
The lineage graph shows dependencies from Bronze source tables through Silver transformations, customer snapshots, and Gold analytical models.

Important Lineage Paths
Bronze transactions
↓
silver_transactions
↓
fact_transactions
Bronze accounts
↓
silver_accounts
↓
fact_transactions
Bronze customers
↓
current_customers
↓
customer_snapshot
↓
dim_customer
↓
fact_transactions
dbt Lineage Evidence
screenshots/dbt_lineage.png

GitHub Actions CI
The repository contains:

.github/workflows/dbt_ci.yml
The CI workflow runs when a pull request targets main.

Pipeline:

Pull Request
↓
Checkout repository
↓
Set up Python
↓
Install dbt-bigquery
↓
Create temporary GCP credentials
↓
Create profiles.yml
↓
dbt debug
↓
dbt parse
↓
dbt test
The GCP credential is stored using the GitHub repository secret:

GCP_DBT_SERVICE_ACCOUNT
The JSON key itself is never committed to Git.

The Phase 2 implementation pull request successfully passed CI before being merged to main.

CI Evidence
screenshots/github_actions_dbt_ci.png

Security
Sensitive files are excluded from Git:

\*.json
.env
.venv/
Generated data and dbt runtime artifacts are also ignored:

data/\*_/_.csv
target/
logs/
dbt_packages/
The local GCP service-account JSON key is stored outside the repository.

Repository Structure
bfs-customer-transaction-data-warehouse/
│
├── .github/
│ └── workflows/
│ └── dbt_ci.yml
│
├── dbt/
│ └── bfs_dbt/
│ ├── analyses/
│ ├── macros/
│ │ └── generate_schema_name.sql
│ │
│ ├── models/
│ │ ├── bronze/
│ │ │ └── sources.yml
│ │ │
│ │ ├── silver/
│ │ │ ├── current_customers.sql
│ │ │ ├── silver_customers.sql
│ │ │ ├── silver_accounts.sql
│ │ │ └── silver_transactions.sql
│ │ │
│ │ ├── gold/
│ │ │ ├── dim_customer.sql
│ │ │ └── fact_transactions.sql
│ │ │
│ │ └── schema.yml
│ │
│ ├── snapshots/
│ │ └── customer_snapshot.yml
│ │
│ └── dbt_project.yml
│
├── screenshots/
│ ├── bigquery_bronze_layer.png
│ ├── bigquery_silver_layer.png
│ ├── bigquery_snapshot.png
│ ├── bigquery_gold_layer.png
│ ├── scd_type2_customer_history.png
│ ├── dbt_lineage.png
│ └── github_actions_dbt_ci.png
│
├── scripts/
│ ├── generate_banking_data.py
│ ├── profile_banking_data.py
│ └── validate_daily_snapshots.py
│
├── .gitignore
└── README.md
How to Reproduce

1. Clone repository
   git clone <repository-url>
   cd bfs-customer-transaction-data-warehouse
2. Create a Python environment
   python -m venv .venv
   Windows PowerShell:

.\.venv\Scripts\Activate.ps1 3. Install dependencies
python -m pip install pandas Faker dbt-bigquery 4. Generate synthetic data
python scripts/generate_banking_data.py 5. Profile Day 1
python scripts/profile_banking_data.py 6. Validate the three snapshots
python scripts/validate_daily_snapshots.py 7. Upload CSV snapshots to GCS
Use:

bronze/YYYY-MM-DD/ 8. Load Bronze tables into BigQuery
Load the three daily snapshots for:

customers
accounts
transactions 9. Configure dbt
Configure profiles.yml to use the GCP service account.

Validate:

dbt debug 10. Run Silver models
dbt run --select silver_customers
dbt run --select silver_accounts
dbt run --select silver_transactions 11. Process SCD snapshots
Run customer state sequentially for:

Day 1
Day 2
Day 3
and execute dbt snapshot after each state.

12. Build Gold
    dbt run --select dim_customer
    dbt run --select fact_transactions
13. Run dbt tests
    dbt test
    Expected:

PASS=25
WARN=0
ERROR=0 14. Generate lineage
dbt docs generate
dbt docs serve 15. Validate GitHub Actions CI
Create a pull request targeting:

main
The CI workflow automatically runs:

dbt debug
dbt parse
dbt test
Merge after the checks succeed.

Final Results
Metric Result
Customers 1,000
Accounts 1,271
Transactions 15,000
Unique transaction IDs 15,000
Day 1 → Day 2 customer changes 75
Day 2 → Day 3 customer changes 75
Customer dimension versions 1,150
Current customer versions 1,000
Historical customer versions 150
Gold transaction facts 15,000
Missing customer surrogate keys 0
dbt tests passed 25
dbt test errors 0
GitHub Actions CI SUCCESS
Key Skills Demonstrated
Medallion Architecture
Google Cloud Storage
BigQuery
dbt Core
dbt sources
dbt incremental models
SCD Type 2
dbt snapshots
Surrogate keys
Dimensional modeling
Data-quality testing
Referential integrity
dbt lineage
Python/Faker synthetic-data generation
pandas data profiling
Git branching
Pull requests
GitHub Actions CI
GCP service accounts
Secret management
Project Status
Completed and tested.

The complete implementation demonstrates:

Synthetic BFS Data
↓
GCS Bronze
↓
BigQuery Bronze
↓
dbt Silver
↓
Incremental Transactions
↓
Customer SCD Type 2
↓
Gold Dimensional Models
↓
25 dbt Data Quality Tests
↓
dbt Lineage
↓
GitHub Actions CI
