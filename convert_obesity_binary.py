import pandas as pd

# Load dataset
df = pd.read_csv("real_foods_labeled.csv")

# Mapping logic
def map_binary(label):
    if label == "Recommended":
        return "Safe"
    else:
        return "Risky"

# Apply conversion
df["obesity_binary"] = df["obesity_label"].apply(map_binary)

# Save new dataset
df.to_csv("real_foods_binary.csv", index=False)

print("✅ Binary obesity dataset created successfully!")
