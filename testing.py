import requests
import sqlite3
import os

# Set up paths
dir_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(dir_path, 'recipes.db')

# Spoonacular settings
base_url = 'https://api.spoonacular.com/recipes'
API_KEY = 'd64af55f4de54f218e403c7b1b41f7cb'

def get_cookie_recipes(number, offset=0):
    url = f"{base_url}/complexSearch?query=cookie&number={number}&offset={offset}&apiKey={API_KEY}"
    response = requests.get(url)
    print(f"Fetching offset {offset}:", response)
    
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return []

# Connect to the database
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Recreate the table (drop old one if it exists)
cur.execute('DROP TABLE IF EXISTS Recipes')
cur.execute('''
    CREATE TABLE Recipes (
        id INTEGER PRIMARY KEY,
        title TEXT,
        image TEXT)
''')

# Fetch and insert recipes in batches
for offset in range(0, 500, 100):  # Change 500 to a higher number if needed
    recipes = get_cookie_recipes(100, offset=offset)
    
    for item in recipes:
        cur.execute('''
            INSERT OR REPLACE INTO Recipes (id, title, image)
            VALUES (?, ?, ?)
        ''', (item.get('id'), item.get('title'), item.get('image')))

    conn.commit()

# Close the connection
conn.close()
print("Done! Recipes inserted into the database.")
