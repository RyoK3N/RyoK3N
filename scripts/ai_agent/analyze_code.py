#!/usr/bin/env python3
"""
AI Agent - Deep Code Analysis Module
Analyzes repository code to extract technical concepts and snippets
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from github import Github
from collections import defaultdict
import re

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# File extensions to analyze
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
    '.ipynb': 'jupyter',
}

# Technical patterns to identify
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
        r'fit\(',
        r'predict\(',
        r'RandomForest|XGBoost|LightGBM',
    ],
    'deep_learning': [
        r'import torch',
        r'import tensorflow',
        r'import keras',
        r'forward\(',
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
    'api_development': [
        r'@app\.route',
        r'@api\.',
        r'FastAPI|Flask',
        r'requests\.',
        r'async def',
    ],
}

def get_github_client() -> Github:
    """Initialize GitHub client"""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not set")
    return Github(token)

def is_code_file(filename: str) -> bool:
    """Check if file should be analyzed"""
    ext = Path(filename).suffix.lower()
    return ext in CODE_EXTENSIONS

def extract_code_snippets(content: str, language: str, max_length: int = 50) -> List[Dict]:
    """Extract meaningful code snippets from file content"""
    snippets = []
    
    # Split into logical blocks
    if language == 'python':
        # Extract class definitions
        class_pattern = r'class\s+(\w+).*?:\n((?:    .*\n)*)'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            class_body = match.group(2)
            lines = class_body.split('\n')[:max_length]
            snippet = f"class {class_name}:\n" + '\n'.join(lines)
            
            snippets.append({
                'type': 'class',
                'name': class_name,
                'code': snippet,
                'language': language,
                'lines': len(lines)
            })
        
        # Extract function definitions
        func_pattern = r'def\s+(\w+)\((.*?)\).*?:\n((?:    .*\n)*)'
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1)
            params = match.group(2)
            func_body = match.group(3)
            
            # Skip private/magic methods
            if func_name.startswith('_'):
                continue
            
            lines = func_body.split('\n')[:max_length]
            snippet = f"def {func_name}({params}):\n" + '\n'.join(lines)
            
            snippets.append({
                'type': 'function',
                'name': func_name,
                'code': snippet,
                'language': language,
                'lines': len(lines)
            })
    
    elif language in ['javascript', 'typescript']:
        # Extract function/class definitions
        func_pattern = r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\((.*?)\)\s*\{([^}]*)\}'
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1)
            snippet = match.group(0)[:500]
            
            snippets.append({
                'type': 'function',
                'name': func_name,
                'code': snippet,
                'language': language,
                'lines': len(snippet.split('\n'))
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
        if file_content.size > 100000:  # 100KB
            return None
        
        content = file_content.decoded_content.decode('utf-8', errors='ignore')
        ext = Path(file_path).suffix.lower()
        language = CODE_EXTENSIONS.get(ext, 'text')
        
        # Extract snippets
        snippets = extract_code_snippets(content, language)
        
        # Identify concepts
        concepts = identify_technical_concepts(content)
        
        if not snippets and not concepts:
            return None
        
        return {
            'path': file_path,
            'language': language,
            'size': file_content.size,
            'concepts': concepts,
            'snippets': snippets[:5],  # Top 5 snippets
            'lines': len(content.split('\n'))
        }
        
    except Exception as e:
        print(f"  ⚠️  Error analyzing {file_path}: {e}")
        return None

def analyze_repository_code(repo_name: str) -> Dict[str, Any]:
    """Deep analysis of repository code"""
    print(f"\n🔬 Deep code analysis: {repo_name}")
    
    g = get_github_client()
    repo = g.get_repo(repo_name)
    
    analysis = {
        'repository': repo_name,
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
        
        print(f"  📁 Found {len(files_to_analyze)} code files")
        
        # Analyze files
        for i, file_path in enumerate(files_to_analyze[:50], 1):  # Limit to 50 files
            if i % 10 == 0:
                print(f"  📊 Analyzed {i}/{min(50, len(files_to_analyze))} files...")
            
            file_analysis = analyze_file(repo, file_path)
            
            if file_analysis:
                analysis['files_analyzed'] += 1
                analysis['total_lines'] += file_analysis['lines']
                analysis['languages'][file_analysis['language']] += 1
                
                # Track concepts
                for concept in file_analysis['concepts']:
                    analysis['concepts'][concept] += 1
                
                # Store best snippets
                for snippet in file_analysis['snippets']:
                    analysis['code_samples'].append({
                        **snippet,
                        'file': file_path,
                        'repo': repo_name
                    })
        
        # Sort and limit code samples
        analysis['code_samples'].sort(key=lambda x: x['lines'], reverse=True)
        analysis['code_samples'] = analysis['code_samples'][:20]  # Top 20
        
        # Convert defaultdicts to regular dicts
        analysis['languages'] = dict(analysis['languages'])
        analysis['concepts'] = dict(sorted(
            analysis['concepts'].items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        # Technical summary
        analysis['technical_summary'] = {
            'primary_language': max(analysis['languages'].items(), key=lambda x: x[1])[0] if analysis['languages'] else 'Unknown',
            'main_concepts': list(analysis['concepts'].keys())[:5],
            'complexity_score': min(100, analysis['total_lines'] / 100),
            'code_quality': 'production' if analysis['files_analyzed'] > 10 else 'prototype'
        }
        
        print(f"  ✅ Analysis complete: {analysis['files_analyzed']} files, {analysis['total_lines']} lines")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    return analysis

def analyze_all_repositories(repo_list: List[str]) -> Dict[str, Any]:
    """Analyze code from multiple repositories"""
    print("🔬 Starting deep code analysis across repositories...")
    
    all_analyses = {}
    
    for i, repo_name in enumerate(repo_list[:10], 1):  # Limit to 10 repos
        print(f"\n📦 [{i}/{min(10, len(repo_list))}] Analyzing: {repo_name}")
        
        try:
            analysis = analyze_repository_code(repo_name)
            all_analyses[repo_name] = analysis
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            continue
    
    return all_analyses

def main():
    """Main code analysis function"""
    try:
        print("🔬 Starting deep code analysis...")
        
        # Load categorized projects
        categories_file = DATA_DIR / "project_categories.json"
        with open(categories_file, 'r') as f:
            data = json.load(f)
        
        repos = data.get('categorized_repositories', [])
        
        # Get full repo names
        username = os.getenv('REPOSITORY', '').split('/')[0]
        repo_names = [f"{username}/{r['name']}" for r in repos if r.get('name')]
        
        print(f"📚 Found {len(repo_names)} repositories to analyze")
        
        # Analyze repositories
        analyses = analyze_all_repositories(repo_names)
        
        # Save results
        output_file = DATA_DIR / "code_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(analyses, f, indent=2)
        
        print(f"\n✅ Code analysis complete!")
        print(f"💾 Saved to {output_file}")
        
        # Summary
        total_files = sum(a['files_analyzed'] for a in analyses.values())
        total_lines = sum(a['total_lines'] for a in analyses.values())
        total_snippets = sum(len(a['code_samples']) for a in analyses.values())
        
        print(f"\n📊 Summary:")
        print(f"  • Repositories analyzed: {len(analyses)}")
        print(f"  • Files analyzed: {total_files}")
        print(f"  • Total lines of code: {total_lines:,}")
        print(f"  • Code snippets extracted: {total_snippets}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
