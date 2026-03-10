import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.planner import NutritionalGoal, MealPlanner

# Load food dataset
foods_df = pd.read_csv("data/foods.csv")

st.title("AI Meal and Diet Planner")

# --- User Inputs ---
st.header("Enter Your Information")

# Basic info
name = st.text_input("Name", value="User")
age = st.number_input("Age", min_value=10, max_value=120, value=25)
weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
height = st.number_input("Height (cm)", min_value=100, max_value=220, value=170)
gender = st.radio("Gender", ["Male", "Female"])
vegetarian = st.checkbox("Vegetarian?", value=False)
include_snacks = st.checkbox("Include Snacks?", value=False)

# Constraints
max_prep_time = st.number_input("Max prep time per meal (minutes)", min_value=5, max_value=120, value=30)
budget = st.number_input("Max cost per meal (PKR)", min_value=50, max_value=3000, value=1000)

# Allergies
allergen_options = ["milk", "eggs", "gluten", "fish", "nuts", "soy", "shellfish"]
allergies = st.multiselect("Select your allergies", options=allergen_options, default=[])

# --- Calorie target ---
st.markdown("### Calorie Target")
calorie_mode = st.radio(
    "Select Calorie Target Mode",
    ["Auto (based on BMR/TDEE)", "Enter manually"]
)

meal_calorie_targets = None  # Ensure defined

if calorie_mode == "Enter manually":
    manual_mode = st.radio(
        "Manual calorie input type",
        ["Daily total only", "Per meal targets"]
    )

    if manual_mode == "Daily total only":
        daily_calories = st.number_input(
            "Daily Calorie Target",
            min_value=1200,
            max_value=5000,
            value=2000,
            step=50
        )
    else:
        st.markdown("### Enter calories per meal")

        breakfast_cals = st.number_input("Breakfast calories", 0, 1000, 350)
        lunch_cals = st.number_input("Lunch calories", 0, 1500, 550)
        dinner_cals = st.number_input("Dinner calories", 0, 1500, 600)

        snack_cals = 0
        if include_snacks:
            snack_cals = st.number_input("Snack calories", 0, 800, 200)

        meal_calorie_targets = {
            "breakfast": breakfast_cals,
            "lunch": lunch_cals,
            "dinner": dinner_cals
        }

        if include_snacks:
            meal_calorie_targets["snack"] = snack_cals

        daily_calories = sum(meal_calorie_targets.values())

else:
    # Calculate BMR
    if gender == "Male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # Activity factor
    st.markdown("### Activity Level")
    activity_level = st.selectbox(
        "Select your typical activity level",
        [
            ("Sedentary (little or no exercise)", 1.2),
            ("Lightly active (light exercise 1-3 days/week)", 1.375),
            ("Moderately active (moderate exercise 3-5 days/week)", 1.55),
            ("Very active (hard exercise 6-7 days/week)", 1.725),
            ("Extra active (very hard exercise, physical job)", 1.9)
        ],
        format_func=lambda x: x[0]
    )

    tdee = bmr * activity_level[1]

    st.markdown(
        f"""
        <div style="background-color:#b3d7f0; padding:15px; border-radius:8px; color:#0b3d91; margin-bottom:10px;">
            <strong>Basal Metabolic Rate (BMR)</strong>: {int(bmr)} kcal/day<br>
            Calories your body needs at rest to maintain basic functions.
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div style="background-color:#b3d7f0; padding:15px; border-radius:8px; color:#0b3d91; margin-bottom:10px;">
            <strong>Total Daily Energy Expenditure (TDEE)</strong>: {int(tdee)} kcal/day
        </div>
        """,
        unsafe_allow_html=True
    )

    daily_calories = st.number_input(
        "Daily Calorie Target (Adjust if needed)",
        min_value=1200,
        max_value=5000,
        value=int(tdee),
        step=50
    )
    meal_calorie_targets = None  # Auto mode

# --- Generate Weekly Plan ---
if st.button("Generate Weekly Plan"):
    goal = NutritionalGoal(
        daily_calories=daily_calories,
        vegetarian=vegetarian,
        max_prep_time=max_prep_time,
        include_snacks=include_snacks
    )

    planner = MealPlanner(goal, "data/foods.csv")

    try:
        weekly_plan = planner.create_weekly_plan(
            max_cost=budget,
            allergens=allergies,
            meal_calorie_targets=meal_calorie_targets
        )

        st.header(f"Weekly Meal Plan for {name}")

        # Helper for table
        def render_table_html(df):
            html = "<table style='width:100%; border-collapse: collapse; text-align:center;'>"
            html += "<thead><tr style='background-color:#001f4d; color:white;'>"
            for col in df.columns:
                html += f"<th style='padding:10px;'>{col}</th>"
            html += "</tr></thead><tbody>"
            for _, row in df.iterrows():
                html += "<tr>"
                for val in row:
                    html += f"<td style='padding:10px;'>{val}</td>"
                html += "</tr>"
            html += "</tbody></table>"
            st.markdown(html, unsafe_allow_html=True)

        # Weekly accumulators
        weekly_calories = {"Breakfast":0,"Lunch":0,"Dinner":0}
        weekly_cost = {"Breakfast":0,"Lunch":0,"Dinner":0}
        if include_snacks:
            weekly_calories["Snack"] = 0
            weekly_cost["Snack"] = 0

        # Tables per day
        for day, meals in weekly_plan.items():
            st.subheader(day)

            table_data = []
            meal_slots = ["Breakfast","Lunch","Dinner"]
            if include_snacks: meal_slots.append("Snack")

            for meal in meal_slots:
                recipe_name = meals.get(meal, None)
                recipe_info = foods_df[foods_df["name"] == recipe_name] if recipe_name else pd.DataFrame()

                if not recipe_info.empty:
                    calories = int(recipe_info["calories"].values[0])
                    cost = recipe_info["cost"].values[0]
                    attrs = recipe_info["attributes"].values[0]
                    vegetarian_flag = "Yes" if recipe_info["vegetarian"].values[0] else "No"
                    weekly_calories[meal] += calories
                    weekly_cost[meal] += cost
                else:
                    calories = "-"
                    cost = "-"
                    attrs = "-"
                    vegetarian_flag = "-"

                table_data.append({
                    "Meal": meal,
                    "Recipe": recipe_name if recipe_name else "-",
                    "Calories": calories,
                    "Cost (PKR)": cost,
                    "Vegetarian": vegetarian_flag,
                    "Attributes": attrs
                })

            df = pd.DataFrame(table_data)
            render_table_html(df)

        # --- Weekly Summary ---
        st.header("📊 Weekly Summary 📊")
        total_weekly_calories = sum([v for v in weekly_calories.values()])
        weekly_target = daily_calories * 7

        st.info(f"**Weekly Calorie Target:** {weekly_target} kcal")
        st.info(f"**Total Calories Planned:** {total_weekly_calories} kcal")
        st.progress(min(total_weekly_calories/weekly_target,1.0))

        # Weekly Calories chart
        cal_df = pd.DataFrame(list(weekly_calories.items()), columns=["Meal","Calories"])
        st.subheader("🍽️ Weekly Calories per Meal")
        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar(cal_df["Meal"], cal_df["Calories"], color=["#4e79a7","#f28e2b","#e15759","#76b7b2"][:len(cal_df)])
        ax.set_ylabel("Calories")
        ax.set_xlabel("Meal")
        ax.set_title("Total Weekly Calories per Meal")
        fig.tight_layout()
        st.pyplot(fig) 

        # Weekly Cost chart
        cost_df = pd.DataFrame(list(weekly_cost.items()), columns=["Meal","Cost"])
        st.subheader("💰 Weekly Cost per Meal")
        fig2, ax2 = plt.subplots(figsize=(6,4))
        ax2.bar(cost_df["Meal"], cost_df["Cost"], color=["#59a14f","#edc948","#b07aa1","#ff9da7"][:len(cost_df)])
        ax2.set_ylabel("Cost (PKR)")
        ax2.set_xlabel("Meal")
        ax2.set_title("Total Weekly Cost per Meal")
        fig2.tight_layout()
        st.pyplot(fig2)

    except ValueError as e:
        st.error("Unable to generate a weekly plan with current constraints.")
        st.info("Try increasing prep time, budget, or relaxing some dietary restrictions/allergens.")
