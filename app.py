# app.py
# app.py
from flask import Flask, request, jsonify, send_file, send_from_directory
import joblib
import pandas as pd
import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)

# ------------------------------------------------------
# LOAD MODELS
# ------------------------------------------------------
models = {
    "diabetes": joblib.load("model_diabetes.joblib"),
    "hypertension": joblib.load("model_hypertension.joblib"),
    "cvd": joblib.load("model_cvd.joblib"),
    "pcos": joblib.load("model_pcos.joblib"),
    "obesity": joblib.load("model_obesity.joblib")
}

# ------------------------------------------------------
# LOAD DATASET
# ------------------------------------------------------
foods = pd.read_csv("real_foods_labeled.csv")
FEATURES = ["calories", "protein", "carbs", "fat", "sugar", "sodium", "gi"]

# ------------------------------------------------------
# ADD ALL MODEL PREDICTIONS
# ------------------------------------------------------
def add_predictions(item):
    X = [[item.get(f, 0) for f in FEATURES]]
    for disease, model in models.items():
        try:
            item[f"{disease}_label"] = str(model.predict(X)[0])
        except:
            item[f"{disease}_label"] = "N/A"
    return item

# ------------------------------------------------------
# PICK DAILY MEALS
# ------------------------------------------------------
def pick_meals(disease):
    df = foods.copy()
    df["label"] = models[disease].predict(df[FEATURES])

    recommended = df[df["label"] == "Recommended"]
    if recommended.empty:
        recommended = df

    return {
        "breakfast": add_predictions(recommended.sample(1).iloc[0].to_dict()),
        "lunch": add_predictions(recommended.sample(1).iloc[0].to_dict()),
        "dinner": add_predictions(recommended.sample(1).iloc[0].to_dict())
    }

# ------------------------------------------------------
# API ROUTES
# ------------------------------------------------------
@app.route("/get_diet", methods=["POST"])
def get_diet():
    data = request.json
    return jsonify(pick_meals(data["disease"]))

@app.route("/get_weekly_diet", methods=["POST"])
def get_weekly_diet():
    data = request.json
    week = {}
    for i in range(1, 8):
        week[f"day{i}"] = pick_meals(data["disease"])
    return jsonify(week)

# ------------------------------------------------------
# PDF DOWNLOAD ROUTE
# ------------------------------------------------------
@app.route("/download_weekly_pdf", methods=["POST"])
def download_weekly_pdf():
    weekly_diet = request.json.get("weekly_diet")

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 40
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, y, "Weekly Diet Plan")
    y -= 30

    pdf.setFont("Helvetica", 11)

    for day, meals in weekly_diet.items():
        pdf.drawString(40, y, day.upper())
        y -= 18

        for meal, item in meals.items():
            line = f"{meal.capitalize()}: {item.get('food')} ({item.get('calories')} kcal)"
            pdf.drawString(60, y, line)
            y -= 14

        y -= 10
        if y < 100:
            pdf.showPage()
            y = height - 40
            pdf.setFont("Helvetica", 11)

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="weekly_diet_plan.pdf",
        mimetype="application/pdf"
    )

# ------------------------------------------------------
# FRONTEND
# ------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/files/<path:filename>")
def serve_files(filename):
    return send_from_directory(".", filename)

# ------------------------------------------------------
# RUN APP
# ------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)




