import requests
import base64
import sqlite3
import os
import time

dir_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(dir_path, "recipes.db")

client_id = "joslynvince-24326124303424765878784d364161685961794144666e646839577a654f626d6c793749664c7352424d7068336a774f534c43346d45594b643648471477074199703906271"
client_secret = "IOovHChygNiZ_SS2GTizZPuklyY6DXUBm7ixfBU8"
LOCATION_ID = "01400439"

def get_kroger_access_token():
    auth = f"{client_id}:{client_secret}"
    b64_auth = base64.b64encode(auth.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "product.compact"
    }
    response = requests.post("https://api.kroger.com/v1/connect/oauth2/token", headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def get_price_for_ingredient(token, query):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    params = {
        "filter.term": query,
        "filter.locationId": LOCATION_ID,
        "filter.limit": 1
    }
    response = requests.get("https://api.kroger.com/v1/products", headers=headers, params=params)
    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            price = data[0].get("items", [{}])[0].get("price", {}).get("regular")
            return price
    return None

def store_all_prices(cur, conn, token):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS KrogerPrices (
            ingredient_id INTEGER PRIMARY KEY,
            price REAL
        )
    ''')

    cur.execute("SELECT id, name FROM IngredientNames")
    ingredients = cur.fetchall()

    for ingredient_id, name in ingredients:
        price = get_price_for_ingredient(token, name)
        if price is not None:
            cur.execute('''
                INSERT OR REPLACE INTO KrogerPrices (ingredient_id, price)
                VALUES (?, ?)
            ''', (ingredient_id, price))
            conn.commit()
        time.sleep(0.5)

def fill_missing_kroger_prices(cur, conn):

    cur.execute("SELECT AVG(price) FROM KrogerPrices")
    avg_price = cur.fetchone()[0]

    cur.execute('''
        SELECT id FROM IngredientNames
        WHERE id NOT IN (SELECT ingredient_id FROM KrogerPrices)
    ''')
    missing_ids = cur.fetchall()

    for (ingredient_id,) in missing_ids:
        cur.execute('''
            INSERT INTO KrogerPrices (ingredient_id, price)
            VALUES (?, ?)
        ''', (ingredient_id, avg_price))

    conn.commit()

def round_all_prices(cur,conn):
    cur.execute('''
        UPDATE KrogerPrices
        SET price = ROUND(price, 2)
    ''')
    conn.commit()

def main():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    token = get_kroger_access_token()
    if token:
        store_all_prices(cur, conn, token)
    fill_missing_kroger_prices(cur, conn)
    round_all_prices(cur, conn)
    
    conn.close()

main()
