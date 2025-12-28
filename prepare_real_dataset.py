import pandas as pd

# ---------- Load datasets ----------
usda = pd.read_csv("usda_foods.csv")
ifct = pd.read_csv("ifct_foods.csv")

# ---------- Select useful columns ----------
usda = usda[[
    "FoodName", "Energy_kcal", "Protein_g",
    "Carbohydrate_g", "Fat_g", "Sugar_g", "Sodium_mg"
]]

usda.columns = [
    "food", "calories", "protein",
    "carbs", "fat", "sugar", "sodium"
]

ifct = ifct[[
    "Food_Name", "Energy", "Protein",
    "Carbohydrate", "Fat"
]]

ifct.columns = [
    "food", "calories", "protein", "carbs", "fat"
]

# ---------- Handle missing values ----------
usda.fillna(0, inplace=True)
ifct.fillna(0, inplace=True)

# ---------- Add missing columns to IFCT ----------
ifct["sugar"] = 0
ifct["sodium"] = 0

# ---------- Merge datasets ----------
combined = pd.concat([usda, ifct], ignore_index=True)

# ---------- Add GI (temporary estimation) ----------
def estimate_gi(carbs):
    if carbs < 20:
        return 40
    elif carbs < 50:
        return 60
    else:
        return 75

combined["gi"] = combined["carbs"].apply(estimate_gi)

# ---------- Save final dataset ----------
combined.to_csv("real_foods_cleaned.csv", index=False)

print("Saved real_foods_cleaned.csv with", len(combined), "rows")
