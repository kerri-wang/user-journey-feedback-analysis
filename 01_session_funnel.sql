WITH session_base AS (
    SELECT
        e.session_id,
        MIN(e.user_id) AS user_id,
        MIN(u.user_type) AS user_type,
        MIN(u.device_type) AS device_type,
        MIN(u.region) AS region,
        COUNT(*) AS num_events,
        MIN(e.event_time) AS session_start_time,
        MAX(e.event_time) AS session_end_time,
        MAX(CASE WHEN e.event_name = 'view_3d_model' THEN 1 ELSE 0 END) AS viewed_3d_flag,
        MAX(CASE WHEN e.event_name = 'view_specs' THEN 1 ELSE 0 END) AS viewed_specs_flag,
        MAX(CASE WHEN e.event_name = 'view_pricing' THEN 1 ELSE 0 END) AS viewed_pricing_flag,
        MAX(CASE WHEN e.event_name = 'start_application' THEN 1 ELSE 0 END) AS application_intent_flag
    FROM events e
    LEFT JOIN users u
        ON e.user_id = u.user_id
    GROUP BY e.session_id
),
last_stage AS (
    SELECT
        session_id,
        page_stage AS dropoff_stage
    FROM (
        SELECT
            session_id,
            page_stage,
            event_time,
            ROW_NUMBER() OVER (
                PARTITION BY session_id
                ORDER BY event_time DESC
            ) AS rn
        FROM events
    ) t
    WHERE rn = 1
)
SELECT
    sb.session_id,
    sb.user_id,
    sb.user_type,
    sb.device_type,
    sb.region,
    sb.num_events,
    sb.session_start_time,
    sb.session_end_time,
    CAST((julianday(sb.session_end_time) - julianday(sb.session_start_time)) * 86400 AS INTEGER) AS session_length_sec,
    sb.viewed_3d_flag,
    sb.viewed_specs_flag,
    sb.viewed_pricing_flag,
    sb.application_intent_flag,
    ls.dropoff_stage
FROM session_base sb
LEFT JOIN last_stage ls
    ON sb.session_id = ls.session_id
ORDER BY sb.session_id;
