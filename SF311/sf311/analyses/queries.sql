--  Average Monthly Request Volume
SELECT year, month, COUNT(*) AS requests
FROM  public_mart.fct_requests
GROUP BY 1,2
ORDER BY 1,2

--  Top 10 Complaint Types
SELECT service_subtype, COUNT(*) AS cnt
FROM  public_mart.fct_requests
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10

--  Requests per Thousand People (Example – can be extended if population data is available)
SELECT neighborhood, total_requests
FROM  public_mart.dim_neighborhood
ORDER BY total_requests DESC
LIMIT 20
