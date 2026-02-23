-- ============================================================
-- Query 3: Campaign Response Rates by Demographic Group
-- ============================================================
-- Identifies which customer profiles respond most to campaigns.
-- Breaks down response rate by education level, presence of
-- children, and age group.
-- Uses CASE for age banding and GROUP BY aggregations.
-- ============================================================

-- (a) Response by education level
SELECT
    Education,
    COUNT(*)                                        AS customers,
    SUM(Response)                                   AS responded,
    ROUND(AVG(Response) * 100, 1)                   AS response_rate_pct,
    ROUND(AVG(TotalSpend), 0)                       AS avg_spend,
    ROUND(AVG(Income), 0)                           AS avg_income
FROM marketing_campaign
WHERE Income IS NOT NULL
GROUP BY Education
ORDER BY response_rate_pct DESC;

-- ──────────────────────────────────────────────────────────

-- (b) Response by children in household
SELECT
    CASE
        WHEN (Kidhome + Teenhome) = 0 THEN 'No Children'
        WHEN (Kidhome + Teenhome) = 1 THEN '1 Child'
        ELSE                               '2+ Children'
    END                                             AS household_type,
    COUNT(*)                                        AS customers,
    SUM(Response)                                   AS responded,
    ROUND(AVG(Response) * 100, 1)                   AS response_rate_pct,
    ROUND(AVG(TotalSpend), 0)                       AS avg_spend
FROM marketing_campaign
GROUP BY household_type
ORDER BY response_rate_pct DESC;

-- ──────────────────────────────────────────────────────────

-- (c) Response by age group
SELECT
    CASE
        WHEN Age < 35              THEN 'Under 35'
        WHEN Age BETWEEN 35 AND 49 THEN '35–49'
        WHEN Age BETWEEN 50 AND 64 THEN '50–64'
        ELSE                            '65+'
    END                                             AS age_group,
    COUNT(*)                                        AS customers,
    SUM(Response)                                   AS responded,
    ROUND(AVG(Response) * 100, 1)                   AS response_rate_pct,
    ROUND(AVG(TotalSpend), 0)                       AS avg_spend,
    ROUND(AVG(Income), 0)                           AS avg_income
FROM marketing_campaign
WHERE Income IS NOT NULL
GROUP BY age_group
ORDER BY
    CASE age_group
        WHEN 'Under 35' THEN 1
        WHEN '35–49'    THEN 2
        WHEN '50–64'    THEN 3
        ELSE                 4
    END;
