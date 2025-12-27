#!/bin/bash
# Build script for Railway deployment

set -e

echo "🔨 Building React frontend..."
cd frontend
npm install
npm run build
cd ..

echo "✅ Build complete!"
echo "Frontend build is in frontend/build/"

