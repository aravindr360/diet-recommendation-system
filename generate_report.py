from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT

def create_project_report():
    doc = SimpleDocTemplate("Project_Report_Smart_Diet.pdf", pagesize=A4,
                            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='CenterTitle', parent=styles['Heading1'], alignment=TA_CENTER, spaceAfter=20))
    styles.add(ParagraphStyle(name='SubTitle', parent=styles['Heading2'], spaceAfter=10, textColor=colors.darkblue))
    styles.add(ParagraphStyle(name='CodeBlock', parent=styles['BodyText'], fontName='Courier', fontSize=9, backColor=colors.whitesmoke, borderPadding=5))

    story = []

    # --- TITLE PAGE ---
    story.append(Paragraph("Smart Diet Planning System", styles['CenterTitle']))
    story.append(Paragraph("Project Documentation & Technical Report", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Submitted by:</b> [Your Names Here]", styles['Normal']))
    story.append(Paragraph("<b>Date:</b> January 2026", styles['Normal']))
    story.append(Spacer(1, 30))

    # --- 1. PROJECT OVERVIEW ---
    story.append(Paragraph("1. Project Overview", styles['SubTitle']))
    text = """
    The Smart Diet Planning System is a web-based application designed to generate personalized nutrition plans using Artificial Intelligence and Machine Learning. 
    Unlike generic diet apps, this system tailors meals based on specific medical conditions (Diabetes, Hypertension, CVD, PCOS, Obesity) while considering user biometrics (Height, Weight, BMI, Age).
    """
    story.append(Paragraph(text, styles['Justify']))
    story.append(Spacer(1, 12))

    # --- 2. TECHNOLOGY STACK ---
    story.append(Paragraph("2. Technology Stack", styles['SubTitle']))
    
    data = [
        ["Component", "Technology Used", "Purpose"],
        ["Language", "Python 3.x", "Core logic and backend processing."],
        ["Backend", "Flask", "Web framework to handle API routes and server logic."],
        ["Frontend", "HTML5, CSS3, JavaScript", "User Interface, Charts, and Dynamic Interactions."],
        ["Database", "SQLite3", "Storing User credentials and Diet History."],
        ["ML Models", "Scikit-Learn (Random Forest)", "Classifying foods as Safe/Unsafe based on nutrients."],
        ["Generative AI", "Google Gemini API", "AI Chatbot for nutritional queries."],
        ["Reporting", "ReportLab", "Generating downloadable PDF diet plans."]
    ]
    
    t = Table(data, colWidths=[80, 150, 290])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # --- 3. ARCHITECTURE & IMPLEMENTATION ---
    story.append(Paragraph("3. Implementation Details", styles['SubTitle']))
    
    story.append(Paragraph("<b>3.1 Backend Logic (app.py)</b>", styles['Heading3']))
    text = """
    The backend is built using Flask. The core logic resides in the <b>generate_smart_daily_plan</b> function.
    Key algorithms implemented:
    """
    story.append(Paragraph(text, styles['Normal']))
    
    list_items = [
        ListItem(Paragraph("<b>Disease Filtering:</b> Uses ML models to filter the dataset. If a user has Diabetes, the system checks the 'diabetes_label' column predicted by our Random Forest model.", styles['Normal'])),
        ListItem(Paragraph("<b>Obesity Logic:</b> If 'Obesity' is selected, the system automatically subtracts 500 calories from the TDEE (Total Daily Energy Expenditure) to create a caloric deficit, capped at a minimum of 1200 kcal for safety.", styles['Normal'])),
        ListItem(Paragraph("<b>Dynamic Portion Scaling:</b> The system calculates a scaling factor based on the target calories. For Diabetics, portions are strictly capped (0.8x - 1.2x) to prevent blood sugar spikes. For Obesity, portions are reduced (down to 0.7x).", styles['Normal'])),
        ListItem(Paragraph("<b>Database Management:</b> SQLite is used to store 'Users' (Authentication) and 'Diets' (History). The system saves Height, Weight, and BMI along with the generated JSON plan.", styles['Normal']))
    ]
    story.append(ListFlowable(list_items, bulletType='bullet', start='square'))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>3.2 Machine Learning (train_models.py)</b>", styles['Heading3']))
    text = """
    We trained 5 separate Random Forest Classifiers for each disease.
    <br/><b>Features Used:</b> Calories, Protein, Carbs, Fat, Sugar, Sodium, GI.
    <br/><b>Target:</b> Labeled data (Recommended / Not Recommended).
    <br/><b>Performance:</b> The models achieve high accuracy in filtering unsafe foods.
    """
    story.append(Paragraph(text, styles['Normal']))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>3.3 Frontend Logic (index.html)</b>", styles['Heading3']))
    text = """
    The frontend is a dynamic Single Page Application (SPA) feel.
    <br/><b>Chart.js:</b> Used to visualize the nutrient breakdown (Protein, Carbs, Fat) for every meal card.
    <br/><b>History Mode:</b> Users can view past approved diets. A sophisticated 'Flagging System' was implemented in JS to pause real-time updates while the user is viewing history.
    <br/><b>Doctor Workflow:</b> Users submit plans via API. Doctors view them in a separate panel (Expert Panel) to Approve/Reject.
    """
    story.append(Paragraph(text, styles['Normal']))
    story.append(Spacer(1, 12))

    # --- 4. KEY FEATURES ---
    story.append(Paragraph("4. Key Features & Innovations", styles['SubTitle']))
    list_items = [
        ListItem(Paragraph("<b>BMI Auto-Calculation:</b> Height and weight inputs automatically calculate BMI and Daily Calorie Needs.", styles['Normal'])),
        ListItem(Paragraph("<b>Smart Portion Control:</b> The algorithm renames food items (e.g., 'Large Portion') based on the calculated scale factor.", styles['Normal'])),
        ListItem(Paragraph("<b>PDF Generation:</b> A custom PDF report is generated using the ReportLab library, organizing the weekly plan into a printable format.", styles['Normal'])),
        ListItem(Paragraph("<b>AI Chatbot:</b> Integrated Google Gemini API to answer general nutrition questions.", styles['Normal']))
    ]
    story.append(ListFlowable(list_items, bulletType='bullet', start='square'))
    story.append(Spacer(1, 12))

    # --- 5. CONCLUSION ---
    story.append(Paragraph("5. Conclusion", styles['SubTitle']))
    text = """
    This project successfully integrates medical constraints with nutritional data. By combining Machine Learning for food safety and a rule-based algorithm for meal assembly, it provides a safe, personalized, and scalable solution for diet planning.
    """
    story.append(Paragraph(text, styles['Justify']))

    doc.build(story)
    print("PDF Generated Successfully: Project_Report_Smart_Diet.pdf")

if __name__ == "__main__":
    create_project_report()