{{ config(materialized='table', schema='mart') }}

SELECT
    neighborhood,
    COUNT(*) AS total_requests
FROM {{ ref('stg_sf311') }}
WHERE neighborhood IS NOT NULL
GROUP BY neighborhood