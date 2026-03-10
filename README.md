# 🍽️ AI Menu Planner for Dietary & Budget Constraints

An AI-driven meal planning system that generates optimized weekly meal plans using Integer Linear Programming (ILP). The system respects dietary restrictions, allergies, budget constraints, and personal preferences while maximizing nutritional goals and meal variety.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![PuLP](https://img.shields.io/badge/PuLP-2.7+-green.svg)](https://coin-or.github.io/pulp/)

## 📌 Overview

Weekly meal planning is a repetitive, constraint-intensive problem. This system acts as an intelligent decision-making agent that evaluates available recipes and selects an optimal combination satisfying all mandatory requirements while maximizing overall meal quality.

### Key Features

- **Hard Constraints** (Must be satisfied):
  - No allergen-containing recipes
  - Exactly one recipe per meal slot
  - Per-meal cost and weekly budget limits
  - Preparation time limits
  - Dietary restrictions (vegetarian, etc.)
  - Max weekly repetitions & no consecutive-day repeats

- **Soft Constraints** (Optimization targets):
  - Preference alignment (quick, healthy, sweet, etc.)
  - Calorie target deviation minimization
  - Meal variety encouragement

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Optimization Engine** | Python + PuLP (CBC Solver) |
| **Frontend** | Streamlit |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Plotly, Matplotlib |
| **Environment** | Python 3.8+ |


## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AreejMazhar/AI-Menu-Planner-for-Dietary-Budget-Constraints-AI-Project
   cd AI_Menu_Planner
   ```
2. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```

3. Run the application
    ```bash
    streamlit run app.py
    ```
> The app will open in your browser at http://localhost:8501

## 📊 Dataset Format
The recipes.csv file contains the recipe database with the following structure:

| Column | Description | Example |
|-----------|------------|------------|
| **id** | Unique identifier | R001 |
| **name** | Recipe name | Chicken Biryani |
| **meal_type**	| breakfast/lunch/dinner/snack | dinner |
| **calories**	| Calories per serving	| 650 |
| **cost**	| Cost in PKR	| 450 |
| **prep_time**	| Preparation time (minutes)	| 35 |
| **vegetarian**	| Boolean flag	| FALSE |
| **allergens**	| list	| gluten, dairy |
| **attributes**	| tags	| spicy, heavy |

## 🔬 Key Algorithms & Techniques
- **Integer Linear Programming (ILP)**
- **Decision Variables:** Binary (recipe-slot-day assignments)
- **Solver:** CBC (Coin-or Branch and Cut)
- **Method:** Branch and Bound with Cutting Planes
- **Guarantee:** Optimal solution if feasible

## 🧠 How It Works
### 1. Environment Representation
The problem is modeled as an Integer Linear Programming (ILP) optimization with binary decision variables:
  ```bash
  x[i,m,d] ∈ {0,1} where:
  i = recipe index
  m = meal slot (breakfast/lunch/dinner/snack)
  d = day (1-7)
  ```
### 2. Objective Function
The solver maximizes a weighted score combining:
- **Attribute Matching Reward:** +2 per matching preference tag
- **Calorie Alignment Penalty:** Minimizes deviation from targets
- **Repetition Penalty:** -1 per recipe reuse (encourages variety)

### 3. Constraint Enforcement
- Exactly one recipe per meal slot
- Allergen exclusion
- Meal-slot compatibility
- Vegetarian restrictions
- Cost and prep-time limits
- Max 2 uses per week, no consecutive days

## Test Scenarios
### Scenario 1: Normal User (Feasible)
Female, 22 years, 57kg, 155cm
Non-vegetarian, includes snacks
Budget: 2000 PKR/meal, Prep time: 45 min
<img width="735" height="831" alt="image" src="https://github.com/user-attachments/assets/64c92f20-14ab-4465-996f-3dd136ff73ca" />
<img width="707" height="882" alt="image" src="https://github.com/user-attachments/assets/244fcbd6-755b-480a-b8b6-5e95bbe056f0" />
<img width="738" height="856" alt="image" src="https://github.com/user-attachments/assets/a1533b82-c596-4d59-8621-c05cbf2ee615" />
<img width="688" height="846" alt="image" src="https://github.com/user-attachments/assets/40d1317e-180a-4469-bc6c-cea892654187" />
<img width="696" height="712" alt="image" src="https://github.com/user-attachments/assets/793f7fc9-d6a3-4f05-bfff-1aefc5c3c0bc" />
<img width="691" height="490" alt="image" src="https://github.com/user-attachments/assets/b2c2b84f-1f0f-48df-998d-57ac849743c0" />

### Scenario 2: Strict Constraints (Infeasible)
Budget: 450 PKR/meal, Prep time: 20 min
Multiple allergies
<img width="729" height="824" alt="image" src="https://github.com/user-attachments/assets/b5f78d90-136c-46b5-a22c-57db74694b2d" />
<img width="741" height="516" alt="image" src="https://github.com/user-attachments/assets/7f3b2d74-ee4e-4641-8e8a-1e707b55ea5f" />

