import sqlite3

# Connect to the database file
try:
    conn = sqlite3.connect('diet_system.db')
    cursor = conn.cursor()

    print("\n--- 👤 USERS TABLE (Login Credentials) ---")
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    if not users:
        print("❌ Table is empty! (Did you run app.py?)")
    else:
        print(f"{'USERNAME':<15} | {'PASSWORD':<10} | {'ROLE':<10}")
        print("-" * 40)
        for u in users:
            print(f"{u[0]:<15} | {u[1]:<10} | {u[2]:<10}")

    print("\n--- 🥗 DIET SUBMISSIONS ---")
    cursor.execute("SELECT id, username, status FROM diets")
    diets = cursor.fetchall()
    if not diets:
        print("ℹ️  No diets submitted yet.")
    else:
        for d in diets:
            print(f"ID: {d[0]} | User: {d[1]} | Status: {d[2]}")

    conn.close()

except Exception as e:
    print("❌ Error reading database. Make sure 'diet_system.db' exists.")
    print(f"Error details: {e}")