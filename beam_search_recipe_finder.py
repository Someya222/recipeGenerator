import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class BeamSearchRecipeFinder:
    def __init__(self, recipes, beam_width=3):
        """
        Initialize the Beam Search recipe finder.
        
        Args:
            recipes (pd.DataFrame): DataFrame containing recipes
            beam_width (int): Number of top nodes to keep at each level (default: 5)
        """
        self.recipes = recipes.copy()
        self.beam_width = beam_width
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
        # Preprocess ingredients if needed
        self.recipes['ingredients_processed'] = self.recipes['ingredients'].apply(
            lambda x: x.lower() if isinstance(x, str) else ''
        )
        
        # Create TF-IDF matrix for all recipes
        self.ingredient_vectors = self.vectorizer.fit_transform(
            self.recipes['ingredients_processed'].fillna('')
        )
    
    def _get_ingredient_similarity(self, query_ingredients):
        """Calculate similarity between query ingredients and all recipes."""
        query_vec = self.vectorizer.transform([' '.join(query_ingredients).lower()])
        similarities = cosine_similarity(query_vec, self.ingredient_vectors).flatten()
        return similarities
    
    def _heuristic_score(self, recipe_idx, query_ingredients):
        """Calculate a heuristic score for a recipe based on ingredients."""
        # Get the recipe's ingredients
        recipe_ingredients = set(self.recipes.iloc[recipe_idx]['ingredients_processed'].lower().split(','))
        query_ingredients = set(ing.lower() for ing in query_ingredients)
        
        # Calculate Jaccard similarity
        intersection = len(recipe_ingredients.intersection(query_ingredients))
        union = len(recipe_ingredients.union(query_ingredients))
        jaccard = intersection / union if union > 0 else 0
        
        # Consider recipe rating if available
        rating = self.recipes.iloc[recipe_idx].get('rating', 0) / 5.0 if 'rating' in self.recipes.columns else 0.5
        
        # Combine scores (70% weight to ingredient match, 30% to rating)
        return 0.7 * jaccard + 0.3 * rating
    
    def search(self, query_ingredients, top_k=3):
        """
        Find recipes using Beam Search algorithm.
        
        Args:
            query_ingredients (str): Space-separated string of ingredients
            top_k (int): Number of top recipes to return (default: 5)
            
        Returns:
            tuple: (top_recipes, visited)
                - top_recipes: DataFrame of top matching recipes
                - visited: List of (recipe_index, score) tuples of visited nodes
        """
        if not query_ingredients.strip():
            return self.recipes.head(top_k).copy(), []
        
        query_ingredients = [ing.strip().lower() for ing in query_ingredients.split() if ing.strip()]
        if not query_ingredients:
            return self.recipes.head(top_k).copy(), []
        
        # Calculate initial similarities
        similarities = self._get_ingredient_similarity(query_ingredients)
        
        # Get top 2*beam_width initial candidates to ensure diversity
        initial_candidates = np.argpartition(similarities, -self.beam_width*2)[-self.beam_width*2:]
        beam = [(int(idx), float(similarities[idx])) for idx in initial_candidates]
        
        # Sort by score and take top beam_width
        beam.sort(key=lambda x: x[1], reverse=True)
        beam = beam[:self.beam_width]
        visited = list(beam)
        
        # Keep track of visited recipe names to avoid duplicates
        visited_names = set(self.recipes.iloc[idx]['name'] for idx, _ in visited)
        
        # Beam search for a few iterations
        for _ in range(2):  # Number of iterations can be adjusted
            new_beam = []
            
            for idx, score in beam:
                # Get current recipe's ingredients
                recipe_ingredients = set(self.recipes.iloc[idx]['ingredients_processed'].lower().split(','))
                
                # Find recipes that share ingredients with the current recipe
                for i, row in self.recipes.iterrows():
                    recipe_name = row['name']
                    if recipe_name not in visited_names:  # Only consider unvisited recipes
                        other_ingredients = set(row['ingredients_processed'].lower().split(','))
                        
                        # Calculate overlap with query ingredients
                        query_overlap = len(set(query_ingredients).intersection(other_ingredients))
                        if query_overlap > 0:  # Only consider recipes that share at least one ingredient with query
                            # Calculate score based on similarity to query and diversity from current beam
                            sim_score = float(similarities[i])
                            
                            # Add some randomness to break ties and encourage diversity
                            rand_factor = 0.9 + 0.2 * np.random.random()
                            diversity_bonus = 0.1 * (1.0 - (len(recipe_ingredients.intersection(other_ingredients)) / 
                                                        len(recipe_ingredients.union(other_ingredients))))
                            
                            total_score = (sim_score + diversity_bonus) * rand_factor
                            new_beam.append((i, total_score))
                            visited_names.add(recipe_name)
                            
                            if len(new_beam) >= self.beam_width * 2:  # Limit number of neighbors
                                break
            
            # Keep only top-scoring new candidates
            if new_beam:
                # Remove duplicates by recipe name
                unique_new = {}
                for idx, score in new_beam:
                    name = self.recipes.iloc[idx]['name']
                    if name not in unique_new or score > unique_new[name][1]:
                        unique_new[name] = (idx, score)
                
                # Sort by score and take top beam_width
                new_beam = sorted(unique_new.values(), key=lambda x: x[1], reverse=True)
                beam = new_beam[:self.beam_width]
                visited.extend(beam)
        
        # Get unique recipes, keeping the highest score for each
        unique_visited = {}
        for idx, score in visited:
            name = self.recipes.iloc[idx]['name']
            if name not in unique_visited or score > unique_visited[name][1]:
                unique_visited[name] = (idx, score)
        
        # Sort by score and get top_k
        sorted_visited = sorted(unique_visited.values(), key=lambda x: x[1], reverse=True)
        
        # Get exactly top_k recipes, ensuring we have unique names
        final_recipes = []
        seen_names = set()
        
        # First, try to get recipes from visited nodes
        for idx, score in sorted_visited:
            name = self.recipes.iloc[idx]['name']
            if name not in seen_names:
                final_recipes.append((idx, score))
                seen_names.add(name)
                if len(final_recipes) >= top_k:
                    break
        
        # If we still don't have enough, get from top similarities
        if len(final_recipes) < top_k:
            for idx in np.argsort(similarities)[::-1]:
                name = self.recipes.iloc[idx]['name']
                if name not in seen_names:
                    final_recipes.append((idx, float(similarities[idx])))
                    seen_names.add(name)
                    if len(final_recipes) >= top_k:
                        break
        
        # Create final result
        top_indices = [idx for idx, _ in final_recipes]
        top_recipes = self.recipes.iloc[top_indices].copy()
        top_recipes['search_score'] = [score for _, score in final_recipes]
        
        return top_recipes, sorted_visited[:top_k]
