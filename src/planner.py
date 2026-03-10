import pandas as pd
from src.constraints import build_and_solve_ilp

# --- Class to encapsulate user nutritional goals ---
class NutritionalGoal:
    def __init__(self, daily_calories, vegetarian=False, max_prep_time=None, include_snacks=False):
        """
        Parameters:
        - daily_calories (int): Target calories per day
        - vegetarian (bool): Whether to only include vegetarian meals
        - max_prep_time (int | None): Maximum allowed preparation time per meal
        - include_snacks (bool): Whether snacks should be included in the plan
        """
        self.daily_calories = daily_calories
        self.vegetarian = vegetarian
        self.max_prep_time = max_prep_time
        self.include_snacks = include_snacks


# --- MealPlanner handles filtering and planning meals ---
class MealPlanner:
    def __init__(self, nutritional_goal: NutritionalGoal, food_data_path="data/foods.csv"):
        """
        Load food dataset and initialize planner with user goals.
        """
        self.goal = nutritional_goal
        self.foods = pd.read_csv(food_data_path)
        # Ensure 'vegetarian' column is boolean for filtering
        if "vegetarian" in self.foods.columns:
            self.foods['vegetarian'] = self.foods['vegetarian'].astype(bool)
        else:
            self.foods['vegetarian'] = False

    def filter_recipes(self, max_cost=None, allergens=[]):
        """
        Apply hard filters based on cost, vegetarian preference, prep time, and allergens.
        Returns a filtered DataFrame of candidate recipes.
        """
        df = self.foods.copy()
        if max_cost:
            df = df[df["cost"] <= max_cost]
        if self.goal.vegetarian:
            df = df[df["vegetarian"] == True]
        if self.goal.max_prep_time:
            df = df[df["prep_time"] <= self.goal.max_prep_time]
        for allergen in allergens:
            df = df[~df["allergens"].str.contains(allergen, case=False, na=False)]
        return df

    def create_weekly_plan(self, max_cost=200, allergens=[], meal_calorie_targets=None):
        """
        Generate a 7-day meal plan using ILP (integer linear programming).
        Raises ValueError if constraints cannot be satisfied.
        """
        if build_and_solve_ilp is None:
            raise RuntimeError("ILP function not available. Cannot generate weekly plan.")
        
        filtered = self.filter_recipes(max_cost=max_cost, allergens=allergens)
        meal_slots = ["breakfast", "lunch", "dinner"]
        if self.goal.include_snacks:
            meal_slots.append("snack")

        # Quick feasibility check to ensure enough options per meal
        for meal in meal_slots:
            candidates = filtered[filtered["meal_type"].str.lower() == meal]
            if len(candidates) == 0:
                raise ValueError(f"No recipes for {meal.capitalize()} with current constraints.")
            if len(candidates) < 4:
                raise ValueError(
                    f"Too few recipes ({len(candidates)}) for {meal.capitalize()} to satisfy repetition rules."
                )

        # Build the ILP plan
        plan = build_and_solve_ilp(
            foods_df=self.foods,
            daily_calories=self.goal.daily_calories,
            vegetarian=self.goal.vegetarian,
            max_prep_time=self.goal.max_prep_time,
            max_cost=max_cost,
            allergens=allergens,
            include_snacks=self.goal.include_snacks,
            meal_calorie_targets=meal_calorie_targets
        )

        if not plan:
            raise ValueError("Unable to generate weekly plan with current constraints.")

        return plan
