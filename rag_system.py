"""
Core RAG system for educational resource retrieval and curriculum generation.
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from markdown_parser import MarkdownParser
import json


class RAGSystem:
    """RAG system for educational resource management."""
    
    def __init__(
        self,
        vector_db_path: str = "./vector_db",
        collection_name: str = "educational_resources",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the RAG system.
        
        Args:
            vector_db_path: Path to store the vector database
            collection_name: Name of the ChromaDB collection
            model_name: Sentence transformer model name
        """
        self.vector_db_path = vector_db_path
        self.collection_name = collection_name
        self.parser = MarkdownParser()
        
        # Initialize embedding model
        print(f"Loading embedding model: {model_name}...")
        self.embedding_model = SentenceTransformer(model_name)
        
        # Initialize ChromaDB
        os.makedirs(vector_db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=vector_db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(collection_name)
            print(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"Created new collection: {collection_name}")
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Add documents to the vector database.
        
        Args:
            documents: List of parsed document dictionaries
        """
        if not documents:
            print("No documents to add.")
            return
        
        texts = []
        metadatas = []
        ids = []
        
        for i, doc in enumerate(documents):
            # Create searchable text
            searchable_text = self.parser.create_searchable_text(doc)
            texts.append(searchable_text)
            
            # Extract metadata for filtering
            filters = self.parser.extract_filters(doc)
            metadata = {
                'file_path': doc.get('file_path', ''),
                'file_name': doc.get('file_name', ''),
                'title': doc.get('metadata', {}).get('title', ''),
                'author': doc.get('metadata', {}).get('author', ''),
                'year': str(doc.get('metadata', {}).get('year', '')),
                'url': doc.get('metadata', {}).get('url', ''),
                'institution': json.dumps(filters['institution']),
                'tags': json.dumps(filters['tags']),
                'target_audience': json.dumps(filters['target_audience']),
                'type': json.dumps(filters['type']),
                'key_concept': json.dumps(filters['key_concept']),
                'relevance': doc.get('metadata', {}).get('relevance_to_ethika', '')
            }
            metadatas.append(metadata)
            ids.append(f"doc_{i}_{doc.get('file_name', 'unknown')}")
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} documents...")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(documents)} documents to the collection.")
    
    def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        institution: Optional[str] = None,
        target_audience: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        resource_type: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant resources.
        
        Args:
            query: Natural language search query
            limit: Maximum number of results
            filters: Additional metadata filters
            institution: Filter by institution name
            target_audience: Filter by target audience
            tags: Filter by tags
            resource_type: Filter by resource type
            
        Returns:
            List of relevant documents with scores
        """
        # Build where clause for filtering
        where_clause = {}
        
        if institution:
            # Search in institution field (JSON array)
            where_clause['institution'] = {"$contains": institution.lower()}
        
        if target_audience:
            # Filter by target audience
            audience_filters = [{"$contains": aud.lower()} for aud in target_audience]
            if len(audience_filters) == 1:
                where_clause['target_audience'] = audience_filters[0]
            else:
                where_clause['$or'] = [
                    {'target_audience': f} for f in audience_filters
                ]
        
        if tags:
            tag_filters = [{"$contains": tag.lower()} for tag in tags]
            if len(tag_filters) == 1:
                where_clause['tags'] = tag_filters[0]
            else:
                # Add to existing $or or create new
                if '$or' in where_clause:
                    where_clause['$or'].extend([{'tags': f} for f in tag_filters])
                else:
                    where_clause['$or'] = [
                        {'tags': f} for f in tag_filters
                    ]
        
        if resource_type:
            type_filters = [{"$contains": rt.lower()} for rt in resource_type]
            if len(type_filters) == 1:
                where_clause['type'] = type_filters[0]
            else:
                if '$or' in where_clause:
                    where_clause['$or'].extend([{'type': f} for f in type_filters])
                else:
                    where_clause['$or'] = [
                        {'type': f} for f in type_filters
                    ]
        
        if filters:
            where_clause.update(filters)
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Search
        if where_clause:
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=limit,
                where=where_clause
            )
        else:
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=limit
            )
        
        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                result = {
                    'id': results['ids'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'document': results['documents'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def generate_curriculum(
        self,
        institution: str,
        target_audience: List[str],
        topics: List[str],
        duration_hours: float = 2.0,
        preferred_types: Optional[List[str]] = None,
        limit_per_topic: int = 3
    ) -> Dict[str, Any]:
        """
        Generate a customized curriculum for an institution.
        
        Args:
            institution: Institution name
            target_audience: List of target audiences (e.g., ["elementary", "middle_school"])
            topics: List of topics to cover
            duration_hours: Workshop duration in hours
            preferred_types: Preferred resource types (e.g., ["activity", "interactive"])
            limit_per_topic: Number of resources per topic
            
        Returns:
            Dictionary containing curriculum structure
        """
        curriculum = {
            'institution': institution,
            'target_audience': target_audience,
            'topics': topics,
            'duration_hours': duration_hours,
            'resources': [],
            'schedule': []
        }
        
        all_resources = []
        
        # Search for resources for each topic
        for topic in topics:
            query = f"{topic} activities for {', '.join(target_audience)} students"
            
            resources = self.search(
                query=query,
                limit=limit_per_topic * 2,  # Get more, then filter
                institution=institution,
                target_audience=target_audience,
                tags=[topic],
                resource_type=preferred_types
            )
            
            # If no results with institution filter, try without
            if not resources:
                resources = self.search(
                    query=query,
                    limit=limit_per_topic * 2,
                    target_audience=target_audience,
                    tags=[topic],
                    resource_type=preferred_types
                )
            
            # Take top results
            all_resources.extend(resources[:limit_per_topic])
        
        # Also do a general search
        general_query = f"AI education resources for {', '.join(target_audience)}"
        general_resources = self.search(
            query=general_query,
            limit=5,
            target_audience=target_audience,
            resource_type=preferred_types
        )
        
        # Combine and deduplicate
        seen_ids = set()
        for resource in all_resources + general_resources:
            if resource['id'] not in seen_ids:
                curriculum['resources'].append(resource)
                seen_ids.add(resource['id'])
        
        # Create a simple schedule estimate
        # Assume each resource takes ~20-30 minutes
        time_per_resource = duration_hours * 60 / max(len(curriculum['resources']), 1)
        time_per_resource = min(time_per_resource, 30)  # Cap at 30 min
        
        for i, resource in enumerate(curriculum['resources']):
            start_time = i * time_per_resource
            curriculum['schedule'].append({
                'resource': resource['metadata'].get('title', 'Untitled'),
                'start_minutes': start_time,
                'duration_minutes': time_per_resource,
                'metadata': resource['metadata']
            })
        
        return curriculum
    
    def get_all_resources(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all resources in the database."""
        results = self.collection.get(limit=limit)
        
        formatted_results = []
        if results['ids']:
            for i in range(len(results['ids'])):
                result = {
                    'id': results['ids'][i],
                    'metadata': results['metadatas'][i],
                    'document': results['documents'][i] if 'documents' in results else None
                }
                formatted_results.append(result)
        
        return formatted_results

