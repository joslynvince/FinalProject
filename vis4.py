import sqlite3
import os
import pandas as pd
import altair as alt

dir_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(dir_path, "recipes.db")

def fetch_price_per_serving():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT price_per_serving FROM FullRecipeInfo")
    prices = [row[0] for row in cur.fetchall()]
    conn.close()
    return prices

def bucket_price_per_serving(prices):
    bins = [0, 5, 10, 15, 20, 25, 30]
    labels = ['0-5', '5-10', '10-15', '15-20', '20-25', '25-30']
    df = pd.DataFrame({'price_per_serving': prices})
    df['range'] = pd.cut(df['price_per_serving'], bins=bins, labels=labels, right=False)
    return df.groupby('range').size().reset_index(name='count')

def plot_price_per_serving_pie(df):
    chart = alt.Chart(df).mark_arc().encode(
        theta='count:Q',
        color=alt.Color('range:N', title='Price per Serving Range'),
        tooltip=['range:N', 'count:Q']
    ).properties(
        title='Recipe Count by Price per Serving Range'
    )

    output_path = os.path.join(dir_path, "vis4.html")
    chart.save(output_path)

def main():
    prices = fetch_price_per_serving()
    df = bucket_price_per_serving(prices)
    plot_price_per_serving_pie(df)

if __name__ == "__main__":
    main()
