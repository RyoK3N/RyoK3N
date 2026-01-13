#!/usr/bin/env python3
"""
AI Agent - Interactive Knowledge Graph Generator
Creates interactive HTML knowledge graph visualization
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import networkx as nx
from pyvis.network import Network

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "docs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Color scheme for categories
CATEGORY_COLORS = {
    "Machine Learning": "#667eea",
    "Computer Vision": "#764ba2",
    "Natural Language Processing": "#f093fb",
    "Data Science": "#4facfe",
    "Web Development": "#43e97b",
    "DevOps": "#38f9d7",
    "Mobile Development": "#fa709a",
    "3D Graphics": "#fee140",
    "Robotics": "#30cfd0",
    "Reinforcement Learning": "#a8edea",
    "Research": "#ff6b6b",
    "Tools & Utilities": "#95a5a6",
    "Uncategorized": "#bdc3c7",
}

def load_categorized_projects() -> Dict[str, Any]:
    """Load categorized projects"""
    categories_file = DATA_DIR / "project_categories.json"
    with open(categories_file, 'r') as f:
        return json.load(f)

def create_knowledge_graph(data: Dict[str, Any]) -> Network:
    """Create interactive knowledge graph"""
    print("🕸️ Creating knowledge graph...")
    
    # Initialize network
    net = Network(
        height="800px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#2c3e50",
        notebook=False,
        directed=False
    )
    
    # Configure physics
    net.barnes_hut(
        gravity=-8000,
        central_gravity=0.3,
        spring_length=250,
        spring_strength=0.001,
        damping=0.09
    )
    
    # Create graph structure
    G = nx.Graph()
    
    # Add category nodes (larger, colored)
    categories = set()
    for repo in data["categorized_repositories"]:
        categories.update(repo["categories"])
    
    for category in categories:
        color = CATEGORY_COLORS.get(category, "#95a5a6")
        G.add_node(
            category,
            title=f"Category: {category}",
            size=40,
            color=color,
            shape="box",
            font={"size": 20, "color": "#ffffff"},
            borderWidth=3,
            borderWidthSelected=5
        )
    
    # Add repository nodes and edges
    for repo in data["categorized_repositories"]:
        repo_name = repo["name"]
        
        # Node title with hover info
        title = f"""<b>{repo_name}</b><br>
Stars: {repo['stars']}<br>
Languages: {', '.join(repo['languages'][:3])}<br>
Categories: {', '.join(repo['categories'])}<br>
<i>{repo['description'][:100]}...</i>"""
        
        # Size based on stars (min 10, max 30)
        size = min(30, max(10, 10 + repo['stars'] / 10))
        
        # Color based on primary category
        primary_cat = repo['categories'][0] if repo['categories'] else "Uncategorized"
        color = CATEGORY_COLORS.get(primary_cat, "#95a5a6")
        
        G.add_node(
            repo_name,
            title=title,
            size=size,
            color=color,
            shape="dot",
            url=repo['url']
        )
        
        # Connect to categories
        for category in repo['categories']:
            G.add_edge(repo_name, category, width=2, color=color)
        
        # Connect related projects (same language)
        for other_repo in data["categorized_repositories"]:
            if other_repo["name"] != repo_name:
                # Connect if they share languages
                shared_langs = set(repo["languages"]) & set(other_repo["languages"])
                if shared_langs and len(shared_langs) >= 2:
                    G.add_edge(
                        repo_name,
                        other_repo["name"],
                        width=1,
                        color="#ecf0f1",
                        dashes=True
                    )
    
    # Convert to pyvis
    net.from_nx(G)
    
    # Set options for interactivity
    net.set_options("""
    {
      "nodes": {
        "font": {
          "size": 14,
          "face": "Arial"
        }
      },
      "edges": {
        "smooth": {
          "type": "continuous"
        }
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 200,
        "navigationButtons": true,
        "keyboard": true
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -8000,
          "springConstant": 0.001,
          "springLength": 250
        },
        "minVelocity": 0.75
      }
    }
    """)
    
    print(f"   ✅ Created graph with {len(G.nodes)} nodes and {len(G.edges)} edges")
    
    return net

def add_custom_styling(html_content: str) -> str:
    """Add custom styling to the HTML"""
    
    custom_css = """
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        #header {
            text-align: center;
            color: white;
            margin-bottom: 20px;
        }
        #header h1 {
            font-size: 32px;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        #header p {
            font-size: 16px;
            opacity: 0.9;
        }
        #mynetwork {
            border: 3px solid white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            background: white;
        }
        #legend {
            position: fixed;
            top: 80px;
            right: 30px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            max-width: 250px;
            z-index: 1000;
        }
        #legend h3 {
            margin: 0 0 10px 0;
            font-size: 16px;
            color: #2c3e50;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin: 8px 0;
            font-size: 13px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 4px;
            margin-right: 8px;
        }
        #controls {
            text-align: center;
            margin-top: 15px;
        }
        .control-btn {
            background: white;
            border: 2px solid #667eea;
            color: #667eea;
            padding: 10px 20px;
            margin: 5px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        .control-btn:hover {
            background: #667eea;
            color: white;
        }
    </style>
    """
    
    header_html = """
    <div id="header">
        <h1>🧠 AI-Powered Project Knowledge Graph</h1>
        <p>Interactive visualization of project categories and relationships</p>
    </div>
    """
    
    legend_html = """
    <div id="legend">
        <h3>📊 Legend</h3>
        <div class="legend-item">
            <div class="legend-color" style="background: #667eea;"></div>
            <span>Large nodes = Categories</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #95a5a6; border-radius: 50%;"></div>
            <span>Small nodes = Projects</span>
        </div>
        <div class="legend-item">
            <div style="width: 30px; height: 2px; background: #2c3e50; margin-right: 8px;"></div>
            <span>Solid = Category link</span>
        </div>
        <div class="legend-item">
            <div style="width: 30px; height: 2px; background: #ecf0f1; border-top: 2px dashed #95a5a6; margin-right: 8px;"></div>
            <span>Dashed = Related projects</span>
        </div>
        <p style="margin-top: 15px; font-size: 11px; color: #7f8c8d;">
            💡 Click and drag to explore<br>
            🔍 Scroll to zoom<br>
            🖱️ Hover for details
        </p>
    </div>
    """
    
    controls_html = """
    <div id="controls">
        <button class="control-btn" onclick="network.fit();">🎯 Reset View</button>
        <button class="control-btn" onclick="togglePhysics();">⚡ Toggle Physics</button>
    </div>
    <script>
        let physicsEnabled = true;
        function togglePhysics() {
            physicsEnabled = !physicsEnabled;
            network.setOptions({physics: {enabled: physicsEnabled}});
        }
    </script>
    """
    
    # Insert custom elements
    html_content = html_content.replace("</head>", f"{custom_css}</head>")
    html_content = html_content.replace("<body>", f"<body>{header_html}{legend_html}")
    html_content = html_content.replace("</body>", f"{controls_html}</body>")
    
    return html_content

def main():
    """Main graph generation function"""
    try:
        print("🎨 Starting knowledge graph generation...")
        
        # Load data
        data = load_categorized_projects()
        
        print(f"📚 Loaded {data['total_repositories']} categorized projects")
        
        # Create graph
        net = create_knowledge_graph(data)
        
        # Generate HTML
        output_file = OUTPUT_DIR / "knowledge-graph.html"
        net.save_graph(str(output_file))
        
        # Add custom styling
        with open(output_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        html_content = add_custom_styling(html_content)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n✅ Knowledge graph generated!")
        print(f"💾 Saved to {output_file}")
        print(f"🌐 Open in browser to view interactive visualization")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
