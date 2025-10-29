import streamlit as st
import pandas as pd
import os
from PIL import Image
from best_first_search import BestFirstSearchRecipeFinder

# --- Load dataset ---
@st.cache_data
def load_data():
    df = pd.read_csv("dataset.csv")
    df = df.dropna(subset=["Cleaned_Ingredients"])
    return df

df = load_data()
search_engine = BestFirstSearchRecipeFinder(df)

st.title("🍳 Recipe Generator using Best First Search (AI Tools Project)")
st.markdown("**Enter ingredients and see how the AI algorithm finds the best recipes!**")

user_input = st.text_input("Enter ingredients (comma or space separated):", "tomato onion garlic")

if st.button("🔍 Find Recipes"):
    if user_input.strip():
        top_recipes, visited = search_engine.search(user_input, top_k=5)

        # --- Save visited nodes for exploration page ---
        visited_df = pd.DataFrame([
            {"Recipe": df.iloc[idx]["Title"], "Heuristic": score}
            for idx, score in visited
        ])
        visited_df.to_csv("visited_nodes.csv", index=False)

        # --- Visualization of Best First Search expansion ---
        st.subheader("🧠 Best First Search Exploration:")
        st.write("Recipes explored in order of heuristic similarity:")
        for idx, score in visited[:10]:
            st.write(f"→ {df.iloc[idx]['Title']} (Heuristic: {score:.3f})")


        st.divider()
        st.subheader("🍽️ Top Matching Recipes:")
        for _, row in top_recipes.iterrows():
            st.markdown(f"### {row['Title']}")

            # Try to show image if available
            img_path = None
            if "Image_Name" in df.columns:
                possible_path = os.path.join("images", str(row["Image_Name"]))
                if os.path.exists(possible_path):
                    img_path = possible_path

            if img_path:
                st.image(Image.open(img_path), width=250)
            else:
                st.info("🖼️ Image not found")

            st.write("**Ingredients:**", row["Ingredients"])
            st.write("**Instructions:**", row["Instructions"])
            st.divider()
    else:
        st.warning("Please enter at least one ingredient.")
# --- Navigation link to exploration page ---
st.markdown("---")
if st.button("📊 View Full Best First Search Exploration"):
    st.switch_page("pages/1_🧠_Exploration.py")
