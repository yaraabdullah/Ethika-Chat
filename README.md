# Ethika Chat

A Retrieval-Augmented Generation (RAG) system for managing educational resources and automatically generating customized AI workshop curriculums.

## Features

- **Semantic Search**: Quickly find relevant educational resources using natural language queries
- **Institution-Specific Filtering**: Retrieve resources tailored to specific institution needs
- **Customized Curriculum Generation**: Automatically create workshop content based on institution requirements
- **Structured Metadata**: Leverages YAML frontmatter for rich filtering (tags, target_audience, type, etc.)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Place your markdown resource files in the `resources/` directory (or specify a custom path)

3. Initialize the vector database:
```bash
python setup_rag.py --resources-dir /path/to/resources
```

## Quick Start

1. **Copy your resource files:**
```bash
python copy_resources.py --source /Users/yara/Downloads --dest ./resources
```

2. **Initialize the RAG system:**
```bash
python setup_rag.py --resources-dir ./resources
```

3. **Test the system!** Choose one of these interfaces:
   - **React Web Interface** (recommended): See [FRONTEND_SETUP.md](FRONTEND_SETUP.md)
   - **Interactive CLI**: `python3 interactive_cli.py`
   - **Command Line**: See [QUICKSTART.md](QUICKSTART.md) for examples

See [TESTING.md](TESTING.md) for detailed testing guide.

## Usage

### Command Line Interface

**Search for resources:**
```bash
python query_rag.py "machine learning activities for elementary students"
```

**Search with filters:**
```bash
python query_rag.py "AI ethics" \
  --target-audience middle_school \
  --tags bias ethics \
  --limit 10
```

**Generate a customized curriculum:**
```bash
python generate_curriculum.py \
  --institution "Carnegie Mellon University" \
  --target-audience middle_school \
  --topics machine_learning ethics \
  --duration 3.0
```

### Python API

```python
from rag_system import RAGSystem
from advanced_curriculum_generator import AdvancedCurriculumGenerator

# Initialize
rag = RAGSystem()

# Search
results = rag.search(
    query="interactive AI activities",
    limit=5,
    target_audience=["elementary"],
    tags=["machine_learning"]
)

# Generate basic curriculum
curriculum = rag.generate_curriculum(
    institution="MIT",
    target_audience=["elementary", "middle_school"],
    topics=["machine_learning", "bias"],
    duration_hours=3
)

# Generate advanced curriculum with detailed content (uses Gemini API)
generator = AdvancedCurriculumGenerator(rag, use_llm=True)
detailed_curriculum = generator.generate_detailed_curriculum(
    institution="MIT",
    target_audience=["middle_school"],
    topics=["machine_learning", "ethics"],
    duration_hours=3.0,
    learning_objectives=[
        "Understand basic ML concepts",
        "Recognize bias in AI systems"
    ]
)
```

### REST API

Start the API server:
```bash
python api_server.py
```

Then use the endpoints:
- `POST /search` - Search for resources
- `POST /curriculum` - Generate curriculum
- `GET /resources` - List all resources

## Project Structure

```
ethika-chat/
├── rag_system.py          # Core RAG system
├── markdown_parser.py     # Parse markdown files with YAML frontmatter
├── setup_rag.py          # Initialize vector database
├── query_rag.py          # CLI for querying
├── generate_curriculum.py # CLI for curriculum generation
├── resources/            # Place your .md files here
└── vector_db/           # Vector database storage (auto-created)
```

