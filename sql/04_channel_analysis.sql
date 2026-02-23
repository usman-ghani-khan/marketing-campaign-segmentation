-- ============================================================
-- Query 4: Purchase Channel Analysis
-- ============================================================
-- Compares how customers use different purchase channels
-- (web, store, catalogue, deals) and identifies whether
-- high-value customers concentrate on specific channels.
-- ============================================================

WITH channel_totals AS (
    SELECT
        CASE
            WHEN TotalSpend < 200                THEN 'Low'
            WHEN TotalSpend BETWEEN 200 AND 800  THEN 'Mid'
            WHEN TotalSpend BETWEEN 801 AND 1800 THEN 'High'
            ELSE                                      'Premium'
        END                                         AS spend_segment,
        NumWebPurchases,
        NumCatalogPurchases,
        NumStorePurchases,
        NumDealsPurchases,
        NumWebPurchases + NumCatalogPurchases
            + NumStorePurchases                     AS total_purchases
    FROM marketing_campaign
)

SELECT
    spend_segment,
    COUNT(*)                                        AS customers,

    -- Absolute avg purchases per channel
    ROUND(AVG(NumStorePurchases), 1)                AS avg_store,
    ROUND(AVG(NumWebPurchases), 1)                  AS avg_web,
    ROUND(AVG(NumCatalogPurchases), 1)              AS avg_catalog,
    ROUND(AVG(NumDealsPurchases), 1)                AS avg_deals,

    -- Channel share (% of total purchases per segment)
    ROUND(100.0 * SUM(NumStorePurchases)
        / NULLIF(SUM(total_purchases), 0), 1)       AS store_share_pct,
    ROUND(100.0 * SUM(NumWebPurchases)
        / NULLIF(SUM(total_purchases), 0), 1)       AS web_share_pct,
    ROUND(100.0 * SUM(NumCatalogPurchases)
        / NULLIF(SUM(total_purchases), 0), 1)       AS catalog_share_pct

FROM channel_totals
GROUP BY spend_segment
ORDER BY
    CASE spend_segment
        WHEN 'Low'     THEN 1
        WHEN 'Mid'     THEN 2
        WHEN 'High'    THEN 3
        WHEN 'Premium' THEN 4
    END;
