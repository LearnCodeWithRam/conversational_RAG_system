# 🚀 Quick Start Guide

## Prerequisites Setup

### 1. Create Project Directory
```bash
mkdir rag-qa-system
cd rag-qa-system
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file with your OpenAI API key and MongoDB password:

```env
# OpenAI Configuration (Required)
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# MongoDB Password (Required)
DB_PASSWORD=your_actual_mongodb_password_here
```

**Important:** Replace `your_actual_mongodb_password_here` with your real MongoDB Atlas password.

## 🔧 Database Setup

### Option 1: Automated Setup (Recommended)
Run the setup script to initialize both databases:

```bash
python setup_database.py
```

This will:
- ✅ Test MongoDB Atlas connection
- ✅ Create necessary collections and indexes
- ✅ Test Qdrant Cloud connection
- ✅ Create vector collection
- ✅ Verify OpenAI API access

### Option 2: Manual Verification

**Test MongoDB Connection:**
```python
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://ihub_incubation:YOUR_PASSWORD@cluster0.gz3io9i.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("✅ MongoDB connected successfully!")
except Exception as e:
    print(f"❌ MongoDB error: {e}")
```

**Test Qdrant Connection:**
```python
from qdrant_client import QdrantClient

client = QdrantClient(
    url="https://402014c0-fdfd-45bd-b26c.us-east-1-1.aws.clouqdrant.io:6333",
    api_key="eyJhbGciOiJIUzI1NiIshY2Nlc3MiOiJtIn0.uYiqYKg_Fe879LUITSJtKR4dmreqpu-GYaGyWzQWK94"
)

try:
    collections = client.get_collections()
    print("✅ Qdrant connected successfully!")
    print(f"Collections: {[c.name for c in collections.collections]}")
except Exception as e:
    print(f"❌ Qdrant error: {e}")
```

## 🚀 Running the Application

### 1. Start the Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Access the Web Interface
Open your browser and go to: **http://localhost:8000**

## 📋 First Time Usage

### 1. Upload a Document
- Click the upload area or drag & drop a PDF/TXT file
- Wait for processing confirmation
- Check that the document appears in the sidebar

### 2. Ask Your First Question
```
What are the main topics covered in this document?
```

### 3. Try Follow-up Questions
Use the AI-generated suggestions or ask specific questions like:
```
How is AI being used in healthcare?
What are the challenges mentioned?
Can you explain machine learning types?
```

## 🧪 Testing with Sample Data

Use the provided sample document (`sample_data/ai_document.txt`) to test the system:

1. Upload the AI document
2. Try these sample questions:
   - "What are the three types of machine learning?"
   - "How is AI being used in healthcare?"
   - "What are the main challenges of AI?"
   - "What does the document say about autonomous vehicles?"

## 📊 API Testing

### Using curl:
```bash
# Upload document
curl -X POST "http://localhost:8000/upload" \
     -F "file=@sample_data/ai_document.txt"

# Ask question
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "test_user",
       "question": "What are the applications of AI?",
       "top_k": 4
     }'

# Get documents list
curl -X GET "http://localhost:8000/documents"

# Get conversation history
curl -X GET "http://localhost:8000/history?user_id=test_user"
```

## 🔍 Troubleshooting

### Common Issues:

**1. MongoDB Connection Failed**
- Verify your password in the `.env` file
- Check your IP is whitelisted in MongoDB Atlas
- Ensure network connectivity

**2. Qdrant Connection Failed**
- Verify the URL and API key are correct
- Check your internet connection
- Confirm Qdrant cluster is running

**3. OpenAI API Errors**
- Verify your API key is valid and has credits
- Check rate limits
- Ensure proper formatting

**4. File Upload Issues**
- Check file size (should be reasonable)
- Verify file format (PDF or TXT only)
- Ensure proper permissions

### Checking Logs:
```bash
# View detailed logs
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## 🎯 Success Indicators

You'll know everything is working when you see:
- ✅ "Successfully connected to MongoDB!" 
- ✅ "Qdrant connection successful! Collection has X points."
- ✅ Document uploads complete successfully
- ✅ Questions return answers with citations and reasoning
- ✅ Follow-up suggestions appear

## 🚀 Next Steps

Once everything is running:
1. **Upload your own documents** (research papers, reports, manuals)
2. **Experiment with different question types** (factual, analytical, comparative)
3. **Test multi-turn conversations** (build on previous questions)
4. **Try the suggestions feature** (click on AI-generated follow-ups)
5. **Explore the API endpoints** (integrate with your own applications)

## 📞 Need Help?

If you encounter issues:
1. Check the console logs for error messages
2. Verify all credentials are correct
3. Ensure all dependencies are installed
4. Test each component individually using the troubleshooting section

**Happy RAG-ing! 🎉**