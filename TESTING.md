# Testing Guide

## Quick Start Testing

### Option 1: Interactive CLI (Recommended for first test)

```bash
# Make sure you have resources set up first
python setup_rag.py --resources-dir ./resources

# Run the interactive CLI
python interactive_cli.py
```

The CLI will guide you through:
- Searching for resources
- Generating curriculums
- Listing all resources

### Option 2: Web Interface (Streamlit)

```bash
# Install streamlit if not already installed
pip install streamlit

# Run the web interface
streamlit run simple_web_ui.py
```

Then open your browser to `http://localhost:8501`

### Option 3: Command Line Tools

```bash
# Search
python query_rag.py "machine learning activities for elementary students"

# Generate curriculum
python generate_curriculum.py \
  --institution "MIT" \
  --target-audience middle_school \
  --topics machine_learning ethics \
  --duration 3.0
```

## Testing Checklist

- [ ] Resources are loaded (run `setup_rag.py`)
- [ ] Can search for resources
- [ ] Can filter by institution, audience, tags
- [ ] Can generate basic curriculum
- [ ] Can generate advanced curriculum (with Gemini API)
- [ ] All resources are accessible

## Troubleshooting

**"Vector database not found"**
- Run: `python setup_rag.py --resources-dir ./resources`

**"No results found"**
- Make sure resources are loaded
- Try a broader search query
- Check that resources directory has .md files

**"Gemini API errors"**
- Check that `google-generativeai` is installed: `pip install google-generativeai`
- API key is pre-configured, but you can set `GEMINI_API_KEY` environment variable

