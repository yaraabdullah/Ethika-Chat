# Ethika Chat Frontend

React frontend for the Ethika Chat RAG system.

## Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

## Backend

Make sure the FastAPI backend is running:
```bash
# In the project root
python3 api_server.py
```

The backend should be running on `http://localhost:8000`

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` folder.
