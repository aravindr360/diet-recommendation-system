import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from imblearn.over_sampling import SMOTE

# ---------- CONFIG ----------
DATA_CSV = "real_foods_binary.csv"

BASE_FEATURES = ["calories", "protein", "carbs", "fat", "sugar", "sodium", "gi"]

FEATURES = [
    "calories", "protein", "carbs", "fat",
    "sugar", "sodium", "gi",
    "carb_ratio", "fat_ratio", "sugar_load"
]

LABELS = {
    "diabetes_label": "model_diabetes.joblib",
    "hypertension_label": "model_hypertension.joblib",
    "cvd_label": "model_cvd.joblib",
    "pcos_label": "model_pcos.joblib",
    "obesity_label": "model_obesity.joblib"
}

TEST_SIZE = 0.1667
RANDOM_STATE = 42

# ---------- helpers ----------
def plot_confusion(y_true, y_pred, classes, out_png):

    cm = confusion_matrix(y_true, y_pred, labels=classes)

    plt.figure(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=classes,
        yticklabels=classes
    )

    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(out_png.replace(".png", ""))
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()


def train_and_eval(label_col, out_name):

    print("\n--- Training:", label_col, "---")

    df = pd.read_csv(DATA_CSV)

    if label_col not in df.columns:
        raise RuntimeError(f"Missing column in CSV: {label_col}")

    sub = df[BASE_FEATURES + [label_col]].dropna()

    # ✅ Feature Engineering (VERY IMPORTANT)
    sub["carb_ratio"] = sub["carbs"] / sub["calories"]
    sub["fat_ratio"] = sub["fat"] / sub["calories"]
    sub["sugar_load"] = sub["sugar"] * sub["gi"]

    X = sub[FEATURES].values
    y = sub[label_col].values

    classes = np.unique(y).tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y if len(classes) > 1 else None
    )

    # ✅ SMOTE (Fix Imbalance)
    smote = SMOTE(random_state=RANDOM_STATE)
    X_train, y_train = smote.fit_resample(X_train, y_train)

    # ✅ Pipeline
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            random_state=RANDOM_STATE,
            class_weight="balanced"
        ))
    ])

    # ✅ Stable Cross Validation
    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE
    )

    # ✅ Improved Hyperparameter Grid
    param_grid = {
        "clf__n_estimators": [200, 400, 600],
        "clf__max_depth": [5, 10, 20, None],
        "clf__min_samples_split": [2, 5, 10],
        "clf__min_samples_leaf": [1, 2, 4]
    }

    print("Running GridSearchCV...")

    grid = GridSearchCV(
        pipeline,
        param_grid,
        cv=cv,
        scoring="f1_weighted",
        n_jobs=-1
    )

    grid.fit(X_train, y_train)

    best_model = grid.best_estimator_

    print("Best Parameters:", grid.best_params_)

    train_pred = best_model.predict(X_train)
    test_pred = best_model.predict(X_test)

    train_acc = accuracy_score(y_train, train_pred)
    test_acc = accuracy_score(y_test, test_pred)

    print("Train accuracy:", round(train_acc, 3))
    print("Test accuracy:", round(test_acc, 3))

    print("\nClassification report (test):")
    print(classification_report(y_test, test_pred))

    # ✅ Confusion Matrix
    cm_png = out_name.replace(".joblib", "_confusion.png")
    plot_confusion(y_test, test_pred, classes, cm_png)

    # ✅ Save Model
    joblib.dump(best_model, out_name)

    print("Saved confusion matrix to", cm_png)
    print("Saved model to", out_name)

    return {
        "label": label_col,
        "train_acc": float(train_acc),
        "test_acc": float(test_acc)
    }


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



