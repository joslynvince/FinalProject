import sqlite3
import os
import pandas as pd
import altair as alt

dir_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(dir_path, "recipes.db")

def fetch_prices():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT total_price FROM FullRecipeInfo")
    prices = [row[0] for row in cur.fetchall()]
    conn.close()
    return prices

def bucket_prices(prices):
    bins = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    labels = ['10-20', '20-30', '30-40', '40-50', '50-60',
              '60-70', '70-80', '80-90', '90-100']
    df = pd.DataFrame({'price': prices})
    df['range'] = pd.cut(df['price'], bins=bins, labels=labels, right=False)
    return df.groupby('range').size().reset_index(name='count')

def plot_pie(df):
    chart = alt.Chart(df).mark_arc().encode(
        theta='count:Q',
        color='range:N',
        tooltip=['range:N', 'count:Q']
    ).properties(
        title='Recipe Count by Price Range'
    )

    output_path = os.path.join(dir_path, "vis1.html")
    chart.save(output_path)

def main():
    prices = fetch_prices()
    df = bucket_prices(prices)
    plot_pie(df)

if __name__ == "__main__":
    main()
