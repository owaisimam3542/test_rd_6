#!/bin/bash

# Pull the model
ollama pull mistral

# Start Ollama in the background
ollama serve &

# Wait for Ollama to become responsive
echo "⏳ Waiting for Ollama..."
until curl -s http://localhost:11434 > /dev/null; do
  sleep 2
done

echo "✅ Ollama is ready. Starting FastAPI..."
uvicorn main:app --host 0.0.0.0 --port 8000