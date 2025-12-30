#!/usr/bin/env python3
"""
AI Agent - Insights Generation Module
Uses Hugging Face API to generate intelligent insights from repository analysis.
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Configuration
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Hugging Face API Configuration
HF_API_URL = "https://api-inference.huggingface.co/models/"
HF_MODELS = {
    "llama": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "mixtral": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "qwen": "Qwen/Qwen2.5-72B-Instruct"
}

def load_analysis_data() -> Dict[str, Any]:
    """Load the repository analysis data."""
    analysis_file = DATA_DIR / "repository_analysis.json"
    
    if not analysis_file.exists():
        raise FileNotFoundError(f"Analysis file not found: {analysis_file}")
    
    with open(analysis_file, 'r') as f:
        return json.load(f)

def query_huggingface_api(
    prompt: str,
    model: str = "llama",
    max_tokens: int = 500,
    temperature: float = 0.7
) -> Optional[str]:
    """Query Hugging Face Inference API."""
    api_key = os.getenv("HF_API_KEY")
    if not api_key:
        raise ValueError("HF_API_KEY environment variable not set")
    
    model_url = HF_API_URL + HF_MODELS[model]
    headers = {"Authorization": f"Bearer {api_key}"}
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.95,
            "return_full_text": False
        }
    }
    
    try:
        print(f"🧠 Querying {model} model...")
        response = requests.post(model_url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").strip()
            elif isinstance(result, dict):
                return result.get("generated_text", "").strip()
            return str(result)
        else:
            print(f"⚠️  API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error querying API: {e}")
        return None

def create_analysis_prompt(data: Dict[str, Any]) -> str:
    """Create a structured prompt for the LLM."""
    commits = data["commits"]
    prs = data["pull_requests"]
    issues = data["issues"]
    code = data["code"]
    
    prompt = f"""You are an expert software development analyst. Analyze the following repository activity and provide insightful observations.

Repository Activity (Last 7 Days):

COMMITS:
- Total: {commits['total_commits']}
- Daily Average: {commits['daily_average']:.1f}
- Top Contributor: {commits['top_author']}
- Recent Messages: {', '.join(commits['commit_messages'][:5])}

PULL REQUESTS:
- Recent PRs: {prs['total_recent']}
- Merged: {prs['merged']}
- Open: {prs['open']}
- Avg Merge Time: {prs['avg_merge_time_hours']:.1f} hours

ISSUES:
- Recent Issues: {issues['total_recent']}
- Open: {issues['open']}
- Closed: {issues['closed']}

CODE:
- Primary Language: {code['primary_language']}
- Language Distribution: {', '.join([f'{k} ({v}%)' for k, v in list(code['languages'].items())[:3]])}

TASK: Provide a concise, insightful analysis (3-4 sentences) that:
1. Summarizes the development focus and activity level
2. Identifies key trends or patterns
3. Provides one constructive suggestion for improvement

Format your response as a natural paragraph without bullet points."""

    return prompt

def create_recommendation_prompt(data: Dict[str, Any]) -> str:
    """Create a prompt specifically for recommendations."""
    commits = data["commits"]
    code = data["code"]
    
    prompt = f"""As a software engineering advisor, provide 3 specific, actionable recommendations for this repository.

Current State:
- Commit frequency: {commits['daily_average']:.1f} per day
- Primary language: {code['primary_language']}
- Recent work: {', '.join(commits['commit_messages'][:3])}

Provide exactly 3 brief recommendations (one line each) that would improve code quality, development workflow, or project organization. Format as:
1. [First recommendation]
2. [Second recommendation]
3. [Third recommendation]"""

    return prompt

def create_prediction_prompt(data: Dict[str, Any]) -> str:
    """Create a prompt for predicting next week's focus."""
    commits = data["commits"]
    prs = data["pull_requests"]
    
    prompt = f"""Based on recent development patterns, predict the likely focus areas for next week.

Recent Activity:
- Commits: {commits['total_commits']} in the last week
- Merged PRs: {', '.join(prs['merged_titles'][:3]) if prs['merged_titles'] else 'None'}
- Recent work: {', '.join(commits['commit_messages'][:5])}

Predict 3 likely development focus areas for next week. Keep predictions realistic and specific. Format as:
1. [First prediction]
2. [Second prediction]
3. [Third prediction]"""

    return prompt

def generate_insights(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate AI insights from analysis data."""
    print("🤖 Generating AI insights...")
    
    insights = {
        "timestamp": datetime.now().isoformat(),
        "model_used": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "analysis": None,
        "recommendations": None,
        "predictions": None,
    }
    
    # Generate main analysis
    analysis_prompt = create_analysis_prompt(data)
    insights["analysis"] = query_huggingface_api(
        analysis_prompt,
        model="llama",
        max_tokens=300,
        temperature=0.7
    )
    
    if not insights["analysis"]:
        insights["analysis"] = "Unable to generate analysis at this time. Please check the logs."
    
    # Generate recommendations
    rec_prompt = create_recommendation_prompt(data)
    insights["recommendations"] = query_huggingface_api(
        rec_prompt,
        model="llama",
        max_tokens=200,
        temperature=0.7
    )
    
    if not insights["recommendations"]:
        insights["recommendations"] = "1. Continue current development pace\n2. Maintain code quality standards\n3. Regular documentation updates"
    
    # Generate predictions
    pred_prompt = create_prediction_prompt(data)
    insights["predictions"] = query_huggingface_api(
        pred_prompt,
        model="llama",
        max_tokens=200,
        temperature=0.8
    )
    
    if not insights["predictions"]:
        insights["predictions"] = "1. Continuation of current project work\n2. Bug fixes and optimizations\n3. Documentation improvements"
    
    return insights

def main():
    """Main insights generation function."""
    try:
        print("🤖 Starting AI insights generation...")
        
        # Load analysis data
        print("📊 Loading repository analysis...")
        data = load_analysis_data()
        
        # Generate insights
        insights = generate_insights(data)
        
        # Save insights
        output_file = DATA_DIR / "ai_insights.json"
        with open(output_file, 'w') as f:
            json.dump(insights, f, indent=2)
        
        print(f"✅ Insights generated! Saved to {output_file}")
        
        # Print summary
        print("\n📋 Generated Insights:")
        print(f"\n💡 Analysis:\n{insights['analysis']}")
        print(f"\n🎯 Recommendations:\n{insights['recommendations']}")
        print(f"\n🔮 Predictions:\n{insights['predictions']}")
        
    except Exception as e:
        print(f"❌ Error generating insights: {e}")
        raise

if __name__ == "__main__":
    main()
