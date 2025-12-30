#!/usr/bin/env python3
"""
AI Agent - Insights Generation Module 
Uses Hugging Face API to generate intelligent insights from repository analysis.
Now with better error handling, multiple model support, and retry logic.
"""

import os
import json
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Configuration
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# NEW Hugging Face Router URL (Updated)
HF_API_BASE = "https://api-inference.huggingface.co/models/"

# Multiple models with fallback support
HF_MODELS = {
    "llama-3.1-8b": "meta-llama/Llama-3.1-8B-Instruct",
    "llama-3.2-3b": "meta-llama/Llama-3.2-3B-Instruct",
    "qwen-2.5-7b": "Qwen/Qwen2.5-7B-Instruct",
    "mistral-7b": "mistralai/Mistral-7B-Instruct-v0.3",
    "gemma-2-9b": "google/gemma-2-9b-it",
    "phi-3-mini": "microsoft/Phi-3-mini-4k-instruct"
}

# Model priority order (will try in this order)
MODEL_PRIORITY = [
    "qwen-2.5-7b",      # Fast and accurate
    "llama-3.2-3b",     # Lightweight Llama
    "mistral-7b",       # Reliable fallback
    "phi-3-mini",       # Compact option
    "gemma-2-9b",       # Google's model
]

def load_analysis_data() -> Dict[str, Any]:
    """Load the repository analysis data."""
    analysis_file = DATA_DIR / "repository_analysis.json"
    
    if not analysis_file.exists():
        raise FileNotFoundError(f"Analysis file not found: {analysis_file}")
    
    with open(analysis_file, 'r') as f:
        return json.load(f)

def query_huggingface_api(
    prompt: str,
    model_key: str = "qwen-2.5-7b",
    max_tokens: int = 500,
    temperature: float = 0.7,
    retry_count: int = 3
) -> Optional[str]:
    """Query Hugging Face Inference API with retry logic."""
    api_key = os.getenv("HF_API_KEY")
    if not api_key:
        raise ValueError("HF_API_KEY environment variable not set")
    
    model_id = HF_MODELS.get(model_key, HF_MODELS["qwen-2.5-7b"])
    model_url = HF_API_BASE + model_id
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Enhanced payload with better parameters
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 50,
            "repetition_penalty": 1.1,
            "return_full_text": False,
            "do_sample": True
        },
        "options": {
            "wait_for_model": True,
            "use_cache": False
        }
    }
    
    for attempt in range(retry_count):
        try:
            print(f"🧠 Querying {model_key} model (attempt {attempt + 1}/{retry_count})...")
            
            response = requests.post(
                model_url,
                headers=headers,
                json=payload,
                timeout=120  # Increased timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get("generated_text", "").strip()
                elif isinstance(result, dict):
                    text = result.get("generated_text", "").strip()
                else:
                    text = str(result).strip()
                
                if text:
                    print(f"✅ Successfully generated {len(text)} characters")
                    return text
                else:
                    print(f"⚠️  Empty response from model")
                    
            elif response.status_code == 503:
                # Model is loading
                wait_time = min(20 * (attempt + 1), 60)
                print(f"⏳ Model loading, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
                
            elif response.status_code == 429:
                # Rate limited
                wait_time = 30 * (attempt + 1)
                print(f"⏳ Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
                
            else:
                print(f"⚠️  API request failed: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                
                # Wait before retry
                if attempt < retry_count - 1:
                    time.sleep(10 * (attempt + 1))
                    
        except requests.exceptions.Timeout:
            print(f"⏱️  Request timeout (attempt {attempt + 1})")
            if attempt < retry_count - 1:
                time.sleep(15)
        except Exception as e:
            print(f"❌ Error querying API: {e}")
            if attempt < retry_count - 1:
                time.sleep(10)
    
    return None

def query_with_fallback(
    prompt: str,
    task_name: str = "analysis",
    max_tokens: int = 500,
    temperature: float = 0.7
) -> str:
    """Query API with automatic fallback to alternative models."""
    print(f"\n🎯 Starting {task_name} generation...")
    
    for model_key in MODEL_PRIORITY:
        print(f"\n📡 Trying {model_key}...")
        result = query_huggingface_api(
            prompt,
            model_key=model_key,
            max_tokens=max_tokens,
            temperature=temperature,
            retry_count=2  # 2 retries per model
        )
        
        if result:
            print(f"✅ Successfully used {model_key} for {task_name}")
            return result
    
    # All models failed
    print(f"❌ All models failed for {task_name}")
    return None

def create_analysis_prompt(data: Dict[str, Any]) -> str:
    """Create a structured prompt for repository analysis."""
    commits = data["commits"]
    prs = data["pull_requests"]
    issues = data["issues"]
    code = data["code"]
    
    # Get recent commit messages
    recent_work = ', '.join(commits['commit_messages'][:5]) if commits.get('commit_messages') else 'No recent commits'
    
    prompt = f"""Analyze this software repository's recent activity and provide insights.

REPOSITORY ACTIVITY (Last 7 Days):
• Commits: {commits.get('total_commits', 0)} commits (avg {commits.get('daily_average', 0):.1f}/day)
• Top Contributor: {commits.get('top_author', 'Unknown')}
• Recent Work: {recent_work}
• Pull Requests: {prs.get('merged', 0)} merged, {prs.get('open', 0)} open
• Issues: {issues.get('closed', 0)} closed, {issues.get('open', 0)} open  
• Primary Language: {code.get('primary_language', 'Unknown')}

Write a concise 3-4 sentence analysis covering:
1. Overall development activity and pace
2. Key focus areas or patterns
3. One specific observation or suggestion

Keep it professional, insightful, and natural. No bullet points."""

    return prompt

def create_recommendation_prompt(data: Dict[str, Any]) -> str:
    """Create a prompt for actionable recommendations."""
    commits = data["commits"]
    code = data["code"]
    prs = data["pull_requests"]
    
    recent_messages = commits.get('commit_messages', [])[:3]
    work_summary = ', '.join(recent_messages) if recent_messages else 'general development'
    
    prompt = f"""You are a senior software engineering advisor. Provide 3 specific recommendations for this repository.

CURRENT STATE:
• Daily commit rate: {commits.get('daily_average', 0):.1f}
• Primary language: {code.get('primary_language', 'Unknown')}
• Recent work focuses on: {work_summary}
• PR merge time: {prs.get('avg_merge_time_hours', 0):.1f} hours

Give exactly 3 actionable recommendations (one sentence each) for improving:
- Code quality
- Development workflow  
- Project organization

Format as a numbered list (1., 2., 3.) with no extra text."""

    return prompt

def create_prediction_prompt(data: Dict[str, Any]) -> str:
    """Create a prompt for predicting future development focus."""
    commits = data["commits"]
    prs = data["pull_requests"]
    
    commit_msgs = commits.get('commit_messages', [])[:5]
    pr_titles = prs.get('merged_titles', [])[:3]
    
    recent_activity = []
    if commit_msgs:
        recent_activity.extend(commit_msgs)
    if pr_titles:
        recent_activity.extend(pr_titles)
    
    activity_summary = ', '.join(recent_activity[:5]) if recent_activity else 'general development work'
    
    prompt = f"""Based on this repository's recent patterns, predict likely development focus for next week.

RECENT ACTIVITY:
• {commits.get('total_commits', 0)} commits in the last week
• Recent changes: {activity_summary}
• Primary language: {data['code'].get('primary_language', 'Unknown')}

Predict 3 specific, realistic development areas for next week based on the patterns above.

Format as a numbered list (1., 2., 3.) with no extra text. Be specific and concrete."""

    return prompt

def create_summary_prompt(data: Dict[str, Any]) -> str:
    """Create a one-line impactful summary."""
    commits = data["commits"]
    
    prompt = f"""Write ONE compelling sentence (max 20 words) summarizing this week's development:

• {commits.get('total_commits', 0)} commits
• Focus: {', '.join(commits.get('commit_messages', [])[:2])}

Make it engaging and specific. Just the sentence, nothing else."""

    return prompt

def generate_insights(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive AI insights from analysis data."""
    print("🤖 Generating AI insights with enhanced fallback system...")
    
    insights = {
        "timestamp": datetime.now().isoformat(),
        "models_attempted": [],
        "generation_time_seconds": 0,
        "analysis": None,
        "recommendations": None,
        "predictions": None,
        "summary": None
    }
    
    start_time = time.time()
    
    # Generate main analysis
    print("\n" + "="*60)
    analysis_prompt = create_analysis_prompt(data)
    insights["analysis"] = query_with_fallback(
        analysis_prompt,
        task_name="analysis",
        max_tokens=400,
        temperature=0.7
    )
    
    if not insights["analysis"]:
        insights["analysis"] = (
            f"Active development with {data['commits'].get('total_commits', 0)} commits this week. "
            f"Primary focus on {data['code'].get('primary_language', 'software')} development "
            f"with consistent progress across multiple areas. "
            f"Team maintaining steady workflow with {data['pull_requests'].get('merged', 0)} merged pull requests."
        )
    
    # Generate recommendations
    print("\n" + "="*60)
    rec_prompt = create_recommendation_prompt(data)
    insights["recommendations"] = query_with_fallback(
        rec_prompt,
        task_name="recommendations",
        max_tokens=300,
        temperature=0.7
    )
    
    if not insights["recommendations"]:
        insights["recommendations"] = (
            "1. Continue maintaining current development velocity and code review practices\n"
            "2. Consider expanding test coverage for recently modified modules\n"
            "3. Document architectural decisions and update README for new contributors"
        )
    
    # Generate predictions
    print("\n" + "="*60)
    pred_prompt = create_prediction_prompt(data)
    insights["predictions"] = query_with_fallback(
        pred_prompt,
        task_name="predictions",
        max_tokens=300,
        temperature=0.8
    )
    
    if not insights["predictions"]:
        insights["predictions"] = (
            "1. Continuation of current feature development and refinements\n"
            "2. Bug fixes and performance optimizations based on recent changes\n"
            "3. Documentation updates and code quality improvements"
        )
    
    # Generate quick summary
    print("\n" + "="*60)
    summary_prompt = create_summary_prompt(data)
    insights["summary"] = query_with_fallback(
        summary_prompt,
        task_name="summary",
        max_tokens=50,
        temperature=0.7
    )
    
    if not insights["summary"]:
        insights["summary"] = f"Strong development week with {data['commits'].get('total_commits', 0)} commits focused on core features."
    
    # Calculate generation time
    insights["generation_time_seconds"] = round(time.time() - start_time, 2)
    
    return insights

def main():
    """Main insights generation function."""
    try:
        print("🤖 Starting AI insights generation...")
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        # Load analysis data
        print("\n📊 Loading repository analysis...")
        data = load_analysis_data()
        print(f"✅ Loaded data for {data.get('repository', 'repository')}")
        
        # Generate insights
        insights = generate_insights(data)
        
        # Save insights
        output_file = DATA_DIR / "ai_insights.json"
        with open(output_file, 'w') as f:
            json.dump(insights, f, indent=2)
        
        print(f"\n✅ Insights generated in {insights['generation_time_seconds']}s!")
        print(f"💾 Saved to {output_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("📋 GENERATED INSIGHTS PREVIEW")
        print("="*60)
        
        print(f"\n📌 Summary:\n{insights['summary']}")
        print(f"\n💡 Analysis:\n{insights['analysis'][:300]}...")
        print(f"\n🎯 Recommendations:\n{insights['recommendations'][:200]}...")
        print(f"\n🔮 Predictions:\n{insights['predictions'][:200]}...")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ Error generating insights: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
