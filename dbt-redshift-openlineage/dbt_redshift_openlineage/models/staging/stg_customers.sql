{{ config(
    materialized='table',
    schema='staging'
) }}

with source as (

    {#-
    Reading from Redshift Spectrum Iceberg table using dbt source
    #}
    select * from {{ source('spectrum_iceberg_db', 'customers') }}

),

renamed as (

    select
        id as customer_id,
        first_name,
        last_name

    from source

)

select * from renamed
