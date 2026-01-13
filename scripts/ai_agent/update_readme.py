#!/usr/bin/env python3
"""
AI Agent - README Update Module (New Features)
Updates README with knowledge graph, featured project, and blog sections
"""

import json
from datetime import datetime
from pathlib import Path
import re

DATA_DIR = Path(__file__).parent / "data"
README_PATH = Path(__file__).parent.parent.parent / "README.md"

def load_all_data():
    """Load all generated data"""
    data = {}
    
    files = {
        'categories': 'project_categories.json',
        'featured': 'featured_project.json',
        'blog': 'blog_post.json',
        'publication': 'publication_history.json',
    }
    
    for key, filename in files.items():
        filepath = DATA_DIR / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                data[key] = json.load(f)
    
    return data

def create_knowledge_graph_section():
    """Create knowledge graph section"""
    
    section = """<!--START_SECTION:knowledge_graph-->
## 🧠 AI-Powered Project Knowledge Graph

<div align="center">

### Explore My Projects Interactively

[![View Knowledge Graph](https://img.shields.io/badge/🕸️_Interactive_Graph-View_Live-blueviolet?style=for-the-badge)](https://ryok3n.github.io/RyoK3N/knowledge-graph.html)

</div>

The knowledge graph above provides an **interactive visualization** of my projects, categorized by AI and connected based on shared technologies and themes. Click nodes to explore, drag to rearrange, and discover the relationships between different projects.

**Features:**
- 🎨 **AI-Categorized**: Projects automatically categorized using machine learning
- 🔗 **Smart Connections**: Related projects linked by shared languages and technologies  
- 📊 **Data-Driven**: Node sizes represent project popularity (stars)
- 🎯 **Interactive**: Click, drag, zoom, and explore in real-time

<div align="center">

[📊 View Full Graph](https://ryok3n.github.io/RyoK3N/knowledge-graph.html) • [🔄 Last Updated: {timestamp}]

</div>

<!--END_SECTION:knowledge_graph-->"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d')
    return section.replace('{timestamp}', timestamp)

def create_featured_project_section(featured: dict):
    """Create featured project section"""
    
    week_year = f"Week {featured['week_number']}, {featured['year']}"
    categories_badges = ' '.join([
        f"![{cat}](https://img.shields.io/badge/{cat.replace(' ', '_')}-purple?style=flat-square)"
        for cat in featured['categories'][:3]
    ])
    
    section = f"""<!--START_SECTION:featured_project-->
## ⭐ Featured Project of the Week

<div align="center">

### 🎯 {week_year}

</div>

<table>
<tr>
<td width="60%">

### 📦 [{featured['name']}]({featured['url']})

{categories_badges}

{featured['ai_description']}

**💡 Why Featured This Week:**

*{featured['why_featured']}*

</td>
<td width="40%">

**📊 Project Stats**

- ⭐ **Stars**: {featured['stars']}
- 🏷️ **Categories**: {', '.join(featured['categories'])}
- 💻 **Languages**: {', '.join(featured['languages'][:3])}

**🔗 Quick Links**

[![View Project](https://img.shields.io/badge/View-Project-blue?style=for-the-badge&logo=github)]({featured['url']})

</td>
</tr>
</table>

<div align="center">

*🤖 AI-selected and described • Updated weekly*

</div>

<!--END_SECTION:featured_project-->"""
    
    return section

def create_blog_section(blog: dict, publication: dict):
    """Create latest blog post section"""
    
    # Get blog URL
    blog_url = f"https://ryok3n.github.io/RyoK3N/blog/{blog.get('slug', 'latest')}.html"
    pub_date = datetime.fromisoformat(blog.get('created_at', datetime.now().isoformat())).strftime('%B %d, %Y')
    
    tags_badges = ' '.join([
        f"`{tag}`" for tag in blog.get('tags', [])[:4]
    ])
    
    section = f"""<!--START_SECTION:latest_blog-->
## 📝 Latest from My Tech Blog

<div align="center">

[![Read Blog](https://img.shields.io/badge/📖_Read-Tech_Blog-black?style=for-the-badge)](https://ryok3n.github.io/RyoK3N/)

</div>

<table>
<tr>
<td>

### 📰 [{blog['title']}]({blog_url})

**Published**: {pub_date}

{blog.get('excerpt', '')}

**Tags**: {tags_badges}

<div align="center">

[![Read Full Post](https://img.shields.io/badge/Read_Full_Post-→-blue?style=for-the-badge)]({blog_url})

</div>

</td>
</tr>
</table>

<div align="center">

### 📚 More Posts

[![All Posts](https://img.shields.io/badge/View_All-Posts-success?style=for-the-badge)](https://ryok3n.github.io/RyoK3N/)
[![RSS Feed](https://img.shields.io/badge/Subscribe-RSS-orange?style=for-the-badge)](https://ryok3n.github.io/RyoK3N/feed.xml)

*🤖 AI-generated and automatically published • Updated weekly*

</div>

<!--END_SECTION:latest_blog-->"""
    
    return section

def update_section(readme: str, section_name: str, new_content: str) -> str:
    """Update a README section"""
    
    pattern = f"<!--START_SECTION:{section_name}-->.*?<!--END_SECTION:{section_name}-->"
    
    if re.search(pattern, readme, re.DOTALL):
        return re.sub(pattern, new_content, readme, flags=re.DOTALL)
    else:
        print(f"⚠️  Section '{section_name}' not found - will be appended")
        # Append before the final closing div
        return readme.replace("</div>\n\n\n", f"</div>\n\n{new_content}\n\n\n")

def main():
    """Main README update function"""
    try:
        print("📝 Updating README with new features...")
        
        # Load data
        print("\n📚 Loading data...")
        data = load_all_data()
        
        # Load README
        print("\n📖 Reading README...")
        with open(README_PATH, 'r', encoding='utf-8') as f:
            readme = f.read()
        
        print(f"   ✅ Loaded {len(readme)} characters")
        
        # Create sections
        print("\n✨ Generating sections...")
        
        print("   1/3: Knowledge Graph")
        kg_section = create_knowledge_graph_section()
        
        if 'featured' in data:
            print("   2/3: Featured Project")
            featured_section = create_featured_project_section(data['featured'])
        else:
            print("   2/3: Featured Project (skipped - no data)")
            featured_section = None
        
        if 'blog' in data:
            print("   3/3: Latest Blog")
            blog_section = create_blog_section(
                data['blog'],
                data.get('publication', {})
            )
        else:
            print("   3/3: Latest Blog (skipped - no data)")
            blog_section = None
        
        # Update README
        print("\n📝 Updating README sections...")
        
        readme = update_section(readme, "knowledge_graph", kg_section)
        
        if featured_section:
            readme = update_section(readme, "featured_project", featured_section)
        
        if blog_section:
            readme = update_section(readme, "latest_blog", blog_section)
        
        # Write updated README
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(readme)
        
        print("\n✅ README updated successfully!")
        
        # Summary
        print("\n" + "="*60)
        print("📋 UPDATE SUMMARY")
        print("="*60)
        print("✓ Knowledge Graph section updated")
        if featured_section:
            print("✓ Featured Project section updated")
        if blog_section:
            print("✓ Latest Blog section updated")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
