#!/usr/bin/env python3
"""
Setup script to initialize the RAG system with markdown resources.
"""
import argparse
from pathlib import Path
from rag_system import RAGSystem
from markdown_parser import MarkdownParser
from tqdm import tqdm


def main():
    parser = argparse.ArgumentParser(
        description="Initialize RAG system with educational resources"
    )
    parser.add_argument(
        '--resources-dir',
        type=str,
        default='./resources',
        help='Directory containing markdown resource files'
    )
    parser.add_argument(
        '--vector-db-path',
        type=str,
        default='./vector_db',
        help='Path to store vector database'
    )
    parser.add_argument(
        '--collection-name',
        type=str,
        default='educational_resources',
        help='Name of the ChromaDB collection'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset existing collection before adding documents'
    )
    
    args = parser.parse_args()
    
    # Initialize RAG system
    rag = RAGSystem(
        vector_db_path=args.vector_db_path,
        collection_name=args.collection_name
    )
    
    # Reset if requested
    if args.reset:
        print("Resetting collection...")
        try:
            rag.client.delete_collection(args.collection_name)
            rag.collection = rag.client.create_collection(
                name=args.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print("Collection reset.")
        except:
            pass
    
    # Parse markdown files
    resources_dir = Path(args.resources_dir)
    if not resources_dir.exists():
        print(f"Error: Resources directory not found: {resources_dir}")
        print(f"Please create the directory and add your .md files there.")
        return
    
    print(f"Scanning for markdown files in: {resources_dir}")
    parser_obj = MarkdownParser()
    documents = parser_obj.parse_directory(resources_dir)
    
    if not documents:
        print(f"No markdown files found in {resources_dir}")
        return
    
    print(f"Found {len(documents)} markdown files")
    
    # Add documents to RAG system
    print("\nAdding documents to vector database...")
    rag.add_documents(documents)
    
    print(f"\n✓ Setup complete! Added {len(documents)} resources to the RAG system.")
    print(f"Vector database stored at: {args.vector_db_path}")


if __name__ == "__main__":
    main()

