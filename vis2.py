import sqlite3
import pandas as pd
import altair as alt
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(dir_path, "recipes.db")

def load_ready_times():
    conn = sqlite3.connect(db_path)
    query = "SELECT readyInMinutes FROM FullRecipeInfo"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def plot_ready_minutes(df):
    count_df = df['readyInMinutes'].value_counts().reset_index()
    count_df.columns = ['readyInMinutes', 'count']
    count_df = count_df.sort_values('readyInMinutes')

    chart = alt.Chart(count_df).mark_bar(color='green').encode(
        x=alt.X('readyInMinutes:O', title='Ready In Minutes'),
        y=alt.Y('count:Q', title='Number of Recipes'),
        tooltip=['readyInMinutes', 'count']
    ).properties(
        title='Number of Recipes by Prep Time',
        width=600,
        height=400
    )

    output_path = os.path.join(dir_path, "ready_minutes_bar.html")
    chart.save(output_path)

def main():
    df = load_ready_times()
    plot_ready_minutes(df)


main()