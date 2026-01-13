#!/usr/bin/env python3
"""
AI Agent - Ghost CMS Publisher
Publishes blog posts to Ghost CMS using Admin API
"""

import os
import json
import jwt
from datetime import datetime as dt
from pathlib import Path
from typing import Dict, Any
import requests

DATA_DIR = Path(__file__).parent / "data"

# Ghost API Configuration
GHOST_API_URL = "https://synexian.ghost.io"
GHOST_ADMIN_API_VERSION = "v5.0"

def load_blog_post() -> Dict[str, Any]:
    """Load generated blog post"""
    blog_file = DATA_DIR / "blog_post.json"
    
    if not blog_file.exists():
        raise FileNotFoundError("No blog post found. Run generate_blog.py first.")
    
    with open(blog_file, 'r') as f:
        return json.load(f)

def generate_ghost_jwt(admin_api_key: str) -> str:
    """Generate JWT token for Ghost Admin API"""
    
    try:
        # Split the key into ID and SECRET
        id_part, secret_part = admin_api_key.split(':')
        
        # Prepare header and payload
        iat = int(dt.now().timestamp())
        
        header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id_part}
        payload = {
            'iat': iat,
            'exp': iat + 5 * 60,  # Token expires in 5 minutes
            'aud': '/admin/'
        }
        
        # Create token - decode if it returns bytes
        token = jwt.encode(
            payload, 
            bytes.fromhex(secret_part), 
            algorithm='HS256', 
            headers=header
        )
        
        # Handle both string and bytes return
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        
        return token
        
    except Exception as e:
        print(f"❌ Error generating JWT: {e}")
        raise ValueError(f"Invalid Ghost Admin API key format: {e}")

def convert_to_html(content: str) -> str:
    """Convert plain text content to simple HTML"""
    
    # Split into paragraphs
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    # Convert to HTML paragraphs
    html_parts = [f"<p>{para}</p>" for para in paragraphs]
    
    return '\n'.join(html_parts)

def convert_to_mobiledoc(content: str) -> str:
    """Convert content to Ghost's mobiledoc format"""
    
    # Convert to HTML first
    html_content = convert_to_html(content)
    
    # Build mobiledoc structure
    mobiledoc = {
        "version": "0.3.1",
        "atoms": [],
        "cards": [
            ["html", {"cardName": "html", "html": html_content}]
        ],
        "markups": [],
        "sections": [[10, 0]]
    }
    
    return json.dumps(mobiledoc)

def create_ghost_post(blog_post: Dict, token: str) -> Dict:
    """Create a post in Ghost CMS"""
    
    # Prepare API endpoint
    api_url = f"{GHOST_API_URL}/ghost/api/{GHOST_ADMIN_API_VERSION}/admin/posts/"
    
    # Convert content to mobiledoc
    mobiledoc_str = convert_to_mobiledoc(blog_post['content'])
    
    # Prepare post data
    post_data = {
        "posts": [{
            "title": blog_post['title'],
            "mobiledoc": mobiledoc_str,
            "status": "published",
            "tags": [{"name": tag} for tag in blog_post.get('tags', [])],
            "custom_excerpt": blog_post.get('excerpt', '')[:300],  # Max 300 chars
            "published_at": dt.now().isoformat(),
            "meta_title": blog_post['title'][:300],
            "meta_description": blog_post.get('excerpt', '')[:500],
        }]
    }
    
    # Make request
    headers = {
        'Authorization': f'Ghost {token}',
        'Content-Type': 'application/json',
        'Accept-Version': GHOST_ADMIN_API_VERSION
    }
    
    print(f"📤 Publishing to Ghost CMS...")
    print(f"   URL: {api_url}")
    print(f"   Title: {blog_post['title']}")
    
    try:
        response = requests.post(
            api_url,
            json=post_data,
            headers=headers,
            timeout=30
        )
        
        # Check for errors
        if response.status_code not in [200, 201]:
            print(f"❌ Ghost API Error: {response.status_code}")
            print(f"Response: {response.text}")
            response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response text: {e.response.text}")
        raise

def save_publication_record(blog_post: Dict, ghost_response: Dict) -> None:
    """Save publication record"""
    
    # Extract post info from response
    published_post = ghost_response.get('posts', [{}])[0]
    
    record = {
        "published_at": dt.now().isoformat(),
        "blog_title": blog_post['title'],
        "ghost_id": published_post.get('id', ''),
        "ghost_url": published_post.get('url', ''),
        "tags": blog_post.get('tags', []),
        "excerpt": blog_post.get('excerpt', ''),
        "status": "published"
    }
    
    # Load existing records
    records_file = DATA_DIR / "publication_history.json"
    
    if records_file.exists():
        with open(records_file, 'r') as f:
            history = json.load(f)
    else:
        history = {"publications": []}
    
    history["publications"].append(record)
    history["total_published"] = len(history["publications"])
    history["last_published"] = dt.now().isoformat()
    
    # Save
    with open(records_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"📝 Publication record saved")

def verify_ghost_credentials(admin_api_key: str) -> bool:
    """Verify Ghost credentials are valid"""
    
    try:
        # Generate token
        token = generate_ghost_jwt(admin_api_key)
        
        # Try to fetch site info
        api_url = f"{GHOST_API_URL}/ghost/api/{GHOST_ADMIN_API_VERSION}/admin/site/"
        
        headers = {
            'Authorization': f'Ghost {token}',
            'Accept-Version': GHOST_ADMIN_API_VERSION
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Ghost credentials verified")
            return True
        else:
            print(f"⚠️  Ghost credential verification failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not verify Ghost credentials: {e}")
        return False

def main():
    """Main Ghost publishing function"""
    try:
        print("🚀 Starting Ghost CMS publication...")
        
        # Get Admin API key from environment
        admin_api_key = os.getenv("GHOST_ADMIN_API_KEY")
        
        if not admin_api_key:
            raise ValueError("GHOST_ADMIN_API_KEY environment variable not set")
        
        print("✅ Admin API key found")
        
        # Verify credentials first
        print("\n🔐 Verifying Ghost credentials...")
        if not verify_ghost_credentials(admin_api_key):
            print("⚠️  Continuing anyway...")
        
        # Load blog post
        print("\n📚 Loading generated blog post...")
        blog_post = load_blog_post()
        print(f"   Title: {blog_post['title']}")
        print(f"   Length: {len(blog_post['content'])} characters")
        print(f"   Tags: {', '.join(blog_post.get('tags', []))}")
        
        # Generate JWT token
        print("\n🔐 Generating authentication token...")
        token = generate_ghost_jwt(admin_api_key)
        print("   ✅ Token generated")
        
        # Publish to Ghost
        print("\n📤 Publishing to Ghost CMS...")
        ghost_response = create_ghost_post(blog_post, token)
        
        # Extract post info
        published_post = ghost_response.get('posts', [{}])[0]
        post_url = published_post.get('url', GHOST_API_URL)
        post_id = published_post.get('id', 'N/A')
        
        print(f"\n✅ Successfully published to Ghost!")
        print(f"   Post ID: {post_id}")
        print(f"   URL: {post_url}")
        
        # Save publication record
        save_publication_record(blog_post, ghost_response)
        
        # Print summary
        print("\n" + "="*60)
        print("📝 PUBLICATION SUMMARY")
        print("="*60)
        print(f"Title: {blog_post['title']}")
        print(f"Published: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"URL: {post_url}")
        print(f"Status: Published ✅")
        print("="*60)
        
        # Update blog post file with publication info
        blog_post['published'] = True
        blog_post['published_at'] = dt.now().isoformat()
        blog_post['ghost_url'] = post_url
        blog_post['ghost_id'] = post_id
        
        blog_file = DATA_DIR / "blog_post.json"
        with open(blog_file, 'w') as f:
            json.dump(blog_post, f, indent=2)
        
        print(f"💾 Updated blog post file with publication info")
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        raise
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
