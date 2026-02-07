import google.generativeai as genai

# PASTE YOUR KEY HERE
genai.configure(api_key="AIzaSyCtqchXbO9VXQ4QZfJhSoNxrD8zAFpY8-o")

print("------------------------------------------------")
print("SEARCHING FOR AVAILABLE MODELS...")
print("------------------------------------------------")

try:
    for m in genai.list_models():
        # We only want models that can generate text (generateContent)
        if 'generateContent' in m.supported_generation_methods:
            print(f"FOUND: {m.name}")
except Exception as e:
    print("Error connecting:", e)

print("------------------------------------------------")