{{ config(materialized='table', schema='mart') }}

SELECT
  service_request_id,
  opened_date,
  DATE_PART('year', opened_date)::int   AS year,
  DATE_PART('month', opened_date)::int  AS month,
  status,
  service_name,
  service_subtype,
  neighborhood
FROM {{ ref('stg_sf311') }}
