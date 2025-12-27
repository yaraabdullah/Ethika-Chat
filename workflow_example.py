"""
Complete workflow example: From resources to customized curriculum.
This demonstrates the full pipeline for creating workshop content.
"""
from rag_system import RAGSystem
from advanced_curriculum_generator import AdvancedCurriculumGenerator
import json


def complete_workflow_example():
    """
    Complete workflow:
    1. Initialize RAG system
    2. Search for relevant resources
    3. Generate customized curriculum
    4. Export curriculum
    """
    print("=" * 80)
    print("ETHIKA CHAT: Creating Customized Workshop Curriculum")
    print("=" * 80)
    
    # Step 1: Initialize RAG system
    print("\n[Step 1] Initializing RAG system...")
    rag = RAGSystem()
    print("✓ RAG system initialized")
    
    # Step 2: Search for resources based on institution needs
    print("\n[Step 2] Searching for relevant resources...")
    institution = "Carnegie Mellon University"
    target_audience = ["elementary", "middle_school"]
    topics = ["machine_learning", "bias", "ethics"]
    
    # Search for each topic
    all_resources = []
    for topic in topics:
        print(f"  Searching for: {topic}")
        results = rag.search(
            query=f"{topic} activities for {', '.join(target_audience)} students",
            limit=5,
            target_audience=target_audience,
            tags=[topic]
        )
        all_resources.extend(results)
        print(f"  Found {len(results)} resources for {topic}")
    
    print(f"\n✓ Total resources found: {len(all_resources)}")
    
    # Step 3: Generate curriculum
    print("\n[Step 3] Generating customized curriculum...")
    curriculum = rag.generate_curriculum(
        institution=institution,
        target_audience=target_audience,
        topics=topics,
        duration_hours=3.0,
        preferred_types=["activity", "interactive", "hands_on"],
        limit_per_topic=3
    )
    
    print(f"✓ Curriculum generated with {len(curriculum['resources'])} resources")
    
    # Step 4: Display curriculum summary
    print("\n[Step 4] Curriculum Summary:")
    print(f"  Institution: {curriculum['institution']}")
    print(f"  Target Audience: {', '.join(curriculum['target_audience'])}")
    print(f"  Topics: {', '.join(curriculum['topics'])}")
    print(f"  Duration: {curriculum['duration_hours']} hours")
    print(f"  Resources: {len(curriculum['resources'])}")
    
    print("\n  Selected Resources:")
    for i, resource in enumerate(curriculum['resources'], 1):
        metadata = resource['metadata']
        title = metadata.get('title', 'Untitled')
        author = metadata.get('author', 'Unknown')
        print(f"    {i}. {title} (by {author})")
    
    # Step 5: Generate detailed content (if LLM available)
    print("\n[Step 5] Generating detailed curriculum content...")
    try:
        generator = AdvancedCurriculumGenerator(rag, use_llm=True)
        detailed_curriculum = generator.generate_detailed_curriculum(
            institution=institution,
            target_audience=target_audience,
            topics=topics,
            duration_hours=3.0,
            learning_objectives=[
                "Understand basic machine learning concepts",
                "Recognize bias in AI systems",
                "Explore ethical considerations in AI",
                "Create a simple machine learning model"
            ],
            institution_context="Students have basic computer skills but no prior AI knowledge"
        )
        
        if 'detailed_content' in detailed_curriculum:
            content = detailed_curriculum['detailed_content']
            print("✓ Detailed content generated")
            print("\n  Learning Objectives:")
            for obj in content.get('learning_objectives', []):
                print(f"    - {obj}")
            
            print("\n  Schedule Preview:")
            for item in content.get('schedule', [])[:3]:
                print(f"    {item.get('time', 'N/A')}: {item.get('activity', 'N/A')}")
    except Exception as e:
        print(f"  ⚠ Advanced generation not available: {e}")
        print("  (This is okay - basic curriculum is still available)")
    
    # Step 6: Export curriculum
    print("\n[Step 6] Exporting curriculum...")
    output_file = "curriculum_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(curriculum, f, indent=2, ensure_ascii=False)
    print(f"✓ Curriculum exported to: {output_file}")
    
    print("\n" + "=" * 80)
    print("WORKFLOW COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Review the generated curriculum")
    print("  2. Customize based on specific needs")
    print("  3. Prepare materials and resources")
    print("  4. Conduct the workshop!")


def institution_specific_example():
    """Example: Creating curriculum for a specific institution's needs."""
    print("\n" + "=" * 80)
    print("INSTITUTION-SPECIFIC EXAMPLE")
    print("=" * 80)
    
    rag = RAGSystem()
    
    # Scenario: MIT wants a 4-hour workshop on AI ethics for high school students
    curriculum = rag.generate_curriculum(
        institution="MIT",
        target_audience=["high_school"],
        topics=["ethics", "bias", "fairness"],
        duration_hours=4.0,
        preferred_types=["activity", "interactive", "discussion"],
        limit_per_topic=4
    )
    
    print(f"\nGenerated {len(curriculum['resources'])} resources for MIT workshop")
    print("\nWorkshop Structure:")
    for i, item in enumerate(curriculum['schedule'], 1):
        start_min = int(item['start_minutes'])
        hours = start_min // 60
        minutes = start_min % 60
        print(f"  {hours:02d}:{minutes:02d} - {item['resource']}")


if __name__ == "__main__":
    # Run complete workflow
    complete_workflow_example()
    
    # Run institution-specific example
    institution_specific_example()

