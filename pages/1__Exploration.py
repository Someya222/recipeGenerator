import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt

# Check if wordcloud is available
WORDCLOUD_AVAILABLE = False
try:
    from wordcloud import WordCloud
    WORDCLOUD_AVAILABLE = True
except ImportError:
    pass

st.set_page_config(
    page_title="Best First Search Exploration",
    layout="wide"
)

# Custom CSS for better visualization
st.markdown("""
<style>
    .stPlotlyChart, .stDataFrame {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 15px;
        background: white;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("Best First Search Algorithm Explorer")
st.markdown("### Visualizing how the algorithm searches for recipes")

# Check if we have exploration data in session state
if 'exploration_data' not in st.session_state or st.session_state.exploration_data is None:
    st.warning("⚠️ No exploration data found! Please run a search on the home page first.")
    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjR2Z3ZzZ2VtY2F3bGZ6d2F3eWJjNnFzZ2JxY2RqZzB6b3Z0cCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7aTskHEUdgCQAXde/giphy.gif", 
             caption="Run a search to see the magic happen!")
    
    if st.button("🔙 Back to Search"):
        st.switch_page("app.py")
    st.stop()

# Get data from session state
visited_df = st.session_state.exploration_data.copy()

# Add exploration order
visited_df['Exploration Order'] = range(1, len(visited_df) + 1)

# Create tabs for different visualizations
tab1, tab2, tab3, tab4 = st.tabs([
    "Search Overview", 
    "Heuristic Analysis", 
    "Search Path",
    "Ingredient Network"
])

with tab1:
    st.subheader("Algorithm Performance")
    
    # Performance metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Recipes Explored", len(visited_df))
    with col2:
        st.metric("Best Heuristic Score", f"{visited_df['Heuristic'].max():.3f}")
    with col3:
        st.metric("Average Heuristic", f"{visited_df['Heuristic'].mean():.3f}")
    
    # Main bar chart
    st.subheader("Recipe Similarity Scores")
    fig = px.bar(
        visited_df.head(15), 
        x="Recipe", 
        y="Heuristic",
        color="Heuristic",
        color_continuous_scale='Viridis',
        labels={"Heuristic": "Similarity Score"},
        height=500
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
with tab2:
    st.subheader("Heuristic Score Distribution")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Distribution plot
        fig = px.histogram(
            visited_df, 
            x="Heuristic",
            nbins=20,
            title="Distribution of Heuristic Scores",
            marginal="box"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top 5 recipes
        st.subheader("Top 5 Recipes")
        top5 = visited_df.nlargest(5, 'Heuristic')
        for idx, row in top5.iterrows():
            st.markdown(f"**{row['Recipe']}**")
            st.markdown(f"Score: {row['Heuristic']:.3f}")
            st.markdown("---")
    
with tab3:
    st.subheader("Search Progression")
    
    # Progress over time
    fig = px.line(
        visited_df, 
        y="Heuristic",
        title="Best Heuristic Score Over Time",
        labels={"index": "Exploration Step", "Heuristic": "Best Score"}
    )
    fig.update_traces(line=dict(width=3))
    st.plotly_chart(fig, use_container_width=True)
    
    # Exploration order vs score
    fig = px.scatter(
        visited_df, 
        x="Exploration Order",
        y="Heuristic",
        size="Heuristic",
        hover_name="Recipe",
        title="Recipe Discovery Order vs. Similarity Score"
    )
    st.plotly_chart(fig, use_container_width=True)
    
with tab4:
    st.subheader("Recipe Similarity Network")
    st.info("This visualization shows how different recipes are connected based on their ingredients")

    # 🔹 Ingredient Network Visualization (add this part)
    import plotly.graph_objects as go
    import networkx as nx

    try:
        # Take first few recipes for a simple demo network
        recipes = visited_df["Recipe"].head(8).tolist()

        # Example: connect recipes in a pattern (replace with your own logic if you have ingredient overlap data)
        edges = [(recipes[i], recipes[j]) for i in range(len(recipes))
                 for j in range(i + 1, len(recipes)) if i % 2 == j % 3]

        # Create and position the graph
        G = nx.Graph()
        G.add_edges_from(edges)
        pos = nx.spring_layout(G, seed=42)

        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        node_x, node_y = [], []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=[str(n) for n in G.nodes()],
            textposition="top center",
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                color=[len(list(G.neighbors(n))) for n in G.nodes()],
                size=18,
                colorbar=dict(
                    thickness=15,
                    title='Connections',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2)
        )

        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title="Ingredient Similarity Network",
                            titlefont_size=20,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=0, l=0, r=0, t=40),
                            xaxis=dict(showgrid=False, zeroline=False),
                            yaxis=dict(showgrid=False, zeroline=False)
                        ))

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.warning(f"Network visualization could not be generated: {str(e)}")

    # 🔹 Word Cloud (your original code continues here)
    st.subheader("Recipe Analysis")

    if WORDCLOUD_AVAILABLE:
        st.markdown("#### Common Ingredients")
        try:
            all_ingredients = " ".join([str(ing) for ing in visited_df['Recipe']])
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_ingredients)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Could not generate word cloud: {str(e)}")
    else:
         st.info("WordCloud package not installed. Skipping ingredient cloud visualization.")

    
    # Show recipe statistics
    st.markdown("#### Recipe Statistics")
    avg_ingredients = len(" ".join(visited_df['Recipe']).split()) / len(visited_df)
    st.metric("Average Recipe Name Length", f"{avg_ingredients:.1f} words")
    
# Raw data section
with st.expander("View Raw Exploration Data"):
    st.dataframe(visited_df)

# Add some space at the bottom
st.markdown("---")
st.caption("Best First Search Algorithm Visualization - Recipe Finder")

# Back to search button at the bottom
if st.button("Back to Search"):
    st.switch_page("app.py")