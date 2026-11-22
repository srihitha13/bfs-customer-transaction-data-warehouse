{{
    config(
        materialized='table',
        schema='bfs_gold'
    )
}}
with customer_history as (

    select
        customer_id,
        customer_name,
        date_of_birth,
        email,
        phone,
        address,
        city,
        state,
        postal_code,
        kyc_status,
        customer_since,
        dbt_valid_from,
        dbt_valid_to

    from {{ ref('customer_snapshot') }}

),

final as (

    select

        to_hex(
            md5(
                concat(
                    cast(customer_id as string),
                    '|',
                    cast(dbt_valid_from as string)
                )
            )
        ) as customer_sk,

        customer_id,
        customer_name,
        date_of_birth,
        email,
        phone,
        address,
        city,
        state,
        postal_code,
        kyc_status,
        customer_since,

        dbt_valid_from,
        dbt_valid_to,

        case
            when dbt_valid_to is null then true
            else false
        end as is_current

    from customer_history

)

select *
from final