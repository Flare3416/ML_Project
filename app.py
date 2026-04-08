from pathlib import Path
import tempfile

import streamlit as st
from PIL import Image

from model import detect_food
from utils.calorie import calculate_calories
from utils.bmi import (
    ActivityLevel,
    MealType,
    calculate_bmi,
    calculate_tdee,
    bmi_category,
    meal_calorie_allocation,
    calculate_health_score,
    calculate_goal_weight,
    calculate_adjusted_tdee_for_goal,
    calculate_weight_loss_plan,
    meal_calorie_targets,
)


st.set_page_config(page_title="NutriScan", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.html("""
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>

/* ─── ROOT ─────────────────────────────────────────────────────────── */
:root {
    --ink:       #0a0a0a;
    --paper:     #f5f2ec;
    --cream:     #ede9df;
    --warm:      #d4c9b0;
    --accent:    #c84b2f;
    --accent2:   #2f6dc8;
    --accent3:   #2dbe6c;
    --muted:     #6b6560;
    --border:    #c9c2b5;
    --card-bg:   #faf8f4;
    --hover:     #f0ece4;
}

/* ─── RESET / GLOBAL ────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif !important;
    background-color: var(--paper) !important;
    color: var(--ink) !important;
}

.stApp {
    background-color: var(--paper) !important;
}

/* ─── SCROLLBAR ─────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--cream); }
::-webkit-scrollbar-thumb { background: var(--warm); border-radius: 3px; }

/* ─── SIDEBAR ───────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--ink) !important;
    border-right: 1px solid #1f1f1f !important;
}

/* Requested: pull sidebar content up by shrinking header gap */
[data-testid="stSidebarHeader"],
.st-emotion-cache-10p9htt {
    margin-bottom: -2rem !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span:not([data-testid]),
[data-testid="stSidebar"] div.stMarkdown {
    color: #e8e2d9 !important;
    font-family: 'Syne', sans-serif !important;
}

[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stNumberInput > div > div > input,
[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: #1a1a1a !important;
    border: 1px solid #333 !important;
    color: #e8e2d9 !important;
    border-radius: 6px !important;
}

[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    color: #f5f2ec !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 1.1rem !important;
}

[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    color: #888 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

[data-testid="stSidebar"] hr {
    border-color: #222 !important;
}

[data-testid="stSidebar"] .stSlider > div {
    padding: 0.2rem 0;
}

[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"] {
    color: #555 !important;
}

/* Sidebar section labels */
[data-testid="stSidebar"] h3 {
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #555 !important;
    margin: 1.2rem 0 0.4rem !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] h2 {
    font-size: 0.8rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #888 !important;
    font-weight: 500 !important;
    border-bottom: 1px solid #1f1f1f !important;
    padding-bottom: 0.5rem !important;
    margin-bottom: 1rem !important;
}

[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stSlider label {
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: #666 !important;
}

[data-testid="stSidebar"] .stExpander {
    border: 1px solid #2a2a2a !important;
    background: #111 !important;
    border-radius: 8px !important;
    overflow: visible !important;
}

[data-testid="stSidebar"] .stExpander > details {
    background: #111 !important;
    border-radius: 8px !important;
}

[data-testid="stSidebar"] .stExpander summary {
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #777 !important;
    padding: 0.5rem 0.8rem !important;
    cursor: pointer !important;
}

[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    display: none !important;
}
[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    display: none !important;
}
[data-testid="stSidebar"] [data-testid="stMetricDelta"] {
    display: none !important;
}
[data-testid="stSidebar"] [data-testid="stMetric"] {
    display: none !important;
}

/* Sidebar is always open: hide all collapse/open controls */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
button[aria-label="Collapse sidebar"],
button[aria-label="Open sidebar"],
button[title="Collapse sidebar"],
button[title="Open sidebar"],
header button[aria-label*="sidebar" i] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
}

/* Keep sidebar panel permanently visible */
[data-testid="stSidebar"] {
    transform: translateX(0) !important;
}

/* ─── MAIN HEADER ───────────────────────────────────────────────────── */
.nutri-hero {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    padding: 2.5rem 0 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}

.nutri-hero-title {
    font-size: 4.5rem;
    font-weight: 800;
    line-height: 0.9;
    letter-spacing: -0.03em;
    color: var(--ink);
}

.nutri-hero-title span {
    color: var(--accent);
}

.nutri-hero-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    letter-spacing: 0.05em;
    text-transform: uppercase;
    max-width: 260px;
    text-align: right;
    line-height: 1.6;
}

/* ─── UPLOAD ZONE ───────────────────────────────────────────────────── */
.upload-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.5rem;
}

[data-testid="stFileUploader"] {
    background: var(--card-bg) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    transition: border-color 0.2s, background 0.2s;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
    background: var(--hover) !important;
}

[data-testid="stFileUploader"] label {
    font-size: 0.75rem !important;
    color: var(--muted) !important;
    letter-spacing: 0.05em !important;
}

/* ─── CONFIDENCE SLIDER ─────────────────────────────────────────────── */
[data-testid="stSlider"] .stMarkdown {
    font-size: 0.65rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: var(--muted) !important;
}

/* ─── SECTION DIVIDER ───────────────────────────────────────────────── */
.section-rule {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 2rem 0 1.2rem;
}

.section-rule-label {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    white-space: nowrap;
}

.section-rule-line {
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ─── IMAGE GRID ────────────────────────────────────────────────────── */
.img-grid-label {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.8rem;
}

[data-testid="stImage"] img {
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    transition: transform 0.2s, box-shadow 0.2s;
    object-fit: cover;
    aspect-ratio: 1 / 1;
}

[data-testid="stImage"] img:hover {
    transform: scale(1.02);
    box-shadow: 0 8px 28px rgba(0,0,0,0.12);
}

/* ─── FOOD DETECTION CARDS ──────────────────────────────────────────── */
.detect-card {
    background: var(--ink);
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    transition: background 0.15s, border-color 0.15s;
}

.detect-card:hover {
    background: #1a1a1a;
    border-color: #444;
}

.detect-card-empty {
    opacity: 1 !important;
    background: #f1ece2;
    border: 1px solid #c9c2b5;
}

.detect-card-empty .detect-card-index {
    color: #6b6560;
}

.detect-card-empty .detect-card-name {
    color: #2f2a24;
    font-weight: 600;
}

.detect-card-empty .detect-kcal {
    color: #4a433b;
}

.detect-card-index {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    color: #444;
    min-width: 28px;
}

.detect-card-name {
    font-weight: 700;
    font-size: 1rem;
    flex: 1;
    letter-spacing: -0.01em;
    color: #f0ece4;
}

.detect-conf-pill {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 999px;
    letter-spacing: 0.04em;
}

.conf-high   { background: #0f3d22; color: #4ade80; }
.conf-med    { background: #3d2a00; color: #fbbf24; }
.conf-low    { background: #3d0f0f; color: #f87171; }

.detect-kcal {
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    font-size: 0.95rem;
    color: #c84b2f;
    min-width: 90px;
    text-align: right;
}

/* ─── SUMMARY BENTO ─────────────────────────────────────────────────── */
.bento-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 1rem;
    margin: 1.5rem 0;
}

.bento-cell {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    position: relative;
    overflow: hidden;
}

.bento-cell::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px;
    height: 100%;
    background: var(--accent);
    opacity: 0;
    transition: opacity 0.2s;
}

.bento-cell:hover::before { opacity: 1; }

.bento-label {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.4rem;
}

.bento-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--ink);
    line-height: 1;
}

.bento-sub {
    font-size: 0.7rem;
    color: var(--muted);
    margin-top: 0.3rem;
    font-family: 'Space Mono', monospace;
}

/* ─── SCORE BAR ─────────────────────────────────────────────────────── */
.score-bar-wrap {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem 2rem;
    margin-bottom: 1rem;
}

.score-bar-title {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 1rem;
}

.score-row {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.score-number {
    font-family: 'Space Mono', monospace;
    font-size: 3.5rem;
    font-weight: 700;
    line-height: 1;
    min-width: 100px;
}

.score-good  { color: var(--accent3); }
.score-ok    { color: var(--accent2); }
.score-bad   { color: var(--accent); }

.score-bar-bg {
    flex: 1;
    height: 8px;
    background: var(--cream);
    border-radius: 999px;
    overflow: hidden;
}

.score-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.8s cubic-bezier(0.22, 1, 0.36, 1);
}

.score-verdict {
    font-size: 0.88rem;
    color: var(--muted);
    margin-top: 0.8rem;
    line-height: 1.5;
    font-style: italic;
}

/* ─── MEAL TARGET TAG ───────────────────────────────────────────────── */
.meal-tag-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 0.8rem;
}

.meal-tag {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    padding: 4px 12px;
    border-radius: 999px;
    background: var(--cream);
    border: 1px solid var(--border);
    color: var(--muted);
}

.meal-tag.active {
    background: var(--ink);
    color: var(--paper);
    border-color: var(--ink);
}

/* ─── SPINNER / PROCESSING ──────────────────────────────────────────── */
[data-testid="stSpinner"] {
    font-size: 0.75rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

/* ─── STREAMLIT OVERRIDES ───────────────────────────────────────────── */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1100px !important;
}

[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    font-size: 0.82rem !important;
    font-family: 'Space Mono', monospace !important;
}

[data-testid="stAlert"] {
    background: #f1edbe !important;
    color: #2f2a24 !important;
}

[data-testid="stAlert"] * {
    color: #2f2a24 !important;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.02em !important;
}

.stCaption {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.68rem !important;
    color: var(--muted) !important;
    letter-spacing: 0.03em !important;
}

footer { display: none !important; }
#MainMenu { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }

/* style the header bar to match our theme, touch nothing else */
[data-testid="stHeader"] {
    background: var(--paper) !important;
    border-bottom: 1px solid var(--border) !important;
    box-shadow: none !important;
}

/* ─── RADIO BUTTONS IN SIDEBAR ──────────────────────────────────────── */
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 0.3rem !important;
}
</style>
""")


# ─── HERO HEADER ──────────────────────────────────────────────────────────────
st.html("""
<div class="nutri-hero">
    <div class="nutri-hero-title">
        NUTRI<br><span>SCAN</span>
    </div>
    <div class="nutri-hero-sub">
        AI-powered food detection<br>
        & personalised calorie tracking<br>
        — upload. detect. optimise.
    </div>
</div>
""")


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.html("""
    <div style="padding:1.225rem 0 1rem; border-bottom:1px solid #1e1e1e; margin-bottom:1rem;">
        <div style="font-family:'Syne',sans-serif; font-size:1.6rem; font-weight:800; letter-spacing:-0.03em; line-height:1; color:#f5f2ec;">
            NUTRI<span style="color:#c84b2f;">SCAN</span>
        </div>
        <div style="font-family:'Space Mono',monospace; font-size:0.58rem; color:#444; letter-spacing:0.1em; margin-top:4px; text-transform:uppercase;">
            Food · Calories · Health
        </div>
    </div>
    """)

    weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5)
    height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)
    age       = st.number_input("Age (years)", min_value=10, max_value=100, value=30, step=1)
    gender    = st.radio("Gender", ["Male", "Female"])
    activity  = st.selectbox(
        "Activity Level",
        ["Sedentary", "Light", "Moderate", "Active", "Very Active"],
        help="Sedentary: little/no exercise · Light: 1-3 days/week · Moderate: 3-5 days/week · Active: 6-7 days/week · Very Active: twice daily",
    )
    meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])

    bmi     = calculate_bmi(weight_kg, height_cm)
    bmi_cat = bmi_category(bmi)

    st.html('<div style="font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;color:#444;font-family:Syne,sans-serif;margin:1rem 0 0.3rem;">Goal Weight</div>')
    recommended_goal = calculate_goal_weight(height_cm, bmi, bmi_cat)
    goal_weight = st.number_input(
        "Goal Weight (kg)",
        min_value=30.0, max_value=200.0,
        value=recommended_goal, step=0.5,
        help=f"Recommended: {recommended_goal:.1f} kg",
    )
    weight_diff   = abs(weight_kg - goal_weight)
    default_weeks = max(1, int(round(weight_diff / 0.5))) if weight_diff > 0 else 1
    timeline_weeks = st.slider(
        "Timeline (weeks)", min_value=1, max_value=104,
        value=min(default_weeks, 104),
    )

    tdee = calculate_tdee(
        weight_kg, height_cm, age, gender,
        ActivityLevel[activity.upper().replace(" ", "_")],
    )
    weekly_adjustment, weeks_to_goal, daily_adjustment = calculate_weight_loss_plan(
        weight_kg, goal_weight, timeline_weeks=timeline_weeks,
    )
    adjusted_tdee = calculate_adjusted_tdee_for_goal(
        tdee, weight_kg, goal_weight, daily_adjustment=daily_adjustment,
    )

    with st.expander("📊 Stats", expanded=False):
        targets = meal_calorie_targets(adjusted_tdee)

        # compact two-column grid via HTML — no st.columns()
        if weight_kg > goal_weight:
            adj_label = "For Loss"
            adj_val   = f"{adjusted_tdee:.0f}"
            adj_delta = f"−{tdee - adjusted_tdee:.0f} kcal/day"
        elif weight_kg < goal_weight:
            adj_label = "For Gain"
            adj_val   = f"{adjusted_tdee:.0f}"
            adj_delta = f"+{adjusted_tdee - tdee:.0f} kcal/day"
        else:
            adj_label = "Maintain"
            adj_val   = f"{adjusted_tdee:.0f}"
            adj_delta = "on track"

        timeline_row = f"<div class='sb-row'><span class='sb-k'>TIMELINE</span><span class='sb-v'>{weeks_to_goal}w</span></div>" if weight_kg != goal_weight else ""

        st.html(f"""
        <style>
        .sb-grid {{ display:flex; flex-direction:column; gap:0; padding: 0.2rem 0; }}
        .sb-section {{ padding: 0.5rem 0; border-bottom: 1px solid #1e1e1e; }}
        .sb-section:last-child {{ border-bottom: none; }}
        .sb-row {{ display:flex; justify-content:space-between; align-items:baseline; padding: 3px 0; }}
        .sb-k {{ font-size:0.6rem; letter-spacing:0.12em; text-transform:uppercase; color:#555; font-family:'Syne',sans-serif; }}
        .sb-v {{ font-size:0.82rem; font-weight:700; color:#e8e2d9; font-family:'Space Mono',monospace; }}
        .sb-delta {{ font-size:0.62rem; color:#888; font-family:'Space Mono',monospace; margin-top:1px; text-align:right; }}
        .sb-meal-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:4px 12px; padding-top:4px; }}
        .sb-meal-cell {{ display:flex; flex-direction:column; }}
        .sb-meal-k {{ font-size:0.58rem; letter-spacing:0.1em; text-transform:uppercase; color:#555; }}
        .sb-meal-v {{ font-size:0.78rem; font-weight:700; color:#e8e2d9; font-family:'Space Mono',monospace; }}
        </style>
        <div class="sb-grid">
          <div class="sb-section">
            <div class="sb-row"><span class="sb-k">BMI</span><span class="sb-v">{bmi:.1f}</span></div>
            <div class="sb-row"><span class="sb-k">STATUS</span><span class="sb-v" style="font-size:0.72rem">{bmi_cat}</span></div>
            <div class="sb-row"><span class="sb-k">NOW → GOAL</span><span class="sb-v">{weight_kg:.1f}→{goal_weight:.1f}kg</span></div>
            {timeline_row}
          </div>
          <div class="sb-section">
            <div class="sb-row"><span class="sb-k">TDEE</span><span class="sb-v">{tdee:.0f} kcal</span></div>
            <div class="sb-row"><span class="sb-k">{adj_label}</span><span class="sb-v">{adj_val} kcal</span></div>
            <div class="sb-delta">{adj_delta}</div>
          </div>
          <div class="sb-section">
            <div class="sb-meal-grid">
              <div class="sb-meal-cell"><span class="sb-meal-k">Breakfast</span><span class="sb-meal-v">{targets[MealType.BREAKFAST]:.0f}</span></div>
              <div class="sb-meal-cell"><span class="sb-meal-k">Lunch</span><span class="sb-meal-v">{targets[MealType.LUNCH]:.0f}</span></div>
              <div class="sb-meal-cell"><span class="sb-meal-k">Dinner</span><span class="sb-meal-v">{targets[MealType.DINNER]:.0f}</span></div>
              <div class="sb-meal-cell"><span class="sb-meal-k">Snack</span><span class="sb-meal-v">{targets[MealType.SNACK]:.0f}</span></div>
            </div>
          </div>
        </div>
        """)


# ─── UPLOAD & CONTROLS ────────────────────────────────────────────────────────
st.html('<div class="upload-label">Upload food images</div>')
uploaded_files = st.file_uploader(
    "Drag & drop or click to browse",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

conf = st.slider(
    "Confidence threshold",
    min_value=0.01, max_value=0.90, value=0.25, step=0.01,
    format="%.2f",
)


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def _save_temp_image(file_bytes: bytes, suffix: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        return tmp.name


def _pretty_food_name(name: str) -> str:
    return " ".join(word.capitalize() for word in name.split())


def _confidence_class(confidence: float) -> tuple[str, str]:
    if confidence >= 0.6:
        return "High", "conf-high"
    if confidence >= 0.35:
        return "Med", "conf-med"
    return "Low", "conf-low"


def _score_class(score: float) -> str:
    if score >= 85:
        return "score-good"
    if score >= 60:
        return "score-ok"
    return "score-bad"


def _score_color(score: float) -> str:
    if score >= 85:
        return "#2dbe6c"
    if score >= 60:
        return "#2f6dc8"
    return "#c84b2f"


# ─── MAIN RESULTS ─────────────────────────────────────────────────────────────
if uploaded_files:
    all_food_items  = []
    total_calories  = 0

    # — IMAGE GRID —
    st.html("""
    <div class="section-rule">
        <span class="section-rule-label">Uploaded images</span>
        <div class="section-rule-line"></div>
    </div>
    """)

    thumb_size = 180
    for row_start in range(0, len(uploaded_files), 4):
        cols      = st.columns(4)
        row_files = uploaded_files[row_start:row_start + 4]
        for col_idx, uf in enumerate(row_files):
            with cols[col_idx]:
                image = Image.open(uf)
                st.image(image, width=thumb_size, caption=f"#{row_start + col_idx + 1}")

    # — DETECTIONS —
    st.html("""
    <div class="section-rule">
        <span class="section-rule-label">Detection results</span>
        <div class="section-rule-line"></div>
    </div>
    """)

    with st.spinner(f"Processing {len(uploaded_files)} image(s) · AI detection running…"):
        for idx, uf in enumerate(uploaded_files):
            image      = Image.open(uf)
            suffix     = Path(uf.name).suffix or ".jpg"
            image_path = _save_temp_image(uf.getvalue(), suffix)

            detections = detect_food(image_path, conf=conf, max_det=1)

            if detections:
                top        = max(detections, key=lambda d: d.get("confidence", 0.0))
                food_name  = _pretty_food_name(top["food"])
                confidence = float(top["confidence"])
                conf_text, conf_cls = _confidence_class(confidence)

                _, details = calculate_calories([top])
                calories   = details[0]["calories"] if details else 0

                all_food_items.append({"food": food_name, "confidence": confidence, "calories": calories})
                total_calories += calories

                st.html(f"""
                <div class="detect-card">
                    <span class="detect-card-index">#{idx+1:02d}</span>
                    <span class="detect-card-name">{food_name}</span>
                    <span class="detect-conf-pill {conf_cls}">{conf_text} · {confidence:.2f}</span>
                    <span class="detect-kcal">{calories} kcal</span>
                </div>
                """)
            else:
                st.html(f"""
                <div class="detect-card detect-card-empty">
                    <span class="detect-card-index">#{idx+1:02d}</span>
                    <span class="detect-card-name">No food detected</span>
                    <span class="detect-conf-pill conf-low">Below threshold</span>
                    <span class="detect-kcal">— kcal</span>
                </div>
                """)

    # — SUMMARY BENTO —
    if all_food_items:
        st.html("""
        <div class="section-rule">
            <span class="section-rule-label">Summary</span>
            <div class="section-rule-line"></div>
        </div>
        """)

        meal_enum           = MealType[meal_type.upper()]
        effective_tdee      = adjusted_tdee
        meal_targets        = meal_calorie_targets(effective_tdee)
        selected_meal_tgt   = meal_targets[meal_enum]
        rec_min, rec_max    = meal_calorie_allocation(effective_tdee, meal_enum)
        score, verdict      = calculate_health_score(total_calories, rec_min, rec_max)

        avg_kcal = round(total_calories / len(all_food_items)) if all_food_items else 0
        pct_of_target = round((total_calories / selected_meal_tgt) * 100) if selected_meal_tgt else 0

        st.html(f"""
        <div class="bento-grid">
            <div class="bento-cell">
                <div class="bento-label">Items detected</div>
                <div class="bento-value">{len(all_food_items)}</div>
                <div class="bento-sub">avg {avg_kcal} kcal/item</div>
            </div>
            <div class="bento-cell">
                <div class="bento-label">Total calories</div>
                <div class="bento-value">{total_calories}</div>
                <div class="bento-sub">kcal · {pct_of_target}% of meal goal</div>
            </div>
            <div class="bento-cell">
                <div class="bento-label">{meal_type} target</div>
                <div class="bento-value">{int(selected_meal_tgt)}</div>
                <div class="bento-sub">kcal · range {int(rec_min)}–{int(rec_max)}</div>
            </div>
        </div>
        """)

        # — SCORE BAR —
        score_cls   = _score_class(score)
        bar_color   = _score_color(score)
        score_label = "Excellent" if score >= 85 else ("On Track" if score >= 60 else "Off Target")

        meal_tags = ""
        for mt in ["Breakfast", "Lunch", "Dinner", "Snack"]:
            active = "active" if mt == meal_type else ""
            t      = meal_targets[MealType[mt.upper()]]
            meal_tags += f'<span class="meal-tag {active}">{mt} · {int(t)} kcal</span>'

        st.html(f"""
        <div class="score-bar-wrap">
            <div class="score-bar-title">Health score · {meal_type}</div>
            <div class="score-row">
                <div class="score-number {score_cls}">{int(score)}</div>
                <div style="flex:1;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                        <span style="font-size:0.7rem;color:var(--muted);font-family:'Space Mono',monospace;letter-spacing:0.05em;">{score_label}</span>
                        <span style="font-size:0.7rem;color:var(--muted);font-family:'Space Mono',monospace;">/100</span>
                    </div>
                    <div class="score-bar-bg">
                        <div class="score-bar-fill" style="width:{int(score)}%;background:{bar_color};"></div>
                    </div>
                </div>
            </div>
            <div class="score-verdict">{verdict}</div>
            <div class="meal-tag-row">{meal_tags}</div>
        </div>
        """)

        st.caption(
            f"Daily adjusted TDEE: {effective_tdee:.0f} kcal · "
            f"Meal window: {int(rec_min)}–{int(rec_max)} kcal · "
            f"Total consumed: {total_calories} kcal"
        )

    else:
        st.warning("No foods detected across all images. Try lowering the confidence threshold.")