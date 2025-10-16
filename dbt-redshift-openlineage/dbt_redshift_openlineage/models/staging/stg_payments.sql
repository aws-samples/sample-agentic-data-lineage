{{ config(
    materialized='table',
    schema='staging'
) }}

with source as (

    {#-
    Reading from Redshift Spectrum Iceberg table using dbt source
    #}
    select * from {{ source('spectrum_iceberg_db', 'payments') }}

),

renamed as (

    select
        id as payment_id,
        order_id,
        payment_method,

        -- `amount` is currently stored in cents, so we convert it to dollars
        amount / 100 as amount

    from source

)

select * from renamed
