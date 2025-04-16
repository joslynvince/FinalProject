import requests
import sqlite3
import os

#Paths and URLS
dir_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(dir_path, 'recipes.db')
base_url = 'https://api.spoonacular.com/recipes'
API_KEY = 'd879a1ceee77438aa8edbd985cfc0aea'


def get_cookie_recipes(number, offset=0):
    url = f"{base_url}/complexSearch?query=cookie&number={number}&offset={offset}&apiKey={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        return []

def connecting_with_recipes_database(cur, conn, target):
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Recipes (
        id INTEGER PRIMARY KEY,
        title TEXT,
        image TEXT)
    ''')
     
    cur.execute("SELECT COUNT(*) FROM Recipes")
    result = cur.fetchone()[0]

    if result >= target:
        return
    
    for offset in range(0, 700, 100):
        recipes = get_cookie_recipes(25, offset=offset)
    
        for item in recipes:
            cur.execute('''
                INSERT OR REPLACE INTO Recipes (id, title, image)
                VALUES (?, ?, ?)
            ''', (item.get('id'), item.get('title'), item.get('image')))

        conn.commit()

    cur.execute("DELETE FROM Recipes WHERE title NOT LIKE ?", ('%cookie%',))
    conn.commit()

def connecting_with_ingreidents_table(cur, conn):
    recipe_keys = []
    cur.execute("SELECT id FROM Recipes")
    all_keys = cur.fetchall()
    for key in all_keys:
        recipe_keys.append(key[0])

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Ingredients (
            id INTEGER PRIMARY KEY,
            servings INTEGER,
            readyInMinutes INTEGER,
            ingredients TEXT
        )
    ''')

    for index in recipe_keys:
        cur.execute("SELECT id FROM Ingredients WHERE id = ?", (index,))
        if cur.fetchone():
            continue

        url = f"{base_url}/{index}/information?includeNutrition=false&apiKey={API_KEY}"
        response = requests.get(url)

        if response.status_code != 200:
            continue

        result = response.json()

        recipe_id = result.get("id")
        servings = result.get("servings")
        ready_in = result.get("readyInMinutes")

        ingredient_names = []
        for item in result.get("extendedIngredients", []):
            name = item.get("name")
            ingredient_names.append(name)

        ingredients_str = ", ".join(ingredient_names)

        cur.execute('''
            INSERT OR REPLACE INTO Ingredients (
                id, servings, readyInMinutes, ingredients
            )
            VALUES (?, ?, ?, ?)
        ''', (recipe_id, servings, ready_in, ingredients_str))

    conn.commit()

def connecting_with_integer_key_table(cur, conn):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS IngredientNames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE)
        ''')

    cur.execute("SELECT id, ingredients FROM Ingredients")
    rows = cur.fetchall()

    for recipe_id, ingredients_str in rows:
        ingredients = [i.strip() for i in ingredients_str.split(",")]
        for ing in ingredients:
            cur.execute('''
                INSERT OR IGNORE INTO IngredientNames (name) VALUES (?)
                ''', (ing,))

    conn.commit()

def ingredients_table_with_integers(cur, conn):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS IngredientsWithIDs (
            id INTEGER PRIMARY KEY,
            servings INTEGER,
            readyInMinutes INTEGER,
            ingredient_ids TEXT
        )
    ''')

    cur.execute("SELECT id, servings, readyInMinutes, ingredients FROM Ingredients")
    all_data = cur.fetchall()

    for recipe_id, servings, readyInMinutes, ingredient_str in all_data:
        ingredient_names = []
        for i in ingredient_str.split(","):
            cleaned_string = i.strip()
            ingredient_names.append(cleaned_string)

        ingredient_ids = []
        for name in ingredient_names:
            cur.execute(
                "SELECT id FROM IngredientNames WHERE name = ?",
                (name,)
            )
            result = cur.fetchone()
            if result:
                ingredient_ids.append(str(result[0]))

        ingredient_ids_str = ", ".join(ingredient_ids)

        cur.execute('''
            INSERT OR REPLACE INTO IngredientsWithIDs (
                id, servings, readyInMinutes, ingredient_ids
            ) VALUES (?, ?, ?, ?)
        ''', (recipe_id, servings, readyInMinutes, ingredient_ids_str))

    conn.commit()

def main():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    connecting_with_recipes_database(cur, conn, 166)
    connecting_with_ingreidents_table(cur, conn)
    connecting_with_integer_key_table(cur, conn)
    ingredients_table_with_integers(cur,conn)
    ingredients_table_with_integers(cur, conn)

    conn.commit()
    conn.close()

main()