WITH engagement_groups AS (
    SELECT
        CASE
            WHEN viewed_3d_flag = 1 AND viewed_specs_flag = 1 THEN 'viewed_both'
            WHEN viewed_3d_flag = 1 AND viewed_specs_flag = 0 THEN 'viewed_3d_only'
            WHEN viewed_3d_flag = 0 AND viewed_specs_flag = 1 THEN 'viewed_specs_only'
            ELSE 'viewed_neither'
        END AS engagement_group,
        num_events,
        session_length_sec,
        viewed_pricing_flag,
        application_intent_flag
    FROM session_summary
)
SELECT
    engagement_group,
    COUNT(*) AS total_sessions,
    ROUND(AVG(num_events), 2) AS avg_num_events,
    ROUND(AVG(session_length_sec), 2) AS avg_session_length_sec,
    SUM(viewed_pricing_flag) AS pricing_reached_sessions,
    ROUND(1.0 * SUM(viewed_pricing_flag) / COUNT(*), 4) AS pricing_reach_rate,
    SUM(application_intent_flag) AS application_intent_sessions,
    ROUND(1.0 * SUM(application_intent_flag) / COUNT(*), 4) AS application_intent_rate
FROM engagement_groups
GROUP BY engagement_group
ORDER BY
    CASE
        WHEN engagement_group = 'viewed_neither' THEN 1
        WHEN engagement_group = 'viewed_3d_only' THEN 2
        WHEN engagement_group = 'viewed_specs_only' THEN 3
        WHEN engagement_group = 'viewed_both' THEN 4
        ELSE 5
    END;
