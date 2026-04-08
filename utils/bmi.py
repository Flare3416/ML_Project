from enum import Enum
import math


class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"  # 1.2
    LIGHT = "light"  # 1.375
    MODERATE = "moderate"  # 1.55
    ACTIVE = "active"  # 1.725
    VERY_ACTIVE = "very_active"  # 1.9


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


def activity_multiplier(level: ActivityLevel) -> float:
    """Return TDEE multiplier based on activity level."""
    multipliers = {
        ActivityLevel.SEDENTARY: 1.2,
        ActivityLevel.LIGHT: 1.375,
        ActivityLevel.MODERATE: 1.55,
        ActivityLevel.ACTIVE: 1.725,
        ActivityLevel.VERY_ACTIVE: 1.9,
    }
    return multipliers.get(level, 1.5)


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation."""
    if gender.lower() == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:  # female
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def calculate_tdee(weight_kg: float, height_cm: float, age: int, gender: str, activity: ActivityLevel) -> float:
    """Calculate Total Daily Energy Expenditure."""
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    return bmr * activity_multiplier(activity)


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI."""
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)


def bmi_category(bmi: float) -> str:
    """Return BMI category."""
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal Weight"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def meal_calorie_allocation(tdee: float, meal_type: MealType) -> tuple[float, float]:
    """
    Return recommended calorie range for a meal.
    Returns (min, max) calorie range.
    """
    # Fixed split that always sums to 100% of daily calories.
    targets = meal_calorie_targets(tdee)
    target = targets.get(meal_type, tdee * 0.25)

    # Tight range (+/- 8%) to make scoring more strict.
    tolerance = target * 0.08
    return target - tolerance, target + tolerance


def meal_calorie_targets(tdee: float) -> dict[MealType, float]:
    """Return exact per-meal calorie targets that sum to daily calories."""
    pct = {
        MealType.BREAKFAST: 0.25,
        MealType.LUNCH: 0.35,
        MealType.DINNER: 0.30,
        MealType.SNACK: 0.10,
    }
    return {meal: tdee * ratio for meal, ratio in pct.items()}


def calculate_health_score(food_calories: int, recommended_min: float, recommended_max: float) -> tuple[float, str]:
    """
    Calculate health score (0-100) based on food calories vs recommended range.
    Returns (score, verdict_text).
    """
    target = (recommended_min + recommended_max) / 2
    if target <= 0:
        return 0.0, "Invalid calorie target."

    deviation_pct = abs(food_calories - target) / target * 100

    # Drastic scoring: every 1% deviation drops score by 2.2 points.
    score = max(0.0, 100.0 - (deviation_pct * 2.2))

    if deviation_pct <= 5:
        verdict = "Excellent match for your current goal."
    elif food_calories < recommended_min:
        verdict = "Too low for this goal-focused meal. Add more calories."
    elif food_calories > recommended_max:
        verdict = "Too high for this goal-focused meal. Reduce calories."
    else:
        verdict = "Close to target, but can be improved."

    return score, verdict


def calculate_goal_weight(height_cm: float, current_bmi: float, bmi_category_str: str) -> float:
    """
    Recommend goal weight based on current BMI category.
    Returns goal weight in kg.
    """
    height_m = height_cm / 100
    
    if bmi_category_str == "Obese":
        # Target: Normal weight (BMI = 24)
        goal_bmi = 24.0
    elif bmi_category_str == "Overweight":
        # Target: Normal weight (BMI = 24)
        goal_bmi = 24.0
    elif bmi_category_str == "Underweight":
        # Target: Normal weight (BMI = 21.5)
        goal_bmi = 21.5
    else:
        # Already normal, maintain
        goal_bmi = current_bmi
    
    return goal_bmi * (height_m ** 2)


def calculate_weight_loss_plan(
    current_weight: float,
    goal_weight: float,
    timeline_weeks: int | None = None,
    weekly_rate_kg: float = 0.5,
) -> tuple[float, int, float]:
    """
    Calculate weight loss/gain plan.
    Returns (weekly_adjustment_kcal, weeks_to_goal, daily_adjustment_kcal).
    """
    weight_diff = abs(current_weight - goal_weight)
    if weight_diff == 0:
        return 0.0, 0, 0.0

    kcal_needed = weight_diff * 7700

    if timeline_weeks is not None and timeline_weeks > 0:
        weeks = timeline_weeks
        weekly_adjustment = kcal_needed / timeline_weeks
    else:
        weekly_adjustment = max(weekly_rate_kg, 0.1) * 7700
        weeks = max(1, math.ceil(kcal_needed / weekly_adjustment))

    daily_adjustment = weekly_adjustment / 7
    return weekly_adjustment, weeks, daily_adjustment


def calculate_adjusted_tdee_for_goal(
    current_tdee: float,
    current_weight: float,
    goal_weight: float,
    daily_adjustment: float | None = None,
) -> float:
    """
    Calculate adjusted TDEE for goal weight.
    If daily_adjustment is provided, use it; otherwise use a default pace.
    """
    if current_weight <= 0:
        return current_tdee

    if daily_adjustment is None:
        _, _, daily_adjustment = calculate_weight_loss_plan(current_weight, goal_weight)
    
    if current_weight > goal_weight:
        # Weight loss: apply calorie deficit
        return max(1200.0, current_tdee - daily_adjustment)
    elif current_weight < goal_weight:
        # Weight gain: add calorie surplus
        return current_tdee + daily_adjustment
    else:
        # Maintain
        return current_tdee