import pandas as pd
import requests
from io import BytesIO
from PIL import Image

def load_dataset(path="dataset.csv"):
    df = pd.read_csv(path)
    print("✅ Dataset loaded successfully!")
    print(f"Total Recipes: {len(df)}")
    print(f"Columns: {df.columns.tolist()}\n")
    return df

def test_image(df):
    img_col = [c for c in df.columns if "image" in c.lower()][0]
    sample = df[img_col].dropna().iloc[0]
    print("🖼️ Testing image from:", sample)
    try:
        if sample.startswith("http"):
            img = Image.open(BytesIO(requests.get(sample, timeout=10).content))
        else:
            img = Image.open(sample)
        print("Image loaded successfully:", img.format, img.size)
        img.show()
    except Exception as e:
        print("❌ Failed to load image:", e)

if __name__ == "__main__":
    df = load_dataset("dataset.csv")
    print(df.head()[["Title", "Ingredients"]])
    test_image(df)
