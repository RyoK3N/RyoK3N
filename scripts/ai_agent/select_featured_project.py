#!/usr/bin/env python3
"""
AI Agent - Featured Project of the Week Selector
AI-powered selection and description of featured project
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
from huggingface_hub import InferenceClient
import random
import time

DATA_DIR = Path(__file__).parent / "data"

MODELS = [
    "meta-llama/Llama-3.2-3B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "microsoft/Phi-3-mini-4k-instruct",
]

def load_data() -> tuple:
    """Load categorized projects and previous selections"""
    categories_file = DATA_DIR / "project_categories.json"
    featured_file = DATA_DIR / "featured_project.json"
    
    with open(categories_file, 'r') as f:
        categories = json.load(f)
    
    previous = None
    if featured_file.exists():
        with open(featured_file, 'r') as f:
            previous = json.load(f)
    
    return categories, previous

def select_project_candidate(repos: list, previous: Optional[Dict]) -> Dict:
    """Select a project candidate using smart algorithm"""
    
    # Filter out previously featured (within last 4 weeks)
    candidates = repos.copy()
    
    if previous:
        try:
            last_date = datetime.fromisoformat(previous.get("selected_date", ""))
            weeks_ago = (datetime.now() - last_date).days / 7
            
            if weeks_ago < 4:
                last_name = previous.get("name")
                candidates = [r for r in candidates if r["name"] != last_name]
        except:
            pass
    
    if not candidates:
        candidates = repos
    
    # Scoring algorithm
    scored = []
    for repo in candidates:
        score = 0
        
        # Stars (up to 50 points)
        score += min(50, repo["stars"] * 2)
        
        # Multiple categories (10 points each)
        score += len(repo["categories"]) * 10
        
        # Has description (20 points)
        if repo["description"]:
            score += 20
        
        # Interesting categories (bonus points)
        interesting = ["Machine Learning", "Computer Vision", "Reinforcement Learning", "Research"]
        if any(cat in repo["categories"] for cat in interesting):
            score += 30
        
        # Add some randomness
        score += random.randint(0, 20)
        
        scored.append((repo, score))
    
    # Sort and select top candidate
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[0][0]

def generate_ai_description(client: InferenceClient, repo: Dict) -> str:
    """Generate AI-powered project description"""
    
    prompt = f"""Write an engaging, professional description for this software project.

Project: {repo['name']}
Description: {repo['description']}
Categories: {', '.join(repo['categories'])}
Languages: {', '.join(repo['languages'])}
Stars: {repo['stars']}

Task: Write a compelling 3-4 sentence description that:
1. Explains what makes this project special
2. Highlights its technical innovation
3. Mentions potential applications or impact

Write in an exciting, professional tone. No bullet points or headers."""

    for model in MODELS:
        try:
            print(f"   🤖 Querying {model.split('/')[-1]}...")
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.8,
            )
            
            if response and response.choices:
                content = response.choices[0].message.content.strip()
                
                if len(content) > 100:
                    print(f"   ✅ Generated description ({len(content)} chars)")
                    return content
                    
        except Exception as e:
            if "503" in str(e) or "loading" in str(e).lower():
                time.sleep(10)
                continue
            print(f"   ⚠️ Error with {model}: {str(e)[:100]}")
    
    # Fallback description
    return generate_fallback_description(repo)

def generate_fallback_description(repo: Dict) -> str:
    """Generate fallback description"""
    categories = ' and '.join(repo['categories'][:2])
    langs = ', '.join(repo['languages'][:2])
    
    templates = [
        f"{repo['name']} is an innovative {categories} project built with {langs}. {repo['description']} This project demonstrates cutting-edge techniques and has attracted {repo['stars']} stars from the developer community, showcasing its value and impact.",
        
        f"Exploring the intersection of {categories}, {repo['name']} leverages {langs} to deliver powerful solutions. {repo['description']} With {repo['stars']} stars, it represents a significant contribution to the open-source ecosystem.",
        
        f"A standout {categories} project, {repo['name']} utilizes {langs} for maximum performance and flexibility. {repo['description']} The {repo['stars']} stars it has received reflect its quality and usefulness to developers worldwide.",
    ]
    
    return random.choice(templates)

def generate_why_featured(client: InferenceClient, repo: Dict) -> str:
    """Generate 'Why Featured' explanation"""
    
    prompt = f"""Explain in 1-2 sentences why this project deserves to be featured this week.

Project: {repo['name']}
Categories: {', '.join(repo['categories'])}
Stars: {repo['stars']}
Description: {repo['description']}

Be specific and enthusiastic. Mention technical innovation or practical value."""

    for model in MODELS[:2]:  # Try first 2 models only
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7,
            )
            
            if response and response.choices:
                content = response.choices[0].message.content.strip()
                if len(content) > 50:
                    return content
                    
        except:
            continue
    
    # Fallback
    reasons = [
        f"This project stands out for its innovative approach to {repo['categories'][0]} and has garnered {repo['stars']} stars from the community.",
        f"Combining cutting-edge {' and '.join(repo['categories'][:2])}, this project represents the future of software development.",
        f"With {repo['stars']} stars and active development, this project demonstrates both technical excellence and practical utility.",
    ]
    return random.choice(reasons)

def main():
    """Main featured project selection"""
    try:
        print("⭐ Starting Featured Project selection...")
        
        # Load data
        print("\n📚 Loading project data...")
        categories_data, previous = load_data()
        repos = categories_data["categorized_repositories"]
        
        print(f"   Found {len(repos)} projects")
        
        # Select candidate
        print("\n🎯 Selecting project candidate...")
        selected = select_project_candidate(repos, previous)
        print(f"   ✅ Selected: {selected['name']}")
        
        # Initialize AI client
        api_key = os.getenv("HF_API_KEY") or os.getenv("HF_TOKEN")
        if not api_key:
            print("⚠️  No HF API key, using fallback descriptions")
            client = None
        else:
            client = InferenceClient(token=api_key)
        
        # Generate descriptions
        print("\n✍️  Generating AI-powered descriptions...")
        
        if client:
            description = generate_ai_description(client, selected)
            why_featured = generate_why_featured(client, selected)
        else:
            description = generate_fallback_description(selected)
            why_featured = f"Featured for its excellence in {selected['categories'][0]} and {selected['stars']} community stars."
        
        # Calculate week number
        week_num = datetime.now().isocalendar()[1]
        
        # Compile featured project data
        featured_data = {
            "name": selected["name"],
            "description": selected["description"],
            "ai_description": description,
            "why_featured": why_featured,
            "categories": selected["categories"],
            "languages": selected["languages"],
            "stars": selected["stars"],
            "url": selected["url"],
            "selected_date": datetime.now().isoformat(),
            "week_number": week_num,
            "year": datetime.now().year,
        }
        
        # Save
        output_file = DATA_DIR / "featured_project.json"
        with open(output_file, 'w') as f:
            json.dump(featured_data, f, indent=2)
        
        print(f"\n✅ Featured project selected!")
        print(f"💾 Saved to {output_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("⭐ FEATURED PROJECT OF THE WEEK")
        print("="*60)
        print(f"📦 Project: {featured_data['name']}")
        print(f"🏷️  Categories: {', '.join(featured_data['categories'])}")
        print(f"⭐ Stars: {featured_data['stars']}")
        print(f"\n📝 AI Description:")
        print(f"{description[:200]}...")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
