from flask import Flask, request, jsonify, send_file, send_from_directory
import joblib
import pandas as pd
import io
import os
import re
import json
import random
import sqlite3 # <--- SQLITE DATABASE
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

app = Flask(__name__)

# --- 🟢 CONFIGURATION ---
genai.configure(api_key="AIzaSyCtqchXbO9VXQ4QZfJhSoNxrD8zAFpY8-o")

# --- LOAD MODELS & DATA ---
models = {
    "diabetes": joblib.load("model_diabetes.joblib"),
    "hypertension": joblib.load("model_hypertension.joblib"),
    "cvd": joblib.load("model_cvd.joblib"),
    "pcos": joblib.load("model_pcos.joblib"),
    "obesity": joblib.load("model_obesity.joblib")
}
foods = pd.read_csv("real_foods_labeled.csv")

# --- 🗄️ DATABASE SETUP (PERSISTENT DATA) ---
DB_NAME = "diet_system.db"

def init_db():
    """Creates the database file and tables automatically."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    
    # 2. Diets Table (Stores the plan as text)
   # Inside init_db() function in app.py
    c.execute('''CREATE TABLE IF NOT EXISTS diets 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, 
                  disease TEXT, 
                  age INTEGER, 
                  height INTEGER,  -- <--- NEW
                  weight INTEGER,  -- <--- NEW
                  bmi REAL,        -- <--- NEW
                  calories INTEGER, 
                  diet_plan_json TEXT, 
                  status TEXT, 
                  doctor_comment TEXT, 
                  timestamp TEXT)''')
    
    # Create Default Users (if not exist)
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?)", ('devika', '1234', 'doctor'))
        c.execute("INSERT INTO users VALUES (?, ?, ?)", ('admin', 'admin', 'doctor'))
        c.execute("INSERT INTO users VALUES (?, ?, ?)", ('aravind', '123', 'user'))
    except:
        pass # Users already exist
    
    conn.commit()
    conn.close()

# Run DB setup on start
init_db()
# --- HELPER FUNCTIONS (UPDATED WITH REGION + PCOS PROTEIN FIX) ---
def generate_smart_daily_plan(disease, age, pref, region, target_cal):
    safe_foods = foods.copy()
    
    # 1. Filter by Disease (The "Secret Filter")
    # This removes unsafe foods (e.g., High Sugar for Diabetes/PCOS)
    if disease:
        col_name = f"{disease.lower()}_label"
        if col_name in safe_foods.columns:
            safe_foods = safe_foods[safe_foods[col_name] == 'Recommended']
    
    # 2. Filter by Age
    if age < 12: target = ["Kids", "All"]
    elif age > 60: target = ["Seniors", "All"]
    else: target = ["Adults", "All"]
    safe_foods = safe_foods[safe_foods["target_audience"].isin(target)]
    
    # 3. Filter by Diet Preference (Veg vs Non-Veg)
    if pref == 'veg': 
        safe_foods = safe_foods[safe_foods['food_type'] == 'Veg']

    # 4. 🟢 NEW: Filter by Region (North vs South)
    # We keep the selected region PLUS "All" (Neutral foods like fruits, eggs, oats)
    if region and region != "All":
        target_regions = [region, "All"]
        if "region" in safe_foods.columns:
            safe_foods = safe_foods[safe_foods["region"].isin(target_regions)]

    # --- PORTION CONTROL ENGINE ---
    def get_meal(m_type, scale_cap=2.0):
        # A. Select Food Options
        options = safe_foods[safe_foods['meal_type'] == m_type]
        if options.empty: return None

        # 🟢 PCOS PRO TWEAK: Prioritize High Protein
        # If PCOS, we don't just pick randomly. We sort by Protein (Highest first)
        # and pick from the top 5 options.
        if disease and disease.lower() == "pcos":
            options = options.sort_values(by='protein', ascending=False).head(5)

        # Pick one random item from the available options
        item = options.sample(1).iloc[0].to_dict()
        
        # B. Calculate Scale (Portion Size)
        base_cal = item['calories']
        required = target_cal / 3
        raw_scale = required / base_cal
        
        # C. Medical Safety Logic (Preserved)
        is_diabetic = disease and disease.lower() == "diabetes"
        is_obese = disease and disease.lower() == "obesity"

        if is_diabetic:
            # Diabetes: Strict Cap (0.8x to 1.2x) to prevent spikes
            scale = 1.2 if raw_scale > 1.2 else (0.8 if raw_scale < 0.8 else raw_scale)

        elif is_obese:
            # Obesity: Allow Small Portions (0.7x) for deficit
            # Strict Cap at 1.1x (No large portions)
            scale = min(raw_scale, 1.1) 
            if scale < 0.7: scale = 0.7 # Minimum limit

        else:
            # Normal Logic (Hypertension, CVD, etc.)
            scale = min(raw_scale, 1.5)
            if scale < 1.0: scale = 1.0 # Standard users eat normal size

        scale = round(scale * 2) / 2
        
        # D. Rename Logic
        if scale >= 1.4: item['food'] += " (Large Portion)"
        elif scale <= 0.8: item['food'] += " (Small Portion)" 
            
        # E. Apply Nutrients
        item['calories'] = int(item['calories'] * scale)
        item['protein'] = round(item['protein'] * scale, 1)
        item['carbs'] = round(item['carbs'] * scale, 1)
        item['fat'] = round(item['fat'] * scale, 1)
        
        return item

    # Generate Meals
    breakfast = get_meal("Breakfast")
    lunch = get_meal("Lunch")
    dinner = get_meal("Dinner")
    
    # Calculate totals
    b_cal = breakfast['calories'] if breakfast else 0
    l_cal = lunch['calories'] if lunch else 0
    d_cal = dinner['calories'] if dinner else 0
    current_total = b_cal + l_cal + d_cal
    
    snack = None
    # Add snack if calories are low (BUT skip snack for Obesity to maintain deficit)
    if disease and disease.lower() != "obesity":
        if current_total < (target_cal - 250):
            snack = get_meal("Snack", scale_cap=1.5)
            
    return {"breakfast": breakfast, "lunch": lunch, "dinner": dinner, "snack": snack}
# --- ROUTES ---
@app.route("/")
def home(): return send_from_directory(".", "login.html")

@app.route("/dashboard")
def dashboard(): return send_from_directory(".", "index.html")

@app.route("/expert_panel")
def expert_panel(): return send_from_directory(".", "expert.html")

# --- 🔐 AUTH API (SQLITE) ---
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    role = data.get("role")
    u = data.get("username")
    p = data.get("password")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=? AND role=?", (u, p, role))
    user = c.fetchone()
    conn.close()

    if user:
        redirect = "/expert_panel" if role == "doctor" else "/dashboard"
        return jsonify({"status": "success", "redirect": redirect})
    
    return jsonify({"status": "error", "msg": "Invalid Credentials"}), 401

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    u = data.get("username")
    p = data.get("password")
    
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (u, p, 'user'))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "msg": "Username already exists"})

# --- 🥗 DIET GENERATION ---
@app.route("/get_diet", methods=["POST"])
def get_diet():
    data = request.json
    age = int(data.get("age", 30))
    pref = data.get("preferences", "non-veg")
    region = data.get('region', 'All')  # You got it here...
    disease = data.get("disease", "diabetes")
    target_cal = int(data.get("daily_calorie", 1800))

    # 🟢 FIX 1: AUTO-DEFICIT FOR OBESITY
    if disease.lower() == "obesity":
        target_cal = max(1200, target_cal - 500) 

    # 🔴 YOU MISSED IT HERE. ADD 'region' TO THE LIST:
    plan = generate_smart_daily_plan(disease, age, pref, region, target_cal) # <--- PASS THIS
    return jsonify(plan)

@app.route("/get_weekly_diet", methods=["POST"])
def get_weekly_diet():
    data = request.json
    age = int(data.get("age", 30))
    pref = data.get("preferences", "non-veg")
    region = data.get('region', 'All')  # You got it here...
    disease = data.get("disease", "diabetes")
    target_cal = int(data.get("daily_calorie", 1800))
    
    # 🟢 FIX 1: AUTO-DEFICIT FOR OBESITY
    if disease.lower() == "obesity":
        target_cal = max(1200, target_cal - 500)

    week = {}
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for day in days:
        # 🔴 YOU MISSED IT HERE TOO:
        week[day] = generate_smart_daily_plan(disease, age, pref, region, target_cal) # <--- PASS THIS
    
    return jsonify(week)

# --- 📤 SUBMISSION API (SQLITE) ---
@app.route("/api/submit_diet", methods=["POST"])
def submit_diet():
    data = request.json
    # Extract new fields
    username = data.get("username")
    disease = data.get("disease")
    age = data.get("age")
    height = data.get("height")  # <--- NEW
    weight = data.get("weight")  # <--- NEW
    bmi = data.get("bmi")        # <--- NEW
    calories = data.get("calories")
    diet_plan_json = json.dumps(data.get("diet_plan")) 
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Insert new fields
    c.execute('''INSERT INTO diets 
                 (username, disease, age, height, weight, bmi, calories, diet_plan_json, status, doctor_comment, timestamp) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                 (username, disease, age, height, weight, bmi, calories, diet_plan_json, "Pending Review", "Waiting for doctor...", timestamp))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# --- 🩺 DOCTOR API (SQLITE) ---
@app.route("/api/get_pending_diets", methods=["GET"])
def get_pending_diets():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM diets ORDER BY id DESC")
    rows = c.fetchall()
    
    diets = []
    for row in rows:
        diets.append({
            "id": row["id"],
            "username": row["username"],
            "disease": row["disease"],
            "age": row["age"],
            "height": row["height"], # <--- NEW
            "weight": row["weight"], # <--- NEW
            "bmi": row["bmi"],       # <--- NEW
            "calories": row["calories"],
            "status": row["status"],
            "doctor_comment": row["doctor_comment"],
            "diet_plan": json.loads(row["diet_plan_json"])
        })
    conn.close()
    return jsonify(diets)

@app.route("/api/submit_review", methods=["POST"])
def submit_review():
    data = request.json
    diet_id = data.get("id")
    action = data.get("action")
    comment = data.get("comment")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE diets SET status=?, doctor_comment=? WHERE id=?", (action, comment, diet_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# --- 📡 USER STATUS CHECK (UPDATED to return full plan) ---
@app.route("/api/get_user_status", methods=["POST"])
def get_user_status():
    username = request.json.get("username")
    
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Find latest submission by this user
    c.execute("SELECT * FROM diets WHERE username=? ORDER BY id DESC LIMIT 1", (username,))
    row = c.fetchone()
    conn.close()
    
    if not row: return jsonify({"status": "No Submission"})
    
    return jsonify({
        "status": row["status"], 
        "doctor_comment": row["doctor_comment"],
        "diet_plan": json.loads(row["diet_plan_json"]),
        # 🟢 NEW: Send Profile Data back to frontend
        "age": row["age"],
        "height": row["height"],
        "weight": row["weight"],
        "bmi": row["bmi"],
        "disease": row["disease"],
        "calories": row["calories"]
    })

# --- 📄 PDF DOWNLOAD (YOUR FIXED VERSION) ---
@app.route("/download_weekly_pdf", methods=["POST"])
def download_weekly_pdf():
    weekly_diet = request.json.get("weekly_diet")
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    y = 800
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, y, "Personalized Diet Plan Report")
    y -= 30
    p.setFont("Helvetica", 10)
    
    order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    sorted_days = [d for d in order if d in weekly_diet]
    remaining_days = [d for d in weekly_diet.keys() if d not in order]
    final_order = sorted_days + remaining_days
    
    for day in final_order:
        meals = weekly_diet[day]
        if y < 150: 
            p.showPage(); y = 800
        p.setFont("Helvetica-Bold", 14)
        p.setFillColorRGB(0.1, 0.3, 0.6)
        p.drawString(40, y, day.upper())
        p.setFillColorRGB(0, 0, 0)
        y -= 20
        p.setFont("Helvetica", 11)
        
        # 🟢 CRITICAL FIX: Skip empty snacks
        for m_type, item in meals.items():
            if not item: continue
            text = f"{m_type.capitalize()}: {item['food']} ({item['calories']} kcal)"
            p.drawString(60, y, text)
            y -= 15
        y -= 15

    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="diet_plan.pdf", mimetype="application/pdf")

# --- 🤖 CHATBOT (KEPT) ---
@app.route("/chat_ai", methods=["POST"])
def chat_ai():
    data = request.json
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(f"Medical AI: {data.get('query')}")
        return jsonify({"reply": response.text})
    except:
        return jsonify({"reply": "AI Error. Try again."})
# --- 📜 NEW: GET USER HISTORY ---
@app.route("/api/user_history", methods=["POST"])
def user_history():
    username = request.json.get("username")
    
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get ALL Approved diets for this user, newest first
    c.execute("SELECT * FROM diets WHERE username=? AND status='Approved' ORDER BY id DESC", (username,))
    rows = c.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "id": row["id"],
            "timestamp": row["timestamp"],
            "doctor_comment": row["doctor_comment"],
            "diet_plan": json.loads(row["diet_plan_json"])
        })
        
    return jsonify(history)
if __name__ == "__main__":
    app.run(debug=True, port=5000)


