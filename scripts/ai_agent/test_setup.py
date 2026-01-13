#!/usr/bin/env python3
"""
Test Setup Script
Verifies all dependencies and API credentials are working
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test all required imports"""
    print("🧪 Testing imports...")
    
    try:
        import requests
        print("  ✅ requests")
    except ImportError as e:
        print(f"  ❌ requests: {e}")
        return False
    
    try:
        from huggingface_hub import InferenceClient
        print("  ✅ huggingface_hub")
    except ImportError as e:
        print(f"  ❌ huggingface_hub: {e}")
        return False
    
    try:
        from github import Github
        print("  ✅ PyGithub")
    except ImportError as e:
        print(f"  ❌ PyGithub: {e}")
        return False
    
    try:
        import jwt
        print("  ✅ PyJWT")
    except ImportError as e:
        print(f"  ❌ PyJWT: {e}")
        return False
    
    try:
        import networkx
        print("  ✅ networkx")
    except ImportError as e:
        print(f"  ❌ networkx: {e}")
        return False
    
    try:
        from pyvis.network import Network
        print("  ✅ pyvis")
    except ImportError as e:
        print(f"  ❌ pyvis: {e}")
        return False
    
    print("\n✅ All imports successful!\n")
    return True

def test_environment():
    """Test environment variables"""
    print("🔑 Testing environment variables...")
    
    required_vars = {
        'GITHUB_TOKEN': False,
        'HF_API_KEY': False,
        'GHOST_ADMIN_API_KEY': False,
    }
    
    for var in required_vars.keys():
        value = os.getenv(var)
        if value:
            required_vars[var] = True
            print(f"  ✅ {var}: {'*' * 20} (set)")
        else:
            print(f"  ⚠️  {var}: Not set")
    
    print()
    
    if not required_vars['GITHUB_TOKEN']:
        print("⚠️  GITHUB_TOKEN not set (required for GitHub Actions)")
    
    if not required_vars['HF_API_KEY']:
        print("⚠️  HF_API_KEY not set (required for AI features)")
    
    if not required_vars['GHOST_ADMIN_API_KEY']:
        print("⚠️  GHOST_ADMIN_API_KEY not set (required for blog publishing)")
    
    return any(required_vars.values())

def test_ghost_credentials():
    """Test Ghost API credentials"""
    print("👻 Testing Ghost CMS credentials...")
    
    admin_key = os.getenv('GHOST_ADMIN_API_KEY')
    
    if not admin_key:
        print("  ⚠️  GHOST_ADMIN_API_KEY not set, skipping test")
        return True
    
    try:
        import jwt
        import requests
        from datetime import datetime as dt
        
        # Split key
        if ':' not in admin_key:
            print("  ❌ Invalid key format (should be id:secret)")
            return False
        
        id_part, secret_part = admin_key.split(':')
        
        # Generate JWT
        iat = int(dt.now().timestamp())
        header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id_part}
        payload = {'iat': iat, 'exp': iat + 300, 'aud': '/admin/'}
        
        token = jwt.encode(payload, bytes.fromhex(secret_part), algorithm='HS256', headers=header)
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        
        # Test API call
        api_url = "https://synexian.ghost.io/ghost/api/v5.0/admin/site/"
        headers = {
            'Authorization': f'Ghost {token}',
            'Accept-Version': 'v5.0'
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("  ✅ Ghost API credentials valid")
            site_data = response.json()
            print(f"  ℹ️  Site: {site_data.get('site', {}).get('title', 'Unknown')}")
            return True
        else:
            print(f"  ❌ Ghost API returned status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"  ❌ Ghost test failed: {e}")
        return False

def test_huggingface():
    """Test Hugging Face API"""
    print("🤗 Testing Hugging Face API...")
    
    api_key = os.getenv('HF_API_KEY') or os.getenv('HF_TOKEN')
    
    if not api_key:
        print("  ⚠️  HF_API_KEY not set, skipping test")
        return True
    
    try:
        from huggingface_hub import InferenceClient
        
        client = InferenceClient(token=api_key)
        
        # Try a simple inference
        response = client.chat.completions.create(
            model="microsoft/Phi-3-mini-4k-instruct",
            messages=[{"role": "user", "content": "Say 'test successful' in 2 words"}],
            max_tokens=10,
            temperature=0.1,
        )
        
        if response and response.choices:
            print("  ✅ Hugging Face API working")
            return True
        else:
            print("  ⚠️  Hugging Face API returned empty response")
            return False
            
    except Exception as e:
        error_str = str(e).lower()
        if "503" in error_str or "loading" in error_str:
            print("  ⚠️  Model loading (this is normal)")
            return True
        print(f"  ❌ Hugging Face test failed: {e}")
        return False

def test_github():
    """Test GitHub API"""
    print("🐙 Testing GitHub API...")
    
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("  ⚠️  GITHUB_TOKEN not set, skipping test")
        return True
    
    try:
        from github import Github
        
        g = Github(token)
        user = g.get_user()
        
        print(f"  ✅ GitHub API working")
        print(f"  ℹ️  Authenticated as: {user.login}")
        print(f"  ℹ️  Rate limit: {g.get_rate_limit().core.remaining}/5000")
        
        return True
        
    except Exception as e:
        print(f"  ❌ GitHub test failed: {e}")
        return False

def test_data_directory():
    """Test data directory"""
    print("📁 Testing data directory...")
    
    data_dir = Path(__file__).parent / "data"
    
    if data_dir.exists():
        print(f"  ✅ Data directory exists: {data_dir}")
        
        # List files
        files = list(data_dir.glob("*.json"))
        if files:
            print(f"  ℹ️  Found {len(files)} JSON files:")
            for f in files:
                print(f"     - {f.name}")
        else:
            print("  ℹ️  No JSON files (this is normal for first run)")
    else:
        print(f"  ℹ️  Creating data directory: {data_dir}")
        data_dir.mkdir(parents=True, exist_ok=True)
        print("  ✅ Data directory created")
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("🔬 AI AGENT SETUP TEST")
    print("=" * 60)
    print()
    
    results = {
        "Imports": test_imports(),
        "Environment": test_environment(),
        "Data Directory": test_data_directory(),
        "Ghost CMS": test_ghost_credentials(),
        "Hugging Face": test_huggingface(),
        "GitHub": test_github(),
    }
    
    print()
    print("=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test:20} {status}")
    
    print("=" * 60)
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Ready to run the AI agent.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
