import requests
import sqlite3
import os

#Paths and URLS
dir_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(dir_path, 'recipes.db')
base_url = 'https://api.spoonacular.com/recipes'
API_KEY = 'e002c80b532244538a3ce9405e6db808'


def get_cookie_recipes(number, offset=0):
    url = f"{base_url}/complexSearch?query=cookie&number={number}&offset={offset}&apiKey={API_KEY}"
    response = requests.get(url)
    print(f"Fetching offset {offset}:", response)
    
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return []

def connecting_with_recipes_database(cur, conn, target):
    cur.execute("SELECT COUNT(*) FROM Recipes")
    result = cur.fetchone()[0]

    if result >= target:
        return
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Recipes (
        id INTEGER PRIMARY KEY,
        title TEXT,
        image TEXT)
    ''')

    # Fetch and insert recipes in batches
    for offset in range(0, 700, 100):
        recipes = get_cookie_recipes(100, offset=offset)
    
        for item in recipes:
            cur.execute('''
                INSERT OR REPLACE INTO Recipes (id, title, image)
                VALUES (?, ?, ?)
            ''', (item.get('id'), item.get('title'), item.get('image')))

        conn.commit()

    #SQL COMMANDS NEEDED
    cur.execute("DELETE FROM Recipes WHERE title NOT LIKE ?", ('%cookie%',))
    conn.commit()

    print("Done! Recipes inserted into the database.")

def connecting_with_ingreidents_table(cur, conn):
    recipe_keys = []
    cur.execute("SELECT id FROM Recipes")
    all_keys = cur.fetchall()

    for key in all_keys:
        recipe_key = key[0]
        print(recipe_key)
        recipe_keys.append(recipe_key)

    print(recipe_keys)

    for index in recipe_keys:
        cur.execute("SELECT id FROM Recipes WHERE id = ?", (index))
        exists = cur.fetchone()[0]
        if exists:
            continue
        url = f"{base_url}/{index}/information?includeNutrition=false&apiKey={API_KEY}"
        response = requests.get(url)

        if response.status_code == 200:
            result = response.json()
            print("Working")
        else:
            break

        recipe_id = result.get("id")
        servings = result.get("servings")
        ready_in = result.get("readyInMinutes")

        ingredient_names = []
        for item in result.get("extendedIngredients", []):
            name = item.get("name")
            ingredient_names.append(name)

        ingredients_str = ", ".join(ingredient_names)

        cur.execute('''
        CREATE TABLE IF NOT EXISTS Ingredients (
            id INTEGER PRIMARY KEY,
            servings INTEGER,
            readyInMinutes INTEGER,
            ingredients TEXT)
            ''')
        
        cur.execute('''
        INSERT OR REPLACE INTO Ingredients (
            id, servings, readyInMinutes, ingredients)
            VALUES (?, ?, ?, ?) ''',
            (recipe_id, servings, ready_in, ingredients_str))
        
    
    conn.commit()


def main():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    connecting_with_recipes_database(cur, conn, 166)
    connecting_with_ingreidents_table(cur, conn)

    conn.commit()
    conn.close()

main()