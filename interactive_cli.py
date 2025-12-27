#!/usr/bin/env python3
"""
Simple interactive CLI for testing Ethika Chat RAG system.
"""
import sys
from rag_system import RAGSystem
from advanced_curriculum_generator import AdvancedCurriculumGenerator


def print_header():
    """Print welcome header."""
    print("\n" + "=" * 80)
    print("ETHIKA CHAT - Interactive RAG System")
    print("=" * 80)
    print()


def print_menu():
    """Print main menu options."""
    print("\n" + "-" * 80)
    print("MAIN MENU")
    print("-" * 80)
    print("1. Search for resources")
    print("2. Generate curriculum")
    print("3. List all resources")
    print("4. Exit")
    print("-" * 80)
    print()


def search_resources(rag):
    """Interactive resource search."""
    print("\n" + "=" * 80)
    print("SEARCH RESOURCES")
    print("=" * 80)
    
    query = input("\nEnter your search query: ").strip()
    if not query:
        print("Query cannot be empty!")
        return
    
    # Optional filters
    print("\nOptional filters (press Enter to skip):")
    institution = input("Institution filter: ").strip() or None
    target_audience_input = input("Target audience (comma-separated, e.g., elementary,middle_school): ").strip()
    target_audience = [a.strip() for a in target_audience_input.split(",")] if target_audience_input else None
    
    tags_input = input("Tags (comma-separated, e.g., machine_learning,ethics): ").strip()
    tags = [t.strip() for t in tags_input.split(",")] if tags_input else None
    
    limit_input = input("Number of results (default: 5): ").strip()
    limit = int(limit_input) if limit_input.isdigit() else 5
    
    print(f"\n🔍 Searching for: '{query}'...")
    print()
    
    try:
        results = rag.search(
            query=query,
            limit=limit,
            institution=institution,
            target_audience=target_audience,
            tags=tags
        )
        
        if not results:
            print("❌ No results found.")
            return
        
        print(f"✅ Found {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            title = metadata.get('title', 'Untitled')
            author = metadata.get('author', 'Unknown')
            url = metadata.get('url', '')
            distance = result.get('distance')
            score = f" (similarity: {1 - distance:.3f})" if distance is not None else ""
            
            print(f"{i}. {title}{score}")
            print(f"   Author: {author}")
            if url:
                print(f"   URL: {url}")
            
            # Show tags if available
            tags_str = metadata.get('tags', '[]')
            if tags_str and tags_str != '[]':
                import json
                try:
                    tags_list = json.loads(tags_str) if isinstance(tags_str, str) else tags_str
                    if tags_list:
                        print(f"   Tags: {', '.join(tags_list)}")
                except:
                    pass
            
            print()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def generate_curriculum(rag):
    """Interactive curriculum generation."""
    print("\n" + "=" * 80)
    print("GENERATE CURRICULUM")
    print("=" * 80)
    
    institution = input("\nInstitution name: ").strip()
    if not institution:
        print("Institution name is required!")
        return
    
    target_audience_input = input("Target audience (comma-separated, e.g., elementary,middle_school): ").strip()
    if not target_audience_input:
        print("Target audience is required!")
        return
    target_audience = [a.strip() for a in target_audience_input.split(",")]
    
    topics_input = input("Topics (comma-separated, e.g., machine_learning,ethics): ").strip()
    if not topics_input:
        print("Topics are required!")
        return
    topics = [t.strip() for t in topics_input.split(",")]
    
    duration_input = input("Duration in hours (default: 2.0): ").strip()
    duration = float(duration_input) if duration_input.replace('.', '').isdigit() else 2.0
    
    use_advanced = input("Use advanced LLM generation? (y/n, default: n): ").strip().lower() == 'y'
    
    print(f"\n📚 Generating curriculum for {institution}...")
    print()
    
    try:
        if use_advanced:
            generator = AdvancedCurriculumGenerator(rag, use_llm=True)
            curriculum = generator.generate_detailed_curriculum(
                institution=institution,
                target_audience=target_audience,
                topics=topics,
                duration_hours=duration
            )
        else:
            curriculum = rag.generate_curriculum(
                institution=institution,
                target_audience=target_audience,
                topics=topics,
                duration_hours=duration
            )
        
        print("✅ Curriculum generated!\n")
        print("=" * 80)
        print("CURRICULUM SUMMARY")
        print("=" * 80)
        print(f"Institution: {curriculum['institution']}")
        print(f"Target Audience: {', '.join(curriculum['target_audience'])}")
        print(f"Topics: {', '.join(curriculum['topics'])}")
        print(f"Duration: {curriculum['duration_hours']} hours")
        print(f"Resources: {len(curriculum['resources'])}")
        
        print("\n📋 Selected Resources:")
        for i, resource in enumerate(curriculum['resources'], 1):
            metadata = resource['metadata']
            title = metadata.get('title', 'Untitled')
            author = metadata.get('author', 'Unknown')
            print(f"  {i}. {title} (by {author})")
        
        if 'detailed_content' in curriculum and use_advanced:
            content = curriculum['detailed_content']
            print("\n📖 Detailed Content:")
            print(f"Overview: {content.get('overview', 'N/A')}")
            print("\nLearning Objectives:")
            for obj in content.get('learning_objectives', []):
                print(f"  - {obj}")
        
        print("\n" + "=" * 80)
        
        save = input("\nSave curriculum to file? (y/n): ").strip().lower()
        if save == 'y':
            filename = input("Filename (default: curriculum.json): ").strip() or "curriculum.json"
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(curriculum, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved to {filename}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def list_all_resources(rag):
    """List all resources in the database."""
    print("\n" + "=" * 80)
    print("ALL RESOURCES")
    print("=" * 80)
    
    limit_input = input("\nLimit (press Enter for all): ").strip()
    limit = int(limit_input) if limit_input.isdigit() else None
    
    print("\n📚 Fetching resources...")
    
    try:
        resources = rag.get_all_resources(limit=limit)
        
        if not resources:
            print("❌ No resources found in database.")
            print("💡 Run 'python setup_rag.py --resources-dir ./resources' first!")
            return
        
        print(f"\n✅ Found {len(resources)} resources:\n")
        for i, resource in enumerate(resources, 1):
            metadata = resource['metadata']
            title = metadata.get('title', 'Untitled')
            author = metadata.get('author', 'Unknown')
            print(f"{i}. {title} (by {author})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main interactive loop."""
    print_header()
    
    # Check if vector database exists
    import os
    if not os.path.exists('./vector_db'):
        print("⚠️  Vector database not found!")
        print("💡 Please run: python setup_rag.py --resources-dir ./resources")
        print()
        setup = input("Would you like to set it up now? (y/n): ").strip().lower()
        if setup == 'y':
            resources_dir = input("Resources directory (default: ./resources): ").strip() or "./resources"
            print(f"\n🔧 Setting up RAG system with resources from: {resources_dir}")
            from setup_rag import main as setup_main
            import sys
            sys.argv = ['setup_rag.py', '--resources-dir', resources_dir]
            try:
                setup_main()
            except Exception as e:
                print(f"❌ Setup failed: {e}")
                return
        else:
            return
    
    # Initialize RAG system
    print("\n🔧 Initializing RAG system...")
    try:
        rag = RAGSystem()
        print("✅ RAG system initialized!\n")
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Main loop
    while True:
        print_menu()
        choice = input("Select an option (1-4): ").strip()
        
        if choice == '1':
            search_resources(rag)
        elif choice == '2':
            generate_curriculum(rag)
        elif choice == '3':
            list_all_resources(rag)
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please select 1-4.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)

