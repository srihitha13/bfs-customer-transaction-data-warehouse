{{
    config(
        materialized='incremental',
        unique_key='transaction_id',
        incremental_strategy='merge'
    )
}}

with all_transactions as (

    select *
    from {{ source('bfs_bronze', 'transactions_day1') }}

    union all

    select *
    from {{ source('bfs_bronze', 'transactions_day2') }}

    union all

    select *
    from {{ source('bfs_bronze', 'transactions_day3') }}

),

cleaned_transactions as (

    select
        cast(transaction_id as string) as transaction_id,

        cast(account_id as string) as account_id,

        safe_cast(
            transaction_timestamp as timestamp
        ) as transaction_timestamp,

        upper(
            trim(cast(transaction_type as string))
        ) as transaction_type,

        safe_cast(amount as numeric) as amount,

        upper(
            trim(cast(transaction_status as string))
        ) as transaction_status,

        upper(
            trim(cast(merchant_category as string))
        ) as merchant_category

    from all_transactions

)

select *
from cleaned_transactions

{% if is_incremental() %}

where transaction_id not in (
    select transaction_id
    from {{ this }}
)

{% endif %}