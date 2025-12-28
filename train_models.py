# train_models.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# ---------- CONFIG ----------
DATA_CSV = "real_foods_labeled.csv"
FEATURES = ["calories", "protein", "carbs", "fat", "sugar", "sodium", "gi"]

# Map label column -> output model file
LABELS = {
    "diabetes_label": "model_diabetes.joblib",
    "hypertension_label": "model_hypertension.joblib",
    "cvd_label": "model_cvd.joblib",
    "pcos_label": "model_pcos.joblib",
    "obesity_label": "model_obesity.joblib"
}

# Training settings
TEST_SIZE = 0.1667  # ~ 1/6 (like before)
RANDOM_STATE = 42

# ---------- helpers ----------
def plot_confusion(y_true, y_pred, classes, out_png):
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=classes, yticklabels=classes)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(out_png.rsplit(".",1)[0])
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

def train_and_eval(label_col, out_name):
    print("\n--- Training:", label_col, "---")
    df = pd.read_csv(DATA_CSV)

    # ensure label_col exists
    if label_col not in df.columns:
        raise RuntimeError(f"Missing column in CSV: {label_col}")

    # Drop rows with NaNs in features or label
    sub = df[FEATURES + [label_col]].dropna()

    X = sub[FEATURES].values
    y = sub[label_col].values

    # encode labels if they are strings (sklearn handles strings, but keep order)
    classes = np.unique(y).tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y if len(classes)>1 else None
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(n_estimators=150, random_state=RANDOM_STATE))
    ])

    pipeline.fit(X_train, y_train)
    train_acc = accuracy_score(y_train, pipeline.predict(X_train))
    test_acc = accuracy_score(y_test, pipeline.predict(X_test))

    print("Train accuracy:", round(train_acc, 3))
    print("Test accuracy:", round(test_acc, 3))
    print("\nClassification report (test):")
    print(classification_report(y_test, pipeline.predict(X_test)))

    # save confusion matrix image and model
    cm_png = out_name.replace(".joblib", "_confusion.png")
    plot_confusion(y_test, pipeline.predict(X_test), classes, cm_png)
    joblib.dump(pipeline, out_name)
    print("Saved confusion matrix to", cm_png)
    print("Saved model to", out_name)

    return {"label": label_col, "train_acc": float(train_acc), "test_acc": float(test_acc)}

def main():
    summaries = []
    for label_col, out_name in LABELS.items():
        try:
            res = train_and_eval(label_col, out_name)
            summaries.append(res)
        except Exception as e:
            print(f"Error training {label_col}: {e}")

    print("\nSummary:")
    for s in summaries:
        print(s)

if __name__ == "__main__":
    main()
