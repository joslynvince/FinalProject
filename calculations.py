import sqlite3
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(dir_path, "recipes.db")

def get_average_recipe_price(cur):
    cur.execute("SELECT AVG(total_price) FROM FullRecipeInfo")
    avg = cur.fetchone()[0]
    if avg is not None:
        final_string = "Avergage price: " + str(avg)
        print(final_string)

def get_min_price(cur):
    cur.execute('''
        SELECT title, total_price 
        FROM FullRecipeInfo 
        ORDER BY total_price ASC 
        LIMIT 1
    ''')
    result = cur.fetchone()
    if result:
        title, price = result
        final_string = title + ": " + str(price)
        print(final_string)

def get_max_price(cur):
    cur.execute('''
        SELECT title, total_price 
        FROM FullRecipeInfo 
        ORDER BY total_price DESC 
        LIMIT 1
    ''')
    result = cur.fetchone()
    if result:
        title, price = result
        final_string = title + ": " + str(price)
        print(final_string)

def get_average_serving_price(cur):
    cur.execute("SELECT AVG(price_per_serving) FROM FullRecipeInfo")
    avg = cur.fetchone()[0]
    if avg is not None:
        final_string = "Avergage price: " + str(avg)
        print(final_string)

def get_min_price_per_serving(cur):
    cur.execute('''
        SELECT title, price_per_serving
        FROM FullRecipeInfo
        ORDER BY price_per_serving ASC
        LIMIT 1
    ''')
    row = cur.fetchone()
    if row:
        title, price = row
        final_string = title + ": " + str(price)
        print(final_string)

def get_max_price_per_serving(cur):
    cur.execute('''
        SELECT title, price_per_serving
        FROM FullRecipeInfo
        ORDER BY price_per_serving DESC
        LIMIT 1
    ''')
    row = cur.fetchone()
    if row:
        title, price = row
        final_string = title + ": " + str(price)
        print(final_string)

def main():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    get_average_recipe_price(cur)
    get_max_price(cur)
    get_min_price(cur)
    get_average_serving_price(cur)
    get_min_price_per_serving(cur)
    get_max_price_per_serving(cur)

    conn.close()

main()