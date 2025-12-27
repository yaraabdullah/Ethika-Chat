# React Frontend Setup

I've created a React frontend to replace Streamlit! Here's how to use it:

## Quick Start

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 2. Start the Backend API Server

In one terminal:
```bash
cd /Users/yara/ethika-chat
python3 api_server.py
```

The API will run on `http://localhost:8000`

### 3. Start the React Frontend

In another terminal:
```bash
cd frontend
npm start
```

The React app will open at `http://localhost:3000`

## Features

The React frontend includes:

- **🔍 Search Tab**: Search for resources with filters
- **📚 Curriculum Tab**: Generate customized curriculums
- **📋 Resources Tab**: Browse all resources in the database

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── SearchTab.tsx      # Search interface
│   │   ├── CurriculumTab.tsx  # Curriculum generation
│   │   └── ResourcesTab.tsx   # Resource browser
│   ├── App.tsx                # Main app component
│   ├── App.css                # Styles
│   └── index.tsx              # Entry point
├── public/
│   └── index.html
└── package.json
```

## Development

- The React app proxies API requests to `http://localhost:8000` (configured in `package.json`)
- Hot reload is enabled - changes will automatically refresh
- TypeScript is used for type safety

## Build for Production

```bash
cd frontend
npm run build
```

This creates an optimized build in `frontend/build/`

## Troubleshooting

**"Backend Not Connected" error:**
- Make sure `python3 api_server.py` is running
- Check that it's running on port 8000

**CORS errors:**
- The API server has CORS enabled for `localhost:3000`
- If using a different port, update CORS settings in `api_server.py`

**Port already in use:**
- React default port is 3000
- If busy, it will ask to use a different port

