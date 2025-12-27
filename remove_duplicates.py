#!/usr/bin/env python3
"""
Script to remove duplicate entries from the ChromaDB collection.
"""
from pathlib import Path
from rag_system import RAGSystem

def remove_duplicates():
    """Remove duplicate entries from the database based on file_path."""
    vector_db_path = Path('vector_db')
    rag = RAGSystem(vector_db_path=str(vector_db_path))
    
    # Get all resources
    all_resources = rag.get_all_resources()
    print(f'Total resources in database: {len(all_resources)}')
    
    # Find duplicates by file_path
    file_paths = {}
    duplicate_ids = []
    
    for i, resource in enumerate(all_resources):
        resource_id = resource.get('id')
        file_path = resource.get('metadata', {}).get('file_path', '')
        
        if file_path:
            if file_path in file_paths:
                # This is a duplicate - keep the first one, mark this for deletion
                duplicate_ids.append(resource_id)
                print(f'Found duplicate: {resource_id} - {file_path}')
            else:
                file_paths[file_path] = resource_id
    
    if duplicate_ids:
        print(f'\nRemoving {len(duplicate_ids)} duplicate entries...')
        rag.collection.delete(ids=duplicate_ids)
        print(f'✓ Removed {len(duplicate_ids)} duplicates')
        print(f'Remaining resources: {len(all_resources) - len(duplicate_ids)}')
    else:
        print('\nNo duplicates found!')

if __name__ == '__main__':
    remove_duplicates()

