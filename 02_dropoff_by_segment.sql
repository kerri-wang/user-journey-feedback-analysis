WITH user_type_summary AS (
    SELECT
        'user_type' AS segment_name,
        user_type AS segment_value,
        COUNT(*) AS total_sessions,
        SUM(CASE WHEN dropoff_stage = 'entry' THEN 1 ELSE 0 END) AS entry_dropoffs,
        SUM(CASE WHEN dropoff_stage = 'browse' THEN 1 ELSE 0 END) AS browse_dropoffs,
        SUM(CASE WHEN dropoff_stage = 'product_detail' THEN 1 ELSE 0 END) AS product_detail_dropoffs,
        SUM(CASE WHEN dropoff_stage = 'pricing' THEN 1 ELSE 0 END) AS pricing_dropoffs,
        SUM(CASE WHEN dropoff_stage = 'application' THEN 1 ELSE 0 END) AS application_reached
    FROM session_summary
    GROUP BY user_type
),
device_type_summary AS (
    SELECT
        'device_type' AS segment_name,
        device_type AS segment_value,
        COUNT(*) AS total_sessions,
        SUM(CASE WHEN dropoff_stage = 'entry' THEN 1 ELSE 0 END) AS entry_dropoffs,
        SUM(CASE WHEN dropoff_stage = 'browse' THEN 1 ELSE 0 END) AS browse_dropoffs,
        SUM(CASE WHEN dropoff_stage = 'product_detail' THEN 1 ELSE 0 END) AS product_detail_dropoffs,
        SUM(CASE WHEN dropoff_stage = 'pricing' THEN 1 ELSE 0 END) AS pricing_dropoffs,
        SUM(CASE WHEN dropoff_stage = 'application' THEN 1 ELSE 0 END) AS application_reached
    FROM session_summary
    GROUP BY device_type
),
combined AS (
    SELECT * FROM user_type_summary
    UNION ALL
    SELECT * FROM device_type_summary
)
SELECT
    segment_name,
    segment_value,
    total_sessions,
    entry_dropoffs,
    ROUND(1.0 * entry_dropoffs / total_sessions, 4) AS entry_dropoff_rate,
    browse_dropoffs,
    ROUND(1.0 * browse_dropoffs / total_sessions, 4) AS browse_dropoff_rate,
    product_detail_dropoffs,
    ROUND(1.0 * product_detail_dropoffs / total_sessions, 4) AS product_detail_dropoff_rate,
    pricing_dropoffs,
    ROUND(1.0 * pricing_dropoffs / total_sessions, 4) AS pricing_dropoff_rate,
    application_reached,
    ROUND(1.0 * application_reached / total_sessions, 4) AS application_reach_rate
FROM combined
ORDER BY segment_name, segment_value;
