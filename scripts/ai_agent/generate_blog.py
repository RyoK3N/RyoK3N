#!/usr/bin/env python3
"""
AI Agent - Tech Blog Generator
Generates comprehensive technical blog posts using AI
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from huggingface_hub import InferenceClient
import time
import random

DATA_DIR = Path(__file__).parent / "data"

MODELS = [
    "meta-llama/Llama-3.2-3B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "microsoft/Phi-3-mini-4k-instruct",
]

BLOG_TOPICS = [
    "Recent developments in Machine Learning",
    "Best practices for {category} development",
    "Lessons learned from building {project}",
    "The future of {category}",
    "Deep dive into {project}",
    "Tips and tricks for {category} engineers",
    "My journey with {category}",
    "Technical challenges in {project}",
]

def load_context_data() -> Dict[str, Any]:
    """Load all context data for blog generation"""
    context = {}
    
    # Load analysis
    analysis_file = DATA_DIR / "repository_analysis.json"
    if analysis_file.exists():
        with open(analysis_file, 'r') as f:
            context['analysis'] = json.load(f)
    
    # Load categories
    categories_file = DATA_DIR / "project_categories.json"
    if categories_file.exists():
        with open(categories_file, 'r') as f:
            context['categories'] = json.load(f)
    
    # Load featured project
    featured_file = DATA_DIR / "featured_project.json"
    if featured_file.exists():
        with open(featured_file, 'r') as f:
            context['featured'] = json.load(f)
    
    return context

def select_blog_topic(context: Dict) -> tuple:
    """Select a blog topic based on context"""
    
    topics = []
    
    # Get top categories
    if 'categories' in context:
        cat_stats = context['categories'].get('category_statistics', {})
        top_categories = sorted(cat_stats.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for cat, _ in top_categories:
            topics.append(("category", cat, f"Best practices for {cat} development"))
            topics.append(("category", cat, f"The future of {cat}"))
    
    # Featured project topic
    if 'featured' in context:
        proj_name = context['featured']['name']
        topics.append(("project", proj_name, f"Deep dive into {proj_name}"))
        topics.append(("project", proj_name, f"Lessons learned from building {proj_name}"))
    
    # General ML topics
    topics.extend([
        ("general", "ML", "Recent developments in Machine Learning and AI"),
        ("general", "ML", "Building production ML systems: Best practices"),
        ("general", "Tech", "My journey as a Machine Learning Engineer"),
    ])
    
    # Random selection
    topic_type, subject, title = random.choice(topics)
    
    return topic_type, subject, title

def query_ai_for_blog(client: InferenceClient, prompt: str, section: str) -> str:
    """Query AI for blog content"""
    
    for attempt, model in enumerate(MODELS):
        try:
            print(f"   🤖 Querying {model.split('/')[-1]} for {section}...")
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800 if section == "main" else 400,
                temperature=0.7,
            )
            
            if response and response.choices:
                content = response.choices[0].message.content.strip()
                
                if len(content) > 200:
                    print(f"   ✅ Generated {len(content)} characters")
                    return content
                    
        except Exception as e:
            error_str = str(e).lower()
            if "503" in error_str or "loading" in error_str:
                wait_time = 15 * (attempt + 1)
                print(f"   ⏳ Model loading, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            print(f"   ⚠️ Error: {str(e)[:100]}")
    
    return ""

def generate_blog_introduction(client: InferenceClient, title: str, context: Dict) -> str:
    """Generate blog introduction"""
    
    prompt = f"""Write an engaging introduction for a technical blog post titled: "{title}"

Context: You're a Machine Learning Engineer sharing insights from your experience.
The blog is on https://synexian.ghost.io

Write a 2-3 paragraph introduction that:
1. Hooks the reader with an interesting opening
2. Provides context for why this topic matters
3. Previews what the reader will learn

Write in a professional yet conversational tone. No headers or bullet points."""

    content = query_ai_for_blog(client, prompt, "introduction")
    
    if not content:
        # Fallback
        content = f"""Technology evolves at breakneck speed, and staying current is both a challenge and an opportunity. Today, I want to share my thoughts on {title.lower()}, drawing from hands-on experience and recent developments in the field.

In this post, we'll explore practical insights, lessons learned, and emerging trends that every developer should be aware of. Whether you're just starting out or are a seasoned professional, there's something here for you."""
    
    return content

def generate_blog_main_content(client: InferenceClient, title: str, topic_type: str, subject: str, context: Dict) -> str:
    """Generate main blog content"""
    
    # Build context-aware prompt
    context_info = ""
    if topic_type == "project" and 'featured' in context:
        featured = context['featured']
        context_info = f"""Project details:
- Name: {featured['name']}
- Description: {featured['description']}
- Technologies: {', '.join(featured['languages'])}
- Categories: {', '.join(featured['categories'])}"""
    
    elif topic_type == "category" and 'categories' in context:
        repos = [r for r in context['categories']['categorized_repositories'] 
                if subject in r['categories']][:5]
        project_names = [r['name'] for r in repos]
        context_info = f"""Related projects in {subject}:
{chr(10).join(f'- {name}' for name in project_names)}"""
    
    prompt = f"""Write the main content for a technical blog post titled: "{title}"

{context_info}

Write 4-5 paragraphs covering:
1. Key concepts and fundamentals
2. Practical examples or case studies
3. Best practices and recommendations
4. Common pitfalls to avoid
5. Future directions or trends

Use a technical but accessible writing style. Include specific details and actionable insights.
No headers, bullet points, or special formatting - just flowing paragraphs."""

    content = query_ai_for_blog(client, prompt, "main")
    
    if not content:
        # Fallback
        content = f"""When working with {subject}, the fundamentals matter immensely. I've learned that a solid understanding of core concepts pays dividends as projects grow in complexity. The key is to balance theoretical knowledge with hands-on practice.

In my experience, the most successful projects share common traits: clean architecture, comprehensive testing, and continuous monitoring. These aren't just buzzwords—they're practical necessities that distinguish production-ready systems from proof-of-concepts.

Looking ahead, the landscape continues to evolve rapidly. New tools and frameworks emerge regularly, each promising to solve yesterday's problems more elegantly. The challenge isn't just keeping up with these developments, but knowing when to adopt new approaches versus sticking with proven solutions.

What matters most is building systems that solve real problems effectively. Whether you're working on cutting-edge research or practical applications, focusing on fundamentals and best practices will serve you well."""
    
    return content

def generate_blog_conclusion(client: InferenceClient, title: str) -> str:
    """Generate blog conclusion"""
    
    prompt = f"""Write a conclusion for a technical blog post titled: "{title}"

Write 2-3 paragraphs that:
1. Summarize the key takeaways
2. Encourage readers to apply what they've learned
3. End with a call to action or thought-provoking question

Conversational and inspiring tone."""

    content = query_ai_for_blog(client, prompt, "conclusion")
    
    if not content:
        # Fallback
        content = """As we've explored, success in this field comes down to continuous learning and practical application. The concepts we've discussed aren't just theoretical—they're tools you can use immediately in your own projects.

I encourage you to experiment, build, and share your own experiences. The best way to truly understand these ideas is to put them into practice. What will you build next?"""
    
    return content

def format_blog_post(title: str, intro: str, main: str, conclusion: str, metadata: Dict) -> Dict:
    """Format blog post with metadata"""
    
    # Combine content
    full_content = f"""{intro}

{main}

{conclusion}"""
    
    # Generate excerpt (first 150 chars)
    excerpt = intro.split('.')[0][:150] + "..."
    
    # Generate tags
    tags = []
    if metadata.get('topic_type') == 'project':
        tags.append(metadata['subject'])
    if metadata.get('topic_type') == 'category':
        tags.append(metadata['subject'])
    
    tags.extend(["Machine Learning", "AI", "Tech", "Engineering"])
    tags = list(set(tags))[:5]  # Max 5 unique tags
    
    return {
        "title": title,
        "content": full_content,
        "excerpt": excerpt,
        "tags": tags,
        "status": "draft",  # Will be published by Ghost script
        "created_at": datetime.now().isoformat(),
        "metadata": metadata,
    }

def main():
    """Main blog generation function"""
    try:
        print("📝 Starting tech blog generation...")
        
        # Load context
        print("\n📚 Loading context data...")
        context = load_context_data()
        
        # Select topic
        print("\n🎯 Selecting blog topic...")
        topic_type, subject, title = select_blog_topic(context)
        print(f"   ✅ Topic: {title}")
        print(f"   Type: {topic_type} | Subject: {subject}")
        
        # Initialize AI client
        api_key = os.getenv("HF_API_KEY") or os.getenv("HF_TOKEN")
        if not api_key:
            raise ValueError("HF_API_KEY required for blog generation")
        
        client = InferenceClient(token=api_key)
        
        # Generate blog sections
        print("\n✍️  Generating blog content with AI...")
        
        print("\n📖 Section 1/3: Introduction")
        intro = generate_blog_introduction(client, title, context)
        
        print("\n📖 Section 2/3: Main Content")
        main = generate_blog_main_content(client, title, topic_type, subject, context)
        
        print("\n📖 Section 3/3: Conclusion")
        conclusion = generate_blog_conclusion(client, title)
        
        # Format blog post
        print("\n🎨 Formatting blog post...")
        blog_post = format_blog_post(
            title, intro, main, conclusion,
            metadata={
                "topic_type": topic_type,
                "subject": subject,
                "generated_by": "AI Agent",
                "generation_date": datetime.now().isoformat(),
            }
        )
        
        # Save
        output_file = DATA_DIR / "blog_post.json"
        with open(output_file, 'w') as f:
            json.dump(blog_post, f, indent=2)
        
        print(f"\n✅ Blog post generated!")
        print(f"💾 Saved to {output_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("📝 GENERATED BLOG POST")
        print("="*60)
        print(f"Title: {blog_post['title']}")
        print(f"Tags: {', '.join(blog_post['tags'])}")
        print(f"Length: {len(blog_post['content'])} characters")
        print(f"\nExcerpt:\n{blog_post['excerpt']}")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
