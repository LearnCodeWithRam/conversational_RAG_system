# 🤖 Conversational RAG Q&A System

A sophisticated Retrieval-Augmented Generation (RAG) system that allows users to upload documents and ask intelligent questions with AI-powered answers, complete with source citations and reasoning. Built with FastAPI, MongoDB Atlas, Qdrant Cloud, and Ollama LLM.

## ✨ Features

- **Document Upload**: Support for PDF and TXT files with automatic text extraction and chunking
- **Intelligent Q&A**: Multi-turn conversations with context awareness using Ollama LLM
- **Source Citations**: Every answer includes references to specific document sections
- **Reasoning Transparency**: Explains how answers were derived from the source material
- **Follow-up Suggestions**: AI-generated related questions to continue the conversation
- **Modern UI**: Clean, responsive web interface with drag-and-drop upload
- **Cloud-Ready**: Uses MongoDB Atlas and Qdrant Cloud for scalability
- **GPU Acceleration**: Deployed on RTX 5090 GPU for optimal performance

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   FastAPI API   │    │   Ollama LLM    │
│   (HTML/CSS/JS) │◄──►│                 │◄──►│   (llama3.1:8b) │
└─────────────────┘    │                 │    └─────────────────┘
                       │                 │    
                       │                 │    ┌─────────────────┐
                       │                 │◄──►│ Sentence Trans. │
                       │                 │    │   (Embeddings)  │
                       └─────────────────┘    └─────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
        ┌───────▼──────┐ ┌─────▼──────┐ ┌────▼──────┐
        │   MongoDB    │ │   Qdrant   │ │  Static   │
        │   (Cloud)    │ │  (Cloud)   │ │  Files    │
        │              │ │            │ │           │
        │ • Documents  │ │ • Vector   │ │ • UI      │
        │ • Metadata   │ │   Store    │ │ • Assets  │
        │ • Chat Hist  │ │ • Semantic │ │           │
        └──────────────┘ │   Search   │ └───────────┘
                         └────────────┘
```

## 📸 User Interface Screenshots

### Main Dashboard
The clean, modern interface provides an intuitive user experience with drag-and-drop document upload and real-time chat interface.

### Document Upload Process
1. **Drag & Drop Area**: Simply drag PDF or TXT files onto the upload area
2. **Processing**: Automatic text extraction and chunking with progress indicators
3. **Confirmation**: Visual feedback showing successful upload and chunk count

### Conversational Q&A
1. **Question Input**: Natural language question input with enter-key support
2. **AI Response**: Detailed answers with reasoning and source citations
3. **Follow-up Suggestions**: Smart question suggestions to continue the conversation
4. **Reference Links**: Click-able references showing document sources and page numbers

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB Atlas account
- Qdrant Cloud account
- RTX 5090 GPU (for optimal performance)
- Ollama server with llama3.1:8b model

### 1. Clone and Setup

```bash
git clone <repository-url>
cd rag-qa-system
pip install -r requirements.txt
```

### 2. Environment Configuration

The system uses hardcoded credentials for simplicity, but you can create a `.env` file for additional customization:

```env
# Optional: Override default settings
CHUNK_SIZE=500
CHUNK_OVERLAP=80
MAX_CONTEXT_LENGTH=2000
```

**Note**: The system is pre-configured with:
- MongoDB Atlas: `mongodb+srv://ihub_incubation:SfDMYHQZGzOhFW9E@cluster0.gz3io9i.mongodb.net/`
- Qdrant Cloud: URL and API key included in code
- Ollama Server: `http://115.241.186.203` with llama3.1:8b model

### 3. Initialize Database

```bash
# Run database setup script
python setup_database.py
```

This script will:
- Test MongoDB Atlas connection
- Create Qdrant collection if not exists
- Test Ollama LLM connection
- Verify all services are operational

### 4. Download Embedding Model

The system automatically downloads the `all-MiniLM-L6-v2` model on first run, but you can pre-download:

```bash
# The model will be saved to ./all-MiniLM-L6-v2/
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2').save('./all-MiniLM-L6-v2')"
```

### 5. Run the Application

```bash
# Development mode
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 6. Access the UI

Open your browser and navigate to: `http://localhost:8000`

## 🌐 Docker Deployment on RTX 5090 GPU Server

### Actual Deployment Setup

The application is deployed using Docker containers with Nginx reverse proxy on an RTX 5090 GPU server.

### 1. Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Create directory for model storage
RUN mkdir -p ./all-MiniLM-L6-v2

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  rag-app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./all-MiniLM-L6-v2:/app/all-MiniLM-L6-v2
    environment:
      - CUDA_VISIBLE_DEVICES=0
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 2. Deploy with Docker

```bash
# Clone repository
git clone <your-repo-url>
cd rag-qa-system

# Build and run with Docker Compose
docker-compose up -d

# Check container status
docker-compose ps

# View logs
docker-compose logs -f rag-app
```

## 📦 Required Files

### Create `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for model storage
RUN mkdir -p ./all-MiniLM-L6-v2

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Create `docker-compose.yml`
```yaml
version: '3.8'
services:
  rag-app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./all-MiniLM-L6-v2:/app/all-MiniLM-L6-v2
      - ./static:/app/static
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped
    networks:
      - rag-network

### 3. Configure Nginx Reverse Proxy

Create Nginx configuration for global access:

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/rag-qa
```

**Nginx configuration** (`/etc/nginx/sites-available/rag-qa`):
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain/IP

    client_max_body_size 100M;  # Allow large file uploads

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts for large file processing
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Optional: Serve static files directly
    location /static/ {
        alias /path/to/your/app/static/;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site and restart Nginx
sudo ln -s /etc/nginx/sites-available/rag-qa /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl reload nginx
```

### 4. Complete Deployment Commands

```bash
# 1. Build and start containers
docker-compose up -d --build

# 2. Verify deployment
docker-compose ps
docker-compose logs -f rag-app

# 3. Test application
curl http://localhost:8000

# 4. Access via domain/IP (after Nginx setup)
# Navigate to: http://your-domain.com
```

### 5. Container Management

```bash
# View running containers
docker-compose ps

# Stop application
docker-compose down

# Update and restart
git pull
docker-compose up -d --build

# View logs
docker-compose logs -f rag-app

# Execute commands inside container
docker-compose exec rag-app python setup_database.py
```

### Create `requirements.txt`
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pymongo==4.6.0
qdrant-client==1.7.0
sentence-transformers==2.2.2
PyPDF2==3.0.1
python-dotenv==1.0.0
pydantic==2.5.0
langchain-ollama==0.0.1
```

```bash
# Install Nginx
sudo apt install nginx

# Create configuration
sudo nano /etc/nginx/sites-available/rag-qa
```

**Nginx configuration** (`/etc/nginx/sites-available/rag-qa`):
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    client_max_body_size 100M;  # Allow large file uploads

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/rag-qa /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

### 5. SSL Certificate (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 6. Firewall Configuration

```bash
# Configure UFW
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Check status
sudo ufw status
```

## 🔧 Production Configuration

### Environment Variables for Production

Create `/etc/environment` or use systemd environment files:

```bash
# Performance tuning
CUDA_VISIBLE_DEVICES=0
OMP_NUM_THREADS=8
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

# Application settings
WORKERS=4
MAX_REQUESTS=1000
KEEP_ALIVE=2
```

### Monitoring and Logging

```bash
# Install monitoring tools
sudo apt install htop nvtop

# Check GPU usage
watch -n 1 nvidia-smi

# Monitor application logs
sudo journalctl -u rag-qa.service -f

# Monitor Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 📚 API Documentation

### Upload Document
```bash
curl -X POST "http://your-domain.com/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf"
```

### Ask Question
```bash
curl -X POST "http://your-domain.com/ask" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user123",
       "question": "What does the document say about AI?",
       "top_k": 4
     }'
```

### Get Conversation History
```bash
curl -X GET "http://your-domain.com/history?user_id=user123"
```

### List Documents
```bash
curl -X GET "http://your-domain.com/documents"
```

### Clear System
```bash
curl -X DELETE "http://your-domain.com/clear"
```

## 📱 API Response Format

### Question Response
```json
{
  "answer": "Based on the uploaded documents, AI refers to...",
  "reasoning": "This answer was derived from section 2.1 of the uploaded report...",
  "references": [
    {
      "document": "AI_Report.pdf",
      "page": 2,
      "chunk_id": "chunk_123",
      "content_snippet": "Artificial Intelligence represents..."
    }
  ],
  "suggestions": [
    "What are the future implications of AI?",
    "How does AI impact different industries?",
    "What are the risks associated with AI?"
  ]
}
```

## 🎯 Usage Process

### Step-by-Step Process

1. **Document Upload**
   - Navigate to the web interface
   - Drag and drop PDF/TXT files or click to browse
   - Wait for processing confirmation with chunk count

2. **Ask Questions**
   - Type your question in natural language
   - Press Enter or click "Ask" button
   - Receive detailed answer with reasoning

3. **Review References**
   - Check source citations for each answer
   - Click on references to see document snippets
   - Verify information accuracy

4. **Continue Conversation**
   - Use suggested follow-up questions
   - Ask related questions for deeper understanding
   - Build on previous context in multi-turn conversations

### Best Practices

- **Upload relevant documents** before asking questions
- **Ask specific questions** for better accuracy
- **Use follow-up suggestions** to explore topics thoroughly
- **Check references** to verify information
- **Clear system** when switching to different document sets

## 🔍 Technical Configuration

### Chunking Parameters
```python
CHUNK_SIZE = 500          # Words per chunk
CHUNK_OVERLAP = 80        # Overlap between chunks
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions
```

### LLM Settings
```python
MODEL = "llama3.1:8b"     # Ollama model
BASE_URL = "http://115.241.186.203"  # Ollama server
TEMPERATURE = 0.7         # Response creativity
TOP_K = 4                 # Context chunks per query
```

### Database Configuration
- **MongoDB**: Document metadata and conversation history
- **Qdrant**: Vector embeddings for semantic search
- **Vector Dimension**: 384 (matches embedding model)
- **Distance Metric**: Cosine similarity

## 🚨 Troubleshooting

### Common Issues

1. **GPU Out of Memory**
   ```bash
   # Check GPU usage
   nvidia-smi
   
   # Restart Ollama service
   sudo systemctl restart ollama
   ```

2. **Database Connection Issues**
   ```bash
   # Test MongoDB connection
   python setup_database.py
   
   # Check network connectivity
   ping cluster0.gz3io9i.mongodb.net
   ```

3. **Ollama Service Issues**
   ```bash
   # Check Ollama status
   systemctl status ollama
   
   # View logs
   journalctl -u ollama -f
   
   # Test model
   ollama run llama3.1:8b "test"
   ```

4. **File Upload Issues**
   - Check Nginx client_max_body_size setting
   - Verify file permissions in upload directory
   - Ensure sufficient disk space

### Performance Optimization

1. **GPU Memory Management**
   - Monitor GPU usage with `nvidia-smi`
   - Adjust batch sizes for large documents
   - Use model quantization if needed

2. **Application Performance**
   - Increase number of workers for high traffic
   - Implement caching for frequent queries
   - Use connection pooling for databases

3. **Network Optimization**
   - Enable gzip compression in Nginx
   - Use CDN for static assets
   - Implement request rate limiting

## 📊 Deployment Status

### Live Demo
- **Deployment Method**: Docker + Nginx
- **GPU Server**: RTX 5090 powered
- **Model**: llama3.1:8b via Ollama
- **Status**: 🟢 Deployed and Running

### Actual System Configuration
```
Deployment: Docker containerized application
Reverse Proxy: Nginx for global access
GPU: NVIDIA RTX 5090 (utilized via Docker GPU support)
LLM Backend: Ollama server (llama3.1:8b)
Databases: MongoDB Atlas + Qdrant Cloud
Embedding Model: all-MiniLM-L6-v2 (local)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test thoroughly
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama Team** for open-source LLM inference
- **MongoDB Atlas** for cloud database services
- **Qdrant** for vector database capabilities
- **Sentence Transformers** for embedding models
- **FastAPI** for the excellent web framework
- **NVIDIA** for RTX 5090 GPU performance

## 📞 Support

For support and questions:
- **Issues**: Open a GitHub issue
- **Documentation**: Check this README and code comments
- **Community**: Join our Discord/Slack (if applicable)

---

**Built with ❤️ for the AI community | Powered by RTX 5090 GPU**