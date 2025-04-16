import sqlite3
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(dir_path, "recipes.db")

def create_recipe_prices_table(cur, conn):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS RecipePrices (
            recipe_id INTEGER PRIMARY KEY,
            total_price REAL
        )
    ''')

    cur.execute("SELECT id, ingredient_ids FROM IngredientsWithIDs")
    recipes = cur.fetchall()

    for recipe_id, ingredient_str in recipes:
        ingredient_ids = []
        for x in ingredient_str.split(","):
            x = x.strip()
            if x.isdigit():
                ingredient_ids.append(int(x))

        total_price = 0.0

        for id in ingredient_ids:
            cur.execute("SELECT price FROM KrogerPrices WHERE ingredient_id = ?", (id,))
            result = cur.fetchone()
            if result and result[0] is not None:
                total_price += result[0]

        cur.execute('''
            INSERT OR REPLACE INTO RecipePrices (recipe_id, total_price)
            VALUES (?, ?)
        ''', (recipe_id, round(total_price, 2)))

    conn.commit()

def create_price_per_serving_table(cur, conn):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS PricePerServing (
            recipe_id INTEGER PRIMARY KEY,
            price_per_serving REAL
        )
    ''')

    cur.execute('''
        INSERT OR REPLACE INTO PricePerServing (recipe_id, price_per_serving)
        SELECT Ingredients.id, ROUND(RecipePrices.total_price * 1.0 / Ingredients.servings, 2)
        FROM Ingredients
        JOIN RecipePrices ON Ingredients.id = RecipePrices.recipe_id
        WHERE Ingredients.servings > 0
    ''')

    conn.commit()

def all_recipe_info(cur, conn):

    cur.execute('''
        CREATE TABLE IF NOT EXISTS FullRecipeInfo (
            recipe_id INTEGER PRIMARY KEY,
            title TEXT,
            servings INTEGER,
            readyInMinutes INTEGER,
            total_price REAL,
            price_per_serving REAL
        )
    ''')

    cur.execute('''
        INSERT OR REPLACE INTO FullRecipeInfo (
            recipe_id, title, servings, readyInMinutes, total_price, price_per_serving
        )
        SELECT
            Recipes.id,
            Recipes.title,
            Ingredients.servings,
            Ingredients.readyInMinutes,
            RecipePrices.total_price,
            ROUND(RecipePrices.total_price * 1.0 / Ingredients.servings, 2)
        FROM Recipes
        JOIN Ingredients ON Recipes.id = Ingredients.id
        JOIN RecipePrices ON Recipes.id = RecipePrices.recipe_id
        WHERE Ingredients.servings > 0
    ''')

    conn.commit()

def main():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    create_recipe_prices_table(cur, conn)
    create_price_per_serving_table(cur, conn)
    all_recipe_info(cur, conn)

    conn.close()

main()
