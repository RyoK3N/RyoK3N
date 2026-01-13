#!/usr/bin/env python3
"""
AI Agent - Enhanced Repository Analysis
Analyzes repositories with categorization support
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path
from github import Github
from collections import Counter, defaultdict

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def get_github_client() -> Github:
    """Initialize GitHub client"""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not set")
    return Github(token)

def analyze_repository_details(repo) -> Dict[str, Any]:
    """Analyze detailed repository information"""
    try:
        # Get languages
        languages = repo.get_languages()
        total_bytes = sum(languages.values())
        language_percentages = {
            lang: round((bytes_count / total_bytes) * 100, 2)
            for lang, bytes_count in languages.items()
        }
        
        # Get topics/tags
        topics = repo.get_topics()
        
        # Get README content
        readme_content = ""
        try:
            readme = repo.get_readme()
            readme_content = readme.decoded_content.decode('utf-8')
        except:
            pass
        
        # Count files by type
        file_types = defaultdict(int)
        try:
            contents = repo.get_contents("")
            while contents:
                file = contents.pop(0)
                if file.type == "dir":
                    try:
                        contents.extend(repo.get_contents(file.path))
                    except:
                        pass
                else:
                    ext = Path(file.path).suffix
                    if ext:
                        file_types[ext] += 1
        except:
            pass
        
        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description or "",
            "languages": language_percentages,
            "topics": topics,
            "readme_content": readme_content[:5000],  # First 5000 chars
            "file_types": dict(file_types),
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "created_at": repo.created_at.isoformat(),
            "updated_at": repo.updated_at.isoformat(),
            "size": repo.size,
            "url": repo.html_url,
            "homepage": repo.homepage or "",
            "has_wiki": repo.has_wiki,
            "has_pages": repo.has_pages,
            "archived": repo.archived,
        }
    except Exception as e:
        print(f"Error analyzing {repo.name}: {e}")
        return None

def get_all_user_repositories(g: Github, username: str) -> List[Dict[str, Any]]:
    """Get all repositories for a user"""
    print(f"🔍 Fetching repositories for {username}...")
    
    user = g.get_user(username)
    repos = list(user.get_repos())
    
    print(f"📚 Found {len(repos)} repositories")
    
    analyzed_repos = []
    for i, repo in enumerate(repos, 1):
        print(f"   Analyzing {i}/{len(repos)}: {repo.name}...")
        repo_data = analyze_repository_details(repo)
        if repo_data:
            analyzed_repos.append(repo_data)
    
    return analyzed_repos

def analyze_main_repository(repo) -> Dict[str, Any]:
    """Analyze the main profile repository"""
    since_date = datetime.now() - timedelta(days=7)
    
    # Get commits
    commits = list(repo.get_commits(since=since_date))
    commit_messages = [c.commit.message.split('\n')[0] for c in commits]
    authors = [c.commit.author.name for c in commits]
    
    # Get PRs
    prs = list(repo.get_pulls(state='all', sort='updated', direction='desc'))
    recent_prs = [pr for pr in prs if pr.updated_at >= since_date]
    
    # Get issues
    issues = list(repo.get_issues(state='all', since=since_date))
    
    return {
        "commits": {
            "total": len(commits),
            "unique_authors": len(set(authors)),
            "top_author": max(set(authors), key=authors.count) if authors else "Unknown",
            "messages": commit_messages[:20],
            "daily_average": len(commits) / 7,
        },
        "pull_requests": {
            "total_recent": len(recent_prs),
            "merged": len([pr for pr in recent_prs if pr.merged]),
            "open": len([pr for pr in recent_prs if pr.state == 'open']),
        },
        "issues": {
            "total": len(issues),
            "open": len([i for i in issues if i.state == 'open' and not i.pull_request]),
            "closed": len([i for i in issues if i.state == 'closed' and not i.pull_request]),
        }
    }

def main():
    """Main analysis function"""
    try:
        print("🤖 Starting enhanced repository analysis...")
        
        g = get_github_client()
        repo_name = os.getenv("REPOSITORY")
        username = repo_name.split('/')[0] if repo_name else None
        
        if not repo_name or not username:
            raise ValueError("REPOSITORY environment variable not set")
        
        # Analyze main profile repository
        print(f"\n📊 Analyzing main repository: {repo_name}")
        main_repo = g.get_repo(repo_name)
        main_analysis = analyze_main_repository(main_repo)
        
        # Get all user repositories
        print(f"\n🔍 Analyzing all repositories for {username}...")
        all_repos = get_all_user_repositories(g, username)
        
        # Compile results
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "main_repository": repo_name,
            "main_repo_activity": main_analysis,
            "all_repositories": all_repos,
            "total_repositories": len(all_repos),
        }
        
        # Save results
        output_file = DATA_DIR / "repository_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(analysis_result, f, indent=2)
        
        print(f"\n✅ Analysis complete!")
        print(f"   • Main repo commits: {main_analysis['commits']['total']}")
        print(f"   • Total repositories: {len(all_repos)}")
        print(f"💾 Results saved to {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
