{{ config(materialized='table', schema='mart') }}

WITH cal AS (
    SELECT *
    FROM generate_series(date '2008-01-01', current_date + 365, interval '1 day') AS d
)
SELECT
    d::date                     AS date,
    EXTRACT(year  FROM d)::int  AS year,
    EXTRACT(month FROM d)::int  AS month,
    EXTRACT(quarter FROM d)::int AS quarter,
    TO_CHAR(d, 'Day')           AS weekday
FROM cal