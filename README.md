this our calorie filling code but may high carb by multiplying food (2idali to 4idali):

# --- HELPER FUNCTIONS (YOUR ORIGINAL LOGIC) ---
def generate_smart_daily_plan(disease, age, pref, target_cal):
    safe_foods = foods.copy()
    if disease:
        col_name = f"{disease.lower()}_label"
        if col_name in safe_foods.columns:
            safe_foods = safe_foods[safe_foods[col_name] == 'Recommended']
    
    if age < 12: target = ["Kids", "All"]
    elif age > 60: target = ["Seniors", "All"]
    else: target = ["Adults", "All"]
    safe_foods = safe_foods[safe_foods["target_audience"].isin(target)]
    
    if pref == 'veg': safe_foods = safe_foods[safe_foods['food_type'] == 'Veg']

    def get_meal(m_type, scale_cap=2.0):
        options = safe_foods[safe_foods['meal_type'] == m_type]
        if options.empty: return None
        item = options.sample(1).iloc[0].to_dict()
        
        base_cal = item['calories']
        required = target_cal / 3
        scale = required / base_cal
        if scale > scale_cap: scale = scale_cap
        if scale < 1.0: scale = 1.0
        
        def replacer(match):
            val = float(match.group(1)) * scale
            return str(int(val)) if val.is_integer() else str(round(val, 1))
        if scale > 1.1:
            item['food'] = re.sub(r"(\d+(?:\.\d+)?)", replacer, item['food'])
        
        item['calories'] = int(item['calories'] * scale)
        item['protein'] = round(item['protein'] * scale, 1)
        item['carbs'] = round(item['carbs'] * scale, 1)
        item['fat'] = round(item['fat'] * scale, 1)
        return item

    breakfast = get_meal("Breakfast")
    lunch = get_meal("Lunch")
    dinner = get_meal("Dinner")
    current_total = breakfast['calories'] + lunch['calories'] + dinner['calories']
    
    snack = None
    if disease.lower() != "obesity":
        if current_total < (target_cal - 250):
            snack = get_meal("Snack", scale_cap=1.5)
            
    return {"breakfast": breakfast, "lunch": lunch, "dinner": dinner, "snack": snack}

   # here is where no doubling is added

    def generate_smart_daily_plan(disease, age, pref, target_cal):
    safe_foods = foods.copy()
    
    # Filter by Disease
    if disease:
        col_name = f"{disease.lower()}_label"
        if col_name in safe_foods.columns:
            safe_foods = safe_foods[safe_foods[col_name] == 'Recommended']
    
    # Filter by Age
    if age < 12: target = ["Kids", "All"]
    elif age > 60: target = ["Seniors", "All"]
    else: target = ["Adults", "All"]
    safe_foods = safe_foods[safe_foods["target_audience"].isin(target)]
    
    # Filter by Preference
    if pref == 'veg': safe_foods = safe_foods[safe_foods['food_type'] == 'Veg']

    # --- 🟢 UPDATED SMART MEAL GENERATOR ---
    def get_meal(m_type, scale_cap=2.0):
        options = safe_foods[safe_foods['meal_type'] == m_type]
        if options.empty: return None
        item = options.sample(1).iloc[0].to_dict()
        
        base_cal = item['calories']
        required = target_cal / 3
        raw_scale = required / base_cal
        
        # 1. Disease Specific Scaling
        if disease and disease.lower() == "diabetes":
            # STRICT LIMIT for Diabetes: Range 0.8x to 1.2x only
            if raw_scale > 1.2: scale = 1.2
            elif raw_scale < 0.8: scale = 0.8
            else: scale = raw_scale
        else:
            # Normal: Range 1.0x to 1.5x (Never go too huge)
            scale = min(raw_scale, 1.5)
            if scale < 1.0: scale = 1.0

        # 2. Round Scale to clean numbers (1.0, 1.5, 2.0)
        scale = round(scale * 2) / 2
        
        # 3. Rename Food (Add Label instead of weird numbers)
        if scale >= 1.5:
            item['food'] += " (Large Portion)"
        elif scale <= 0.8:
            item['food'] += " (Small Portion)"
            
        # 4. Calculate Nutrients
        item['calories'] = int(item['calories'] * scale)
        item['protein'] = round(item['protein'] * scale, 1)
        item['carbs'] = round(item['carbs'] * scale, 1)
        item['fat'] = round(item['fat'] * scale, 1)
        return item
    # --- END UPDATED LOGIC ---

    breakfast = get_meal("Breakfast")
    lunch = get_meal("Lunch")
    dinner = get_meal("Dinner")
    
    # Calculate totals
    b_cal = breakfast['calories'] if breakfast else 0
    l_cal = lunch['calories'] if lunch else 0
    d_cal = dinner['calories'] if dinner else 0
    current_total = b_cal + l_cal + d_cal
    
    snack = None
    # Add snack if calories are low (except for Obesity)
    if disease and disease.lower() != "obesity":
        if current_total < (target_cal - 250):
            snack = get_meal("Snack", scale_cap=1.5)
            
    return {"breakfast": breakfast, "lunch": lunch, "dinner": dinner, "snack": snack}

# code for adding cobination food


# --- HELPER FUNCTIONS (YOUR ORIGINAL LOGIC) ---
def generate_smart_daily_plan(disease, age, pref, target_cal):
    safe_foods = foods.copy()
    
    # Filter by Disease
    if disease:
        col_name = f"{disease.lower()}_label"
        if col_name in safe_foods.columns:
            safe_foods = safe_foods[safe_foods[col_name] == 'Recommended']
    
    # Filter by Age
    if age < 12: target = ["Kids", "All"]
    elif age > 60: target = ["Seniors", "All"]
    else: target = ["Adults", "All"]
    safe_foods = safe_foods[safe_foods["target_audience"].isin(target)]
    
    # Filter by Preference
    if pref == 'veg': safe_foods = safe_foods[safe_foods['food_type'] == 'Veg']

    # --- 🟢 SOPHISTICATED MEAL GENERATOR ---
    def get_meal(m_type, scale_cap=2.0):
        # 1. Select Food
        options = safe_foods[safe_foods['meal_type'] == m_type]
        if options.empty: return None
        item = options.sample(1).iloc[0].to_dict()
        
        # 2. Calculate Scale
        base_cal = item['calories']
        required = target_cal / 3
        raw_scale = required / base_cal
        
        # 3. Safety Logic
        is_diabetic = disease and disease.lower() == "diabetes"
        
        if is_diabetic:
            scale = 1.2 if raw_scale > 1.2 else (0.8 if raw_scale < 0.8 else raw_scale)
        else:
            scale = min(raw_scale, 1.5)
            if scale < 1.0: scale = 1.0

        scale = round(scale * 2) / 2
        
        # 4. Rename Main Dish
        if scale >= 1.4: item['food'] += " (Large Portion)"
        elif scale <= 0.8: item['food'] += " (Small Portion)"
            
        # 5. Apply Nutrients
        final_cal = int(item['calories'] * scale)
        final_prot = item['protein'] * scale
        final_carb = item['carbs'] * scale
        final_fat = item['fat'] * scale
        
        # --- 6. INTELLIGENT SIDE DISH PAIRING ---
        calorie_gap = required - final_cal
        
        if calorie_gap > 80:
            food_name = item['food'].lower()
            possible_sides = []

            # A. BREAKFAST / CONTINENTAL
            if any(x in food_name for x in ["oats", "bread", "toast", "egg", "soup", "salad", "pasta", "sandwich"]):
                possible_sides = [
                    {"name": " & 5 Almonds", "cal": 45, "p": 2, "c": 1, "f": 4},
                    {"name": " & Walnuts", "cal": 60, "p": 2, "c": 2, "f": 6},
                    {"name": " & 1 Boiled Egg", "cal": 70, "p": 6, "c": 0.5, "f": 5},
                    {"name": " & 1/2 Apple", "cal": 50, "p": 0, "c": 12, "f": 0}
                ]

            # B. INDIAN MEALS
            else:
                possible_sides = [
                    {"name": " & Cucumber Salad", "cal": 30, "p": 1, "c": 6, "f": 0},
                    {"name": " & Buttermilk", "cal": 50, "p": 2, "c": 4, "f": 2},
                    {"name": " & Small Bowl Curd", "cal": 60, "p": 3, "c": 4, "f": 3},
                    {"name": " & Sautéed Beans", "cal": 40, "p": 2, "c": 7, "f": 0}
                ]
            
            # Shuffle
            random.shuffle(possible_sides)

            # Add sides
            sides_added = 0
            for side in possible_sides:
                if calorie_gap < 40 or sides_added >= 2: break
                
                # Context Checks
                if "Egg" in side['name'] and pref == "veg": continue
                if "soup" in food_name and ("curd" in side['name'].lower() or "buttermilk" in side['name'].lower()): continue

                item['food'] += side['name']
                final_cal += side['cal']
                final_prot += side['p']
                final_carb += side['c']
                final_fat += side['f']
                
                calorie_gap -= side['cal']
                sides_added += 1

        # 7. Final Save
        item['calories'] = int(final_cal)
        item['protein'] = round(final_prot, 1)
        item['carbs'] = round(final_carb, 1)
        item['fat'] = round(final_fat, 1)
        return item
    # --- END OF MEAL GENERATOR ---

    breakfast = get_meal("Breakfast")
    lunch = get_meal("Lunch")
    dinner = get_meal("Dinner")
    
    # Calculate totals
    b_cal = breakfast['calories'] if breakfast else 0
    l_cal = lunch['calories'] if lunch else 0
    d_cal = dinner['calories'] if dinner else 0
    current_total = b_cal + l_cal + d_cal
    
    snack = None
    if disease and disease.lower() != "obesity":
        if current_total < (target_cal - 250):
            snack = get_meal("Snack", scale_cap=1.5)
            
    return {"breakfast": breakfast, "lunch": lunch, "dinner": dinner, "snack": snack}

### new genrate dialy function
def generate_smart_daily_plan(disease, age, pref, target_cal):
    safe_foods = foods.copy()
    
    # Filter by Disease
    if disease:
        col_name = f"{disease.lower()}_label"
        if col_name in safe_foods.columns:
            safe_foods = safe_foods[safe_foods[col_name] == 'Recommended']
    
    # Filter by Age
    if age < 12: target = ["Kids", "All"]
    elif age > 60: target = ["Seniors", "All"]
    else: target = ["Adults", "All"]
    safe_foods = safe_foods[safe_foods["target_audience"].isin(target)]
    
    # Filter by Preference
    if pref == 'veg': safe_foods = safe_foods[safe_foods['food_type'] == 'Veg']

    def get_meal(m_type, scale_cap=2.0):
        # 1. Select Food
        options = safe_foods[safe_foods['meal_type'] == m_type]
        if options.empty: return None
        item = options.sample(1).iloc[0].to_dict()
        
        # 2. Calculate Scale
        base_cal = item['calories']
        required = target_cal / 3
        raw_scale = required / base_cal
        
        # 3. Safety Logic (UPDATED)
        is_diabetic = disease and disease.lower() == "diabetes"
        is_obese = disease and disease.lower() == "obesity"

        if is_diabetic:
            # Diabetes: Strict Cap (0.8 to 1.2)
            scale = 1.2 if raw_scale > 1.2 else (0.8 if raw_scale < 0.8 else raw_scale)

        elif is_obese:
            # 🟢 FIX 2: OBESITY LOGIC
            # Allow scaling DOWN to 0.7x (Small Portion) to hit the deficit.
            # STRICT CAP UP: Never go beyond 1.1x (No large portions).
            scale = min(raw_scale, 1.1) 
            if scale < 0.7: scale = 0.7 # Minimum limit to prevent starvation

        else:
            # Normal Logic (Hypertension, CVD, etc.)
            scale = min(raw_scale, 1.5)
            if scale < 1.0: scale = 1.0 # Standard users shouldn't eat tiny portions

        scale = round(scale * 2) / 2
        
        # 4. Rename Logic
        if scale >= 1.4: item['food'] += " (Large Portion)"
        elif scale <= 0.8: item['food'] += " (Small Portion)" 
            
        # 5. Apply Nutrients
        item['calories'] = int(item['calories'] * scale)
        item['protein'] = round(item['protein'] * scale, 1)
        item['carbs'] = round(item['carbs'] * scale, 1)
        item['fat'] = round(item['fat'] * scale, 1)
        
        return item

    breakfast = get_meal("Breakfast")
    lunch = get_meal("Lunch")
    dinner = get_meal("Dinner")
    
    # Calculate totals
    b_cal = breakfast['calories'] if breakfast else 0
    l_cal = lunch['calories'] if lunch else 0
    d_cal = dinner['calories'] if dinner else 0
    current_total = b_cal + l_cal + d_cal
    
    snack = None
    # Add snack if calories are low (except for Obesity)
    if disease and disease.lower() != "obesity":
        if current_total < (target_cal - 250):
            snack = get_meal("Snack", scale_cap=1.5)
            
    return {"breakfast": breakfast, "lunch": lunch, "dinner": dinner, "snack": snack}