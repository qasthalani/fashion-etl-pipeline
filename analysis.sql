-- =============================================================================
-- Fashion Studio Product Analysis
-- =============================================================================
-- Author   : Nabilah Yasmin Qasthalani
-- Dataset  : Fashion Studio (fashion-studio.dicoding.dev)
-- Loaded to: PostgreSQL via ETL Pipeline
-- Table    : products
-- Purpose  : Business intelligence queries to extract insights from
--            scraped & transformed fashion product data
-- =============================================================================


-- =============================================================================
-- SECTION 1: Dataset Overview
-- =============================================================================

-- 1.1 General statistics: total products, average price, and average rating
SELECT
    COUNT(*)                                    AS total_products,
    ROUND(AVG("Price")::numeric, 2)            AS avg_price_idr,
    ROUND(MIN("Price")::numeric, 2)            AS min_price_idr,
    ROUND(MAX("Price")::numeric, 2)            AS max_price_idr,
    ROUND(AVG("Rating")::numeric, 2)           AS avg_rating,
    ROUND(AVG("Colors")::numeric, 2)           AS avg_colors_available
FROM products;


-- =============================================================================
-- SECTION 2: Gender Segmentation Analysis
-- =============================================================================

-- 2.1 Product count and average price per gender segment
SELECT
    "Gender",
    COUNT(*)                              AS total_products,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage,
    ROUND(AVG("Price")::numeric, 2)               AS avg_price_idr,
    ROUND(MIN("Price")::numeric, 2)               AS min_price_idr,
    ROUND(MAX("Price")::numeric, 2)               AS max_price_idr,
    ROUND(AVG("Rating")::numeric, 2)              AS avg_rating
FROM products
GROUP BY "Gender"
ORDER BY total_products DESC;


-- =============================================================================
-- SECTION 3: Rating Analysis
-- =============================================================================

-- 3.1 Top 10 highest-rated products
SELECT
    "Title",
    "Gender",
    "Size",
    "Colors",
    "Rating",
    "Price"
FROM products
ORDER BY "Rating" DESC, "Price" ASC
LIMIT 10;

-- 3.2 Rating distribution by bucket (low / medium / high)
SELECT
    CASE
        WHEN "Rating" < 3.0 THEN 'Low (< 3.0)'
        WHEN "Rating" BETWEEN 3.0 AND 4.0 THEN 'Medium (3.0 - 4.0)'
        WHEN "Rating" > 4.0 THEN 'High (> 4.0)'
    END                                   AS rating_category,
    COUNT(*)                              AS total_products,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage,
    ROUND(AVG("Price")::numeric, 2)               AS avg_price_idr
FROM products
GROUP BY rating_category
ORDER BY avg_price_idr DESC;


-- =============================================================================
-- SECTION 4: Price Segmentation Analysis
-- =============================================================================

-- 4.1 Classify products into price tiers and compare with rating
SELECT * FROM (
    SELECT
        CASE
            WHEN "Price" < 500000   THEN 'Budget (< Rp 500K)'
            WHEN "Price" < 2000000  THEN 'Mid-Range (Rp 500K - 2M)'
            WHEN "Price" < 5000000  THEN 'Premium (Rp 2M - 5M)'
            ELSE                         'Luxury (> Rp 5M)'
        END                                   AS price_tier,
        COUNT(*)                              AS total_products,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage,
        ROUND(AVG("Rating")::numeric, 2)      AS avg_rating,
        ROUND(AVG("Colors")::numeric, 2)      AS avg_colors,
        CASE
            WHEN "Price" < 500000   THEN 1
            WHEN "Price" < 2000000  THEN 2
            WHEN "Price" < 5000000  THEN 3
            ELSE                         4
        END                                   AS sort_order
    FROM products
    GROUP BY price_tier, sort_order
) sub
ORDER BY sort_order;

-- 4.2 Most expensive products per gender
SELECT
    "Gender",
    "Title",
    "Price",
    "Rating"
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY "Gender"
            ORDER BY "Price" DESC
        ) AS rank
    FROM products
) ranked
WHERE rank <= 3
ORDER BY "Gender", rank;


-- =============================================================================
-- SECTION 5: Color Variety vs. Rating Analysis
-- =============================================================================

-- 5.1 Does more color options correlate with higher ratings?
SELECT
    "Colors"                              AS color_options,
    COUNT(*)                              AS total_products,
    ROUND(AVG("Rating")::numeric, 3)              AS avg_rating,
    ROUND(AVG("Price")::numeric, 2)               AS avg_price_idr
FROM products
GROUP BY "Colors"
ORDER BY "Colors" ASC;

-- 5.2 Products with maximum color variety
SELECT
    "Title",
    "Gender",
    "Colors",
    "Rating",
    "Price"
FROM products
WHERE "Colors" = (SELECT MAX("Colors") FROM products)
ORDER BY "Rating" DESC;


-- =============================================================================
-- SECTION 6: Size Distribution Analysis
-- =============================================================================

-- 6.1 Product count per size category
SELECT
    "Size",
    COUNT(*)                              AS total_products,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage,
    ROUND(AVG("Price")::numeric, 2)               AS avg_price_idr,
    ROUND(AVG("Rating")::numeric, 2)              AS avg_rating
FROM products
GROUP BY "Size"
ORDER BY total_products DESC;


-- =============================================================================
-- SECTION 7: Combined Business Intelligence Summary
-- =============================================================================

-- 7.1 Best value products: high rating AND affordable price
SELECT
    "Title",
    "Gender",
    "Size",
    "Colors",
    "Rating",
    "Price",
    ROUND(("Rating" / ("Price" / 1000000.0))::numeric, 4) AS value_score
FROM products
WHERE "Rating" >= 4.0
ORDER BY value_score DESC
LIMIT 15;

-- 7.2 Summary by Gender x Price Tier (cross-analysis)
SELECT
    "Gender",
    CASE
        WHEN "Price" < 500000   THEN 'Budget'
        WHEN "Price" < 2000000  THEN 'Mid-Range'
        WHEN "Price" < 5000000  THEN 'Premium'
        ELSE                         'Luxury'
    END                               AS price_tier,
    COUNT(*)                          AS total_products,
    ROUND(AVG("Rating")::numeric, 2)  AS avg_rating
FROM products
GROUP BY "Gender", price_tier
ORDER BY "Gender", total_products DESC;