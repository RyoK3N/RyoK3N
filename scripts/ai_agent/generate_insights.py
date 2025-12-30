#!/usr/bin/env python3
"""
AI Agent - Insights Generation Module 
Uses Hugging Face InferenceClient with chat_completion for conversational models.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Import the correct client
try:
    from huggingface_hub import InferenceClient
    print("✅ InferenceClient imported successfully")
except ImportError:
    print("❌ ERROR: huggingface_hub not installed!")
    print("   Run: pip install huggingface-hub")
    exit(1)

# Configuration
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Models that work well with chat completion (free tier compatible)
MODEL_LIST = [
    "meta-llama/Llama-3.2-3B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "microsoft/Phi-3-mini-4k-instruct",
    "HuggingFaceH4/zephyr-7b-beta",
    "google/gemma-2-2b-it",
]

def load_analysis_data() -> Dict[str, Any]:
    """Load the repository analysis data."""
    analysis_file = DATA_DIR / "repository_analysis.json"
    
    if not analysis_file.exists():
        raise FileNotFoundError(f"Analysis file not found: {analysis_file}")
    
    with open(analysis_file, 'r') as f:
        return json.load(f)

def query_model(
    client: InferenceClient,
    prompt: str,
    model: str,
    max_tokens: int = 500,
    temperature: float = 0.7,
    retry_count: int = 2
) -> Optional[str]:
    """Query a model using chat_completion with retry logic."""
    
    for attempt in range(retry_count):
        try:
            print(f"🧠 Querying {model.split('/')[-1]} (attempt {attempt + 1}/{retry_count})...")
            
            # Use chat_completion (chat.completions.create) for conversational models
            messages = [{"role": "user", "content": prompt}]
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95,
            )
            
            # Extract the message content
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content and len(content) > 50:
                    print(f"✅ Generated {len(content)} characters")
                    return content.strip()
                else:
                    print(f"⚠️  Response too short")
                    
        except Exception as e:
            error_msg = str(e).lower()
            
            if "503" in error_msg or "loading" in error_msg:
                wait_time = 20 * (attempt + 1)
                print(f"⏳ Model loading, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            elif "429" in error_msg or "rate" in error_msg:
                wait_time = 30 * (attempt + 1)
                print(f"⏳ Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            elif "404" in error_msg or "not found" in error_msg:
                print(f"⚠️  Model not available: {str(e)[:100]}")
                break  # Skip to next model
            else:
                print(f"⚠️  Error: {str(e)[:200]}")
                if attempt < retry_count - 1:
                    time.sleep(5)
    
    return None

def query_with_fallback(
    client: InferenceClient,
    prompt: str,
    task_name: str = "generation",
    max_tokens: int = 500,
    temperature: float = 0.7
) -> Optional[str]:
    """Query with automatic model fallback."""
    print(f"\n{'='*60}")
    print(f"🎯 Starting {task_name}...")
    print(f"{'='*60}")
    
    for model in MODEL_LIST:
        print(f"\n📡 Trying {model}...")
        result = query_model(
            client,
            prompt,
            model,
            max_tokens=max_tokens,
            temperature=temperature,
            retry_count=2
        )
        
        if result:
            print(f"✅ Success with {model}")
            return result
        else:
            print(f"❌ Failed with {model}, trying next...")
    
    # All models failed
    print(f"❌ All models failed for {task_name}")
    return None

def create_analysis_prompt(data: Dict[str, Any]) -> str:
    """Create prompt for repository analysis."""
    commits = data["commits"]
    prs = data["pull_requests"]
    issues = data["issues"]
    code = data["code"]
    
    recent_work = ', '.join(commits.get('commit_messages', [])[:5]) or 'No recent commits'
    
    prompt = f"""Analyze this software repository's recent activity and provide insights.

REPOSITORY ACTIVITY (Last 7 Days):
• Commits: {commits.get('total_commits', 0)} commits ({commits.get('daily_average', 0):.1f}/day average)
• Top Contributor: {commits.get('top_author', 'Unknown')}
• Recent Work: {recent_work}
• Pull Requests: {prs.get('merged', 0)} merged, {prs.get('open', 0)} open
• Issues: {issues.get('closed', 0)} closed, {issues.get('open', 0)} open
• Primary Language: {code.get('primary_language', 'Unknown')}

Task: Write a concise 3-4 sentence professional analysis covering:
1. Development activity level and pace
2. Key focus areas based on recent work
3. One specific observation or insight

Keep it natural and professional. No bullet points, headers, or special formatting."""

    return prompt

def create_recommendation_prompt(data: Dict[str, Any]) -> str:
    """Create prompt for recommendations."""
    commits = data["commits"]
    code = data["code"]
    
    recent = ', '.join(commits.get('commit_messages', [])[:3]) or 'general development'
    
    prompt = f"""You are a senior software engineer. Provide 3 specific, actionable recommendations for this repository.

CURRENT STATE:
• Daily commit rate: {commits.get('daily_average', 0):.1f}
• Primary language: {code.get('primary_language', 'Unknown')}
• Recent work: {recent}

Task: Give exactly 3 recommendations (one brief sentence each) for improving:
1. Code quality
2. Development workflow
3. Project organization

Format your response as a simple numbered list:
1. [First recommendation]
2. [Second recommendation]
3. [Third recommendation]

No extra text before or after the list."""

    return prompt

def create_prediction_prompt(data: Dict[str, Any]) -> str:
    """Create prompt for predictions."""
    commits = data["commits"]
    prs = data["pull_requests"]
    
    recent_activity = commits.get('commit_messages', [])[:5] + prs.get('merged_titles', [])[:3]
    activity = ', '.join(recent_activity[:5]) or 'general development'
    
    prompt = f"""Based on recent development patterns, predict the likely focus areas for next week.

RECENT ACTIVITY:
• {commits.get('total_commits', 0)} commits in the last week
• Recent changes: {activity}
• Primary language: {data['code'].get('primary_language', 'Unknown')}

Task: Predict 3 specific, realistic development focus areas for next week based on these patterns.

Format as a numbered list:
1. [First prediction]
2. [Second prediction]
3. [Third prediction]

No extra text."""

    return prompt

def create_summary_prompt(data: Dict[str, Any]) -> str:
    """Create one-line summary."""
    commits = data["commits"]
    recent = ', '.join(commits.get('commit_messages', [])[:2])
    
    prompt = f"""Write ONE compelling sentence (maximum 15 words) summarizing this week's software development:

• {commits.get('total_commits', 0)} commits
• Focus: {recent}

Just write the single sentence, nothing else."""

    return prompt

def generate_insights(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate AI insights using InferenceClient."""
    print("🤖 Generating AI insights with InferenceClient...")
    
    # Initialize client
    api_key = os.getenv("HF_API_KEY") or os.getenv("HF_TOKEN")
    if not api_key:
        raise ValueError("HF_API_KEY or HF_TOKEN environment variable not set")
    
    client = InferenceClient(token=api_key)
    print(f"✅ InferenceClient initialized")
    
    insights = {
        "timestamp": datetime.now().isoformat(),
        "generation_time_seconds": 0,
        "analysis": None,
        "recommendations": None,
        "predictions": None,
        "summary": None
    }
    
    start_time = time.time()
    
    # Generate analysis
    analysis_prompt = create_analysis_prompt(data)
    insights["analysis"] = query_with_fallback(
        client, analysis_prompt, "analysis", max_tokens=400, temperature=0.7
    )
    
    if not insights["analysis"]:
        insights["analysis"] = (
            f"Active development with {data['commits'].get('total_commits', 0)} commits this week. "
            f"Primary focus on {data['code'].get('primary_language', 'software')} development "
            f"with consistent progress across multiple areas. "
            f"Team maintaining steady workflow with {data['pull_requests'].get('merged', 0)} merged pull requests."
        )
    
    # Generate recommendations
    rec_prompt = create_recommendation_prompt(data)
    insights["recommendations"] = query_with_fallback(
        client, rec_prompt, "recommendations", max_tokens=300, temperature=0.7
    )
    
    if not insights["recommendations"]:
        insights["recommendations"] = (
            "1. Continue maintaining current development velocity and code review practices\n"
            "2. Consider expanding test coverage for recently modified modules\n"
            "3. Document architectural decisions and update README for new contributors"
        )
    
    # Generate predictions
    pred_prompt = create_prediction_prompt(data)
    insights["predictions"] = query_with_fallback(
        client, pred_prompt, "predictions", max_tokens=300, temperature=0.8
    )
    
    if not insights["predictions"]:
        insights["predictions"] = (
            "1. Continuation of current feature development and refinements\n"
            "2. Bug fixes and performance optimizations based on recent changes\n"
            "3. Documentation updates and code quality improvements"
        )
    
    # Generate summary
    summary_prompt = create_summary_prompt(data)
    insights["summary"] = query_with_fallback(
        client, summary_prompt, "summary", max_tokens=50, temperature=0.7
    )
    
    if not insights["summary"]:
        insights["summary"] = f"Strong development week with {data['commits'].get('total_commits', 0)} commits."
    
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
        
        if insights.get('summary'):
            print(f"\n📌 Summary:\n{insights['summary']}")
        if insights.get('analysis'):
            print(f"\n💡 Analysis:\n{insights['analysis'][:400]}...")
        if insights.get('recommendations'):
            print(f"\n🎯 Recommendations:\n{insights['recommendations'][:250]}...")
        if insights.get('predictions'):
            print(f"\n🔮 Predictions:\n{insights['predictions'][:250]}...")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ Error generating insights: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
