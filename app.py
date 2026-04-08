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


st.set_page_config(page_title="Calorie Tracker", page_icon="🍽️", layout="wide")
st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    .food-item-card {
        padding: 1rem;
        border: 1px solid #e6e8ef;
        border-radius: 10px;
        background: #fafbff;
        color: #0f172a;
        margin-bottom: 0.8rem;
    }
    .card {
        padding: 1rem 1.1rem;
        border: 1px solid #e6e8ef;
        border-radius: 14px;
        background: #fafbff;
        color: #0f172a;
    }
    .small-label {
        font-size: 0.85rem;
        color: #475569;
        letter-spacing: 0.01em;
    }
    .big-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0f172a;
    }
    .conf-badge {
        display: inline-block;
        margin-top: 0.5rem;
        padding: 0.25rem 0.55rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .food-item-image {
        width: 100%;
        max-width: 200px;
        height: auto;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🍽️ Food Calorie & Health Tracker")
st.caption("Upload multiple food images and get personalized health recommendations based on cumulative calories.")

with st.sidebar:
    st.header("👤 Your Profile")
    weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5)
    height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)
    age = st.number_input("Age (years)", min_value=10, max_value=100, value=30, step=1)
    gender = st.radio("Gender", ["Male", "Female"])
    activity = st.selectbox(
        "Activity Level",
        ["Sedentary", "Light", "Moderate", "Active", "Very Active"],
        help="Sedentary: little/no exercise, Light: 1-3 days/week, Moderate: 3-5 days/week, Active: 6-7 days/week, Very Active: twice daily",
    )
    meal_type = st.selectbox(
        "🍴 Meal Type",
        ["Breakfast", "Lunch", "Dinner", "Snack"],
    )

    bmi = calculate_bmi(weight_kg, height_cm)
    bmi_cat = bmi_category(bmi)
    
    st.divider()
    st.subheader("🎯 Weight Management")
    recommended_goal = calculate_goal_weight(height_cm, bmi, bmi_cat)
    goal_weight = st.number_input(
        "Goal Weight (kg)",
        min_value=30.0,
        max_value=200.0,
        value=recommended_goal,
        step=0.5,
        help=f"Recommended: {recommended_goal:.1f} kg based on your BMI",
    )

    weight_diff = abs(weight_kg - goal_weight)
    default_weeks = max(1, int(round(weight_diff / 0.5))) if weight_diff > 0 else 1
    timeline_weeks = st.slider(
        "Timeline (weeks)",
        min_value=1,
        max_value=104,
        value=min(default_weeks, 104),
        help="Shorter timeline means larger daily calorie adjustment.",
    )

    tdee = calculate_tdee(
        weight_kg,
        height_cm,
        age,
        gender,
        ActivityLevel[activity.upper().replace(" ", "_")],
    )

    # Dynamic plan based on selected timeline.
    weekly_adjustment, weeks_to_goal, daily_adjustment = calculate_weight_loss_plan(
        weight_kg,
        goal_weight,
        timeline_weeks=timeline_weeks,
    )
    adjusted_tdee = calculate_adjusted_tdee_for_goal(
        tdee,
        weight_kg,
        goal_weight,
        daily_adjustment=daily_adjustment,
    )
    
    with st.expander("📊 Your Stats"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("BMI", f"{bmi:.1f}")
            st.metric("Status", bmi_cat)
        with col2:
            st.metric("Current → Goal", f"{weight_kg:.1f} → {goal_weight:.1f} kg")
            if weight_kg != goal_weight:
                st.metric("Timeline", f"{weeks_to_goal} weeks")
        
        st.divider()
        col3, col4 = st.columns(2)
        with col3:
            st.metric("Daily TDEE (Maintenance)", f"{tdee:.0f} kcal")
        with col4:
            if weight_kg > goal_weight:
                adjustment = tdee - adjusted_tdee
                st.metric("Adjusted for Loss", f"{adjusted_tdee:.0f} kcal", delta=f"-{adjustment:.0f} kcal/day")
            elif weight_kg < goal_weight:
                adjustment = adjusted_tdee - tdee
                st.metric("Adjusted for Gain", f"{adjusted_tdee:.0f} kcal", delta=f"+{adjustment:.0f} kcal/day")
            else:
                st.metric("Target TDEE", f"{adjusted_tdee:.0f} kcal", delta="Maintain")

        if weight_kg != goal_weight:
            st.caption(
                f"Weekly calorie adjustment: {weekly_adjustment:.0f} kcal/week | "
                f"Daily adjustment: {daily_adjustment:.0f} kcal/day"
            )

        targets = meal_calorie_targets(adjusted_tdee)
        st.divider()
        st.caption("Goal Meal Plan (sums to adjusted daily calories)")
        t1, t2, t3, t4 = st.columns(4)
        with t1:
            st.metric("Breakfast", f"{targets[MealType.BREAKFAST]:.0f} kcal")
        with t2:
            st.metric("Lunch", f"{targets[MealType.LUNCH]:.0f} kcal")
        with t3:
            st.metric("Dinner", f"{targets[MealType.DINNER]:.0f} kcal")
        with t4:
            st.metric("Snack", f"{targets[MealType.SNACK]:.0f} kcal")


uploaded_files = st.file_uploader("Upload food images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
conf = st.slider("Confidence Threshold", min_value=0.01, max_value=0.90, value=0.25, step=0.01)


def _save_temp_image(file_bytes: bytes, suffix: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        return tmp.name


def _pretty_food_name(name: str) -> str:
    return " ".join(word.capitalize() for word in name.split())


def _confidence_style(confidence: float) -> tuple[str, str, str]:
    if confidence >= 0.6:
        return "High Confidence", "#0f766e", "#d1fae5"
    if confidence >= 0.35:
        return "Medium Confidence", "#b45309", "#fef3c7"
    return "Low Confidence", "#b91c1c", "#fee2e2"


if uploaded_files:
    all_food_items = []
    total_calories = 0

    st.subheader("📸 Uploaded Images")
    thumb_size = 190
    for row_start in range(0, len(uploaded_files), 4):
        row_cols = st.columns(4)
        row_files = uploaded_files[row_start:row_start + 4]
        for col_idx, uploaded_file in enumerate(row_files):
            with row_cols[col_idx]:
                image = Image.open(uploaded_file)
                st.image(image, width=thumb_size, caption=f"Image {row_start + col_idx + 1}")

    st.subheader("🎯 Detection Results")
    with st.spinner(f"Processing {len(uploaded_files)} image(s)..."):
        for idx, uploaded_file in enumerate(uploaded_files):
            image = Image.open(uploaded_file)
            suffix = Path(uploaded_file.name).suffix or ".jpg"
            image_path = _save_temp_image(uploaded_file.getvalue(), suffix)

            detections = detect_food(image_path, conf=conf, max_det=1)

            if detections:
                top = max(detections, key=lambda d: d.get("confidence", 0.0))
                food_name = _pretty_food_name(top["food"])
                confidence = float(top["confidence"])
                conf_text, conf_color, conf_bg = _confidence_style(confidence)

                _, details = calculate_calories([top])
                calories = details[0]["calories"] if details else 0

                all_food_items.append({"food": food_name, "confidence": confidence, "calories": calories})
                total_calories += calories

                st.markdown(
                    f"""
                    <div class='food-item-card'>
                        <strong>{food_name}</strong> | Confidence: <span style='color:{conf_color}'>{confidence:.2f}</span> ({conf_text}) | Calories: <strong>{calories} kcal</strong>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.warning(f"❌ Image {idx+1}: No food detected")

    if all_food_items:
        st.divider()
        st.subheader("💪 Overall Health Score & Summary")

        meal_enum = MealType[meal_type.upper()]
        # Goal scoring always uses adjusted TDEE meal split.
        effective_tdee = adjusted_tdee
        meal_targets = meal_calorie_targets(effective_tdee)
        selected_meal_target = meal_targets[meal_enum]
        rec_min, rec_max = meal_calorie_allocation(effective_tdee, meal_enum)
        score, verdict = calculate_health_score(total_calories, rec_min, rec_max)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Items", len(all_food_items))
        with col2:
            st.metric("Health Score", f"{score:.0f}/100", delta=f"Goal: {selected_meal_target:.0f} kcal")
        with col3:
            st.metric("Total Calories", f"{total_calories} kcal")

        st.caption(
            f"Selected meal target range ({meal_type}): {rec_min:.0f}-{rec_max:.0f} kcal | "
            f"Daily goal total: {effective_tdee:.0f} kcal"
        )

        st.divider()
        if score >= 90:
            st.success(f"✅ {verdict}")
        elif score >= 70:
            st.info(f"⚠️ {verdict}")
        else:
            st.warning(f"❌ {verdict}")

        st.success(f"✨ Total: {total_calories} kcal for {meal_type.lower()}")
    else:
        st.warning("No foods detected in any images. Try a lower confidence value.")
