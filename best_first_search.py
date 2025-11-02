from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import heapq
import pandas as pd


class BestFirstSearchRecipeFinder:
    def __init__(self, recipes):
        self.recipes = recipes.copy()  # make a copy to avoid warnings

        # 🧩 Convert ingredients lists into space-separated strings
        self.recipes["ingredients"] = self.recipes["ingredients"].apply(
            lambda x: " ".join(x) if isinstance(x, list) else str(x)
        )

        # ✅ Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = self.vectorizer.fit_transform(self.recipes["ingredients"])

    def heuristic(self, user_input_vec, recipe_index):
        """Heuristic: cosine similarity score"""
        recipe_vec = self.tfidf_matrix[recipe_index]
        return cosine_similarity(user_input_vec, recipe_vec).flatten()[0]

    def search(self, user_input, top_k=3):
        """Find exactly top_k unique recipes with highest heuristic scores"""
        user_input_vec = self.vectorizer.transform([user_input])
        seen_names = set()
        results = []
        
        # Calculate all heuristics with recipe names
        heuristics = []
        for i in range(len(self.recipes)):
            h_val = self.heuristic(user_input_vec, i)
            recipe_name = self.recipes.iloc[i]["name"]
            heuristics.append((h_val, i, recipe_name))
        
        # Sort by heuristic in descending order
        heuristics.sort(reverse=True, key=lambda x: x[0])
        
        # Prepare results and exploration lists with unique recipes
        exploration = []
        
        for h_val, idx, name in heuristics:
            if name not in seen_names:
                seen_names.add(name)
                recipe_data = {
                    "name": name,
                    "ingredients": self.recipes.iloc[idx]["ingredients"],
                    "steps": self.recipes.iloc[idx]["steps"],
                    "image": self.recipes.iloc[idx]["image"],
                    "Heuristic": h_val
                }
                
                # Add to results if we haven't reached top_k
                if len(results) < top_k:
                    results.append(recipe_data)
                
                # Add to exploration (exactly top_k unique recipes)
                if len(exploration) < top_k:
                    exploration.append((idx, h_val))
                
                # Stop as soon as we have enough for both results and exploration
                if len(results) >= top_k and len(exploration) >= top_k:
                    break
        
        # Ensure we return exactly top_k results
        return pd.DataFrame(results[:top_k]), exploration[:top_k]


