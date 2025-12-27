# Ethika Chat Architecture

## Overview

Ethika Chat is a RAG (Retrieval-Augmented Generation) system designed to help AI education institutions quickly find and organize educational resources, and automatically generate customized workshop curriculums.

## Components

### 1. Markdown Parser (`markdown_parser.py`)
- Parses markdown files with YAML frontmatter
- Extracts structured metadata (title, author, tags, target_audience, etc.)
- Creates searchable text representations
- Handles filtering metadata

### 2. RAG System (`rag_system.py`)
- **Vector Database**: Uses ChromaDB for persistent storage
- **Embeddings**: Uses Sentence Transformers (all-MiniLM-L6-v2) for semantic search
- **Search**: Semantic search with metadata filtering
- **Curriculum Generation**: Automatically selects and organizes resources

### 3. Advanced Curriculum Generator (`advanced_curriculum_generator.py`)
- Extends basic curriculum generation with LLM integration
- Creates detailed workshop content including:
  - Learning objectives
  - Detailed schedules
  - Activity descriptions
  - Assessment ideas
  - Materials needed

### 4. CLI Tools
- `setup_rag.py`: Initialize vector database from markdown files
- `query_rag.py`: Search for resources via command line
- `generate_curriculum.py`: Generate curriculums via command line
- `copy_resources.py`: Helper to copy resource files

### 5. API Server (`api_server.py`)
- FastAPI-based REST API
- Endpoints for search and curriculum generation
- Can be integrated into other systems

## Data Flow

```
Markdown Files (with YAML frontmatter)
    ↓
Markdown Parser
    ↓
Extract Metadata + Content
    ↓
Create Searchable Text
    ↓
Generate Embeddings (Sentence Transformers)
    ↓
Store in Vector Database (ChromaDB)
    ↓
Query with Semantic Search + Filters
    ↓
Retrieve Relevant Resources
    ↓
Generate Curriculum (Basic or Advanced with LLM)
```

## Key Features

### Semantic Search
- Natural language queries
- Finds resources based on meaning, not just keywords
- Example: "interactive activities for teaching AI ethics" finds relevant resources even if they don't contain those exact words

### Metadata Filtering
- Filter by institution
- Filter by target audience (elementary, middle_school, high_school)
- Filter by tags (machine_learning, ethics, bias, etc.)
- Filter by resource type (activity, interactive, hands_on, etc.)

### Curriculum Generation
- Automatically selects resources based on:
  - Institution needs
  - Target audience
  - Topics to cover
  - Workshop duration
- Creates time-based schedule
- Can generate detailed content with LLM

## File Structure

```
ethika-chat/
├── markdown_parser.py          # Parse .md files
├── rag_system.py               # Core RAG functionality
├── advanced_curriculum_generator.py  # LLM-enhanced generation
├── setup_rag.py               # Initialize database
├── query_rag.py               # CLI search tool
├── generate_curriculum.py     # CLI curriculum generator
├── copy_resources.py          # Helper script
├── api_server.py              # REST API
├── workflow_example.py        # Complete workflow demo
├── example_usage.py           # Usage examples
├── resources/                 # Your .md files go here
├── vector_db/                 # Vector database (auto-created)
└── requirements.txt           # Dependencies
```

## Technology Stack

- **Vector Database**: ChromaDB (persistent, local)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **LLM Integration**: Google Gemini API (Flash 2.5, optional, for advanced features)
- **API Framework**: FastAPI
- **Data Format**: YAML frontmatter in Markdown

## Customization

### Change Embedding Model
Edit `rag_system.py`:
```python
rag = RAGSystem(model_name="all-mpnet-base-v2")  # Larger, more accurate
```

### Add Custom Filters
Extend `markdown_parser.py` to extract additional metadata fields.

### Customize Curriculum Generation
Modify `rag_system.py` `generate_curriculum()` method to adjust resource selection logic.

## Performance Considerations

- **Embedding Model**: all-MiniLM-L6-v2 is fast and efficient (80MB)
- **Vector Database**: ChromaDB uses HNSW index for fast similarity search
- **Scaling**: Can handle thousands of resources efficiently
- **LLM Calls**: Only used in advanced curriculum generation (optional)

## Future Enhancements

- Multi-modal support (images, videos)
- Collaborative filtering (recommendations based on similar institutions)
- Analytics (track which resources are most effective)
- Export to various formats (PDF, Google Docs, etc.)
- Integration with learning management systems

