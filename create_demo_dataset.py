import pandas as pd
import random

foods = [
 "idli","dosa","chapati","rice","oats","poha","sambar","paneer","fish","chicken",
 "banana","apple","mango","ghee","almonds","curd","egg","milk","dal","vegetable_curry"
]

rows = []
for f in foods:
    calories = random.randint(50, 400)
    protein = round(random.uniform(0.5, 25),1)
    carbs = round(random.uniform(5, 70),1)
    fat = round(random.uniform(0.1, 30),1)
    sugar = round(random.uniform(0,20),1)
    sodium = random.randint(10,600)
    gi = random.randint(30,90)

    if sugar < 6: d_label = "Recommended"
    elif sugar <= 12: d_label = "Moderate"
    else: d_label = "Avoid"

    if sodium < 150: h_label = "Recommended"
    elif sodium <= 350: h_label = "Moderate"
    else: h_label = "Avoid"

    if fat < 8: c_label = "Recommended"
    elif fat <= 18: c_label = "Moderate"
    else: c_label = "Avoid"

    rows.append({
        "food": f, "calories": calories, "protein": protein, "carbs": carbs,
        "fat": fat, "sugar": sugar, "sodium": sodium, "gi": gi,
        "diabetes_label": d_label, "hypertension_label": h_label, "cvd_label": c_label
    })

df = pd.DataFrame(rows)
df.to_csv("demo_foods.csv", index=False)
print("Wrote demo_foods.csv with", len(df), "rows")
