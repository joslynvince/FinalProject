import sqlite3
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(dir_path, "recipes.db")

def get_average_recipe_price(cur, file):
    cur.execute("SELECT AVG(total_price) FROM FullRecipeInfo")
    avg = cur.fetchone()[0]
    if avg is not None:
        final_string = "Avergage price of recipes in database: " + "$" + str(avg)
        file.write(final_string + "\n")

def get_min_price(cur, file):
    cur.execute('''
        SELECT title, total_price 
        FROM FullRecipeInfo 
        ORDER BY total_price ASC 
        LIMIT 1
    ''')
    result = cur.fetchone()
    if result:
        title, price = result
        final_string = title + ", \n         with a price of: " + "$" + str(price) + "\n"
        file.write("The name of the recipe with the **lowest cost** is  - " +
                    final_string + "\n")

def get_max_price(cur, file):
    cur.execute('''
        SELECT title, total_price 
        FROM FullRecipeInfo 
        ORDER BY total_price DESC 
        LIMIT 1
    ''')
    result = cur.fetchone()
    if result:
        title, price = result
        final_string = title + ", \n         with a price of: " + "$" + str(price) + "\n"
        file.write("The name of the recipe with the **highest cost** is  - " +
                    final_string)

def get_average_serving_price(cur, file):
    cur.execute("SELECT AVG(price_per_serving) FROM FullRecipeInfo")
    avg = cur.fetchone()[0]
    if avg is not None:
        final_string = "Avergage price per servings of recipes in database: " + "$" + str(avg)
        file.write(final_string + "\n")

def get_min_price_per_serving(cur, file):
    cur.execute('''
        SELECT title, price_per_serving
        FROM FullRecipeInfo
        ORDER BY price_per_serving ASC
        LIMIT 1
    ''')
    row = cur.fetchone()
    if row:
        title, price = row
        final_string = title + ", \n         with a price per serving cost of: " + "$" + str(price) + "\n"
        file.write("The name of the recipe with the **lowest cost** is  - " +
                    final_string + "\n")

def get_max_price_per_serving(cur, file):
    cur.execute('''
        SELECT title, price_per_serving
        FROM FullRecipeInfo
        ORDER BY price_per_serving DESC
        LIMIT 1
    ''')
    row = cur.fetchone()
    if row:
        title, price = row
        final_string = title + ", \n        with a price per serving cost of: " +  "$" + str(price)
        file.write("The name of the recipe with the **highest cost** is  - " +
                    final_string + "\n")

def main():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    output_path = os.path.join(dir_path, "final_calculations.txt")
    with open(output_path, "w") as f:
        f.write("Getting Information about Recipe Average, Max Price, and Min Price" + "\n")
        f.write("-------------------------------------------------------------------" + "\n"
)
        get_average_recipe_price(cur, f)
        get_max_price(cur, f)
        get_min_price(cur, f)

        f.write("Getting Information about Price Per Serving Average, Max Price, and Min Price" + "\n")
        f.write("--------------------------------------------------------------------------------" + "\n")
                
        get_average_serving_price(cur, f)
        get_max_price_per_serving(cur, f)
        get_min_price_per_serving(cur, f)

    conn.close()

main()