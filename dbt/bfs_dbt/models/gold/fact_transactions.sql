{{
    config(
        materialized='table',
        schema='bfs_gold'
    )
}}

with transactions as (

    select
        transaction_id,
        account_id,
        transaction_timestamp,
        transaction_type,
        amount,
        transaction_status,
        merchant_category

    from {{ ref('silver_transactions') }}

),

accounts as (

    select
        account_id,
        customer_id,
        account_type,
        account_status,
        branch_code

    from {{ ref('silver_accounts') }}

),

current_customers as (

    select
        customer_sk,
        customer_id

    from {{ ref('dim_customer') }}

    where is_current = true

),

final as (

    select
        t.transaction_id,
        t.account_id,

        a.customer_id,
        c.customer_sk,

        t.transaction_timestamp,
        t.transaction_type,
        t.amount,
        t.transaction_status,
        t.merchant_category,

        a.account_type,
        a.account_status,
        a.branch_code

    from transactions t

    inner join accounts a
        on t.account_id = a.account_id

    inner join current_customers c
        on a.customer_id = c.customer_id

)

select *
from final