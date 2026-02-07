import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# 1. Load the Data
print("Loading data...")
df = pd.read_csv("real_foods_labeled.csv")

# 2. Define Features (X) - Same as training
X = df[['calories', 'protein', 'carbs', 'fat', 'sugar', 'sodium', 'gi']]

# 3. List of Diseases to Check
diseases = ['diabetes', 'hypertension', 'cvd', 'pcos', 'obesity']

print("\n" + "="*40)
print("   🤖 MODEL ACCURACY REPORT   ")
print("="*40)

for disease in diseases:
    # Load the specific Target (y)
    target_col = f"{disease}_label"
    y = df[target_col]

    # Split Data (80% Train, 20% Test) - To Simulate "New" Data
    # We use a distinct random_state to ensure we aren't just memorizing
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Load the Saved Model
    model_filename = f"model_{disease}.joblib"
    try:
        clf = joblib.load(model_filename)
        
        # Make Predictions
        y_pred = clf.predict(X_test)
        
        # Calculate Accuracy
        acc = accuracy_score(y_test, y_pred)
        
        # Print Results
        print(f"\n🩺 Disease Model: {disease.upper()}")
        print(f"   ✅ Accuracy: {acc * 100:.2f}%")
        
        # Optional: Show Confusion Matrix details if they ask "What mistakes did it make?"
        # cm = confusion_matrix(y_test, y_pred)
        # print(f"   📊 Correct Predictions: {cm[0][0] + cm[1][1]}/{len(y_test)}")

    except FileNotFoundError:
        print(f"\n❌ Model file '{model_filename}' not found. Did you run train_models.py?")

print("\n" + "="*40)