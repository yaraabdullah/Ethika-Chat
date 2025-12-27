"""
Example usage of the RAG system.
"""
from rag_system import RAGSystem
from advanced_curriculum_generator import AdvancedCurriculumGenerator


def example_basic_search():
    """Example: Basic search functionality."""
    print("=" * 80)
    print("EXAMPLE 1: Basic Search")
    print("=" * 80)
    
    rag = RAGSystem()
    
    # Search for resources
    results = rag.search(
        query="interactive machine learning activities for elementary students",
        limit=5
    )
    
    print(f"\nFound {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        print(f"{i}. {metadata.get('title', 'Untitled')}")
        print(f"   Author: {metadata.get('author', 'Unknown')}")
        print(f"   URL: {metadata.get('url', 'N/A')}")
        print()


def example_filtered_search():
    """Example: Search with filters."""
    print("=" * 80)
    print("EXAMPLE 2: Filtered Search")
    print("=" * 80)
    
    rag = RAGSystem()
    
    # Search with filters
    results = rag.search(
        query="AI ethics and bias",
        limit=5,
        target_audience=["middle_school"],
        tags=["bias", "ethics"],
        resource_type=["activity", "interactive"]
    )
    
    print(f"\nFound {len(results)} filtered results:\n")
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        print(f"{i}. {metadata.get('title', 'Untitled')}")
        print(f"   Target: {metadata.get('target_audience', 'N/A')}")
        print()


def example_basic_curriculum():
    """Example: Generate basic curriculum."""
    print("=" * 80)
    print("EXAMPLE 3: Basic Curriculum Generation")
    print("=" * 80)
    
    rag = RAGSystem()
    
    curriculum = rag.generate_curriculum(
        institution="Carnegie Mellon University",
        target_audience=["elementary", "middle_school"],
        topics=["machine_learning", "bias"],
        duration_hours=2.0,
        preferred_types=["activity", "interactive"]
    )
    
    print(f"\nGenerated curriculum for {curriculum['institution']}")
    print(f"Topics: {', '.join(curriculum['topics'])}")
    print(f"Resources: {len(curriculum['resources'])}")
    print("\nResources:")
    for i, resource in enumerate(curriculum['resources'], 1):
        metadata = resource['metadata']
        print(f"  {i}. {metadata.get('title', 'Untitled')}")


def example_advanced_curriculum():
    """Example: Generate advanced curriculum with LLM."""
    print("=" * 80)
    print("EXAMPLE 4: Advanced Curriculum Generation (with LLM)")
    print("=" * 80)
    
    rag = RAGSystem()
    generator = AdvancedCurriculumGenerator(rag, use_llm=True)
    
    curriculum = generator.generate_detailed_curriculum(
        institution="MIT",
        target_audience=["middle_school"],
        topics=["machine_learning", "ethics"],
        duration_hours=3.0,
        learning_objectives=[
            "Understand basic machine learning concepts",
            "Recognize bias in AI systems",
            "Create a simple machine learning model"
        ],
        institution_context="Students have basic programming knowledge"
    )
    
    print(f"\nGenerated detailed curriculum for {curriculum['institution']}")
    
    if 'detailed_content' in curriculum:
        content = curriculum['detailed_content']
        print("\nOverview:")
        print(content.get('overview', 'N/A'))
        print("\nLearning Objectives:")
        for obj in content.get('learning_objectives', []):
            print(f"  - {obj}")
        print("\nSchedule:")
        for item in content.get('schedule', []):
            print(f"  {item.get('time', 'N/A')}: {item.get('activity', 'N/A')}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("ETHIKA CHAT - EXAMPLES")
    print("=" * 80 + "\n")
    
    print("Note: Make sure you've run 'python setup_rag.py' first to initialize the database.\n")
    
    # Uncomment the examples you want to run:
    # example_basic_search()
    # example_filtered_search()
    # example_basic_curriculum()
    # example_advanced_curriculum()
    
    print("\nUncomment examples in the script to run them.")

