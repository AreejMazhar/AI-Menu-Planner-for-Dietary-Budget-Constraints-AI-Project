import pulp

def build_and_solve_ilp(
    foods_df,
    daily_calories,
    vegetarian,
    max_prep_time,
    max_cost,
    allergens,
    include_snacks,
    meal_calorie_targets=None
):
    """
    Build and solve a weekly meal plan using integer linear programming.
    
    Hard constraints:
    - Forbidden foods (allergens, vegetarian, prep time, cost)
    - Exactly 1 recipe per meal per day
    - Max 2 repeats per week per recipe
    - No consecutive-day repetition
    
    Soft scoring:
    - Attribute matching (quick, sweet, healthy, etc.)
    - Calorie alignment
    - Repetition penalty
    """
    meal_slots = ["breakfast", "lunch", "dinner"]
    if include_snacks:
        meal_slots.append("snack")
    num_days = 7

    foods_df = foods_df.copy()
    foods_df["id"] = foods_df.index  # unique identifier for ILP variables

    # ------------------
    # Identify forbidden foods based on constraints
    # ------------------
    def has_allergen(row):
        allergens_clean = str(row["allergens"]).lower()
        return any(a.lower() in allergens_clean for a in allergens)

    foods_df["forbidden"] = False
    foods_df.loc[foods_df.apply(has_allergen, axis=1), "forbidden"] = True
    if vegetarian:
        foods_df.loc[foods_df["vegetarian"] == False, "forbidden"] = True
    if max_prep_time:
        foods_df.loc[foods_df["prep_time"] > max_prep_time, "forbidden"] = True
    if max_cost:
        foods_df.loc[foods_df["cost"] > max_cost, "forbidden"] = True

    # ------------------
    # Initialize ILP model
    # ------------------
    model = pulp.LpProblem("Weekly_Meal_Planner", pulp.LpMaximize)

    # Decision variables: x[i, meal, day] = 1 if recipe i is chosen for meal on day
    x = {}
    for i in foods_df["id"]:
        for m in meal_slots:
            for d in range(1, num_days+1):
                x[(i, m, d)] = pulp.LpVariable(f"x_{i}_{m}_{d}", cat="Binary")

    # --- Hard constraints ---

    # Exactly 1 recipe per meal per day
    for d in range(1, num_days+1):
        for m in meal_slots:
            model += pulp.lpSum(x[(i, m, d)] for i in foods_df["id"]) == 1

    # Forbidden foods cannot be selected
    for _, row in foods_df.iterrows():
        if row["forbidden"]:
            for m in meal_slots:
                for d in range(1, num_days+1):
                    model += x[(row["id"], m, d)] == 0

    # Max 2 repetitions per week per recipe
    MAX_REPEATS = 2
    for i in foods_df["id"]:
        model += pulp.lpSum(x[(i, m, d)] for m in meal_slots for d in range(1, num_days+1)) <= MAX_REPEATS

    # No consecutive-day repetition
    for i in foods_df["id"]:
        for d in range(1, num_days):
            model += (pulp.lpSum(x[(i, m, d)] for m in meal_slots) +
                      pulp.lpSum(x[(i, m, d+1)] for m in meal_slots)) <= 1

    # ------------------
    # Soft scoring: preference matching and calorie alignment
    # ------------------
    preferred_attrs = {
        "breakfast": ["quick", "sweet"],
        "lunch": ["light", "healthy"],
        "dinner": ["healthy", "spicy"],
        "snack": ["quick", "light"]
    }

    # Attribute score per recipe and meal
    attribute_score = {}
    for i, row in foods_df.iterrows():
        # takes attribute column, coverts into lower case list, strip removes extra spaces
        attrs = [a.strip().lower() for a in str(row["attributes"]).split(",")]
        for m in meal_slots:
            matches = sum(a in preferred_attrs.get(m, []) for a in attrs)
            attribute_score[(i, m)] = matches * 2

    # Ideal calorie fractions per meal
    def ideal_fraction(m):
        if m == "breakfast": return 0.25
        if m == "lunch": return 0.35
        if m == "dinner": return 0.40
        return 0.10  # snack

    # Calorie deviation penalty (smaller deviation = better)
    calorie_penalty = {}
    for i, row in foods_df.iterrows():
        for m in meal_slots:
            if meal_calorie_targets is not None:
                ideal = meal_calorie_targets.get(m, 0)
            else:
                ideal = daily_calories * ideal_fraction(m)

            calorie_penalty[(i, m)] = abs(row["calories"] - ideal) / 100.0

    # Penalty for repeating same recipe
    repetition_penalty = {i: 1 for i in foods_df["id"]}

    # Objective function: maximize attributes match, minimize calorie deviation and repetition
    model += pulp.lpSum(
        attribute_score[(i, m)] * x[(i, m, d)]
        - calorie_penalty[(i, m)] * x[(i, m, d)]
        - repetition_penalty[i] * x[(i, m, d)]
        for i in foods_df["id"]
        for m in meal_slots
        for d in range(1, num_days+1)
    )

    # Solve the ILP
    model.solve(pulp.PULP_CBC_CMD(msg=0))

    if pulp.LpStatus[model.status] != "Optimal":
        raise ValueError("Unable to generate a weekly plan. Constraints too strict.")

    # ------------------
    # Extract chosen recipes into a readable dictionary
    # ------------------
    final_plan = {}
    for d in range(1, num_days+1):
        final_plan[f"Day {d}"] = {}
        for m in meal_slots:
            chosen = None
            for i in foods_df["id"]:
                if pulp.value(x[(i, m, d)]) == 1:
                    chosen = foods_df.loc[foods_df["id"] == i, "name"].iloc[0]
                    break
            final_plan[f"Day {d}"][m.capitalize()] = chosen

    return final_plan
