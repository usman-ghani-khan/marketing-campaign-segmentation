-- ============================================================
-- Query 1: Data Quality Checks
-- ============================================================
-- Before any analysis, audit the dataset for:
--   (a) Missing values in key columns
--   (b) Duplicate customer IDs
--   (c) Outlier income values (z-score > 3)
--   (d) Logical checks: customers with negative spend
-- ============================================================

-- (a) Null audit
SELECT
    COUNT(*)                                                        AS total_rows,
    SUM(CASE WHEN Income          IS NULL THEN 1 ELSE 0 END)       AS null_income,
    SUM(CASE WHEN Age             IS NULL THEN 1 ELSE 0 END)       AS null_age,
    SUM(CASE WHEN Education       IS NULL THEN 1 ELSE 0 END)       AS null_education,
    SUM(CASE WHEN Marital_Status  IS NULL THEN 1 ELSE 0 END)       AS null_marital_status,
    SUM(CASE WHEN TotalSpend      IS NULL THEN 1 ELSE 0 END)       AS null_total_spend,
    ROUND(
        100.0 * SUM(CASE WHEN Income IS NULL THEN 1 ELSE 0 END)
              / COUNT(*), 2
    )                                                               AS income_null_pct
FROM marketing_campaign;

-- ──────────────────────────────────────────────────────────

-- (b) Duplicate customer IDs
SELECT
    ID,
    COUNT(*) AS occurrences
FROM marketing_campaign
GROUP BY ID
HAVING COUNT(*) > 1;

-- ──────────────────────────────────────────────────────────

-- (c) Income outliers using z-score
-- Assumption: Income IS NULL rows excluded from calculation
WITH income_stats AS (
    SELECT
        AVG(Income)    AS mean_income,
        STDDEV(Income) AS std_income
    FROM marketing_campaign
    WHERE Income IS NOT NULL
)
SELECT
    ID,
    Income,
    ROUND(
        (Income - s.mean_income) / NULLIF(s.std_income, 0), 2
    ) AS z_score
FROM marketing_campaign m
CROSS JOIN income_stats s
WHERE Income IS NOT NULL
  AND ABS((Income - s.mean_income) / NULLIF(s.std_income, 0)) > 3
ORDER BY z_score DESC;

-- ──────────────────────────────────────────────────────────

-- (d) Logical check: any negative spend values?
SELECT
    COUNT(*) AS negative_spend_rows
FROM marketing_campaign
WHERE TotalSpend < 0
   OR MntWines < 0
   OR MntMeatProducts < 0;
