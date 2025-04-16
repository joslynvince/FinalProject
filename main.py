import sqlite3
import os

from recipes import (
    connecting_with_recipes_database,
    connecting_with_ingredients_table,
    connecting_with_integer_key_table,
    ingredients_table_with_integers
)

# Set up the path to your SQLite database
dir_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(dir_path, 'recipes.db')

def main():
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Run each Spoonacular-related step
    connecting_with_recipes_database(cur, conn, 166)
    connecting_with_ingredients_table(cur, conn)
    connecting_with_integer_key_table(cur, conn)
    ingredients_table_with_integers(cur, conn)

    # Save changes and close connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
