"""
Parser for educational resource markdown files with YAML frontmatter.
"""
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


class MarkdownParser:
    """Parse markdown files with YAML frontmatter."""
    
    def __init__(self):
        self.yaml_pattern = re.compile(
            r'^---\s*\n(.*?)\n---\s*\n(.*)$',
            re.DOTALL | re.MULTILINE
        )
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a markdown file and extract YAML frontmatter and content.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            Dictionary with 'metadata' and 'content' keys
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = self.yaml_pattern.match(content)
            
            if match:
                yaml_content = match.group(1)
                markdown_content = match.group(2)
                
                try:
                    metadata = yaml.safe_load(yaml_content)
                    if metadata is None:
                        metadata = {}
                except yaml.YAMLError as e:
                    print(f"Error parsing YAML in {file_path}: {e}")
                    metadata = {}
            else:
                # No frontmatter found
                metadata = {}
                markdown_content = content
            
            return {
                'metadata': metadata,
                'content': markdown_content.strip(),
                'file_path': str(file_path),
                'file_name': file_path.name
            }
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return {
                'metadata': {},
                'content': '',
                'file_path': str(file_path),
                'file_name': file_path.name
            }
    
    def parse_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """
        Parse all markdown files in a directory.
        
        Args:
            directory: Path to directory containing markdown files
            
        Returns:
            List of parsed documents
        """
        documents = []
        md_files = list(directory.glob('*.md')) + list(directory.glob('**/*.md'))
        
        for md_file in md_files:
            doc = self.parse_file(md_file)
            if doc['content'] or doc['metadata']:
                documents.append(doc)
        
        return documents
    
    def create_searchable_text(self, doc: Dict[str, Any]) -> str:
        """
        Create a searchable text representation from a parsed document.
        
        Args:
            doc: Parsed document dictionary
            
        Returns:
            Combined text for embedding/search
        """
        parts = []
        metadata = doc.get('metadata', {})
        
        # Add title
        if 'title' in metadata:
            parts.append(f"Title: {metadata['title']}")
        
        # Add author
        if 'author' in metadata:
            parts.append(f"Author: {metadata['author']}")
        
        # Add description/relevance
        if 'relevance_to_ethika' in metadata:
            parts.append(f"Relevance: {metadata['relevance_to_ethika']}")
        
        # Add tags
        if 'tags' in metadata:
            tags = metadata['tags']
            if isinstance(tags, list):
                parts.append(f"Tags: {', '.join(tags)}")
            else:
                parts.append(f"Tags: {tags}")
        
        # Add target audience
        if 'target_audience' in metadata:
            audience = metadata['target_audience']
            if isinstance(audience, list):
                parts.append(f"Target Audience: {', '.join(audience)}")
            else:
                parts.append(f"Target Audience: {audience}")
        
        # Add type
        if 'type' in metadata:
            types = metadata['type']
            if isinstance(types, list):
                parts.append(f"Type: {', '.join(types)}")
            else:
                parts.append(f"Type: {types}")
        
        # Add key concepts
        if 'key_concept' in metadata:
            concepts = metadata['key_concept']
            if isinstance(concepts, list) and concepts:
                parts.append(f"Key Concepts: {', '.join(concepts)}")
        
        # Add content
        if doc.get('content'):
            parts.append(f"Content: {doc['content']}")
        
        return "\n".join(parts)
    
    def extract_filters(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract filterable metadata for advanced search.
        
        Args:
            doc: Parsed document dictionary
            
        Returns:
            Dictionary of filterable attributes
        """
        metadata = doc.get('metadata', {})
        
        filters = {
            'institution': self._normalize_list(metadata.get('institution', [])),
            'tags': self._normalize_list(metadata.get('tags', [])),
            'target_audience': self._normalize_list(metadata.get('target_audience', [])),
            'type': self._normalize_list(metadata.get('type', [])),
            'year': metadata.get('year'),
            'author': metadata.get('author'),
            'key_concept': self._normalize_list(metadata.get('key_concept', []))
        }
        
        return filters
    
    @staticmethod
    def _normalize_list(value):
        """Normalize a value to a list."""
        if value is None:
            return []
        if isinstance(value, list):
            return [str(v).lower() for v in value]
        return [str(value).lower()]

