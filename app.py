import streamlit as st
import pandas as pd
import os
import time
import random
from PIL import Image
from best_first_search import BestFirstSearchRecipeFinder
from beam_search_recipe_finder import BeamSearchRecipeFinder
import json
from streamlit_lottie import st_lottie
from streamlit_tags import st_tags

# Initialize session state for search results and algorithm
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'search_algorithm' not in st.session_state:
    st.session_state.search_algorithm = "Best-First Search"

# --- Load dataset ---
@st.cache_data
def load_data():
    df = pd.read_csv("recipes3k_cleaned.csv")  # use the CSV you created
    df = df.dropna(subset=["ingredients"])
    return df

# Initialize search engines
def initialize_search_engines():
    if 'search_engines' not in st.session_state:
        # Make sure data is loaded
        df = load_data()
        st.session_state.search_engines = {
            "Best-First Search": BestFirstSearchRecipeFinder(df),
            "Beam Search": BeamSearchRecipeFinder(df, beam_width=3)
        }

# Initialize session state for search results and algorithm
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'search_algorithm' not in st.session_state:
    st.session_state.search_algorithm = "Best-First Search"

# Initialize search engines after all functions are defined
initialize_search_engines()

# Get the selected search engine
search_engine = st.session_state.search_engines[st.session_state.search_algorithm]

# Load Lottie animation
def load_lottie_file(filepath: str):
    with open(filepath, 'r') as f:
        return json.load(f)

# Cooking animation
cooking_anim = load_lottie_file('cooking_animation.json')  # You'll need to add this file

# Sample search suggestions (replace with your actual ingredient list)
INGREDIENT_SUGGESTIONS = [
    'tomato', 'onion', 'garlic', 'chicken', 'beef', 'pasta', 'rice', 
    'cheese', 'mushroom', 'potato', 'carrot', 'broccoli', 'spinach',
    'chocolate', 'flour', 'sugar', 'eggs', 'milk', 'butter', 'olive oil'
]

def get_suggestions(text):
    if not text:
        return []
    text = text.lower()
    return [ing for ing in INGREDIENT_SUGGESTIONS if text in ing.lower()][:5]

# Load the data
df = load_data()

# Custom CSS for better UI
st.markdown("""
<style>
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.recipe-card {
    border-radius: 12px;
    padding: 20px;
    margin: 15px 0;
    background: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeIn 0.6s ease-out forwards;
    opacity: 0;
    border: 1px solid rgba(0,0,0,0.05);
}

.recipe-card:nth-child(1) { animation-delay: 0.1s; }
.recipe-card:nth-child(2) { animation-delay: 0.2s; }
.recipe-card:nth-child(3) { animation-delay: 0.3s; }
.recipe-card:nth-child(4) { animation-delay: 0.4s; }
.recipe-card:nth-child(5) { animation-delay: 0.5s; }

.recipe-card:hover {
    transform: translateY(-5px) scale(1.01);
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}

.ingredient-tag {
    display: inline-block;
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
    padding: 4px 12px;
    border-radius: 15px;
    margin: 3px;
    font-size: 0.8em;
    color: #2d3748;
    border: 1px solid #e2e8f0;
    transition: all 0.2s ease;
}

.ingredient-tag:hover {
    background: linear-gradient(135deg, #e4e8f0 0%, #cbd5e0 100%);
    transform: translateY(-1px);
}

.recipe-title {
    color: #2d3748;
    margin-bottom: 10px;
    font-weight: 700;
    font-size: 1.5rem;
    line-height: 1.3;
}

.recipe-metric {
    font-size: 0.9rem;
    color: #4a5568;
    display: flex;
    align-items: center;
    margin-bottom: 5px;
}

.recipe-metric svg {
    margin-right: 6px;
    color: #4a5568;
}
</style>
""", unsafe_allow_html=True)

# Header with animation
with st.container():
    st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 10px;'> What's in my fridge?</h1>
        <p style='font-size: 1.1rem; color: #4a5568;'>Enter ingredients you have and discover delicious recipes you can make!</p>
    </div>
    """, unsafe_allow_html=True)

# Search algorithm selection
st.markdown("### Choose Search Algorithm")
st.session_state.search_algorithm = st.selectbox(
    "Select search algorithm:",
    ["Best-First Search", "Beam Search"],
    index=["Best-First Search", "Beam Search"].index(st.session_state.get('search_algorithm', 'Best-First Search')),
    help="Best-First Search explores the most promising nodes first. Beam Search is more memory efficient but may not find the optimal path.",
    key='algorithm_selector'
)

# Search with suggestions
st.markdown("### Enter Ingredients")
user_input = st_tags(
    label='',
    text='Add ingredients...',
    value=[],
    suggestions=INGREDIENT_SUGGESTIONS,
    maxtags=10,
    key='ingredient_tags'
)

# Convert list to string for the search
ingredients_str = ' '.join(user_input) if user_input else "tomato onion garlic"

# Get the appropriate search engine based on selection
search_engine = st.session_state.search_engines[st.session_state.search_algorithm]

# Check if we have previous search results to display
if st.session_state.search_results is not None:
    top_recipes, visited, search_query = st.session_state.search_results
    st.success(f"Found {len(top_recipes)} delicious recipe{'s' if len(top_recipes) != 1 else ''} that match your ingredients!")
    st.subheader("Top Matching Recipes")
    
    # Display the search query that was used
    st.caption(f"Showing results for: {search_query}")
    
    # Add a button to clear the results
    if st.button(" Clear Results", type="secondary"):
        st.session_state.search_results = None
        st.rerun()
    
    # Add some space
    st.write("")
else:
    # Only show the search interface if we don't have results to display
    if st.button("Find Recipes", type="primary", use_container_width=True):
        if ingredients_str.strip():
            # Store the search query
            st.session_state.search_query = ingredients_str
            
            # Create a container for the loading animation and messages
            loading_container = st.container()
            with loading_container:
                
                
                # Create two columns: one for animation, one for messages
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Container for the animation
                    anim_placeholder = st.empty()
                    
                with col2:
                    # Container for the loading messages
                    status_text = st.markdown("###  Starting your search...")
                    
                # Add some space
                st.write("")
                st.write("")
                
                # Progress bar for visual feedback
                progress_bar = st.progress(0)
                status_text2 = st.empty()
            
            # Start the search in a separate thread to allow animation to continue
            import threading
            from queue import Queue
            
            result_queue = Queue()
            
            def perform_search():
                try:
                    top_recipes, visited = search_engine.search(ingredients_str, top_k=3)  # Changed from 5 to 3
                    result_queue.put((top_recipes, visited, None))
                except Exception as e:
                    result_queue.put((None, None, str(e)))
            
            # Start the search in a separate thread
            search_thread = threading.Thread(target=perform_search)
            search_thread.start()
            
            # Loading phrases to cycle through
            loading_phrases = [
                "Preheating the oven...",
                "Chopping and dicing ingredients...",
                "Mixing flavors to perfection...",
                "Adding a pinch of magic...",
                "Almost ready... Just a few more seconds!"
            ]
            
            # Keep the animation and messages running until search completes
            search_complete = False
            phrase_index = 0
            start_time = time.time()
            
            while not search_complete and (time.time() - start_time) < 30:  # 30 seconds timeout
                # Update the animation
                with loading_container:
                    with col1:
                        anim_placeholder.empty()
                        st_lottie(cooking_anim, height=200, key=f"cooking_{time.time()}")
                    
                    # Update the loading message
                    current_phrase = loading_phrases[phrase_index % len(loading_phrases)]
                    status_text.markdown(f"### {current_phrase}")
                    
                    # Update progress
                    progress = min(90, int(((time.time() - start_time) / 30) * 90))  # Max 90% until done
                    progress_bar.progress(progress)
                    status_text2.markdown(f"*Searching... {progress}%*")
                    
                    phrase_index += 1
                
                # Check if search is complete
                try:
                    if not result_queue.empty():
                        result = result_queue.get()
                        if result[2]:  # If there's an error
                            st.error(f"Error during search: {result[2]}")
                            loading_container.empty()
                            st.stop()  # Stop execution instead of returning
                        else:
                            top_recipes, visited, _ = result
                            search_complete = True
                            break
                except:
                    pass
                
                # Small delay before next update
                time.sleep(1.5)
            
            # If we timed out, show an error
            if not search_complete:
                st.error("Search is taking too long. Please try again.")
                st.stop()  # Stop execution without using return
                
            # Update progress to 100%
            with loading_container:
                progress_bar.progress(100)
                status_text2.markdown("*Done! Displaying your recipes...*")
                time.sleep(0.5)  # Let the user see 100%
            
            # Store the search results in session state
            st.session_state.search_results = (top_recipes, visited, ingredients_str)
            
            # Clear the loading container and rerun
            loading_container.empty()
            st.rerun()
        else:
            st.warning("Please enter some ingredients to search for recipes.")
    
    # Don't proceed further if we don't have search results
    st.stop()

# Display the recipe results
for idx, (_, row) in enumerate(top_recipes.iterrows(), 1):
    with st.container():
        st.markdown(f"<div class='recipe-card' id='recipe-{idx}'>", unsafe_allow_html=True)
        
        # Recipe header with nutrition and time
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {row['name']}")
        with col2:
            if 'nutrition' in row and pd.notna(row['nutrition']):
                st.metric("Calories", f"{row['nutrition']} kcal" if isinstance(row['nutrition'], (int, float)) else row['nutrition'])
            if 'cook_time' in row and pd.notna(row['cook_time']):
                st.metric("Cook Time", f"{row['cook_time']} min" if isinstance(row['cook_time'], (int, float)) else row['cook_time'])
        
        # Recipe image with better error handling
        if pd.notna(row.get("image")) and isinstance(row["image"], str):
            img_url = row["image"].strip()
            if not img_url.startswith(('http://', 'https://')):
                img_url = f"https:{img_url}" if img_url.startswith('//') else img_url
            
            # Create a container for the image with fixed height
            image_container = st.container()
            with image_container:
                try:
                    # Add a small delay to prevent rate limiting
                    time.sleep(0.1)
                    # Use a column to control the width
                    col_img, _ = st.columns([3, 1])
                    with col_img:
                        st.image(
                            img_url,
                            use_container_width=True,
                            output_format='auto',
                            caption=f"Image for {row['name']}"
                        )
                except Exception as e:
                    # Show a nice error message with the recipe name
                    st.markdown(
                        f"<div style='background-color: #fff5f5; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;'>"
                        f"<p style='color: #e53e3e; margin: 0;'>Couldn't load image for {row['name']}</p>"
                        f"<p style='color: #718096; font-size: 0.8rem; margin: 0.5rem 0 0;'>{str(e)[:100]}...</p>"
                        "</div>",
                        unsafe_allow_html=True
                    )
                    # Show a fallback food emoji based on the recipe name
                    food_emojis = ['🍳', '🍲', '🥘', '🍛', '🍜', '🍝', '🍠', '🥗', '🍕', '🍔']
                    emoji = random.choice(food_emojis)
                    st.markdown(
                        f"<div style='font-size: 4rem; text-align: center; opacity: 0.5;'>{emoji}</div>",
                        unsafe_allow_html=True
                    )
        else:
            # Show a placeholder with a random food emoji
            food_emojis = ['🍳', '🍲', '🥘', '🍛', '🍜', '🍝', '🍠', '🥗', '🍕', '🍔']
            emoji = random.choice(food_emojis)
            st.markdown(
                f"<div style='font-size: 4rem; text-align: center; opacity: 0.3;'>{emoji}</div>",
                unsafe_allow_html=True
            )
                
        # Ingredients as tags
        st.markdown("#### Ingredients")
        ingredients = eval(row["ingredients"]) if isinstance(row["ingredients"], str) and row["ingredients"].startswith("[") else [row["ingredients"]]
        st.markdown(" ".join([f"<span class='ingredient-tag'>{ing}</span>" for ing in ingredients]), unsafe_allow_html=True)
        
        # Instructions with smooth reveal
        with st.expander("View Recipe Instructions"):
            st.write(row.get("steps", "No instructions available"))
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Save visited nodes data for the exploration page
        visited_data = [{"Recipe": df.iloc[int(idx)]['name'], "Heuristic": score} for idx, score in visited]
        if visited_data:
            pd.DataFrame(visited_data).to_csv("visited_nodes.csv", index=False)
            
        # Add smooth scroll to top button
        st.markdown("""
        <style>
        .back-to-top {
            position: fixed;
            bottom: 20px;
            right: 20px;
            font-size: 20px;
            background: #ff4b4b;
            color: white;
            cursor: pointer;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            text-align: center;
            line-height: 40px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            z-index: 999;
        }
        </style>
        <a href='#' class='back-to-top' title='Back to top'>↑</a>
        """, unsafe_allow_html=True)

        # --- Save exploration data for next page ---
        if visited:  # Check if visited is not empty
            visited_df = pd.DataFrame(
                [(df.iloc[int(idx)]['name'], score) for idx, score in visited],
                columns=["Recipe", "Heuristic"]
            )
            visited_df.to_csv("visited_nodes.csv", index=False)
        else:
            st.warning("No recipes found. Please try different ingredients.")
            st.stop()

# --- Navigation link to exploration page ---
st.markdown("---")
if st.button("📊 View Full Best First Search Exploration"):
    st.switch_page("pages/1_🧠_Exploration.py")

