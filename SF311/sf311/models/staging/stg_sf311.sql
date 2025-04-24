{{ config(materialized='table', schema='staging') }}

SELECT
  service_request_id,
  opened_date::timestamp                AS opened_date,
  "Closed"::timestamp                   AS closed_date,
  status,
  service_name,
  service_subtype,
  "Neighborhood"                        AS neighborhood,
  lat::double precision                 AS lat,
  lon::double precision                 AS lon
FROM raw.sf311
