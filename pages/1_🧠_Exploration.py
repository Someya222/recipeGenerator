import streamlit as st
import pandas as pd

st.set_page_config(page_title="Best First Search Exploration", page_icon="🍳")

st.title("🍽️ Best First Search Exploration")
st.write("Recipes explored in order of heuristic similarity:")

try:
    visited_df = pd.read_csv("visited_nodes.csv")
    st.dataframe(visited_df)

    st.bar_chart(
        data=visited_df.set_index("Recipe")["Heuristic"],
        use_container_width=True
    )
except FileNotFoundError:
    st.warning("Run the search first on the home page to generate exploration data!")
