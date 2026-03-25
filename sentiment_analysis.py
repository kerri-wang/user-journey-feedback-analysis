import pandas as pd
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

feedback_df = pd.read_csv(RAW_DIR / "feedback.csv")
users_df = pd.read_csv(RAW_DIR / "users.csv")


def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


positive_words = {
    "useful",
    "realistic",
    "engaging",
    "fun",
    "clear",
    "easy",
    "smooth",
    "liked",
    "good",
    "helpful",
    "detailed",
    "interactive",
}

negative_words = {
    "confusing",
    "hard",
    "slow",
    "lag",
    "laggy",
    "frustrating",
    "buried",
    "trouble",
    "could not",
    "not intuitive",
    "unclear",
    "poor",
}

theme_keywords = {
    "navigation": ["navigation", "menu", "confusing", "next step", "find", "layout", "journey"],
    "pricing": ["pricing", "price", "cost"],
    "performance": ["slow", "lag", "laggy", "loading", "response time"],
    "product_value": ["useful", "realistic", "engaging", "detailed", "interactive", "clear"],
}


def compute_sentiment_score(text):
    score = 0
    for word in positive_words:
        if word in text:
            score += 1
    for word in negative_words:
        if word in text:
            score -= 1
    return score


def assign_sentiment_label(score):
    if score > 0:
        return "positive"
    if score < 0:
        return "negative"
    return "neutral"


def tag_theme(text, keywords):
    for keyword in keywords:
        if keyword in text:
            return 1
    return 0


feedback_df["feedback_text_clean"] = feedback_df["feedback_text"].apply(clean_text)
feedback_df["sentiment_score"] = feedback_df["feedback_text_clean"].apply(compute_sentiment_score)
feedback_df["sentiment_label"] = feedback_df["sentiment_score"].apply(assign_sentiment_label)

feedback_df["theme_navigation"] = feedback_df["feedback_text_clean"].apply(
    lambda x: tag_theme(x, theme_keywords["navigation"])
)
feedback_df["theme_pricing"] = feedback_df["feedback_text_clean"].apply(
    lambda x: tag_theme(x, theme_keywords["pricing"])
)
feedback_df["theme_performance"] = feedback_df["feedback_text_clean"].apply(
    lambda x: tag_theme(x, theme_keywords["performance"])
)
feedback_df["theme_product_value"] = feedback_df["feedback_text_clean"].apply(
    lambda x: tag_theme(x, theme_keywords["product_value"])
)

feedback_scored_df = feedback_df[
    [
        "feedback_id",
        "user_id",
        "session_id",
        "feedback_date",
        "journey_stage",
        "rating",
        "source",
        "feedback_text",
        "feedback_text_clean",
        "sentiment_score",
        "sentiment_label",
        "theme_navigation",
        "theme_pricing",
        "theme_performance",
        "theme_product_value",
    ]
].copy()

feedback_scored_df.to_csv(PROCESSED_DIR / "feedback_scored.csv", index=False)

feedback_enriched_df = feedback_scored_df.merge(
    users_df[["user_id", "user_type", "device_type", "region"]],
    on="user_id",
    how="left",
)

feedback_enriched_df["is_negative"] = (
    feedback_enriched_df["sentiment_label"] == "negative"
).astype(int)


def build_segment_summary(df, segment_col):
    grouped = (
        df.groupby(segment_col)
        .agg(
            feedback_count=("feedback_id", "count"),
            negative_feedback_count=("is_negative", "sum"),
            negative_feedback_rate=("is_negative", "mean"),
            avg_sentiment_score=("sentiment_score", "mean"),
            avg_rating=("rating", "mean"),
            theme_navigation_count=("theme_navigation", "sum"),
            theme_pricing_count=("theme_pricing", "sum"),
            theme_performance_count=("theme_performance", "sum"),
            theme_product_value_count=("theme_product_value", "sum"),
        )
        .reset_index()
    )

    grouped["segment_name"] = segment_col
    grouped = grouped.rename(columns={segment_col: "segment_value"})

    def get_top_theme(row):
        theme_values = {
            "navigation": row["theme_navigation_count"],
            "pricing": row["theme_pricing_count"],
            "performance": row["theme_performance_count"],
            "product_value": row["theme_product_value_count"],
        }
        return max(theme_values, key=theme_values.get)

    grouped["top_theme"] = grouped.apply(get_top_theme, axis=1)
    grouped["negative_feedback_rate"] = grouped["negative_feedback_rate"].round(4)
    grouped["avg_sentiment_score"] = grouped["avg_sentiment_score"].round(2)
    grouped["avg_rating"] = grouped["avg_rating"].round(2)

    return grouped[
        [
            "segment_name",
            "segment_value",
            "feedback_count",
            "negative_feedback_count",
            "negative_feedback_rate",
            "avg_sentiment_score",
            "avg_rating",
            "top_theme",
        ]
    ]


summary_user_type = build_segment_summary(feedback_enriched_df, "user_type")
summary_device_type = build_segment_summary(feedback_enriched_df, "device_type")
summary_journey_stage = build_segment_summary(feedback_enriched_df, "journey_stage")

feedback_sentiment_summary_df = pd.concat(
    [summary_user_type, summary_device_type, summary_journey_stage], ignore_index=True
)

feedback_sentiment_summary_df.to_csv(
    PROCESSED_DIR / "feedback_sentiment_summary.csv", index=False
)

print("Sentiment analysis files created successfully.")
