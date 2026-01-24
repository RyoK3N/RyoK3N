#!/usr/bin/env python3
"""
AI Agent - Deep Code Analysis Module
Analyzes a single repository's code to extract technical concepts and snippets
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from github import Github, Auth
from collections import defaultdict
import re

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

CODE_EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.jsx': 'javascript',
    '.tsx': 'typescript',
    '.cpp': 'cpp',
    '.c': 'c',
    '.h': 'cpp',
    '.hpp': 'cpp',
    '.java': 'java',
    '.jl': 'julia',
    '.r': 'r',
    '.scala': 'scala',
}

TECHNICAL_PATTERNS = {
    'neural_network': [
        r'class.*\(nn\.Module\)',
        r'class.*\(tf\.keras\.Model\)',
        r'Sequential\(',
        r'Dense\(',
        r'Conv\d+D',
        r'LSTM|GRU',
    ],
    'machine_learning': [
        r'sklearn',
        r'train_test_split',
        r'\.fit\(',
        r'\.predict\(',
        r'RandomForest|XGBoost|LightGBM',
    ],
    'deep_learning': [
        r'import torch',
        r'import tensorflow',
        r'import keras',
        r'def forward\(',
        r'backward\(',
    ],
    'computer_vision': [
        r'cv2\.',
        r'Image\.',
        r'transforms\.',
        r'imread|imshow',
        r'detect|segment|classify',
    ],
    'nlp': [
        r'tokenize',
        r'embedding',
        r'transformer',
        r'bert|gpt',
        r'nltk|spacy',
    ],
    'data_processing': [
        r'pandas|pd\.',
        r'numpy|np\.',
        r'DataFrame',
        r'merge|join|groupby',
    ],
}

def get_github_client() -> Github:
    """Initialize GitHub client with proper auth"""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not set")
    auth = Auth.Token(token)
    return Github(auth=auth)

def is_code_file(filename: str) -> bool:
    """Check if file should be analyzed"""
    ext = Path(filename).suffix.lower()
    return ext in CODE_EXTENSIONS

def extract_code_snippets(content: str, language: str, filepath: str) -> List[Dict]:
    """Extract meaningful code snippets from file content"""
    snippets = []
    
    if language == 'python':
        # Extract class definitions
        class_pattern = r'class\s+(\w+).*?:\n((?:(?:    |\t).*\n)*)'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            class_body = match.group(2)
            
            # Get first 25 lines of class
            lines = [f"class {class_name}:"] + class_body.split('\n')[:25]
            snippet = '\n'.join(lines)
            
            snippets.append({
                'type': 'class',
                'name': class_name,
                'code': snippet,
                'language': language,
                'file': filepath,
                'lines': len(lines)
            })
        
        # Extract function definitions
        func_pattern = r'def\s+(\w+)\((.*?)\).*?:\n((?:(?:    |\t).*\n)*)'
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1)
            params = match.group(2)
            func_body = match.group(3)
            
            # Skip private methods
            if func_name.startswith('_') and not func_name.startswith('__'):
                continue
            
            # Get first 20 lines
            lines = [f"def {func_name}({params}):"] + func_body.split('\n')[:20]
            snippet = '\n'.join(lines)
            
            snippets.append({
                'type': 'function',
                'name': func_name,
                'code': snippet,
                'language': language,
                'file': filepath,
                'lines': len(lines)
            })
    
    return snippets

def identify_technical_concepts(content: str) -> List[str]:
    """Identify technical concepts in code"""
    concepts = []
    
    for concept, patterns in TECHNICAL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                concepts.append(concept)
                break
    
    return list(set(concepts))

def analyze_file(repo, file_path: str) -> Optional[Dict]:
    """Analyze a single code file"""
    try:
        file_content = repo.get_contents(file_path)
        
        # Skip large files
        if file_content.size > 150000:
            return None
        
        content = file_content.decoded_content.decode('utf-8', errors='ignore')
        ext = Path(file_path).suffix.lower()
        language = CODE_EXTENSIONS.get(ext, 'text')
        
        # Extract snippets
        snippets = extract_code_snippets(content, language, file_path)
        
        # Identify concepts
        concepts = identify_technical_concepts(content)
        
        if not snippets and not concepts:
            return None
        
        return {
            'path': file_path,
            'language': language,
            'size': file_content.size,
            'concepts': concepts,
            'snippets': snippets,
            'lines': len(content.split('\n'))
        }
        
    except Exception as e:
        return None

def analyze_repository_code(repo_full_name: str) -> Dict[str, Any]:
    """Deep analysis of a single repository's code"""
    print(f"\nAnalyzing repository: {repo_full_name}")
    
    g = get_github_client()
    
    try:
        repo = g.get_repo(repo_full_name)
    except Exception as e:
        print(f"  Error accessing repository: {e}")
        return {}
    
    analysis = {
        'repository': repo_full_name,
        'name': repo.name,
        'description': repo.description or '',
        'files_analyzed': 0,
        'total_lines': 0,
        'languages': defaultdict(int),
        'concepts': defaultdict(int),
        'code_samples': [],
        'technical_summary': {},
    }
    
    try:
        # Get all files
        contents = repo.get_contents("")
        files_to_analyze = []
        
        while contents:
            file_content = contents.pop(0)
            
            if file_content.type == "dir":
                try:
                    contents.extend(repo.get_contents(file_content.path))
                except:
                    pass
            elif is_code_file(file_content.path):
                files_to_analyze.append(file_content.path)
        
        print(f"  Found {len(files_to_analyze)} code files")
        
        # Analyze files (limit to 40 files for performance)
        for i, file_path in enumerate(files_to_analyze[:40], 1):
            if i % 10 == 0:
                print(f"  Progress: {i}/{min(40, len(files_to_analyze))} files analyzed")
            
            file_analysis = analyze_file(repo, file_path)
            
            if file_analysis:
                analysis['files_analyzed'] += 1
                analysis['total_lines'] += file_analysis['lines']
                analysis['languages'][file_analysis['language']] += 1
                
                for concept in file_analysis['concepts']:
                    analysis['concepts'][concept] += 1
                
                for snippet in file_analysis['snippets']:
                    analysis['code_samples'].append(snippet)
        
        # Sort and limit code samples by lines (prefer substantial code)
        analysis['code_samples'].sort(key=lambda x: x['lines'], reverse=True)
        analysis['code_samples'] = analysis['code_samples'][:15]
        
        # Convert defaultdicts
        analysis['languages'] = dict(analysis['languages'])
        analysis['concepts'] = dict(sorted(
            analysis['concepts'].items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        # Technical summary
        if analysis['languages']:
            analysis['technical_summary'] = {
                'primary_language': max(analysis['languages'].items(), key=lambda x: x[1])[0],
                'main_concepts': list(analysis['concepts'].keys())[:5],
                'complexity_score': min(100, analysis['total_lines'] / 100),
                'code_quality': 'production' if analysis['files_analyzed'] > 10 else 'prototype'
            }
        
        print(f"  Analysis complete: {analysis['files_analyzed']} files, {analysis['total_lines']} lines")
        print(f"  Code samples extracted: {len(analysis['code_samples'])}")
        
    except Exception as e:
        print(f"  Error during analysis: {e}")
    
    return analysis

def select_repository_for_analysis(categories_data: Dict) -> Optional[str]:
    """Select a repository to analyze based on stars and categories"""
    repos = categories_data.get('categorized_repositories', [])
    
    if not repos:
        return None
    
    # Filter repos with interesting categories and stars
    interesting_categories = [
        'Machine Learning', 'Computer Vision', 'Deep Learning',
        'Natural Language Processing', 'Data Science'
    ]
    
    candidates = []
    for repo in repos:
        # Score based on stars and categories
        score = repo.get('stars', 0) * 2
        
        # Boost score for interesting categories
        for cat in repo.get('categories', []):
            if cat in interesting_categories:
                score += 10
        
        if score > 0:
            candidates.append((repo['name'], score))
    
    if not candidates:
        # Just pick first repo
        return repos[0]['name']
    
    # Sort by score and pick top one
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]

def get_username_from_env() -> str:
    """Get username from REPOSITORY environment variable"""
    repo_env = os.getenv('REPOSITORY', '')
    
    if not repo_env:
        # Fallback: try to get from GitHub context
        github_repository = os.getenv('GITHUB_REPOSITORY', '')
        if github_repository:
            repo_env = github_repository
    
    if '/' in repo_env:
        return repo_env.split('/')[0]
    
    raise ValueError(
        "Could not determine username. "
        "Please set REPOSITORY or GITHUB_REPOSITORY environment variable "
        "in format 'username/repo'"
    )

def main():
    """Main code analysis function"""
    try:
        print("Starting deep code analysis...")
        
        # Get username with better error handling
        try:
            username = get_username_from_env()
            print(f"Username: {username}")
        except ValueError as e:
            print(f"Error: {e}")
            print("\nEnvironment variables:")
            print(f"  REPOSITORY: {os.getenv('REPOSITORY', 'NOT SET')}")
            print(f"  GITHUB_REPOSITORY: {os.getenv('GITHUB_REPOSITORY', 'NOT SET')}")
            
            # Create empty analysis file so workflow doesn't fail
            output_file = DATA_DIR / "code_analysis.json"
            with open(output_file, 'w') as f:
                json.dump({}, f, indent=2)
            print(f"\nCreated empty analysis file: {output_file}")
            print("Workflow will continue with generic blog generation")
            return
        
        # Load categorized projects
        categories_file = DATA_DIR / "project_categories.json"
        if not categories_file.exists():
            print("Error: project_categories.json not found")
            print("Creating empty analysis file...")
            output_file = DATA_DIR / "code_analysis.json"
            with open(output_file, 'w') as f:
                json.dump({}, f, indent=2)
            return
        
        with open(categories_file, 'r') as f:
            categories_data = json.load(f)
        
        # Select repository to analyze
        repo_name = select_repository_for_analysis(categories_data)
        
        if not repo_name:
            print("No suitable repository found for analysis")
            output_file = DATA_DIR / "code_analysis.json"
            with open(output_file, 'w') as f:
                json.dump({}, f, indent=2)
            return
        
        repo_full_name = f"{username}/{repo_name}"
        print(f"\nSelected repository for deep analysis: {repo_full_name}")
        
        # Analyze the repository
        analysis = analyze_repository_code(repo_full_name)
        
        if not analysis or analysis.get('files_analyzed', 0) == 0:
            print("Warning: No code analyzed. This may affect blog quality.")
            analysis = {'repository': repo_full_name, 'code_samples': []}
        
        # Save results
        output_file = DATA_DIR / "code_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\nAnalysis complete!")
        print(f"Saved to: {output_file}")
        
        # Summary
        if analysis.get('files_analyzed', 0) > 0:
            print(f"\nSummary:")
            print(f"  Repository: {repo_full_name}")
            print(f"  Files analyzed: {analysis['files_analyzed']}")
            print(f"  Total lines: {analysis['total_lines']:,}")
            print(f"  Code snippets: {len(analysis.get('code_samples', []))}")
            print(f"  Concepts: {', '.join(list(analysis.get('concepts', {}).keys())[:5])}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Create empty analysis file so workflow doesn't completely fail
        output_file = DATA_DIR / "code_analysis.json"
        with open(output_file, 'w') as f:
            json.dump({}, f, indent=2)
        print(f"\nCreated empty analysis file: {output_file}")
        print("Workflow will continue with generic blog generation")

if __name__ == "__main__":
    main()
