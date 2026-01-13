#!/usr/bin/env python3
"""
AI Agent - Project Categorization
Uses AI to intelligently categorize repositories
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from huggingface_hub import InferenceClient
import time

DATA_DIR = Path(__file__).parent / "data"

MODELS = [
    "meta-llama/Llama-3.2-3B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "microsoft/Phi-3-mini-4k-instruct",
]

CATEGORY_DEFINITIONS = {
    "Machine Learning": ["ML", "neural networks", "deep learning", "AI", "tensorflow", "pytorch"],
    "Computer Vision": ["CV", "image", "video", "pose estimation", "object detection"],
    "Natural Language Processing": ["NLP", "text", "language", "transformers", "LLM"],
    "Data Science": ["data analysis", "visualization", "pandas", "jupyter", "statistics"],
    "Web Development": ["web", "frontend", "backend", "API", "REST", "GraphQL"],
    "DevOps": ["docker", "kubernetes", "CI/CD", "deployment", "automation"],
    "Mobile Development": ["android", "iOS", "mobile", "app", "react native"],
    "3D Graphics": ["3D", "openGL", "graphics", "rendering", "visualization"],
    "Robotics": ["robot", "ROS", "control", "sensors", "arduino"],
    "Reinforcement Learning": ["RL", "agent", "policy", "reward", "Q-learning"],
    "Research": ["paper", "publication", "experimental", "research", "academic"],
    "Tools & Utilities": ["tool", "utility", "helper", "library", "framework"],
}

def load_analysis() -> Dict[str, Any]:
    """Load repository analysis"""
    analysis_file = DATA_DIR / "repository_analysis.json"
    with open(analysis_file, 'r') as f:
        return json.load(f)

def query_ai_for_categorization(client: InferenceClient, repo_data: Dict) -> List[str]:
    """Use AI to categorize a repository"""
    
    # Build prompt with repository information
    repo_info = f"""Repository: {repo_data['name']}
Description: {repo_data['description']}
Languages: {', '.join(repo_data['languages'].keys())}
Topics: {', '.join(repo_data['topics'])}
README excerpt: {repo_data['readme_content'][:500]}"""
    
    available_categories = ', '.join(CATEGORY_DEFINITIONS.keys())
    
    prompt = f"""Analyze this software repository and assign it to 1-3 relevant categories.

{repo_info}

Available categories: {available_categories}

Task: Return ONLY a comma-separated list of categories (max 3). No explanation.
Example output: Machine Learning, Computer Vision"""

    for model in MODELS:
        try:
            print(f"   Querying {model.split('/')[-1]}...")
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.3,
            )
            
            if response and response.choices:
                content = response.choices[0].message.content.strip()
                
                # Parse categories
                categories = [c.strip() for c in content.split(',')]
                categories = [c for c in categories if c in CATEGORY_DEFINITIONS]
                
                if categories:
                    print(f"   ✅ Categorized: {', '.join(categories)}")
                    return categories[:3]  # Max 3 categories
                    
        except Exception as e:
            if "503" in str(e) or "loading" in str(e).lower():
                time.sleep(10)
                continue
            print(f"   Error with {model}: {str(e)[:100]}")
    
    # Fallback: simple keyword matching
    return fallback_categorization(repo_data)

def fallback_categorization(repo_data: Dict) -> List[str]:
    """Fallback categorization using keywords"""
    text = f"{repo_data['description']} {' '.join(repo_data['topics'])} {repo_data['readme_content']}"
    text = text.lower()
    
    category_scores = {}
    for category, keywords in CATEGORY_DEFINITIONS.items():
        score = sum(1 for keyword in keywords if keyword.lower() in text)
        if score > 0:
            category_scores[category] = score
    
    # Return top 2 categories
    sorted_cats = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    return [cat for cat, _ in sorted_cats[:2]]

def categorize_all_repositories(repos: List[Dict]) -> Dict[str, Any]:
    """Categorize all repositories"""
    print("\n🧠 Categorizing repositories with AI...")
    
    api_key = os.getenv("HF_API_KEY") or os.getenv("HF_TOKEN")
    if not api_key:
        print("⚠️  No HF API key, using fallback categorization")
        client = None
    else:
        client = InferenceClient(token=api_key)
    
    categorized = []
    category_counts = {}
    
    for i, repo in enumerate(repos, 1):
        print(f"\n📂 {i}/{len(repos)}: {repo['name']}")
        
        if client:
            categories = query_ai_for_categorization(client, repo)
        else:
            categories = fallback_categorization(repo)
        
        if not categories:
            categories = ["Uncategorized"]
        
        categorized.append({
            "name": repo["name"],
            "description": repo["description"],
            "categories": categories,
            "languages": list(repo["languages"].keys()),
            "topics": repo["topics"],
            "stars": repo["stars"],
            "url": repo["url"],
        })
        
        # Count categories
        for cat in categories:
            category_counts[cat] = category_counts.get(cat, 0) + 1
    
    return {
        "categorized_repositories": categorized,
        "category_statistics": category_counts,
        "total_repositories": len(categorized),
        "timestamp": json.dumps({"iso": "now"})
    }

def main():
    """Main categorization function"""
    try:
        print("🎯 Starting project categorization...")
        
        # Load analysis
        data = load_analysis()
        repos = data.get("all_repositories", [])
        
        if not repos:
            print("❌ No repositories found in analysis")
            return
        
        print(f"📚 Found {len(repos)} repositories to categorize")
        
        # Categorize
        results = categorize_all_repositories(repos)
        
        # Save results
        output_file = DATA_DIR / "project_categories.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Categorization complete!")
        print(f"💾 Saved to {output_file}")
        
        # Print summary
        print("\n📊 Category Distribution:")
        for cat, count in sorted(results["category_statistics"].items(), 
                                 key=lambda x: x[1], reverse=True):
            print(f"   • {cat}: {count} projects")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
