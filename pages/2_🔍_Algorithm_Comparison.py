import streamlit as st
import pandas as pd
import time
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import matplotlib.pyplot as plt
from io import StringIO

st.set_page_config(
    page_title="Algorithm Comparison",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for the page
st.markdown("""
<style>
.algorithm-card {
    border-radius: 12px;
    padding: 20px;
    margin: 15px 0;
    background: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    border: 1px solid rgba(0,0,0,0.05);
}
.metric-card {
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    background: #f8f9fa;
    border-left: 4px solid #4e79a7;
}
</style>
""", unsafe_allow_html=True)

st.title("Algorithm Comparison: Best-First Search vs Beam Search")
st.markdown("""
This page compares the performance and behavior of Best-First Search and Beam Search algorithms
when searching through recipe data. Adjust the beam width to see how it affects the search.
""")

# Sample data (replace with your actual algorithm implementations)
@st.cache_data
def run_algorithm(algorithm_name, query):
    # Simulate algorithm execution
    start_time = time.time()
    
    # Simulate different performance characteristics
    if algorithm_name == "Best-First Search":
        time.sleep(0.5)  # Simulate computation time
        nodes_visited = len(query.split()) * 50
        path_length = len(query.split()) * 2
    else:  # Beam Search
        time.sleep(0.7)  # Simulate computation time
        beam_width = 2  # Default beam width
        nodes_visited = len(query.split()) * 40
        path_length = len(query.split()) * 1.82
    
    execution_time = time.time() - start_time
    
    return {
        'execution_time': execution_time,
        'nodes_visited': nodes_visited,
        'path_length': path_length,
        'path': [f"Node {i+1}" for i in range(int(path_length))]
    }

# Search interface
st.header("Search Parameters")
col1, col2 = st.columns(2)
with col1:
    query = st.text_input("Enter ingredients (comma separated):", "chicken, rice, tomato")
with col2:
    max_depth = st.slider("Maximum search depth:", 1, 10, 5)

# Run algorithms
if st.button("Run Comparison"):
    # Add beam width control
    beam_width = st.slider("Beam Width", 1, 5, 2, key="beam_width")
    
    # Create tabs for each algorithm
    tab1, tab2 = st.tabs(["Best-First Search", f"Beam Search (Width={beam_width})"])
    
    with tab1:
        st.header("Best-First Search")
        with st.spinner("Running Best-First Search..."):
            bf_result = run_algorithm("Best-First Search", query)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Execution Time", f"{bf_result['execution_time']:.4f} seconds")
            with col2:
                st.metric("Nodes Visited", bf_result['nodes_visited'])
            with col3:
                st.metric("Path Length", len(bf_result['path']))
            
            # Visualization
            st.subheader("Search Tree")
            fig = go.Figure(go.Treemap(
                labels=["Root"] + bf_result['path'],
                parents=[""] + ["Root"] * len(bf_result['path']),
                values=[100] + [100/(i+1) for i in range(len(bf_result['path']))],
                textinfo="label+value"
            ))
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header(f"Beam Search (Width={beam_width})")
        with st.spinner("Running Beam Search..."):
            beam_result = run_algorithm("Beam Search", query)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Execution Time", f"{beam_result['execution_time']:.4f} seconds")
            with col2:
                st.metric("Nodes Visited", beam_result['nodes_visited'])
            with col3:
                st.metric("Path Length", len(beam_result['path']))
            
            st.info(f"Beam Search explores only the top {beam_width} nodes at each level, making it more memory efficient than Best-First Search.")
            
            # Beam Search Visualization
            st.subheader("Beam Search Exploration")
            
            # Create a graph to represent beam search
            G = nx.DiGraph()
            
            # Add nodes for each level with beam width
            for level in range(len(beam_result['path'])):
                # Add nodes for current beam
                for beam in range(beam_width):
                    node_name = f"L{level+1}B{beam+1}"
                    G.add_node(node_name, 
                             level=level+1, 
                             beam=beam+1,
                             label=f"{beam_result['path'][level] if level < len(beam_result['path']) else 'Goal'}")
                    
                    # Connect to previous level nodes
                    if level > 0:
                        for prev_beam in range(min(beam_width, level)):  # Ensure we don't go negative
                            prev_node = f"L{level}B{prev_beam+1}"
                            if prev_node in G:
                                G.add_edge(prev_node, node_name)
            
            # Position nodes in a hierarchical layout
            pos = {}
            for node in G.nodes():
                level = G.nodes[node]['level']
                beam = G.nodes[node]['beam']
                # Position nodes in a grid
                pos[node] = [level, (beam_width + 1) / 2 - beam]
            
            # Create edge traces
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            # Create node traces
            node_x = []
            node_y = []
            node_text = []
            node_colors = []
            
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(f"{G.nodes[node]['label']}<br>Level: {G.nodes[node]['level']}<br>Beam: {G.nodes[node]['beam']}")
                node_colors.append(G.nodes[node]['level'])
            
            # Create the figure with edges and nodes
            fig = go.Figure(
                data=[
                    # Add edges
                    go.Scatter(
                        x=edge_x, 
                        y=edge_y,
                        line=dict(width=1, color='#888'),
                        hoverinfo='none',
                        mode='lines'
                    ),
                    # Add nodes
                    go.Scatter(
                        x=node_x, 
                        y=node_y,
                        mode='markers+text',
                        text=[G.nodes[node]['label'] for node in G.nodes()],
                        textposition="middle center",
                        hoverinfo='text',
                        hovertext=node_text,
                        marker=dict(
                            showscale=True,
                            colorscale='Viridis',
                            color=node_colors,
                            size=20,
                            colorbar=dict(
                                thickness=15,
                                title='Level',
                                xanchor='left',
                                title_side='right'
                            ),
                            line_width=2
                        )
                    )
                ]
            )
            
            # Update layout
            fig.update_layout(
                title=f'Beam Search (Beam Width: {beam_width})',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=True, title='Search Depth'),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Comparison Section
    st.markdown("---")
    st.header("Algorithm Comparison")
    
    # Create a comparison dataframe
    comparison_data = {
        'Metric': ['Execution Time (s)', 'Nodes Visited', 'Path Length'],
        'Best-First Search': [
            f"{bf_result['execution_time']:.4f}",
            bf_result['nodes_visited'],
            len(bf_result['path'])
        ],
        'Beam Search': [
            f"{beam_result['execution_time']:.4f}",
            beam_result['nodes_visited'],
            len(beam_result['path'])
        ]
    }
    
    # Display comparison table
    st.dataframe(comparison_data, use_container_width=True, hide_index=True)
    
    # Add some analysis
    st.subheader("Analysis")
    if bf_result['execution_time'] < beam_result['execution_time']:
        st.success("Best-First Search was faster in this case.")
    else:
        st.info("Beam Search was more efficient in node exploration.")
    
    st.markdown("""
    **Key Observations:**
    - Best-First Search explores more nodes but may find a more optimal path
    - Beam Search is more memory efficient as it only keeps a limited number of nodes at each level
    - The beam width parameter allows you to balance between search quality and memory usage
    """)
    
    if bf_result['nodes_visited'] < beam_result['nodes_visited']:
        st.info("Best-First Search explored fewer nodes.")
    else:
        st.info("Beam Search was more efficient in node exploration.")
    
# Add some educational content
st.markdown("---")
st.header("About These Algorithms")

with st.expander("Best-First Search"):
    st.markdown("""
    **Best-First Search** is an informed search algorithm that explores a graph by expanding the most promising node 
    chosen according to a specified rule. It uses a priority queue to select the next node to explore based on a 
    heuristic function that estimates the cost to reach the goal from the current node.
    
    **Key Characteristics:**
    - Uses a priority queue (typically implemented with a heap)
    - Expands the most promising node first
    - Not guaranteed to find the optimal path
    - Can use significant memory for large search spaces
    
    **Time Complexity:** O(b^d) where b is the branching factor and d is the depth of the solution
    """)

with st.expander("Beam Search"):
    st.markdown("""
    **Beam Search** is a heuristic search algorithm that explores a graph by expanding the most promising nodes 
    in a limited set. Unlike Best-First Search, it only keeps a fixed number (beam width) of best nodes at each level.
    
    **Key Characteristics:**
    - Uses a beam width parameter (adjustable in the interface)
    - Only keeps the top-k most promising nodes at each level
    - More memory efficient than Best-First Search
    - May not find the optimal solution if the beam width is too small
    
    **Time Complexity:** O(b * k * d) where:
    - b is the branching factor
    - k is the beam width
    - d is the depth of the solution
    
    **When to use Beam Search:**
    - When memory is a concern
    - When you're okay with a good (but not necessarily optimal) solution
    - When the search space is large but the solution is not too deep
    """)
    st.markdown("""
    **Best-First Search** is an informed search algorithm that explores a graph by expanding the most promising node 
    chosen according to a specified rule. It uses a priority queue to select the most promising node based on a 
    heuristic function that estimates the cost to reach the goal from the current node.
    
    **Advantages:**
    - More efficient than uninformed search algorithms
    - Can find good solutions quickly with the right heuristic
    
    **Disadvantages:**
    - Not optimal (may not find the shortest path)
    - Can get stuck in local minima
    """)
