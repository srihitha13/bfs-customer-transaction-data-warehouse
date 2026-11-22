{{ config(materialized='view') }}

with source_customers as (

    select *
    from {{ source('bfs_bronze', 'customers_day1') }}

),

cleaned_customers as (

    select
        cast(customer_id as string) as customer_id,

        trim(cast(customer_name as string)) as customer_name,

        safe_cast(date_of_birth as date) as date_of_birth,

        lower(
            trim(cast(email as string))
        ) as email,

        trim(
            cast(phone as string)
        ) as phone,

        trim(
            cast(address as string)
        ) as address,

        trim(
            cast(city as string)
        ) as city,

        trim(
            cast(state as string)
        ) as state,

        cast(postal_code as string) as postal_code,

        upper(
            trim(cast(kyc_status as string))
        ) as kyc_status,

        safe_cast(customer_since as date) as customer_since

    from source_customers

)

select *
from cleaned_customers
