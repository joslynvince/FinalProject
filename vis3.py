import sqlite3
import os
import pandas as pd
import altair as alt

dir_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(dir_path, "recipes.db")

def fetch_servings():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT servings FROM FullRecipeInfo")
    servings = [row[0] for row in cur.fetchall()]
    conn.close()
    return servings

def bucket_servings(servings):
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, float('inf')]
    labels = ['0-10', '10-20', '20-30', '30-40', '40-50',
              '50-60', '60-70', '70-80', '80-90', '90-100', '100+']
    
    df = pd.DataFrame({'servings': servings})
    df['range'] = pd.cut(df['servings'], bins=bins, labels=labels, right=False)
    return df.groupby('range').size().reset_index(name='count')

def plot_histogram(df):
    chart = alt.Chart(df).mark_bar(color="orange").encode(
    x=alt.X('range:N',
            title='Serving Size Range',
            sort=['0-10', '10-20', '20-30', '30-40', '40-50',
                  '50-60', '60-70', '70-80', '80-90', '90-100', '100+']),
    y=alt.Y('count:Q', title='Number of Recipes'),
    tooltip=['range:N', 'count:Q']
).properties(
    title='Recipe Count by Serving Size Range'
)

    output_path = os.path.join(dir_path, "vis3.html")
    chart.save(output_path)

def main():
    servings = fetch_servings()
    df = bucket_servings(servings)
    plot_histogram(df)

if __name__ == "__main__":
    main()