{{ config(materialized='view') }}

{% set snapshot_day = var('customer_snapshot_day', 1) %}

{% if snapshot_day == 1 %}

    select *
    from {{ source('bfs_bronze', 'customers_day1') }}

{% elif snapshot_day == 2 %}

    select *
    from {{ source('bfs_bronze', 'customers_day2') }}

{% elif snapshot_day == 3 %}

    select *
    from {{ source('bfs_bronze', 'customers_day3') }}

{% else %}

    {{ exceptions.raise_compiler_error(
        "customer_snapshot_day must be 1, 2, or 3"
    ) }}

{% endif %}