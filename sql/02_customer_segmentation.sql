-- ============================================================
-- Query 2: Customer Segmentation by Spend Tier
-- ============================================================
-- Divides customers into Low / Mid / High / Premium spend tiers
-- and profiles each segment by demographics and campaign behaviour.
-- Uses CASE for segmentation and GROUP BY for aggregation.
-- ============================================================

WITH segmented AS (
    SELECT
        *,
        CASE
            WHEN TotalSpend < 682                    THEN 'Low (<$682)'
            WHEN TotalSpend BETWEEN 682 AND 987      THEN 'Mid ($682–$988)'
            WHEN TotalSpend BETWEEN 988 AND 1546     THEN 'High ($988–$1547)'
            ELSE                                          'Premium (>$1547)'
        END AS spend_segment
    FROM marketing_campaign
    WHERE Income IS NOT NULL    -- exclude 24 null-income rows from segment analysis
)

SELECT
    spend_segment,

    -- Volume
    COUNT(*)                                                    AS num_customers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)         AS pct_of_customers,

    -- Spend profile
    ROUND(AVG(TotalSpend), 0)                                   AS avg_total_spend,
    ROUND(AVG(Income), 0)                                       AS avg_income,

    -- Demographics
    ROUND(AVG(Age), 0)                                          AS avg_age,
    ROUND(AVG(Kidhome + Teenhome), 2)                          AS avg_children,

    -- Engagement
    ROUND(AVG(Recency), 0)                                      AS avg_days_since_purchase,
    ROUND(AVG(NumWebVisitsMonth), 1)                            AS avg_web_visits_month,

    -- Campaign response
    ROUND(AVG(Response) * 100, 1)                               AS final_campaign_response_pct,
    ROUND(AVG(TotalCampaignsAccepted), 2)                       AS avg_campaigns_accepted,

    -- Channel preference
    ROUND(AVG(NumStorePurchases), 1)                            AS avg_store_purchases,
    ROUND(AVG(NumWebPurchases), 1)                              AS avg_web_purchases,
    ROUND(AVG(NumCatalogPurchases), 1)                          AS avg_catalog_purchases

FROM segmented
GROUP BY spend_segment
ORDER BY AVG(TotalSpend);
