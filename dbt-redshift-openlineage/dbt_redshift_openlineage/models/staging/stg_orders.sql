{{ config(
    materialized='table',
    schema='staging'
) }}

with source as (

    {#-
    Reading from Redshift Spectrum Iceberg table using dbt source
    #}
    select * from {{ source('spectrum_iceberg_db', 'orders') }}

),

renamed as (

    select
        id as order_id,
        user_id as customer_id,
        order_date,
        status

    from source

)

select * from renamed
