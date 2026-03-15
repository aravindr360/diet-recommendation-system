import google.generativeai as genai

# 1. Setup your key
genai.configure(api_key="AIzaSyBvblC5SRlzLvQhlABfyYJVZtI6gyhap-o")

print("Checking available models...")

try:
    # 2. Ask Google what models are available for this key
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ FOUND MODEL: {m.name}")

    # 3. Try a simple test
    print("\nAttempting to chat with 'models/gemini-1.5-flash'...")
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    response = model.generate_content("Hello")
    print(f"🎉 SUCCESS! Reply: {response.text}")

except Exception as e:
    print(f"\n❌ ERROR DETAILS: {e}")