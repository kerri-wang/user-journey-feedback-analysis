import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from pathlib import Path

# =========================
# Config
# =========================
RANDOM_SEED = 42
NUM_USERS = 800
NUM_SESSIONS = 2400
NUM_FEEDBACK = 1000

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def weighted_choice(options, probs):
    return np.random.choice(options, p=probs)


def random_datetime(start_date, end_date):
    delta = end_date - start_date
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start_date + timedelta(seconds=random_seconds)


# =========================
# 1. Generate users.csv
# =========================
user_ids = [f"U{str(i).zfill(4)}" for i in range(1, NUM_USERS + 1)]

user_type_options = ["new", "returning"]
user_type_probs = [0.62, 0.38]

device_type_options = ["mobile", "desktop"]
device_type_probs = [0.68, 0.32]

region_options = ["East", "North", "South", "West"]
region_probs = [0.30, 0.23, 0.25, 0.22]

age_group_options = ["18-24", "25-34", "35-44", "45+"]
age_group_probs = [0.26, 0.38, 0.24, 0.12]

users = []
for user_id in user_ids:
    user_type = weighted_choice(user_type_options, user_type_probs)
    device_type = weighted_choice(device_type_options, device_type_probs)
    region = weighted_choice(region_options, region_probs)
    age_group = weighted_choice(age_group_options, age_group_probs)

    users.append(
        {
            "user_id": user_id,
            "user_type": user_type,
            "device_type": device_type,
            "region": region,
            "age_group": age_group,
        }
    )

users_df = pd.DataFrame(users)

# =========================
# 2. Generate events.csv
# =========================
start_date = datetime(2026, 3, 1)
end_date = datetime(2026, 3, 21)

event_rows = []
session_records = []

event_stage_map = {
    "app_open": "entry",
    "home_view": "entry",
    "search_view": "browse",
    "product_view": "product_detail",
    "view_3d_model": "product_detail",
    "view_specs": "product_detail",
    "view_pricing": "pricing",
    "start_application": "application",
    "exit": None,
}

for i in range(1, NUM_SESSIONS + 1):
    session_id = f"S{str(i).zfill(5)}"

    user_row = users_df.sample(1, random_state=np.random.randint(0, 999999)).iloc[0]
    user_id = user_row["user_id"]
    user_type = user_row["user_type"]
    device_type = user_row["device_type"]
    region = user_row["region"]

    session_start = random_datetime(start_date, end_date)

    view_3d_prob = 0.45
    view_specs_prob = 0.40

    if user_type == "returning":
        view_3d_prob += 0.10
        view_specs_prob += 0.12
    if device_type == "desktop":
        view_3d_prob += 0.08
        view_specs_prob += 0.05
    if region in ["East", "North"]:
        view_specs_prob += 0.03

    viewed_3d = np.random.rand() < view_3d_prob
    viewed_specs = np.random.rand() < view_specs_prob

    content_score = 0
    if viewed_3d:
        content_score += 1
    if viewed_specs:
        content_score += 1

    pricing_prob = 0.20
    if user_type == "returning":
        pricing_prob += 0.10
    if device_type == "desktop":
        pricing_prob += 0.05
    pricing_prob += 0.12 * content_score

    viewed_pricing = np.random.rand() < min(pricing_prob, 0.85)

    application_prob = 0.06
    if viewed_pricing:
        application_prob += 0.15
    if content_score == 2:
        application_prob += 0.08
    if user_type == "returning":
        application_prob += 0.05

    started_application = np.random.rand() < min(application_prob, 0.55)

    early_dropoff_bias = 0
    if user_type == "new":
        early_dropoff_bias += 0.20
    if device_type == "mobile":
        early_dropoff_bias += 0.10

    session_events = ["app_open", "home_view"]

    if np.random.rand() < (0.88 - early_dropoff_bias):
        session_events.append("search_view")
    else:
        session_events.append("exit")

    if "exit" not in session_events:
        if np.random.rand() < (0.78 - early_dropoff_bias * 0.4):
            session_events.append("product_view")
        else:
            session_events.append("exit")

    if "exit" not in session_events and viewed_3d:
        session_events.append("view_3d_model")

    if "exit" not in session_events and viewed_specs:
        session_events.append("view_specs")

    if "exit" not in session_events and viewed_pricing:
        session_events.append("view_pricing")

    if "exit" not in session_events and started_application:
        session_events.append("start_application")

    if session_events[-1] != "exit":
        session_events.append("exit")

    if "start_application" in session_events:
        dropoff_stage = "application"
    elif "view_pricing" in session_events:
        dropoff_stage = "pricing"
    elif (
        "product_view" in session_events
        or "view_3d_model" in session_events
        or "view_specs" in session_events
    ):
        dropoff_stage = "product_detail"
    elif "search_view" in session_events:
        dropoff_stage = "browse"
    else:
        dropoff_stage = "entry"

    session_records.append(
        {
            "session_id": session_id,
            "user_id": user_id,
            "user_type": user_type,
            "device_type": device_type,
            "region": region,
            "viewed_3d": int(viewed_3d),
            "viewed_specs": int(viewed_specs),
            "viewed_pricing": int(viewed_pricing),
            "started_application": int(started_application),
            "dropoff_stage": dropoff_stage,
            "session_start": session_start,
        }
    )

    current_time = session_start
    for event_name in session_events:
        if event_name == "exit":
            page_stage = dropoff_stage
        else:
            page_stage = event_stage_map[event_name]

        event_rows.append(
            {
                "session_id": session_id,
                "user_id": user_id,
                "event_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "event_name": event_name,
                "page_stage": page_stage,
            }
        )
        current_time += timedelta(seconds=random.randint(4, 45))

events_df = pd.DataFrame(event_rows)
session_df = pd.DataFrame(session_records)

# =========================
# 3. Generate feedback.csv
# =========================
negative_templates = {
    "navigation": [
        "Navigation was confusing and I could not figure out the next step",
        "It was hard to find the information I needed",
        "The menu layout was not intuitive for a first-time user",
        "I kept clicking around and still could not find the pricing page",
        "The journey felt unclear and I was not sure where to go next",
    ],
    "pricing": [
        "It was hard to find pricing information",
        "Pricing details were buried and took too many clicks to reach",
        "I wanted to see pricing earlier in the journey",
        "The pricing page was not easy to discover",
        "I had trouble locating cost information quickly",
    ],
    "performance": [
        "The app was slow and laggy on my phone",
        "Loading felt too slow and made the experience frustrating",
        "The 3D view looked interesting but performance was poor",
        "There was too much lag during the early part of the session",
        "The page response time felt slow on mobile",
    ],
}

positive_templates = {
    "product_value": [
        "The 3D model was realistic and useful",
        "I liked the spec panel and the experience felt engaging",
        "The product information was clear and easy to explore",
        "The showroom experience felt interactive and fun",
        "I liked how detailed the content was once I found it",
    ],
    "navigation": [
        "The layout was easy to use",
        "I could find the information I needed quickly",
        "Navigation felt smooth and simple",
        "The steps were clear and easy to follow",
        "It was easy to move from product details to pricing",
    ],
}

neutral_templates = [
    "The experience was okay overall",
    "I looked through a few sections and then left",
    "Some parts were useful but others were average",
    "The app worked fine but did not stand out",
    "I found some information but did not continue further",
]

feedback_rows = []

feedback_session_sample = session_df.sample(
    n=NUM_FEEDBACK,
    replace=True,
    weights=(
        1
        + 1.2 * (session_df["dropoff_stage"].isin(["entry", "browse"]).astype(int))
        + 0.8 * (session_df["device_type"].eq("mobile").astype(int))
        + 0.8 * (session_df["user_type"].eq("new").astype(int))
    ),
    random_state=RANDOM_SEED,
).reset_index(drop=True)

for i, row in feedback_session_sample.iterrows():
    feedback_id = f"F{str(i + 1).zfill(5)}"
    user_id = row["user_id"]
    session_id = row["session_id"]
    user_type = row["user_type"]
    device_type = row["device_type"]
    viewed_3d = row["viewed_3d"]
    viewed_specs = row["viewed_specs"]
    viewed_pricing = row["viewed_pricing"]
    journey_stage = row["dropoff_stage"]

    negative_score = 0.30
    positive_score = 0.22
    neutral_score = 0.48

    if user_type == "new":
        negative_score += 0.16
        positive_score -= 0.05
    if device_type == "mobile":
        negative_score += 0.10
    if journey_stage in ["entry", "browse"]:
        negative_score += 0.18
        positive_score -= 0.06
    if viewed_3d and viewed_specs:
        positive_score += 0.14
        negative_score -= 0.10
    if viewed_pricing:
        positive_score += 0.05

    probs = np.array([negative_score, neutral_score, positive_score])
    probs = np.clip(probs, 0.05, None)
    probs = probs / probs.sum()

    sentiment = np.random.choice(["negative", "neutral", "positive"], p=probs)

    if sentiment == "negative":
        theme_options = ["navigation", "pricing", "performance"]
        theme_probs = [0.42, 0.30, 0.28]

        if journey_stage in ["entry", "browse"]:
            theme_probs = [0.50, 0.24, 0.26]
        if device_type == "mobile":
            theme_probs = [0.35, 0.22, 0.43]

        theme = np.random.choice(theme_options, p=np.array(theme_probs) / np.sum(theme_probs))
        feedback_text = random.choice(negative_templates[theme])

        if theme == "navigation":
            rating = np.random.choice([1, 2], p=[0.55, 0.45])
        elif theme == "pricing":
            rating = np.random.choice([1, 2, 3], p=[0.35, 0.45, 0.20])
        else:
            rating = np.random.choice([1, 2], p=[0.45, 0.55])

    elif sentiment == "positive":
        if viewed_3d and viewed_specs:
            theme = "product_value"
            feedback_text = random.choice(positive_templates["product_value"])
        else:
            theme = np.random.choice(["product_value", "navigation"], p=[0.65, 0.35])
            feedback_text = random.choice(positive_templates[theme])

        rating = np.random.choice([4, 5], p=[0.40, 0.60])

    else:
        theme = "neutral"
        feedback_text = random.choice(neutral_templates)
        rating = np.random.choice([3, 4], p=[0.75, 0.25])

    source = np.random.choice(["in_app", "post_session_survey"], p=[0.65, 0.35])

    feedback_rows.append(
        {
            "feedback_id": feedback_id,
            "user_id": user_id,
            "session_id": session_id,
            "feedback_date": row["session_start"].strftime("%Y-%m-%d"),
            "journey_stage": journey_stage,
            "rating": int(rating),
            "feedback_text": feedback_text,
            "source": source,
        }
    )

feedback_df = pd.DataFrame(feedback_rows)

users_df.to_csv(RAW_DIR / "users.csv", index=False)
events_df.to_csv(RAW_DIR / "events.csv", index=False)
feedback_df.to_csv(RAW_DIR / "feedback.csv", index=False)

print("Files generated successfully:")
print("- data/raw/users.csv")
print("- data/raw/events.csv")
print("- data/raw/feedback.csv")
