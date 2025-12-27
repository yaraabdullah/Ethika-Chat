# Quick Start Guide

## 1. Installation

```bash
# Navigate to the project directory
cd /Users/yara/ethika-chat

# Install dependencies
pip install -r requirements.txt
```

## 2. Prepare Your Resources

Place all your markdown resource files in a directory. For example:

```bash
mkdir -p resources
# Copy your .md files to the resources directory
cp /Users/yara/Downloads/RES-*.md resources/
```

## 3. Initialize the RAG System

```bash
# Initialize the vector database with your resources
python setup_rag.py --resources-dir ./resources

# Or if your resources are elsewhere:
python setup_rag.py --resources-dir /path/to/your/resources
```

This will:
- Parse all markdown files
- Extract metadata and content
- Generate embeddings
- Store in a vector database

## 4. Search for Resources

```bash
# Basic search
python query_rag.py "machine learning activities for elementary students"

# Search with filters
python query_rag.py "AI ethics" \
  --target-audience middle_school \
  --tags bias ethics \
  --limit 10
```

## 5. Generate Customized Curriculums

```bash
# Basic curriculum generation
python generate_curriculum.py \
  --institution "Carnegie Mellon University" \
  --target-audience elementary middle_school \
  --topics machine_learning bias \
  --duration 2.5

# Save to file
python generate_curriculum.py \
  --institution "MIT" \
  --target-audience middle_school \
  --topics machine_learning ethics \
  --duration 3.0 \
  --save curriculum_mit.json
```

## 6. Use the API Server (Optional)

```bash
# Start the API server
python api_server.py

# In another terminal, test the API:
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "interactive AI activities",
    "limit": 5,
    "target_audience": ["elementary"]
  }'

# Generate curriculum via API
curl -X POST "http://localhost:8000/curriculum" \
  -H "Content-Type: application/json" \
  -d '{
    "institution": "MIT",
    "target_audience": ["middle_school"],
    "topics": ["machine_learning", "ethics"],
    "duration_hours": 3.0
  }'
```

## 7. Advanced Features (with OpenAI API)

For advanced curriculum generation with detailed content:

1. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

2. Use the advanced generator in Python:
```python
from rag_system import RAGSystem
from advanced_curriculum_generator import AdvancedCurriculumGenerator

rag = RAGSystem()
generator = AdvancedCurriculumGenerator(rag, use_llm=True)

curriculum = generator.generate_detailed_curriculum(
    institution="MIT",
    target_audience=["middle_school"],
    topics=["machine_learning", "ethics"],
    duration_hours=3.0,
    learning_objectives=[
        "Understand basic ML concepts",
        "Recognize bias in AI"
    ]
)
```

## Tips

- **Reset the database**: Use `--reset` flag when running `setup_rag.py` to start fresh
- **Multiple resource directories**: You can run `setup_rag.py` multiple times to add more resources
- **Filtering**: Use `--institution`, `--target-audience`, `--tags`, and `--type` to narrow searches
- **JSON output**: Add `--json` flag to `query_rag.py` for machine-readable output

## Troubleshooting

- **No results found**: Make sure you've run `setup_rag.py` first
- **Import errors**: Ensure all dependencies are installed: `pip install -r requirements.txt`
- **OpenAI errors**: Check that your API key is set correctly if using advanced features

