#!/usr/bin/env python3
"""
AI Agent - Repository Analysis Module
Analyzes GitHub repository activity and generates structured data for AI insights.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path
from github import Github
from collections import Counter

# Configuration
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def get_github_client() -> Github:
    """Initialize GitHub client with authentication."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")
    return Github(token)

def analyze_commits(repo, since_date: datetime) -> Dict[str, Any]:
    """Analyze commit activity since given date."""
    commits = list(repo.get_commits(since=since_date))
    
    # Extract commit metadata
    commit_messages = [c.commit.message.split('\n')[0] for c in commits]
    authors = [c.commit.author.name for c in commits]
    
    # Count languages modified (approximate from file extensions)
    languages = []
    for commit in commits[:50]:  # Limit to recent 50 for API efficiency
        try:
            for file in commit.files:
                ext = Path(file.filename).suffix
                if ext:
                    languages.append(ext)
        except Exception as e:
            print(f"Warning: Could not process commit {commit.sha}: {e}")
            continue
    
    language_counts = Counter(languages)
    
    return {
        "total_commits": len(commits),
        "unique_authors": len(set(authors)),
        "top_author": max(set(authors), key=authors.count) if authors else "Unknown",
        "commit_messages": commit_messages[:20],  # Last 20 messages
        "languages_modified": dict(language_counts.most_common(5)),
        "daily_average": len(commits) / 7,
    }

def analyze_pull_requests(repo, since_date: datetime) -> Dict[str, Any]:
    """Analyze pull request activity."""
    prs = list(repo.get_pulls(state='all', sort='updated', direction='desc'))
    recent_prs = [pr for pr in prs if pr.updated_at >= since_date]
    
    open_prs = [pr for pr in recent_prs if pr.state == 'open']
    merged_prs = [pr for pr in recent_prs if pr.merged]
    
    return {
        "total_recent": len(recent_prs),
        "open": len(open_prs),
        "merged": len(merged_prs),
        "merged_titles": [pr.title for pr in merged_prs[:10]],
        "avg_merge_time_hours": calculate_avg_merge_time(merged_prs),
    }

def analyze_issues(repo, since_date: datetime) -> Dict[str, Any]:
    """Analyze issue activity."""
    issues = list(repo.get_issues(state='all', since=since_date))
    
    open_issues = [i for i in issues if i.state == 'open' and not i.pull_request]
    closed_issues = [i for i in issues if i.state == 'closed' and not i.pull_request]
    
    # Extract labels
    labels = []
    for issue in issues[:50]:
        labels.extend([label.name for label in issue.labels])
    label_counts = Counter(labels)
    
    return {
        "total_recent": len(issues),
        "open": len(open_issues),
        "closed": len(closed_issues),
        "top_labels": dict(label_counts.most_common(5)),
        "recent_titles": [i.title for i in issues[:10]],
    }

def analyze_code_frequency(repo) -> Dict[str, Any]:
    """Analyze code frequency and language distribution."""
    try:
        languages = repo.get_languages()
        total_bytes = sum(languages.values())
        
        language_percentages = {
            lang: round((bytes_count / total_bytes) * 100, 2)
            for lang, bytes_count in languages.items()
        }
        
        return {
            "languages": language_percentages,
            "primary_language": max(languages.items(), key=lambda x: x[1])[0] if languages else "Unknown",
            "total_languages": len(languages),
        }
    except Exception as e:
        print(f"Warning: Could not analyze code frequency: {e}")
        return {"languages": {}, "primary_language": "Unknown", "total_languages": 0}

def calculate_avg_merge_time(merged_prs: List) -> float:
    """Calculate average time to merge PRs in hours."""
    if not merged_prs:
        return 0.0
    
    merge_times = []
    for pr in merged_prs[:20]:  # Limit to recent 20
        if pr.created_at and pr.merged_at:
            delta = pr.merged_at - pr.created_at
            merge_times.append(delta.total_seconds() / 3600)
    
    return round(sum(merge_times) / len(merge_times), 2) if merge_times else 0.0

def analyze_repository_activity(repo) -> Dict[str, Any]:
    """Get overall repository activity metrics."""
    return {
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "watchers": repo.watchers_count,
        "open_issues_count": repo.open_issues_count,
        "created_at": repo.created_at.isoformat(),
        "updated_at": repo.updated_at.isoformat(),
        "size_kb": repo.size,
        "default_branch": repo.default_branch,
    }

def main():
    """Main analysis function."""
    try:
        print("🤖 Starting repository analysis...")
        
        # Initialize GitHub client
        g = get_github_client()
        repo_name = os.getenv("REPOSITORY")
        
        if not repo_name:
            raise ValueError("REPOSITORY environment variable not set")
        
        repo = g.get_repo(repo_name)
        print(f"✓ Connected to repository: {repo_name}")
        
        # Set analysis time window (last 7 days)
        since_date = datetime.now() - timedelta(days=7)
        
        # Perform analyses
        print("📊 Analyzing commits...")
        commit_data = analyze_commits(repo, since_date)
        
        print("🔀 Analyzing pull requests...")
        pr_data = analyze_pull_requests(repo, since_date)
        
        print("🐛 Analyzing issues...")
        issue_data = analyze_issues(repo, since_date)
        
        print("💻 Analyzing code frequency...")
        code_data = analyze_code_frequency(repo)
        
        print("📈 Gathering repository metrics...")
        repo_data = analyze_repository_activity(repo)
        
        # Compile all data
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "analysis_period_days": 7,
            "repository": repo_name,
            "commits": commit_data,
            "pull_requests": pr_data,
            "issues": issue_data,
            "code": code_data,
            "repository_metrics": repo_data,
        }
        
        # Save to file
        output_file = DATA_DIR / "repository_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(analysis_result, f, indent=2)
        
        print(f"✅ Analysis complete! Results saved to {output_file}")
        
        # Print summary
        print("\n📋 Quick Summary:")
        print(f"   • Commits: {commit_data['total_commits']}")
        print(f"   • PRs: {pr_data['total_recent']} ({pr_data['merged']} merged)")
        print(f"   • Issues: {issue_data['total_recent']} ({issue_data['open']} open)")
        print(f"   • Primary Language: {code_data['primary_language']}")
        
        # Debug mode output
        if os.getenv("DEBUG_MODE", "false").lower() == "true":
            print("\n🔍 Debug: Full Analysis Result")
            print(json.dumps(analysis_result, indent=2))
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise

if __name__ == "__main__":
    main()
