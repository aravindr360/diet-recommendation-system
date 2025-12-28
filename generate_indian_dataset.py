# generate_indian_dataset.py  (simple, deterministic)
import pandas as pd
import random
random.seed(42)

base_foods = [
 "rice","roti","chapati","idli","dosa","poha","upma","paratha","pulao","puliyodarai",
 "biryani","sambar","paneer","fish","chicken","banana","apple","mango","ghee","almonds",
 "curd","egg","milk","dal","vegetable_curry","aloo_curry","palak_paneer","chole","rajma",
 "moong_dal","grilled_chicken","fried_fish","samosa","vada","pakora","pav_bhaji","pani_puri",
 "kathi_roll","pomegranate","guava","peanuts","cashews"
]

# We'll make about 150 items by repeating base list and adding a variant suffix
foods = []
suffix = 1
while len(foods) < 150:
    for f in base_foods:
        name = f if suffix == 1 else f + f"_v{suffix}"
        foods.append(name)
        if len(foods) >= 150:
            break
    suffix += 1

rows = []
for f in foods[:150]:
    # simple nutrient assignment (keeps script fast)
    calories = random.randint(30, 420)
    protein = round(random.uniform(0.2, 30),1)
    carbs = round(random.uniform(0.0, 80),1)
    fat = round(random.uniform(0.0, 35),1)
    sugar = round(random.uniform(0,25),1)
    sodium = random.randint(0,900)
    gi = random.randint(20,90)

    # labels using simple thresholds (existing)
    if sugar < 6:
        d_label = "Recommended"
    elif sugar <= 12:
        d_label = "Moderate"
    else:
        d_label = "Avoid"

    if sodium < 150:
        h_label = "Recommended"
    elif sodium <= 350:
        h_label = "Moderate"
    else:
        h_label = "Avoid"

    if fat < 8:
        c_label = "Recommended"
    elif fat <= 18:
        c_label = "Moderate"
    else:
        c_label = "Avoid"

    # --- NEW LABELS: PCOS & OBESITY ---
    # PCOS: sensitive to sugar and high carbs
    # (you can tune thresholds later with real data / nutritionist)
    if sugar > 15 or carbs > 60:
        pcos_label = "Avoid"
    elif sugar > 8 or carbs > 40:
        pcos_label = "Moderate"
    else:
        pcos_label = "Recommended"

    # Obesity: sensitive to calories and fat
    if calories > 350 or fat > 20:
        obesity_label = "Avoid"
    elif calories > 250 or fat > 12:
        obesity_label = "Moderate"
    else:
        obesity_label = "Recommended"

    rows.append({
        "food": f,
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "sugar": sugar,
        "sodium": sodium,
        "gi": gi,
        "diabetes_label": d_label,
        "hypertension_label": h_label,
        "cvd_label": c_label,
        "pcos_label": pcos_label,
        "obesity_label": obesity_label
    })

df = pd.DataFrame(rows)
df.to_csv("indian_foods_dataset.csv", index=False)
print("Wrote indian_foods_dataset.csv with", len(df), "rows")

