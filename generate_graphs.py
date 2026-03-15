import matplotlib
matplotlib.use('Agg')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import warnings

warnings.filterwarnings("ignore")

# ✅ CONFIGURATION (UPDATED)
CSV_FILE = "real_foods_binary.csv"

FEATURES = ['calories', 'protein', 'carbs', 'fat', 'sugar', 'sodium', 'gi']

DISEASE_TARGETS = [
    'diabetes_label',
    'hypertension_label',
    'cvd_label',
    'pcos_label',
    'obesity_label'
]

print(f"📊 Loading {CSV_FILE} for Learning Curves...")

try:
    df = pd.read_csv(CSV_FILE)
    df.columns = df.columns.str.strip().str.lower()

    X = df[FEATURES].fillna(0)

    for target_col in DISEASE_TARGETS:

        if target_col not in df.columns:
            continue

        disease_name = (
            target_col
            .replace('_label', '')
            .replace('cvd', 'Heart Disease')
            .title()
        )

        print(f"📈 Generating Graph for: {disease_name}...")

        le = LabelEncoder()
        y = le.fit_transform(df[target_col].astype(str))

        # ✅ Regularized Model (Stable & Realistic)
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            min_samples_split=10,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=42
        )

        train_sizes, train_scores, test_scores = learning_curve(
            model,
            X,
            y,
            cv=10,
            scoring='accuracy',
            n_jobs=-1,
            train_sizes=np.linspace(0.2, 1.0, 20)
        )

        train_mean = np.mean(train_scores, axis=1)
        test_mean = np.mean(test_scores, axis=1)

        plt.figure(figsize=(8, 6))

        plt.plot(train_sizes, train_mean, 'o-', label="Train Accuracy")
        plt.plot(train_sizes, test_mean, 'o-', label="Validation Accuracy")

        plt.title(f"Learning Curve: {disease_name}", fontsize=14, fontweight='bold')
        plt.xlabel("Training Samples")
        plt.ylabel("Accuracy")

        plt.legend(loc="lower right")
        plt.grid(True, linestyle='--', alpha=0.6)

        plt.ylim(0.80, 1.01)

        filename = f"learning_curve_{disease_name.lower().replace(' ', '_')}.png"

        plt.savefig(filename)
        print(f"   ✅ Saved: {filename}")

        plt.close()

    print("\n🎉 DONE! Graphs generated successfully.")

except Exception as e:
    print(f"❌ ERROR: {e}")
