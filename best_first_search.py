from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import heapq
import pandas as pd

class BestFirstSearchRecipeFinder:
    def __init__(self, recipes):
        self.recipes = recipes
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = self.vectorizer.fit_transform(recipes["Cleaned_Ingredients"])

    def heuristic(self, user_input_vec, recipe_index):
        """Heuristic: cosine similarity score"""
        recipe_vec = self.tfidf_matrix[recipe_index]
        return cosine_similarity(user_input_vec, recipe_vec).flatten()[0]

    def search(self, user_input, top_k=5):
        """Perform Best First Search to find top_k best matches"""
        user_input_vec = self.vectorizer.transform([user_input])
        pq = []  # priority queue (max-heap)
        visited = []
        results = []

        for i in range(len(self.recipes)):
            h_val = self.heuristic(user_input_vec, i)
            heapq.heappush(pq, (-h_val, i))

        seen = set()
        while pq and len(results) < top_k:
            score, idx = heapq.heappop(pq)
            if idx not in seen:
                seen.add(idx)
                visited.append((idx, -score))  # record exploration
                results.append(self.recipes.iloc[idx])

        # ✅ make sure two things are returned
        return pd.DataFrame(results), visited
