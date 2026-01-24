#!/usr/bin/env python3
"""
AI Agent - Technical Blog Generator with Code Analysis
Generates technical blog posts based on actual repository code
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from huggingface_hub import InferenceClient
import time
import random

DATA_DIR = Path(__file__).parent / "data"

MODELS = [
    "Qwen/Qwen2.5-7B-Instruct",
    "meta-llama/Llama-3.2-3B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
]

def load_context_data() -> Dict[str, Any]:
    """Load all context data"""
    context = {}
    
    files = {
        'code_analysis': 'code_analysis.json',
        'categories': 'project_categories.json',
        'featured': 'featured_project.json',
    }
    
    for key, filename in files.items():
        filepath = DATA_DIR / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                context[key] = json.load(f)
    
    return context

def query_ai(client: InferenceClient, prompt: str, section: str, max_tokens: int = 800) -> str:
    """Query AI with fallback"""
    
    for attempt, model in enumerate(MODELS):
        try:
            print(f"    Querying {model.split('/')[-1]} for {section}...")
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            
            if response and response.choices:
                content = response.choices[0].message.content.strip()
                
                if len(content) > 200:
                    print(f"    Generated {len(content)} characters")
                    return content
                    
        except Exception as e:
            error_str = str(e).lower()
            if "503" in error_str or "loading" in error_str:
                wait = 15 * (attempt + 1)
                print(f"    Model loading, waiting {wait}s...")
                time.sleep(wait)
                continue
            print(f"    Error: {str(e)[:100]}")
    
    return ""

def generate_technical_blog(context: Dict, client: InferenceClient) -> Dict:
    """Generate complete technical blog post"""
    
    code_data = context.get('code_analysis', {})
    
    # Check if we have code analysis
    if not code_data or not code_data.get('code_samples'):
        print("  Warning: No code analysis found, generating generic blog")
        return generate_generic_blog(context, client)
    
    repo_name = code_data.get('name', 'Project')
    description = code_data.get('description', '')
    concepts = list(code_data.get('concepts', {}).keys())[:3]
    snippets = code_data.get('code_samples', [])[:6]
    
    print(f"\nGenerating technical blog about: {repo_name}")
    print(f"  Concepts: {', '.join(concepts) if concepts else 'General'}")
    print(f"  Code snippets: {len(snippets)}")
    
    # Generate title
    concept_text = concepts[0].replace('_', ' ').title() if concepts else 'Software Architecture'
    title = f"Technical Deep Dive: {repo_name} - {concept_text} Implementation"
    
    print(f"\nTitle: {title}")
    
    # Build context for AI
    code_context = f"""
Repository: {repo_name}
Description: {description}
Technical Focus: {', '.join(concepts) if concepts else 'Software Engineering'}
Available Code Samples: {len(snippets)} snippets from actual implementation
Primary Language: {code_data.get('technical_summary', {}).get('primary_language', 'Python')}
Total Lines Analyzed: {code_data.get('total_lines', 0):,}
"""
    
    # Generate Introduction
    print("\nGenerating introduction...")
    intro_prompt = f"""Write a technical introduction for a blog post titled: "{title}"

{code_context}

Write 3 paragraphs that:
1. Start with a specific technical challenge or problem this project addresses
2. Explain the engineering approach and key technical decisions
3. Preview what readers will learn from examining the actual code

Be technical and specific. Write for experienced software engineers. No emojis or casual language."""

    intro = query_ai(client, intro_prompt, "introduction", 600)
    
    if not intro:
        intro = f"""When building {repo_name}, the primary challenge was implementing {concept_text.lower()} in a way that balances performance, maintainability, and scalability. This required careful consideration of algorithmic complexity, data structure selection, and system architecture.

The implementation leverages {code_data.get('technical_summary', {}).get('primary_language', 'modern')} to create a robust solution that handles edge cases while maintaining clean, testable code. The architecture follows best practices for {concept_text.lower()}, with clear separation of concerns and modular design.

In this technical analysis, we'll examine the actual implementation details, walking through key code sections and explaining the engineering decisions behind them. We'll cover architecture, algorithms, and optimization strategies used in production."""
    
    # Generate Main Technical Content
    print("Generating main content...")
    
    # Build snippet summary for AI
    snippet_summaries = []
    for s in snippets[:4]:
        snippet_summaries.append(f"- {s['type'].title()}: {s['name']} ({s['language']}, {s['lines']} lines)")
    
    main_prompt = f"""Write technical content analyzing this software project: {repo_name}

{code_context}

Key code components available:
{chr(10).join(snippet_summaries)}

Write 5-6 detailed paragraphs covering:
1. System Architecture: Overall design and component organization
2. Core Algorithms: Key algorithmic approaches and data structures
3. Implementation Details: Specific technical implementation choices
4. Performance Optimization: How the code achieves efficiency
5. Error Handling: Robustness and edge case management
6. Extensibility: How the design supports future modifications

Be highly technical. Reference actual implementation patterns. Use precise technical terminology. Write for senior engineers."""

    main_content = query_ai(client, main_prompt, "main content", 1200)
    
    if not main_content:
        main_content = f"""The architecture of {repo_name} follows a modular design with clear separation between data processing, business logic, and presentation layers. Each module is designed with single responsibility in mind, making the codebase maintainable and testable.

Core algorithms leverage efficient data structures to achieve optimal time complexity. Hash-based lookups provide O(1) access times for frequent operations, while tree structures handle hierarchical data efficiently. The implementation carefully balances memory usage against computational speed.

Implementation details reveal thoughtful engineering decisions. Type safety is enforced through static typing, reducing runtime errors. The code includes comprehensive input validation and clear error messages. Asynchronous operations are used judiciously to prevent blocking on I/O operations.

Performance optimization focuses on hotspots identified through profiling. Caching strategies reduce redundant computations, while lazy evaluation defers expensive operations until necessary. Memory allocation is minimized through object pooling and efficient data structure choices.

Error handling follows fail-fast principles with explicit exception types. The code validates assumptions early and provides clear error messages with context. Logging is structured and includes sufficient detail for debugging production issues.

The extensibility of the design comes from its use of interfaces and dependency injection. New features can be added without modifying existing code. The plugin architecture allows for customization points without cluttering the core implementation."""
    
    # Generate Conclusion
    print("Generating conclusion...")
    conclusion_prompt = f"""Write a conclusion for this technical blog post about {repo_name}.

Summarize in 2-3 paragraphs:
1. Key technical insights from the code analysis
2. Practical takeaways for engineers
3. End with a technical question or topic for discussion

Be concise and actionable. Professional tone."""

    conclusion = query_ai(client, conclusion_prompt, "conclusion", 400)
    
    if not conclusion:
        conclusion = f"""The implementation of {repo_name} demonstrates solid software engineering principles applied to real-world problems. From architectural decisions to algorithmic choices, the code reflects careful consideration of trade-offs between performance, maintainability, and scalability.

For engineers working on similar systems, the key takeaways include the importance of profiling before optimizing, the value of clear error messages, and the benefits of modular design. These patterns are applicable across different domains and programming languages.

How would you approach optimizing the most performance-critical components while maintaining code clarity? What trade-offs would you make between memory usage and computational speed in your specific context?"""
    
    # Format code sections
    code_sections = format_code_sections(snippets[:6])
    
    # Combine all content
    full_content = f"""{intro}

{main_content}

{code_sections}

{conclusion}"""
    
    # Generate excerpt
    excerpt = intro.split('.')[0][:150] + "..."
    
    # Generate tags
    tags = ['Technical', 'Engineering', 'Code Analysis']
    if concepts:
        tags.extend([c.replace('_', ' ').title() for c in concepts[:2]])
    tags = list(set(tags))[:5]
    
    return {
        "title": title,
        "content": full_content,
        "excerpt": excerpt,
        "tags": tags,
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "metadata": {
            "repository": repo_name,
            "code_snippets_count": len(snippets),
            "concepts": concepts,
            "generated_by": "AI Agent - Technical",
            "generation_date": datetime.now().isoformat(),
        }
    }

def format_code_sections(snippets: List[Dict]) -> str:
    """Format code snippets for blog"""
    
    if not snippets:
        return ""
    
    sections = ["\n## Code Analysis\n"]
    sections.append("Let's examine the key implementations:\n")
    
    for i, snippet in enumerate(snippets, 1):
        code = snippet['code']
        language = snippet['language']
        name = snippet.get('name', 'Implementation')
        file = snippet.get('file', 'source')
        snippet_type = snippet.get('type', 'code')
        
        # Clean code
        lines = code.split('\n')
        cleaned = []
        for line in lines[:35]:  # Max 35 lines per snippet
            if line.strip() or (cleaned and cleaned[-1].strip()):
                cleaned.append(line)
        
        code = '\n'.join(cleaned).rstrip()
        
        sections.append(f"""### {i}. {snippet_type.title()}: {name}

**Source**: `{file}`

```{language}
{code}
```

""")
    
    return '\n'.join(sections)

def generate_generic_blog(context: Dict, client: InferenceClient) -> Dict:
    """Generate generic blog when no code analysis available"""
    
    print("  Generating generic technical blog...")
    
    categories = context.get('categories', {}).get('category_statistics', {})
    topic = list(categories.keys())[0] if categories else "Software Engineering"
    
    title = f"Technical Insights: {topic} Best Practices"
    
    intro_prompt = f"""Write a technical introduction about {topic} best practices.
3 paragraphs for experienced engineers. Technical tone."""
    
    intro = query_ai(client, intro_prompt, "introduction", 500) or f"Technical article about {topic}."
    
    main_prompt = f"""Write 4-5 paragraphs about {topic} implementation best practices.
Cover architecture, patterns, and optimization. Technical detail."""
    
    main = query_ai(client, main_prompt, "main", 1000) or f"Details about {topic} implementation."
    
    conclusion = "Apply these patterns to build robust, scalable systems. Consider your specific requirements and constraints when making architectural decisions."
    
    full_content = f"{intro}\n\n{main}\n\n{conclusion}"
    
    return {
        "title": title,
        "content": full_content,
        "excerpt": intro.split('.')[0][:150] + "...",
        "tags": [topic, "Technical", "Engineering"],
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "metadata": {
            "generated_by": "AI Agent - Generic",
            "generation_date": datetime.now().isoformat(),
        }
    }

def main():
    """Main blog generation function"""
    try:
        print("Starting technical blog generation...")
        
        # Load context
        print("\nLoading context data...")
        context = load_context_data()
        
        # Initialize AI client
        api_key = os.getenv("HF_API_KEY") or os.getenv("HF_TOKEN")
        if not api_key:
            raise ValueError("HF_API_KEY required")
        
        client = InferenceClient(token=api_key)
        
        # Generate blog
        print("\nGenerating blog content with AI...")
        blog_post = generate_technical_blog(context, client)
        
        # Save
        output_file = DATA_DIR / "blog_post.json"
        with open(output_file, 'w') as f:
            json.dump(blog_post, f, indent=2)
        
        print(f"\nBlog post generated successfully!")
        print(f"Saved to: {output_file}")
        
        # Summary
        print("\n" + "="*60)
        print("GENERATED BLOG POST")
        print("="*60)
        print(f"Title: {blog_post['title']}")
        print(f"Length: {len(blog_post['content'])} characters")
        print(f"Tags: {', '.join(blog_post['tags'])}")
        if blog_post.get('metadata', {}).get('code_snippets_count'):
            print(f"Code Snippets: {blog_post['metadata']['code_snippets_count']}")
        print("="*60)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
