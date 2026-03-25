# User Journey & Customer Feedback Analysis for UX Optimization

## Overview

This project combines user journey analysis and customer feedback sentiment analysis to identify UX friction points, explain pain points by segment, and support product improvement recommendations.

Using synthetic data inspired by internship-style analytics work, I built a lightweight workflow that:
- analyzes session progression and drop-off patterns with SQL
- scores customer feedback sentiment with Python
- tags common complaint themes
- combines behavioral and feedback KPIs into one segment-level summary

The goal is not to replicate a production system, but to demonstrate a practical, interview-friendly analytics project that is easy to explain end to end.

---

## Business Problem

Product teams often have both behavioral event data and open-text feedback, but these sources are usually analyzed separately.

This project asks:

- Where do users drop off in the journey?
- Which user segments show the most friction?
- What themes appear most often in negative feedback?
- Are richer product interactions associated with deeper progression in the journey?

The objective is to turn raw event logs and messy feedback text into clear, business-facing insight.

---

## Project Objective

The project is designed to answer three core questions:

1. Are new users more likely to drop off early in the journey?
2. Are mobile users experiencing more friction than desktop users?
3. Does engagement with high-value content relate to better downstream behavior such as pricing reach or application intent?

---

## Dataset

This project uses **synthetic data** created for portfolio purposes.

### Raw input tables
- `users.csv`
- `events.csv`
- `feedback.csv`

### Processed output tables
- `session_summary.csv`
- `dropoff_by_segment.csv`
- `engagement_driver_summary.csv`
- `feedback_scored.csv`
- `feedback_sentiment_summary.csv`
- `segment_kpi_summary.csv`

### Key fields included
- user type
- device type
- region
- session events and journey stage
- feedback text
- rating
- sentiment score
- theme tags

---

## Analysis Workflow

### 1. Fake data generation
Synthetic user, event, and feedback datasets were generated to simulate:
- early-stage drop-off among new users
- stronger downstream behavior among users who engaged with richer product content
- more negative feedback from new and mobile users

### 2. SQL-based journey analysis
SQL was used to:
- transform event-level logs into a session-level funnel table
- compare drop-off patterns by user type and device type
- evaluate whether engagement with high-value content was associated with pricing reach and application intent

### 3. Feedback sentiment analysis
Python was used to:
- clean feedback text
- apply lightweight rule-based sentiment scoring
- label feedback as positive, neutral, or negative
- tag common themes such as navigation, pricing, performance, and product value

### 4. Segment-level KPI summary
Behavioral metrics and sentiment outputs were combined into one summary table to compare:
- entry drop-off rate
- browse drop-off rate
- pricing reach rate
- application reach rate
- negative feedback rate
- average sentiment score
- top complaint theme

---

## Repository Structure

```text
user-journey-feedback-analysis/
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   │   ├── users.csv
│   │   ├── events.csv
│   │   └── feedback.csv
│   │
│   └── processed/
│       ├── session_summary.csv
│       ├── dropoff_by_segment.csv
│       ├── engagement_driver_summary.csv
│       ├── feedback_scored.csv
│       ├── feedback_sentiment_summary.csv
│       └── segment_kpi_summary.csv
│
├── sql/
│   ├── 01_session_funnel.sql
│   ├── 02_dropoff_by_segment.sql
│   └── 03_engagement_driver.sql
│
└── src/
    ├── generate_fake_data.py
    ├── sentiment_analysis.py
    └── reporting.py

## Key Outputs

### `session_summary.csv`
Session-level journey summary with:
- user segment attributes
- number of events
- content engagement flags
- pricing reach flag
- application intent flag
- drop-off stage

### `feedback_scored.csv`
Feedback-level sentiment table with:
- cleaned text
- sentiment score
- sentiment label
- theme tags

### `segment_kpi_summary.csv`
Combined segment-level KPI table with both behavioral and sentiment metrics.

## Key Findings

### 1. New users show significantly higher early-stage friction
Compared with returning users:
- **entry drop-off rate:** `37.9%` vs `19.0%`
- **negative feedback rate:** `42.8%` vs `27.7%`

This suggests that the biggest UX issue is not product value itself, but the early user journey.

### 2. Mobile users show weaker journey progression and more negative sentiment
Compared with desktop users:
- **entry drop-off rate:** `33.4%` vs `24.8%`
- **negative feedback rate:** `40.3%` vs `32.4%`

This points to a likely mobile usability or discoverability issue.

### 3. Richer product engagement is associated with stronger downstream behavior
Sessions that viewed both high-value content types performed best:
- **pricing reach rate:** `47.8%` for `viewed_both` vs `4.7%` for `viewed_neither`
- **application intent rate:** `23.4%` for `viewed_both` vs `2.9%` for `viewed_neither`

This suggests that surfacing richer product information earlier may help users progress further.

### 4. Navigation is the main pain point in the most affected segments
For both:
- `new` users
- `mobile` users

the top negative theme was **navigation**.

This aligns with the pattern that friction is concentrated in the early journey rather than in later-stage product evaluation.

## Business Recommendations

Based on the combined journey and feedback analysis, the main recommendations are:

1. **Simplify early navigation for new users**  
   Reduce confusion in entry and browse stages by making the next step clearer.

2. **Surface key product information earlier**  
   Bring pricing, specs, or richer product content closer to the top of the journey.

3. **Prioritize mobile UX improvements**  
   Mobile users show higher drop-off and more negative sentiment, so early-stage mobile usability should be reviewed first.

## Why This Project Matters

This project is designed to showcase practical analytics skills for data analyst, product analytics, BI, and analytics engineering roles.

It demonstrates:
- SQL for journey and funnel analysis
- Python for text cleaning and sentiment scoring
- customer segmentation
- KPI reporting
- business interpretation
- translating analysis into product recommendations

## Tech Stack

- SQL
- Python
- Pandas
- NumPy
- CSV
- Jupyter / Google Colab
