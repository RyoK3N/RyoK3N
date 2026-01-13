#!/usr/bin/env python3
"""
AI Agent - Blog Page Generator
Creates beautiful HTML blog pages for GitHub Pages
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import re

DATA_DIR = Path(__file__).parent / "data"
BLOG_DIR = Path(__file__).parent.parent.parent / "docs" / "blog"
ASSETS_DIR = Path(__file__).parent.parent.parent / "docs" / "assets"

# Create directories
BLOG_DIR.mkdir(parents=True, exist_ok=True)
(ASSETS_DIR / "css").mkdir(parents=True, exist_ok=True)
(ASSETS_DIR / "js").mkdir(parents=True, exist_ok=True)

def load_blog_post() -> Dict[str, Any]:
    """Load generated blog post"""
    blog_file = DATA_DIR / "blog_post.json"
    
    if not blog_file.exists():
        raise FileNotFoundError("No blog post found")
    
    with open(blog_file, 'r') as f:
        return json.load(f)

def load_blog_history() -> List[Dict]:
    """Load all previous blog posts"""
    history_file = DATA_DIR / "blog_history.json"
    
    if history_file.exists():
        with open(history_file, 'r') as f:
            return json.load(f).get('posts', [])
    
    return []

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text[:100]

def format_date(iso_date: str) -> str:
    """Format ISO date to readable format"""
    try:
        dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y')
    except:
        return datetime.now().strftime('%B %d, %Y')

def create_blog_post_html(post: Dict) -> str:
    """Create HTML for individual blog post"""
    
    # Format content paragraphs
    paragraphs = [p.strip() for p in post['content'].split('\n\n') if p.strip()]
    content_html = '\n'.join([f'        <p>{p}</p>' for p in paragraphs])
    
    # Format tags
    tags_html = ' '.join([
        f'<span class="tag">{tag}</span>' 
        for tag in post.get('tags', [])
    ])
    
    # Reading time estimate (200 words per minute)
    word_count = len(post['content'].split())
    read_time = max(1, word_count // 200)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post['title']} - Reiyo's Tech Blog</title>
    <meta name="description" content="{post.get('excerpt', '')}">
    <meta name="keywords" content="{', '.join(post.get('tags', []))}">
    <meta name="author" content="Reiyo">
    
    <!-- Open Graph / Social Media -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{post['title']}">
    <meta property="og:description" content="{post.get('excerpt', '')}">
    <meta property="og:url" content="https://ryok3n.github.io/RyoK3N/blog/{post['slug']}.html">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{post['title']}">
    <meta name="twitter:description" content="{post.get('excerpt', '')}">
    
    <link rel="stylesheet" href="../assets/css/blog.css">
    <link rel="canonical" href="https://ryok3n.github.io/RyoK3N/blog/{post['slug']}.html">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="../index.html" class="nav-logo">🧠 Reiyo's Blog</a>
            <div class="nav-links">
                <a href="../index.html">Home</a>
                <a href="../knowledge-graph.html">Projects</a>
                <a href="https://github.com/RyoK3N">GitHub</a>
                <a href="../feed.xml">RSS</a>
            </div>
        </div>
    </nav>

    <article class="blog-post">
        <header class="post-header">
            <h1 class="post-title">{post['title']}</h1>
            
            <div class="post-meta">
                <span class="meta-item">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="16" y1="2" x2="16" y2="6"></line>
                        <line x1="8" y1="2" x2="8" y2="6"></line>
                        <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                    {format_date(post.get('created_at', ''))}
                </span>
                
                <span class="meta-item">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    {read_time} min read
                </span>
                
                <span class="meta-item">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                        <line x1="7" y1="7" x2="7.01" y2="7"></line>
                    </svg>
                    {len(post.get('tags', []))} tags
                </span>
            </div>
            
            <div class="post-tags">
                {tags_html}
            </div>
        </header>

        <div class="post-content">
{content_html}
        </div>

        <footer class="post-footer">
            <div class="share-section">
                <h3>Share this post</h3>
                <div class="share-buttons">
                    <a href="https://twitter.com/intent/tweet?text={post['title']}&url=https://ryok3n.github.io/RyoK3N/blog/{post['slug']}.html" 
                       class="share-btn twitter" target="_blank" rel="noopener">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z"></path>
                        </svg>
                        Twitter
                    </a>
                    <a href="https://www.linkedin.com/sharing/share-offsite/?url=https://ryok3n.github.io/RyoK3N/blog/{post['slug']}.html" 
                       class="share-btn linkedin" target="_blank" rel="noopener">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M16 8a6 6 0 016 6v7h-4v-7a2 2 0 00-2-2 2 2 0 00-2 2v7h-4v-7a6 6 0 016-6zM2 9h4v12H2z"></path>
                            <circle cx="4" cy="4" r="2"></circle>
                        </svg>
                        LinkedIn
                    </a>
                </div>
            </div>
            
            <div class="author-section">
                <div class="author-info">
                    <h3>About the Author</h3>
                    <p>
                        <strong>Reiyo</strong> is a Machine Learning Engineer specializing in Computer Vision, 
                        Deep Learning, and AI Research. Currently working at Synexian Labs, building intelligent 
                        systems that bridge perception and cognition.
                    </p>
                    <div class="author-links">
                        <a href="https://github.com/RyoK3N">GitHub</a>
                        <a href="https://linkedin.com/in/reiyo06">LinkedIn</a>
                        <a href="https://oreiyo.space">Portfolio</a>
                    </div>
                </div>
            </div>
            
            <a href="../index.html" class="back-link">← Back to all posts</a>
        </footer>
    </article>

    <script src="../assets/js/blog.js"></script>
</body>
</html>'''
    
    return html

def create_blog_index_html(all_posts: List[Dict]) -> str:
    """Create blog homepage with all posts"""
    
    # Sort posts by date (newest first)
    sorted_posts = sorted(
        all_posts, 
        key=lambda x: x.get('created_at', ''), 
        reverse=True
    )
    
    # Create post cards
    posts_html = []
    for post in sorted_posts:
        tags = ' '.join([f'<span class="tag">{tag}</span>' for tag in post.get('tags', [])[:3]])
        
        posts_html.append(f'''
        <article class="post-card">
            <div class="post-card-header">
                <h2 class="post-card-title">
                    <a href="blog/{post['slug']}.html">{post['title']}</a>
                </h2>
                <time class="post-card-date">{format_date(post.get('created_at', ''))}</time>
            </div>
            
            <p class="post-card-excerpt">{post.get('excerpt', '')}</p>
            
            <div class="post-card-footer">
                <div class="post-card-tags">{tags}</div>
                <a href="blog/{post['slug']}.html" class="read-more">
                    Read More →
                </a>
            </div>
        </article>''')
    
    posts_grid = '\n'.join(posts_html)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reiyo's Tech Blog - AI, ML & Computer Vision</title>
    <meta name="description" content="Technical blog about Machine Learning, AI, Computer Vision, and Software Engineering by Reiyo">
    <meta name="keywords" content="Machine Learning, AI, Computer Vision, Deep Learning, Tech Blog">
    <link rel="stylesheet" href="assets/css/blog.css">
    <link rel="alternate" type="application/rss+xml" title="Reiyo's Blog RSS" href="feed.xml">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="index.html" class="nav-logo">🧠 Reiyo's Blog</a>
            <div class="nav-links">
                <a href="index.html" class="active">Blog</a>
                <a href="knowledge-graph.html">Projects</a>
                <a href="https://github.com/RyoK3N">GitHub</a>
                <a href="feed.xml">RSS</a>
            </div>
        </div>
    </nav>

    <header class="hero">
        <div class="hero-content">
            <h1 class="hero-title">Reiyo's Tech Blog</h1>
            <p class="hero-subtitle">
                Exploring Machine Learning, AI, Computer Vision, and the Future of Intelligent Systems
            </p>
            <div class="hero-stats">
                <div class="stat">
                    <span class="stat-number">{len(all_posts)}</span>
                    <span class="stat-label">Posts</span>
                </div>
                <div class="stat">
                    <span class="stat-number">{len(set(tag for post in all_posts for tag in post.get('tags', [])))}</span>
                    <span class="stat-label">Topics</span>
                </div>
                <div class="stat">
                    <span class="stat-number">∞</span>
                    <span class="stat-label">Ideas</span>
                </div>
            </div>
        </div>
    </header>

    <main class="container">
        <div class="posts-grid">
{posts_grid}
        </div>
    </main>

    <footer class="footer">
        <div class="footer-content">
            <p>&copy; {datetime.now().year} Reiyo. All rights reserved.</p>
            <div class="footer-links">
                <a href="https://github.com/RyoK3N">GitHub</a>
                <a href="https://linkedin.com/in/reiyo06">LinkedIn</a>
                <a href="https://oreiyo.space">Portfolio</a>
                <a href="feed.xml">RSS</a>
            </div>
        </div>
    </footer>

    <script src="assets/js/blog.js"></script>
</body>
</html>'''
    
    return html

def save_blog_history(new_post: Dict, all_posts: List[Dict]) -> None:
    """Save blog history"""
    
    history_file = DATA_DIR / "blog_history.json"
    
    history = {
        "posts": all_posts,
        "total_posts": len(all_posts),
        "last_updated": datetime.now().isoformat()
    }
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)

def main():
    """Main blog page generation"""
    try:
        print("📝 Generating blog pages...")
        
        # Load current post
        print("\n📚 Loading blog post...")
        blog_post = load_blog_post()
        
        # Create slug
        slug = slugify(blog_post['title'])
        blog_post['slug'] = slug
        
        print(f"   Title: {blog_post['title']}")
        print(f"   Slug: {slug}")
        
        # Load history
        all_posts = load_blog_history()
        
        # Check if this post already exists
        existing_slugs = [p['slug'] for p in all_posts]
        
        if slug not in existing_slugs:
            # Add to history
            all_posts.append({
                'title': blog_post['title'],
                'slug': slug,
                'excerpt': blog_post.get('excerpt', ''),
                'tags': blog_post.get('tags', []),
                'created_at': blog_post.get('created_at', datetime.now().isoformat()),
                'content': blog_post['content']
            })
            print(f"   ✅ Added to history (total: {len(all_posts)})")
        else:
            print(f"   ℹ️  Post already exists, updating...")
            # Update existing post
            for i, p in enumerate(all_posts):
                if p['slug'] == slug:
                    all_posts[i] = {
                        'title': blog_post['title'],
                        'slug': slug,
                        'excerpt': blog_post.get('excerpt', ''),
                        'tags': blog_post.get('tags', []),
                        'created_at': blog_post.get('created_at', datetime.now().isoformat()),
                        'content': blog_post['content']
                    }
        
        # Save history
        save_blog_history(blog_post, all_posts)
        
        # Generate individual post page
        print("\n📄 Generating individual post page...")
        post_html = create_blog_post_html(blog_post)
        
        post_file = BLOG_DIR / f"{slug}.html"
        with open(post_file, 'w', encoding='utf-8') as f:
            f.write(post_html)
        
        print(f"   ✅ Saved: {post_file}")
        
        # Generate blog index
        print("\n🏠 Generating blog homepage...")
        index_html = create_blog_index_html(all_posts)
        
        index_file = Path(__file__).parent.parent.parent / "docs" / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        print(f"   ✅ Saved: {index_file}")
        
        # Summary
        print("\n" + "="*60)
        print("📝 BLOG PAGES GENERATED")
        print("="*60)
        print(f"Post URL: blog/{slug}.html")
        print(f"Total Posts: {len(all_posts)}")
        print(f"Blog Index: index.html")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
