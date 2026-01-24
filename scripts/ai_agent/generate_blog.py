#!/usr/bin/env python3
"""
AI Agent - Technical Blog Generator with Code Snippets
Generates in-depth technical blog posts with actual code from repositories
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
    """Load all context data including code analysis"""
    context = {}
    
    files = {
        'analysis': 'repository_analysis.json',
        'categories': 'project_categories.json',
        'featured': 'featured_project.json',
        'code_analysis': 'code_analysis.json',
    }
    
    for key, filename in files.items():
        filepath = DATA_DIR / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                context[key] = json.load(f)
    
    return context

def select_technical_topic(context: Dict) -> tuple:
    """Select a technical blog topic based on code analysis"""
    
    if 'code_analysis' not in context:
        # Fallback to category-based selection
        return select_category_topic(context)
    
    code_data = context['code_analysis']
    
    # Find repos with substantial code
    substantial_repos = []
    for repo_name, analysis in code_data.items():
        if analysis.get('files_analyzed', 0) > 5:
            substantial_repos.append((repo_name, analysis))
    
    if not substantial_repos:
        return select_category_topic(context)
    
    # Select random repo
    repo_name, analysis = random.choice(substantial_repos)
    repo_short = repo_name.split('/')[-1]
    
    # Get main concepts
    concepts = analysis.get('concepts', {})
    main_concept = list(concepts.keys())[0] if concepts else 'programming'
    
    # Generate technical topics
    topics = [
        ("technical_deep_dive", repo_short, f"Deep Dive: Building {repo_short} - Architecture and Implementation"),
        ("code_explained", repo_short, f"Code Walkthrough: Understanding {repo_short}'s Core Components"),
        ("technical_patterns", main_concept, f"Design Patterns in {main_concept.replace('_', ' ').title()}: Lessons from {repo_short}"),
        ("implementation_guide", repo_short, f"Implementation Guide: Key Algorithms in {repo_short}"),
    ]
    
    return random.choice(topics)

def select_category_topic(context: Dict) -> tuple:
    """Fallback topic selection"""
    categories = context.get('categories', {}).get('category_statistics', {})
    if categories:
        cat = list(categories.keys())[0]
        return ("category", cat, f"Technical Overview: {cat}")
    return ("general", "ML", "Machine Learning Engineering Best Practices")

def get_relevant_code_snippets(context: Dict, topic_type: str, subject: str) -> List[Dict]:
    """Get relevant code snippets for the blog topic"""
    
    if 'code_analysis' not in context:
        return []
    
    code_data = context['code_analysis']
    snippets = []
    
    for repo_name, analysis in code_data.items():
        repo_short = repo_name.split('/')[-1]
        
        # Match repo or concept
        if topic_type in ['technical_deep_dive', 'code_explained', 'implementation_guide']:
            if subject.lower() not in repo_short.lower():
                continue
        
        # Get code samples
        for sample in analysis.get('code_samples', [])[:5]:
            snippets.append({
                **sample,
                'repo': repo_short,
                'full_repo': repo_name
            })
    
    return snippets[:10]  # Top 10 snippets

def format_code_snippet(snippet: Dict) -> str:
    """Format code snippet for blog"""
    code = snippet['code']
    language = snippet['language']
    name = snippet.get('name', 'Code')
    file = snippet.get('file', '')
    
    # Clean code
    lines = code.split('\n')
    # Remove excessive blank lines
    cleaned_lines = []
    prev_blank = False
    for line in lines:
        if line.strip():
            cleaned_lines.append(line)
            prev_blank = False
        elif not prev_blank:
            cleaned_lines.append(line)
            prev_blank = True
    
    code = '\n'.join(cleaned_lines[:30])  # Max 30 lines
    
    return f"""### {name}
**File**: `{file}`

```{language}
{code}
```
"""

def query_ai_for_technical_blog(client: InferenceClient, prompt: str, section: str) -> str:
    """Query AI for blog content with technical focus"""
    
    for attempt, model in enumerate(MODELS):
        try:
            print(f"   🤖 Querying {model.split('/')[-1]} for {section}...")
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200 if section == "main" else 500,
                temperature=0.7,
            )
            
            if response and response.choices:
                content = response.choices[0].message.content.strip()
                
                if len(content) > 300:
                    print(f"   ✅ Generated {len(content)} characters")
                    return content
                    
        except Exception as e:
            if "503" in str(e).lower() or "loading" in str(e).lower():
                wait = 15 * (attempt + 1)
                print(f"   ⏳ Model loading, waiting {wait}s...")
                time.sleep(wait)
                continue
            print(f"   ⚠️ Error: {str(e)[:100]}")
    
    return ""

def generate_technical_introduction(client: InferenceClient, title: str, context: Dict, snippets: List[Dict]) -> str:
    """Generate technical blog introduction"""
    
    # Build context about code
    code_context = ""
    if snippets:
        languages = set(s['language'] for s in snippets)
        concepts = []
        if 'code_analysis' in context:
            for analysis in context['code_analysis'].values():
                concepts.extend(analysis.get('concepts', {}).keys())
        concepts = list(set(concepts))[:5]
        
        code_context = f"""
Technical Context:
- Languages: {', '.join(languages)}
- Key Concepts: {', '.join(concepts) if concepts else 'Software Architecture'}
- Code Samples Available: {len(snippets)}
"""
    
    prompt = f"""Write a compelling technical introduction for a blog post titled: "{title}"

{code_context}

Context: You're a Machine Learning Engineer writing an in-depth technical article. This will include actual code examples and implementation details.

Write a 3-4 paragraph introduction that:
1. Opens with a technical challenge or interesting problem
2. Explains why this topic matters for software engineers
3. Previews the technical concepts that will be covered
4. Mentions that actual code examples will be analyzed

Write in a technical but engaging tone. Be specific about technical challenges. No headers or bullet points."""

    content = query_ai_for_technical_blog(client, prompt, "introduction")
    
    if not content:
        content = f"""Building robust software systems requires deep understanding of both architecture and implementation. In this technical deep dive, we'll explore {title.lower()}, examining real code and discussing the engineering decisions that make it work.

Whether you're building production ML systems, designing scalable architectures, or optimizing performance-critical code, understanding these patterns is essential. We'll go beyond theory and look at actual implementations, discussing trade-offs and best practices along the way.

This article includes code walkthroughs, architectural diagrams, and practical insights from real-world projects. Let's dive into the technical details."""
    
    return content

def generate_technical_main_content(client: InferenceClient, title: str, context: Dict, snippets: List[Dict]) -> str:
    """Generate main technical content with code analysis"""
    
    # Build code examples text
    code_examples_text = ""
    if snippets:
        snippet_summaries = []
        for s in snippets[:3]:
            snippet_summaries.append(f"- {s.get('name', 'Function')} ({s['language']}): {s['type']} with {s['lines']} lines")
        code_examples_text = "\n".join(snippet_summaries)
    
    prompt = f"""Write the main technical content for: "{title}"

Available code examples to reference:
{code_examples_text if code_examples_text else 'General software architecture patterns'}

Write 5-6 detailed paragraphs covering:
1. **Core Architecture**: Explain the system architecture and design decisions
2. **Key Components**: Describe the main components and their responsibilities
3. **Implementation Details**: Discuss specific implementation approaches
4. **Technical Challenges**: Explain challenges faced and how they were solved
5. **Performance Considerations**: Discuss optimization and scalability
6. **Best Practices**: Share engineering best practices learned

Use technical language appropriate for experienced developers. Reference actual implementation patterns. Include specific technical details like algorithms, data structures, or design patterns used.

Write in flowing paragraphs, not bullet points. Be technically precise."""

    content = query_ai_for_technical_blog(client, prompt, "main")
    
    if not content:
        content = """The architecture follows a modular design with clear separation of concerns. At its core, the system leverages object-oriented principles to ensure maintainability and extensibility. Each component is designed with a single responsibility, making the codebase easier to test and debug.

Implementation details reveal interesting choices in data structure selection and algorithm optimization. For instance, the use of hash maps for O(1) lookups combined with careful memory management ensures both speed and efficiency. These decisions weren't arbitrary—they emerged from profiling and iterative optimization.

One of the key technical challenges involved balancing flexibility with performance. The initial implementation used a naive approach that was simple but slow. Through careful refactoring and the introduction of caching strategies, we achieved a 10x performance improvement while maintaining code clarity.

The system's scalability comes from its asynchronous design and efficient resource pooling. By leveraging concurrent processing and minimizing I/O blocking, the architecture can handle significant load without degradation. This required careful attention to thread safety and race conditions.

From a best practices perspective, the code demonstrates strong typing, comprehensive error handling, and extensive unit testing. These aren't just nice-to-haves—they're essential for production systems that need to be reliable and maintainable over time."""
    
    return content

def generate_code_sections(snippets: List[Dict]) -> str:
    """Generate code walkthrough sections"""
    
    if not snippets:
        return ""
    
    sections = ["\n## Code Walkthrough\n"]
    sections.append("Let's examine some key implementations:\n")
    
    for snippet in snippets[:4]:  # Include top 4 snippets
        sections.append(format_code_snippet(snippet))
        sections.append("")  # Blank line
    
    return "\n".join(sections)

def generate_technical_conclusion(client: InferenceClient, title: str, has_code: bool) -> str:
    """Generate technical conclusion"""
    
    prompt = f"""Write a conclusion for a technical blog post: "{title}"

{'The article included actual code examples and implementation details.' if has_code else ''}

Write 2-3 paragraphs that:
1. Summarize the key technical insights
2. Encourage readers to explore the code and try implementations
3. End with a thought-provoking question about future directions

Be technical but inspiring."""

    content = query_ai_for_technical_blog(client, prompt, "conclusion")
    
    if not content:
        content = """The technical patterns we've explored demonstrate the importance of thoughtful system design. From architectural decisions to implementation details, each choice impacts performance, maintainability, and scalability. These aren't just academic exercises—they're practical considerations that shape real-world software.

I encourage you to explore the code, experiment with the implementations, and adapt these patterns to your own projects. The best way to truly understand these concepts is through hands-on practice and iteration.

What engineering challenges are you currently facing? How might these patterns apply to your work? Share your experiences and let's continue the conversation."""
    
    return content

def main():
    """Main technical blog generation function"""
    try:
        print("📝 Starting technical blog generation with code analysis...")
        
        # Load context
        print("\n📚 Loading context data...")
        context = load_context_data()
        
        # Select topic
        print("\n🎯 Selecting technical topic...")
        topic_type, subject, title = select_technical_topic(context)
        print(f"   ✅ Topic: {title}")
        print(f"   Type: {topic_type} | Subject: {subject}")
        
        # Get relevant code snippets
        print("\n💻 Finding relevant code snippets...")
        snippets = get_relevant_code_snippets(context, topic_type, subject)
        print(f"   ✅ Found {len(snippets)} code snippets")
        
        # Initialize AI client
        api_key = os.getenv("HF_API_KEY") or os.getenv("HF_TOKEN")
        if not api_key:
            raise ValueError("HF_API_KEY required for blog generation")
        
        client = InferenceClient(token=api_key)
        
        # Generate blog sections
        print("\n✍️  Generating technical blog content...")
        
        print("\n📖 Section 1/3: Technical Introduction")
        intro = generate_technical_introduction(client, title, context, snippets)
        
        print("\n📖 Section 2/3: Main Technical Content")
        main = generate_technical_main_content(client, title, context, snippets)
        
        print("\n📖 Section 3/3: Code Examples")
        code_sections = generate_code_sections(snippets)
        
        print("\n📖 Section 4/4: Conclusion")
        conclusion = generate_technical_conclusion(client, title, len(snippets) > 0)
        
        # Combine content
        full_content = f"""{intro}

{main}

{code_sections}

{conclusion}"""
        
        # Generate excerpt
        excerpt = intro.split('.')[0][:150] + "..."
        
        # Generate tags
        tags = ['Engineering', 'Code', 'Tech']
        if topic_type != 'general':
            tags.append(subject)
        if snippets:
            tags.extend([s['language'].title() for s in snippets[:2]])
        tags = list(set(tags))[:5]
        
        # Format blog post
        blog_post = {
            "title": title,
            "content": full_content,
            "excerpt": excerpt,
            "tags": tags,
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "metadata": {
                "topic_type": topic_type,
                "subject": subject,
                "code_snippets_count": len(snippets),
                "generated_by": "AI Agent - Technical",
                "generation_date": datetime.now().isoformat(),
            }
        }
        
        # Save
        output_file = DATA_DIR / "blog_post.json"
        with open(output_file, 'w') as f:
            json.dump(blog_post, f, indent=2)
        
        print(f"\n✅ Technical blog post generated!")
        print(f"💾 Saved to {output_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("📝 GENERATED TECHNICAL BLOG POST")
        print("="*60)
        print(f"Title: {blog_post['title']}")
        print(f"Tags: {', '.join(blog_post['tags'])}")
        print(f"Length: {len(blog_post['content'])} characters")
        print(f"Code Snippets: {len(snippets)}")
        print(f"\nExcerpt:\n{blog_post['excerpt']}")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
