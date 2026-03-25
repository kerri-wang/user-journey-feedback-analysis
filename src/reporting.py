import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

dropoff_df = pd.read_csv(PROCESSED_DIR / "dropoff_by_segment.csv")
feedback_summary_df = pd.read_csv(PROCESSED_DIR / "feedback_sentiment_summary.csv")
session_summary_df = pd.read_csv(PROCESSED_DIR / "session_summary.csv")

dropoff_filtered_df = dropoff_df[
    dropoff_df["segment_name"].isin(["user_type", "device_type"])
].copy()

feedback_filtered_df = feedback_summary_df[
    feedback_summary_df["segment_name"].isin(["user_type", "device_type"])
].copy()

user_type_pricing = (
    session_summary_df.groupby("user_type")
    .agg(
        sessions=("session_id", "count"),
        pricing_reached_sessions=("viewed_pricing_flag", "sum"),
    )
    .reset_index()
)
user_type_pricing["segment_name"] = "user_type"
user_type_pricing = user_type_pricing.rename(columns={"user_type": "segment_value"})
user_type_pricing["pricing_reach_rate"] = (
    user_type_pricing["pricing_reached_sessions"] / user_type_pricing["sessions"]
).round(4)

device_type_pricing = (
    session_summary_df.groupby("device_type")
    .agg(
        sessions=("session_id", "count"),
        pricing_reached_sessions=("viewed_pricing_flag", "sum"),
    )
    .reset_index()
)
device_type_pricing["segment_name"] = "device_type"
device_type_pricing = device_type_pricing.rename(columns={"device_type": "segment_value"})
device_type_pricing["pricing_reach_rate"] = (
    device_type_pricing["pricing_reached_sessions"] / device_type_pricing["sessions"]
).round(4)

pricing_summary_df = pd.concat(
    [user_type_pricing, device_type_pricing], ignore_index=True
)[["segment_name", "segment_value", "sessions", "pricing_reach_rate"]]

segment_kpi_summary_df = (
    pricing_summary_df.merge(
        dropoff_filtered_df[
            [
                "segment_name",
                "segment_value",
                "total_sessions",
                "entry_dropoff_rate",
                "browse_dropoff_rate",
                "application_reach_rate",
            ]
        ],
        on=["segment_name", "segment_value"],
        how="left",
    )
    .merge(
        feedback_filtered_df[
            [
                "segment_name",
                "segment_value",
                "feedback_count",
                "negative_feedback_rate",
                "avg_sentiment_score",
                "avg_rating",
                "top_theme",
            ]
        ],
        on=["segment_name", "segment_value"],
        how="left",
    )
)

segment_kpi_summary_df["sessions"] = segment_kpi_summary_df["total_sessions"]

segment_kpi_summary_df = segment_kpi_summary_df[
    [
        "segment_name",
        "segment_value",
        "sessions",
        "entry_dropoff_rate",
        "browse_dropoff_rate",
        "pricing_reach_rate",
        "application_reach_rate",
        "feedback_count",
        "negative_feedback_rate",
        "avg_sentiment_score",
        "avg_rating",
        "top_theme",
    ]
].copy()

segment_kpi_summary_df.to_csv(PROCESSED_DIR / "segment_kpi_summary.csv", index=False)

print("segment_kpi_summary.csv created successfully.")
print(segment_kpi_summary_df)
