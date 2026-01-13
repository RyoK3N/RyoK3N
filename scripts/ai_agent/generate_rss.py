#!/usr/bin/env python3
"""
AI Agent - RSS Feed Generator
Generates RSS feed for blog posts
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import html

DATA_DIR = Path(__file__).parent / "data"
DOCS_DIR = Path(__file__).parent.parent.parent / "docs"

def load_blog_history() -> List[Dict]:
    """Load blog history"""
    history_file = DATA_DIR / "blog_history.json"
    
    if history_file.exists():
        with open(history_file, 'r') as f:
            return json.load(f).get('posts', [])
    
    return []

def format_rfc822(iso_date: str) -> str:
    """Convert ISO date to RFC 822 format"""
    try:
        dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
        return dt.strftime('%a, %d %b %Y %H:%M:%S %z')
    except:
        return datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

def escape_html(text: str) -> str:
    """Escape HTML special characters"""
    return html.escape(text)

def truncate_content(content: str, max_words: int = 100) -> str:
    """Truncate content to specified word count"""
    words = content.split()
    if len(words) <= max_words:
        return content
    return ' '.join(words[:max_words]) + '...'

def generate_rss_feed(posts: List[Dict]) -> str:
    """Generate RSS 2.0 feed"""
    
    # Sort posts by date (newest first)
    sorted_posts = sorted(
        posts,
        key=lambda x: x.get('created_at', ''),
        reverse=True
    )[:10]  # Latest 10 posts
    
    # Generate items
    items = []
    for post in sorted_posts:
        # Prepare content
        description = escape_html(post.get('excerpt', truncate_content(post.get('content', ''))))
        content_escaped = escape_html(post.get('content', ''))
        
        # Categories (tags)
        categories = '\n'.join([
            f'        <category>{escape_html(tag)}</category>'
            for tag in post.get('tags', [])
        ])
        
        item = f'''    <item>
        <title>{escape_html(post['title'])}</title>
        <link>https://ryok3n.github.io/RyoK3N/blog/{post['slug']}.html</link>
        <guid isPermaLink="true">https://ryok3n.github.io/RyoK3N/blog/{post['slug']}.html</guid>
        <pubDate>{format_rfc822(post.get('created_at', ''))}</pubDate>
        <description><![CDATA[{description}]]></description>
        <content:encoded><![CDATA[{content_escaped}]]></content:encoded>
        <author>reiyo1113@gmail.com (Reiyo)</author>
{categories}
    </item>'''
        
        items.append(item)
    
    items_xml = '\n\n'.join(items)
    
    # Build RSS feed
    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" 
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Reiyo's Tech Blog</title>
    <link>https://ryok3n.github.io/RyoK3N/</link>
    <description>Technical blog about Machine Learning, AI, Computer Vision, and Software Engineering</description>
    <language>en-us</language>
    <lastBuildDate>{format_rfc822(datetime.now().isoformat())}</lastBuildDate>
    <atom:link href="https://ryok3n.github.io/RyoK3N/feed.xml" rel="self" type="application/rss+xml" />
    <generator>AI Blog Generator</generator>
    <image>
      <url>https://github.com/RyoK3N.png</url>
      <title>Reiyo's Tech Blog</title>
      <link>https://ryok3n.github.io/RyoK3N/</link>
    </image>
    <webMaster>reiyo1113@gmail.com (Reiyo)</webMaster>
    <copyright>Copyright {datetime.now().year} Reiyo</copyright>
    
{items_xml}
    
  </channel>
</rss>'''
    
    return rss

def main():
    """Main RSS generation"""
    try:
        print("📡 Generating RSS feed...")
        
        # Load posts
        posts = load_blog_history()
        
        if not posts:
            print("⚠️  No posts found, skipping RSS generation")
            return
        
        print(f"   Found {len(posts)} posts")
        
        # Generate RSS
        rss_content = generate_rss_feed(posts)
        
        # Save
        rss_file = DOCS_DIR / "feed.xml"
        with open(rss_file, 'w', encoding='utf-8') as f:
            f.write(rss_content)
        
        print(f"✅ RSS feed generated!")
        print(f"💾 Saved to: {rss_file}")
        print(f"🔗 URL: https://ryok3n.github.io/RyoK3N/feed.xml")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
