#!/usr/bin/env python3
"""
AI Agent - README Update Module (Enhanced)
Updates the README.md file with AI-generated insights.
Now with better formatting, emoji support, and error handling.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Configuration
DATA_DIR = Path(__file__).parent / "data"
README_PATH = Path(__file__).parent.parent.parent / "README.md"

def load_data_files() -> Dict[str, Any]:
    """Load all generated data files."""
    analysis_file = DATA_DIR / "repository_analysis.json"
    insights_file = DATA_DIR / "ai_insights.json"
    metrics_file = DATA_DIR / "agent_metrics.json"
    
    data = {}
    
    if analysis_file.exists():
        with open(analysis_file, 'r') as f:
            data['analysis'] = json.load(f)
    
    if insights_file.exists():
        with open(insights_file, 'r') as f:
            data['insights'] = json.load(f)
    
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            data['metrics'] = json.load(f)
    
    return data

def format_language_distribution(languages: Dict[str, float], max_langs: int = 3) -> str:
    """Format language distribution as a readable string."""
    if not languages:
        return "No data available"
    
    items = list(languages.items())[:max_langs]
    formatted = []
    
    for lang, pct in items:
        # Add color indicators
        if pct > 50:
            emoji = "🔥"
        elif pct > 25:
            emoji = "⭐"
        else:
            emoji = "📊"
        formatted.append(f"{emoji} {lang} ({pct}%)")
    
    return " • ".join(formatted)

def format_commit_stats(commits: Dict[str, Any]) -> str:
    """Format commit statistics with context."""
    total = commits.get('total_commits', 0)
    daily_avg = commits.get('daily_average', 0)
    
    if daily_avg > 5:
        pace = "🚀 Very Active"
    elif daily_avg > 2:
        pace = "⚡ Active"
    elif daily_avg > 1:
        pace = "📈 Steady"
    else:
        pace = "🔄 Moderate"
    
    return f"{total} commits • {pace} ({daily_avg:.1f}/day)"

def format_pr_stats(prs: Dict[str, Any]) -> str:
    """Format PR statistics."""
    merged = prs.get('merged', 0)
    open_prs = prs.get('open', 0)
    avg_time = prs.get('avg_merge_time_hours', 0)
    
    stats = []
    if merged > 0:
        stats.append(f"✅ {merged} merged")
    if open_prs > 0:
        stats.append(f"🔄 {open_prs} open")
    if avg_time > 0:
        stats.append(f"⏱️ {avg_time:.1f}h avg merge")
    
    return " • ".join(stats) if stats else "No recent PR activity"

def format_issue_stats(issues: Dict[str, Any]) -> str:
    """Format issue statistics."""
    closed = issues.get('closed', 0)
    open_issues = issues.get('open', 0)
    
    stats = []
    if closed > 0:
        stats.append(f"✅ {closed} resolved")
    if open_issues > 0:
        stats.append(f"🔍 {open_issues} active")
    
    return " • ".join(stats) if stats else "No recent issues"

def clean_ai_text(text: str) -> str:
    """Clean and format AI-generated text."""
    if not text:
        return text
    
    # Remove any markdown artifacts
    text = text.replace('```', '').replace('**', '')
    
    # Remove leading/trailing quotes
    text = text.strip('"\'')
    
    # Ensure proper spacing
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def format_list_items(text: str) -> str:
    """Ensure list items are properly formatted."""
    if not text:
        return text
    
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Ensure numbered items start properly
        if re.match(r'^\d+[\.\)]\s*', line):
            # Already numbered
            formatted_lines.append(line)
        elif line and not line.startswith(('•', '-', '*')):
            # Add bullet if not already present
            formatted_lines.append(f"• {line}")
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def create_insights_section(data: Dict[str, Any]) -> str:
    """Create the formatted insights section for README."""
    analysis = data.get('analysis', {})
    insights = data.get('insights', {})
    metrics = data.get('metrics', {})
    
    # Extract data
    commits = analysis.get('commits', {})
    prs = analysis.get('pull_requests', {})
    issues = analysis.get('issues', {})
    code = analysis.get('code', {})
    repo_metrics = analysis.get('repository_metrics', {})
    
    # Format timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    
    # Get AI insights
    ai_analysis = clean_ai_text(insights.get('analysis', 'Analysis pending...'))
    ai_recommendations = format_list_items(insights.get('recommendations', 'Generating recommendations...'))
    ai_predictions = format_list_items(insights.get('predictions', 'Generating predictions...'))
    ai_summary = clean_ai_text(insights.get('summary', ''))
    generation_time = insights.get('generation_time_seconds', 0)
    
    # Agent performance
    agent_runs = metrics.get('total_runs', 0)
    success_rate = metrics.get('success_rate', 100.0)
    
    # Build the section
    section = f"""<!--START_SECTION:ai_insights-->
**🤖 AI Agent Last Updated**: {timestamp}

{f"**💡 Quick Insight**: *{ai_summary}*" if ai_summary else ""}

---

### 📊 Development Activity (Last 7 Days)

<table>
<tr>
<td width="50%">

**💻 Code Contributions**
- **Commits**: {format_commit_stats(commits)}
- **Primary Language**: {format_language_distribution(code.get('languages', {}))}
- **Top Contributor**: {commits.get('top_author', 'Unknown')} 👨‍💻

</td>
<td width="50%">

**🔄 Collaboration**
- **Pull Requests**: {format_pr_stats(prs)}
- **Issues**: {format_issue_stats(issues)}
- **Repository Stars**: ⭐ {repo_metrics.get('stars', 0)}

</td>
</tr>
</table>

---

### 🧠 AI-Powered Analysis

**What's Happening:**

*{ai_analysis}*

---

### 💡 Intelligent Recommendations

{ai_recommendations}

---

### 🔮 Next Week's Predicted Focus

Based on current development patterns and commit history:

{ai_predictions}

---

### 📈 Agent Performance

<div align="center">

| Metric | Value | Status |
|--------|-------|--------|
| 🎯 Total Runs | {agent_runs} | 🟢 Active |
| ✅ Success Rate | {success_rate}% | {"🟢 Excellent" if success_rate >= 95 else "🟡 Good" if success_rate >= 85 else "🔴 Attention"} |
| ⚡ Last Gen Time | {generation_time:.1f}s | {"🟢 Fast" if generation_time < 10 else "🟡 Normal" if generation_time < 30 else "🔴 Slow"} |
| 🤖 AI Model | Multi-Model Ensemble | 🟢 Advanced |

</div>

---

<div align="center">

*🤖 Autonomously generated using Hugging Face AI • Updated daily at 00:00 UTC*

[![View Workflow](https://img.shields.io/badge/View-Workflow-blue?style=flat-square&logo=github)](https://github.com/{analysis.get('repository', 'user/repo')}/actions)
[![Agent Status](https://img.shields.io/badge/Status-Active-success?style=flat-square&logo=robot)](https://github.com/{analysis.get('repository', 'user/repo')}/actions)

</div>

<!--END_SECTION:ai_insights-->"""
    
    return section

def update_readme_section(
    readme_content: str,
    section_name: str,
    new_content: str
) -> str:
    """Update a specific section in the README."""
    pattern = f"<!--START_SECTION:{section_name}-->.*?<!--END_SECTION:{section_name}-->"
    
    if re.search(pattern, readme_content, re.DOTALL):
        updated_content = re.sub(
            pattern,
            new_content,
            readme_content,
            flags=re.DOTALL
        )
        return updated_content
    else:
        print(f"⚠️  Section {section_name} not found in README")
        print(f"    Add these markers to enable auto-updates:")
        print(f"    <!--START_SECTION:{section_name}-->")
        print(f"    <!--END_SECTION:{section_name}-->")
        return readme_content

def validate_readme_structure(content: str) -> bool:
    """Validate that the README has the required structure."""
    required_sections = ["ai_insights"]
    
    for section in required_sections:
        start_tag = f"<!--START_SECTION:{section}-->"
        end_tag = f"<!--END_SECTION:{section}-->"
        
        if start_tag not in content or end_tag not in content:
            print(f"❌ Missing section markers for: {section}")
            return False
    
    return True

def create_backup(readme_path: Path) -> Path:
    """Create a backup of the current README."""
    backup_dir = readme_path.parent / ".readme_backups"
    backup_dir.mkdir(exist_ok=True)
    
    backup_path = backup_dir / f"README.{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📦 Backup created: {backup_path}")
        
        # Clean old backups (keep last 10)
        backups = sorted(backup_dir.glob("README.*.md"), reverse=True)
        for old_backup in backups[10:]:
            old_backup.unlink()
            print(f"🗑️  Removed old backup: {old_backup.name}")
        
        return backup_path
    
    return None

def main():
    """Main README update function."""
    try:
        print("📝 Starting README update...")
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        # Check if README exists
        if not README_PATH.exists():
            raise FileNotFoundError(f"README not found: {README_PATH}")
        
        # Load current README
        print("\n📖 Reading current README...")
        with open(README_PATH, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        print(f"✅ Loaded README ({len(readme_content)} characters)")
        
        # Validate structure
        print("\n🔍 Validating README structure...")
        if not validate_readme_structure(readme_content):
            print("\n⚠️  README structure validation failed!")
            print("\n📝 Add this section to your README:")
            print("="*60)
            print("<!--START_SECTION:ai_insights-->")
            print("AI insights will appear here automatically")
            print("<!--END_SECTION:ai_insights-->")
            print("="*60)
            return
        
        print("✅ README structure valid")
        
        # Create backup
        print("\n💾 Creating backup...")
        create_backup(README_PATH)
        
        # Load data
        print("\n📊 Loading analysis data...")
        data = load_data_files()
        
        if not data:
            print("⚠️  No data files found. Skipping update.")
            return
        
        print(f"✅ Loaded {len(data)} data files")
        
        # Generate new insights section
        print("\n✨ Generating insights section...")
        new_insights = create_insights_section(data)
        
        print(f"✅ Generated {len(new_insights)} characters of content")
        
        # Update README
        print("\n📝 Updating README...")
        updated_content = update_readme_section(
            readme_content,
            "ai_insights",
            new_insights
        )
        
        # Check if content actually changed
        if updated_content == readme_content:
            print("ℹ️  No changes detected, README already up to date")
            return
        
        # Write updated README
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ README updated successfully!")
        
        # Show summary
        print("\n" + "="*60)
        print("📋 UPDATE SUMMARY")
        print("="*60)
        print(f"✓ Backup created")
        print(f"✓ README validated")
        print(f"✓ AI insights updated")
        print(f"✓ {len(new_insights)} characters written")
        print("="*60)
        
        # Show preview
        preview_length = 400
        print(f"\n📖 Preview (first {preview_length} chars):")
        print("="*60)
        print(new_insights[:preview_length] + "...")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error updating README: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
