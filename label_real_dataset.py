import pandas as pd

df = pd.read_csv("real_foods_cleaned.csv")

def diabetes_label(row):
    if row["sugar"] > 15 or row["gi"] > 70:
        return "Avoid"
    elif row["sugar"] > 7:
        return "Moderate"
    return "Recommended"

def hypertension_label(row):
    if row["sodium"] > 400:
        return "Avoid"
    elif row["sodium"] > 200:
        return "Moderate"
    return "Recommended"

def cvd_label(row):
    if row["fat"] > 20:
        return "Avoid"
    elif row["fat"] > 10:
        return "Moderate"
    return "Recommended"

def pcos_label(row):
    if row["sugar"] > 12 or row["carbs"] > 60:
        return "Avoid"
    elif row["sugar"] > 6:
        return "Moderate"
    return "Recommended"

def obesity_label(row):
    if row["calories"] > 350:
        return "Avoid"
    elif row["calories"] > 250:
        return "Moderate"
    return "Recommended"

df["diabetes_label"] = df.apply(diabetes_label, axis=1)
df["hypertension_label"] = df.apply(hypertension_label, axis=1)
df["cvd_label"] = df.apply(cvd_label, axis=1)
df["pcos_label"] = df.apply(pcos_label, axis=1)
df["obesity_label"] = df.apply(obesity_label, axis=1)

df.to_csv("real_foods_labeled.csv", index=False)
print("Saved real_foods_labeled.csv")
