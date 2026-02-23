-- ============================================================
-- Query 5: Campaign Performance Comparison
-- ============================================================
-- Compares acceptance rates across all 5 historical campaigns
-- plus the final campaign. Identifies which campaigns performed
-- best and whether performance has drifted over time.
-- Uses UNION ALL to stack campaigns into a single result set.
-- ============================================================

SELECT
    'Campaign 1'                                    AS campaign,
    1                                               AS campaign_order,
    COUNT(*)                                        AS total_targeted,
    SUM(AcceptedCmp1)                               AS accepted,
    ROUND(AVG(AcceptedCmp1) * 100, 2)               AS acceptance_rate_pct,
    ROUND(AVG(CASE WHEN AcceptedCmp1 = 1
                   THEN TotalSpend END), 0)         AS avg_spend_acceptors,
    ROUND(AVG(CASE WHEN AcceptedCmp1 = 0
                   THEN TotalSpend END), 0)         AS avg_spend_non_acceptors
FROM marketing_campaign

UNION ALL SELECT 'Campaign 2', 2, COUNT(*), SUM(AcceptedCmp2),
    ROUND(AVG(AcceptedCmp2)*100,2),
    ROUND(AVG(CASE WHEN AcceptedCmp2=1 THEN TotalSpend END),0),
    ROUND(AVG(CASE WHEN AcceptedCmp2=0 THEN TotalSpend END),0)
FROM marketing_campaign

UNION ALL SELECT 'Campaign 3', 3, COUNT(*), SUM(AcceptedCmp3),
    ROUND(AVG(AcceptedCmp3)*100,2),
    ROUND(AVG(CASE WHEN AcceptedCmp3=1 THEN TotalSpend END),0),
    ROUND(AVG(CASE WHEN AcceptedCmp3=0 THEN TotalSpend END),0)
FROM marketing_campaign

UNION ALL SELECT 'Campaign 4', 4, COUNT(*), SUM(AcceptedCmp4),
    ROUND(AVG(AcceptedCmp4)*100,2),
    ROUND(AVG(CASE WHEN AcceptedCmp4=1 THEN TotalSpend END),0),
    ROUND(AVG(CASE WHEN AcceptedCmp4=0 THEN TotalSpend END),0)
FROM marketing_campaign

UNION ALL SELECT 'Campaign 5', 5, COUNT(*), SUM(AcceptedCmp5),
    ROUND(AVG(AcceptedCmp5)*100,2),
    ROUND(AVG(CASE WHEN AcceptedCmp5=1 THEN TotalSpend END),0),
    ROUND(AVG(CASE WHEN AcceptedCmp5=0 THEN TotalSpend END),0)
FROM marketing_campaign

UNION ALL SELECT 'Final Campaign', 6, COUNT(*), SUM(Response),
    ROUND(AVG(Response)*100,2),
    ROUND(AVG(CASE WHEN Response=1 THEN TotalSpend END),0),
    ROUND(AVG(CASE WHEN Response=0 THEN TotalSpend END),0)
FROM marketing_campaign

ORDER BY campaign_order;
