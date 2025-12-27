#!/usr/bin/env python3
"""
CLI tool for querying the RAG system.
"""
import argparse
import json
from rag_system import RAGSystem


def format_result(result, index):
    """Format a search result for display."""
    metadata = result['metadata']
    title = metadata.get('title', 'Untitled')
    author = metadata.get('author', 'Unknown')
    file_name = metadata.get('file_name', 'Unknown')
    distance = result.get('distance')
    score = f" (similarity: {1 - distance:.3f})" if distance is not None else ""
    
    output = f"\n{'='*80}\n"
    output += f"Result #{index + 1}{score}\n"
    output += f"{'='*80}\n"
    output += f"Title: {title}\n"
    output += f"Author: {author}\n"
    output += f"File: {file_name}\n"
    
    if metadata.get('url'):
        output += f"URL: {metadata['url']}\n"
    
    if metadata.get('tags'):
        tags = json.loads(metadata['tags']) if isinstance(metadata['tags'], str) else metadata['tags']
        output += f"Tags: {', '.join(tags) if isinstance(tags, list) else tags}\n"
    
    if metadata.get('target_audience'):
        audience = json.loads(metadata['target_audience']) if isinstance(metadata['target_audience'], str) else metadata['target_audience']
        output += f"Target Audience: {', '.join(audience) if isinstance(audience, list) else audience}\n"
    
    if metadata.get('relevance'):
        output += f"Relevance: {metadata['relevance']}\n"
    
    output += f"\nPreview:\n{result['document'][:300]}...\n"
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Query the RAG system for educational resources"
    )
    parser.add_argument(
        'query',
        type=str,
        help='Search query'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Maximum number of results (default: 5)'
    )
    parser.add_argument(
        '--institution',
        type=str,
        help='Filter by institution name'
    )
    parser.add_argument(
        '--target-audience',
        type=str,
        nargs='+',
        help='Filter by target audience (e.g., elementary middle_school)'
    )
    parser.add_argument(
        '--tags',
        type=str,
        nargs='+',
        help='Filter by tags'
    )
    parser.add_argument(
        '--type',
        type=str,
        nargs='+',
        dest='resource_type',
        help='Filter by resource type'
    )
    parser.add_argument(
        '--vector-db-path',
        type=str,
        default='./vector_db',
        help='Path to vector database'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    args = parser.parse_args()
    
    # Initialize RAG system
    rag = RAGSystem(vector_db_path=args.vector_db_path)
    
    # Search
    results = rag.search(
        query=args.query,
        limit=args.limit,
        institution=args.institution,
        target_audience=args.target_audience,
        tags=args.tags,
        resource_type=args.resource_type
    )
    
    if not results:
        print("No results found.")
        return
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\nFound {len(results)} results for: '{args.query}'\n")
        for i, result in enumerate(results):
            print(format_result(result, i))


if __name__ == "__main__":
    main()

