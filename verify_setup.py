#!/usr/bin/env python3
"""
Verify that the RAG system is set up correctly.
"""
import sys
from pathlib import Path


def check_dependencies():
    """Check if all required packages are installed."""
    print("Checking dependencies...")
    required_packages = [
        'chromadb',
        'sentence_transformers',
        'yaml',
        'fastapi',
        'uvicorn'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'yaml':
                __import__('yaml')
            else:
                __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    else:
        print("\n✓ All dependencies installed")
        return True


def check_structure():
    """Check if project structure is correct."""
    print("\nChecking project structure...")
    required_files = [
        'rag_system.py',
        'markdown_parser.py',
        'setup_rag.py',
        'query_rag.py',
        'generate_curriculum.py'
    ]
    
    all_present = True
    for file in required_files:
        if Path(file).exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (missing)")
            all_present = False
    
    return all_present


def check_resources():
    """Check if resources directory exists and has files."""
    print("\nChecking resources...")
    resources_dir = Path('resources')
    
    if not resources_dir.exists():
        print(f"  ⚠ resources/ directory not found")
        print("  Create it and add your .md files, or use:")
        print("  python copy_resources.py --source /Users/yara/Downloads")
        return False
    
    md_files = list(resources_dir.glob('*.md'))
    if not md_files:
        print(f"  ⚠ No .md files found in resources/")
        print("  Add your markdown resource files to the resources/ directory")
        return False
    
    print(f"  ✓ Found {len(md_files)} markdown files in resources/")
    return True


def check_vector_db():
    """Check if vector database exists."""
    print("\nChecking vector database...")
    vector_db = Path('vector_db')
    
    if not vector_db.exists():
        print("  ⚠ Vector database not initialized")
        print("  Run: python setup_rag.py --resources-dir ./resources")
        return False
    
    # Check if collection exists
    try:
        from rag_system import RAGSystem
        rag = RAGSystem()
        count = len(rag.get_all_resources())
        if count > 0:
            print(f"  ✓ Vector database initialized with {count} resources")
            return True
        else:
            print("  ⚠ Vector database exists but is empty")
            print("  Run: python setup_rag.py --resources-dir ./resources")
            return False
    except Exception as e:
        print(f"  ⚠ Error checking vector database: {e}")
        return False


def main():
    print("=" * 80)
    print("ETHIKA CHAT - SETUP VERIFICATION")
    print("=" * 80)
    
    deps_ok = check_dependencies()
    structure_ok = check_structure()
    resources_ok = check_resources()
    db_ok = check_vector_db()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if deps_ok and structure_ok:
        print("✓ Core system ready")
    else:
        print("✗ Core system issues - fix before proceeding")
        sys.exit(1)
    
    if resources_ok:
        print("✓ Resources available")
    else:
        print("⚠ No resources found - add .md files to resources/")
    
    if db_ok:
        print("✓ Vector database ready")
        print("\n🎉 System is ready to use!")
        print("\nTry:")
        print("  python query_rag.py 'machine learning activities'")
    else:
        print("⚠ Vector database not initialized")
        if resources_ok:
            print("\nTo initialize, run:")
            print("  python setup_rag.py --resources-dir ./resources")


if __name__ == "__main__":
    main()

