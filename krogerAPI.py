import requests
import sqlite3
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(dir_path, 'recipes.db')

def create_price_table(cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS IngredientPrices (
            name TEXT PRIMARY KEY,
            price REAL
        )
    ''')

client_id = "joslynvince-24326124303424765878784d364161685961794144666e646839577a654f626d6c793749664c7352424d7068336a774f534c43346d45594b643648471477074199703906271"
client_secret = "IOovHChygNiZ_SS2GTizZPuklyY6DXUBm7ixfBU8"
LOCATION_ID = "01400439"


def get_token(client_id, client_secret):
    url = "https://api.kroger.com/v1/connect/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "product.compact"
    }

    response = requests.post(url, headers=headers, data=data, auth=(client_id, client_secret))
    response.raise_for_status()
    return response.json()["access_token"]

def get_price_for_ingredient(token, name):
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    params = {
        "filter.term": name,
        "filter.locationId": LOCATION_ID,
        "limit": 1
    }

    print(f"Calling Kroger API for: {name}")

    response = requests.get(
        "https://api.kroger.com/v1/products",
        headers=headers,
        params=params,
        timeout=10 
    )

    data = response.json()
    try:
        return float(data["data"][0]["items"][0]["price"]["regular"])
    except (KeyError, IndexError, TypeError):
        return None

def store_all_prices(cur, conn, token):
    cur.execute("SELECT id, name FROM IngredientNames")
    ingredients = cur.fetchall()
    ingredient_names = [i[1] for i in ingredients]

    for name in ingredient_names:
        # Check if price already exists
        cur.execute("SELECT price FROM IngredientPrices WHERE name = ?", (name,))
        if cur.fetchone():
            print(f"✔️ Skipping {name} (already priced)")
            continue

        print(f"💰 Fetching price for: {name}")

        try:
            price = get_price_for_ingredient(token, name)
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed for {name}: {e}")
            price = None

        if price is not None:
            cur.execute('''
                INSERT OR REPLACE INTO IngredientPrices (name, price)
                VALUES (?, ?)
            ''', (name, price))
            conn.commit()


#FOR TESTING

def main():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    create_price_table(cur)
    token = get_token(client_id, client_secret)
    store_all_prices(cur, conn, token)

    conn.close()

if __name__ == "__main__":
    main()
