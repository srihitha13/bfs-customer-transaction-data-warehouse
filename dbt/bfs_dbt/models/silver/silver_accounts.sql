{{ config(materialized='view') }}

with source_accounts as (

    select *
    from {{ source('bfs_bronze', 'accounts_day1') }}

),

cleaned_accounts as (

    select
        cast(account_id as string) as account_id,

        cast(customer_id as string) as customer_id,

        upper(
            trim(cast(account_type as string))
        ) as account_type,

        upper(
            trim(cast(account_status as string))
        ) as account_status,

        upper(
            trim(cast(branch_code as string))
        ) as branch_code,

        safe_cast(balance as numeric) as balance,

        safe_cast(opened_date as date) as opened_date

    from source_accounts

)

select *
from cleaned_accounts