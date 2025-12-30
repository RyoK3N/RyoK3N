#!/usr/bin/env python3
"""
AI Agent - README Update Module
Updates the README.md file with AI-generated insights.
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
    
    data = {}
    
    if analysis_file.exists():
        with open(analysis_file, 'r') as f:
            data['analysis'] = json.load(f)
    
    if insights_file.exists():
        with open(insights_file, 'r') as f:
            data['insights'] = json.load(f)
    
    return data

def format_language_distribution(languages: Dict[str, float]) -> str:
    """Format language distribution as a readable string."""
    if not languages:
        return "No data available"
    
    items = list(languages.items())[:3]  # Top 3 languages
    return " • ".join([f"{lang} ({pct}%)" for lang, pct in items])

def create_insights_section(data: Dict[str, Any]) -> str:
    """Create the formatted insights section for README."""
    analysis = data.get('analysis', {})
    insights = data.get('insights', {})
    
    # Extract data
    commits = analysis.get('commits', {})
    prs = analysis.get('pull_requests', {})
    issues = analysis.get('issues', {})
    code = analysis.get('code', {})
    
    # Format timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    
    # Build the section
    section = f"""<!--START_SECTION:ai_insights-->
**Last Analysis**: {timestamp}

**📈 Recent Activity Summary**
- **Commits This Week**: {commits.get('total_commits', 0)} commits across multiple repositories
- **Primary Language**: {format_language_distribution(code.get('languages', {}))}
- **Pull Requests**: {prs.get('merged', 0)} merged • {prs.get('open', 0)} open
- **Issues**: {issues.get('closed', 0)} closed • {issues.get('open', 0)} open

**🔍 AI-Generated Insights**
*"{insights.get('analysis', 'Analysis pending...')}"*

**💡 Recommendations**
{insights.get('recommendations', 'No recommendations available.')}

**🎯 Next Week's Predicted Focus**
Based on recent patterns, likely areas of development:
{insights.get('predictions', 'No predictions available.')}
<!--END_SECTION:ai_insights-->"""
    
    return section

def update_readme_section(
    readme_content: str,
    section_name: str,
    new_content: str
) -> str:
    """Update a specific section in the README."""
    # Pattern to match the section
    pattern = f"<!--START_SECTION:{section_name}-->.*?<!--END_SECTION:{section_name}-->"
    
    # Check if section exists
    if re.search(pattern, readme_content, re.DOTALL):
        # Replace existing section
        updated_content = re.sub(
            pattern,
            new_content,
            readme_content,
            flags=re.DOTALL
        )
        return updated_content
    else:
        print(f"⚠️  Section {section_name} not found in README")
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
    backup_path = readme_path.parent / f"README.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    if readme_path.exists():
        with open(readme_path, 'r') as f:
            content = f.read()
        
        with open(backup_path, 'w') as f:
            f.write(content)
        
        print(f"📦 Backup created: {backup_path}")
        return backup_path
    
    return None

def main():
    """Main README update function."""
    try:
        print("📝 Starting README update...")
        
        # Check if README exists
        if not README_PATH.exists():
            raise FileNotFoundError(f"README not found: {README_PATH}")
        
        # Load current README
        print("📖 Reading current README...")
        with open(README_PATH, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        # Validate structure
        print("🔍 Validating README structure...")
        if not validate_readme_structure(readme_content):
            print("⚠️  README structure validation failed. Please ensure the required section markers exist.")
            print("    Add this to your README where you want the insights:")
            print("    <!--START_SECTION:ai_insights-->")
            print("    Content will be inserted here")
            print("    <!--END_SECTION:ai_insights-->")
            return
        
        # Create backup
        create_backup(README_PATH)
        
        # Load data
        print("📊 Loading analysis data...")
        data = load_data_files()
        
        if not data:
            print("⚠️  No data files found. Skipping update.")
            return
        
        # Generate new insights section
        print("✨ Generating insights section...")
        new_insights = create_insights_section(data)
        
        # Update README
        print("📝 Updating README...")
        updated_content = update_readme_section(
            readme_content,
            "ai_insights",
            new_insights
        )
        
        # Write updated README
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ README updated successfully!")
        
        # Show what was updated
        print("\n📋 Updated Section Preview:")
        print("=" * 60)
        print(new_insights[:500] + "..." if len(new_insights) > 500 else new_insights)
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error updating README: {e}")
        raise

if __name__ == "__main__":
    main()
