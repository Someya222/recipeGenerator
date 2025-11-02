# Recipe Generator with Best-First Search

A Streamlit application that helps you find recipes based on the ingredients you have, using a Best-First Search algorithm to find the most relevant matches.

## Features

- **Smart Ingredient Search**: Find recipes based on available ingredients
- **Visual Exploration**: See how the search algorithm works
- **Responsive Design**: Works on both desktop and mobile devices
- **Interactive Visualizations**: Explore recipe data with interactive charts

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd recipeGenerator
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # On Windows
   # or
   source .venv/bin/activate  # On macOS/Linux
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Place your recipe data in a file named `recipes3k_cleaned.csv` in the project root.

## Usage

1. Run the application:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and navigate to `http://localhost:8501`

3. Enter the ingredients you have and click "Find Recipes"

4. Explore the search visualization by clicking "View Search Exploration"

## Project Structure

- `app.py` - Main application file
- `best_first_search.py` - Best-First Search algorithm implementation
- `pages/1_🧠_Exploration.py` - Search visualization page
- `requirements.txt` - Python dependencies
- `README.md` - This file

## Dependencies

- Python 3.8+
- Streamlit
- Pandas
- Plotly
- Matplotlib
- streamlit-lottie
- streamlit-tags

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
