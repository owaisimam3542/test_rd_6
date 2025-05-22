FROM ubuntu:22.04

RUN apt-get update && apt-get install -y curl gnupg python3 python3-pip git sudo

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Environment (optional)
ENV OLLAMA_MODELS=mistral

WORKDIR /app
COPY . /app

# Install Python packages
RUN pip install fastapi uvicorn python-multipart fitz PyMuPDF requests pydantic

# Copy and make wait script executable
COPY wait-for-ollama.sh /app/wait-for-ollama.sh
RUN chmod +x /app/wait-for-ollama.sh

EXPOSE 8000

# Use wait script as entry point
CMD ["/app/wait-for-ollama.sh"]