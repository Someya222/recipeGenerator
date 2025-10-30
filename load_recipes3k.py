import pandas as pd
import os
import json

# Directory containing JSON files
data_dir = "dataset"
all_data = []

# Load and combine all recipe JSON files
for file in os.listdir(data_dir):
    if file.endswith(".json"):
        path = os.path.join(data_dir, file)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for recipe in data:
                recipe["source_file"] = file
            all_data.extend(data)

df = pd.DataFrame(all_data)

print(f"✅ Loaded {len(df)} recipes from {len(os.listdir(data_dir))} files")
print("Columns:", df.columns.tolist())

# --- Keep only needed columns ---
keep_cols = ["name", "ingredients", "steps", "image", "url", "description", "maincategory"]
df = df[keep_cols].dropna(subset=["ingredients", "name"]).reset_index(drop=True)

# Save cleaned version
df.to_csv("recipes3k_cleaned.csv", index=False, encoding="utf-8")
print("\n✅ Saved cleaned dataset as 'recipes3k_cleaned.csv'")
print(df.head(3))

