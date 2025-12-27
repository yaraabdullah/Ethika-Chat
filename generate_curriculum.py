#!/usr/bin/env python3
"""
CLI tool for generating customized curriculums using the RAG system.
"""
import argparse
import json
from rag_system import RAGSystem


def format_curriculum(curriculum, output_format='text'):
    """Format curriculum for display."""
    if output_format == 'json':
        return json.dumps(curriculum, indent=2)
    
    output = f"\n{'='*80}\n"
    output += f"CUSTOMIZED CURRICULUM\n"
    output += f"{'='*80}\n\n"
    output += f"Institution: {curriculum['institution']}\n"
    output += f"Target Audience: {', '.join(curriculum['target_audience'])}\n"
    output += f"Topics: {', '.join(curriculum['topics'])}\n"
    output += f"Duration: {curriculum['duration_hours']} hours\n"
    output += f"Total Resources: {len(curriculum['resources'])}\n"
    
    output += f"\n{'='*80}\n"
    output += f"RESOURCES\n"
    output += f"{'='*80}\n\n"
    
    for i, resource in enumerate(curriculum['resources'], 1):
        metadata = resource['metadata']
        title = metadata.get('title', 'Untitled')
        author = metadata.get('author', 'Unknown')
        url = metadata.get('url', '')
        
        output += f"{i}. {title}\n"
        output += f"   Author: {author}\n"
        if url:
            output += f"   URL: {url}\n"
        
        tags = json.loads(metadata.get('tags', '[]')) if isinstance(metadata.get('tags'), str) else metadata.get('tags', [])
        if tags:
            output += f"   Tags: {', '.join(tags)}\n"
        
        output += "\n"
    
    output += f"\n{'='*80}\n"
    output += f"SUGGESTED SCHEDULE\n"
    output += f"{'='*80}\n\n"
    
    for item in curriculum['schedule']:
        start_min = int(item['start_minutes'])
        duration_min = int(item['duration_minutes'])
        hours = start_min // 60
        minutes = start_min % 60
        start_time = f"{hours:02d}:{minutes:02d}"
        
        output += f"{start_time} ({duration_min} min) - {item['resource']}\n"
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Generate customized curriculum using RAG system"
    )
    parser.add_argument(
        '--institution',
        type=str,
        required=True,
        help='Institution name'
    )
    parser.add_argument(
        '--target-audience',
        type=str,
        nargs='+',
        required=True,
        help='Target audience (e.g., elementary middle_school)'
    )
    parser.add_argument(
        '--topics',
        type=str,
        nargs='+',
        required=True,
        help='Topics to cover (e.g., machine_learning ethics bias)'
    )
    parser.add_argument(
        '--duration',
        type=float,
        default=2.0,
        help='Workshop duration in hours (default: 2.0)'
    )
    parser.add_argument(
        '--type',
        type=str,
        nargs='+',
        dest='preferred_types',
        help='Preferred resource types (e.g., activity interactive)'
    )
    parser.add_argument(
        '--resources-per-topic',
        type=int,
        default=3,
        help='Number of resources per topic (default: 3)'
    )
    parser.add_argument(
        '--vector-db-path',
        type=str,
        default='./vector_db',
        help='Path to vector database'
    )
    parser.add_argument(
        '--output',
        type=str,
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--save',
        type=str,
        help='Save curriculum to file'
    )
    
    args = parser.parse_args()
    
    # Initialize RAG system
    rag = RAGSystem(vector_db_path=args.vector_db_path)
    
    # Generate curriculum
    print("Generating customized curriculum...")
    curriculum = rag.generate_curriculum(
        institution=args.institution,
        target_audience=args.target_audience,
        topics=args.topics,
        duration_hours=args.duration,
        preferred_types=args.preferred_types,
        limit_per_topic=args.resources_per_topic
    )
    
    # Format and display
    formatted = format_curriculum(curriculum, args.output)
    print(formatted)
    
    # Save if requested
    if args.save:
        with open(args.save, 'w', encoding='utf-8') as f:
            if args.output == 'json':
                f.write(json.dumps(curriculum, indent=2))
            else:
                f.write(formatted)
        print(f"\nCurriculum saved to: {args.save}")


if __name__ == "__main__":
    main()

