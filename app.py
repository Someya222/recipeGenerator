import streamlit as st
import pandas as pd
import os
from PIL import Image
from best_first_search import BestFirstSearchRecipeFinder

# --- Load dataset ---
@st.cache_data
def load_data():
    df = pd.read_csv("recipes3k_cleaned.csv")  # use the CSV you created
    df = df.dropna(subset=["ingredients"])
    return df

df = load_data()
search_engine = BestFirstSearchRecipeFinder(df)

st.title("🍳 Recipe Generator using Best First Search (AI Tools Project)")
st.markdown("**Enter ingredients and see how the AI algorithm finds the best recipes!**")

user_input = st.text_input("Enter ingredients (comma or space separated):", "tomato onion garlic")

if st.button("🔍 Find Recipes"):
    if user_input.strip():
        top_recipes, visited = search_engine.search(user_input, top_k=5)

        # --- Visualization of Best First Search exploration ---
        st.subheader("🔍 Top 4 Most Relevant Recipes:")
        seen = set()
        visited_data = []
        
        for idx, score in visited:
            if len(seen) >= 4:  # Show exactly 4 unique recipes
                break
            recipe_name = df.iloc[int(idx)]['name']
            if recipe_name not in seen:
                seen.add(recipe_name)
                st.write(f"• {recipe_name} (Similarity: {score:.3f}")
                visited_data.append({"Recipe": recipe_name, "Heuristic": score})
        
        # Save visited nodes data for the exploration page
        if visited_data:
            pd.DataFrame(visited_data).to_csv("visited_nodes.csv", index=False)

        st.divider()
        st.subheader("🍽️ Top Matching Recipes:")
        for _, row in top_recipes.iterrows():
            st.markdown(f"### {row['name']}")

            # 🖼️ Try to show image (now from URL)
            if pd.notna(row.get("image")) and str(row["image"]).startswith("http"):
                st.image(row["image"], width=300)
            else:
                st.info("🖼️ Image not available")

            st.write("**Ingredients:**", ", ".join(eval(row["ingredients"])) if isinstance(row["ingredients"], str) and row["ingredients"].startswith("[") else row["ingredients"])
            st.write("**Instructions:**", row.get("steps", "No instructions available"))
            st.divider()

        # --- Save exploration data for next page ---
        visited_df = pd.DataFrame(
            [(df.iloc[idx]['name'], score) for idx, score in visited],
            columns=["Recipe", "Heuristic"]
        )
        visited_df.to_csv("visited_nodes.csv", index=False)
    else:
        st.warning("Please enter at least one ingredient.")

# --- Navigation link to exploration page ---
st.markdown("---")
if st.button("📊 View Full Best First Search Exploration"):
    st.switch_page("pages/1_🧠_Exploration.py")

