import pandas as pd

print("🚀 Loading dataset...")

df = pd.read_csv("real_foods_labeled.csv")

LABEL_COLUMNS = [
    "diabetes_label",
    "hypertension_label",
    "cvd_label",
    "pcos_label",
    "obesity_label"
]

def convert_label(value):
    if value == "Avoid":
        return "Risky"
    else:
        return "Safe"   # Recommended + Moderate

for col in LABEL_COLUMNS:
    if col in df.columns:
        df[col] = df[col].apply(convert_label)

print("✅ Conversion complete")

df.to_csv("real_foods_binary.csv", index=False)

print("🎉 Saved as real_foods_binary.csv")
