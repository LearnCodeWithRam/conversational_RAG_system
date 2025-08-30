#!/usr/bin/env python3
"""
Database Setup Script for RAG Q&A System
This script initializes and tests connections to MongoDB Atlas and Qdrant Cloud
"""
from qdrant_client.http import models
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_core.messages import SystemMessage, HumanMessage
from config import  COLLECTION_NAME, mongo_client, qdrant_client

# Load environment variables
load_dotenv()

def setup_mongodb():
    """Connect to MongoDB Atlas using verifying connections"""
    print("🔄 Setting up MongoDB Atlas...")

    try:
        mongo_client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        return True
    except Exception as e:
        print(f"❌ MongoDB setup failed: {e}")
        return False




def setup_qdrant():
    """Setup Qdrant Cloud connection and create collection"""
    print("🔄 Setting up Qdrant Cloud...")
    
    try:
        # Initialize Qdrant client with your credentials
      
        # Check if collection exists
        collections = qdrant_client.get_collections()
        collection_names = [col.name for col in collections.collections]

        if COLLECTION_NAME not in collection_names:
            # Create collection for document embeddings
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=384,  # all-MiniLM-L6-v2 embedding size
                    distance=models.Distance.COSINE
                ),
            )
            print(f"✅ Qdrant collection '{COLLECTION_NAME}' created successfully!")
        else:
            print(f"✅ Qdrant collection '{COLLECTION_NAME}' already exists!")

        # Get collection info
        collection_info = qdrant_client.get_collection(COLLECTION_NAME)
        print(f"📊 Qdrant Collection Stats:")
        print(f"   - Points: {collection_info.points_count}")
        print(f"   - Vector size: {collection_info.config.params.vectors.size}")
        print(f"   - Distance metric: {collection_info.config.params.vectors.distance}")
        
        return True
        
    except Exception as e:
        print(f"❌ Qdrant setup failed: {e}")
        print("Please check your Qdrant URL and API key.")
        return False

def test_ollama():
    """Test Ollama API connection"""
    print("🔄 Testing Ollama API...")

    try:

        # Set up Ollama LLM
        llm = OllamaLLM(
            model="llama3.1:8b",  # Use the model you're hosting
            base_url="http://115.241.186.203",  # Ollama server URL
            temperature=0.3
        )

        # Use simple system/user messages for testing
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Hello!")
        ]

        print("🔄 Sending test message to Ollama...")

        response = llm.invoke(messages)

        print("✅ Ollama API connection successful!")
        print("🧠 Response:", response)
        return True

    except Exception as e:
        print(f"❌ Ollama API test failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 RAG Q&A System Database Setup")
    print("=" * 50)
    
    # Setup results
    mongodb_ok = setup_mongodb()
    print()
    
    qdrant_ok = setup_qdrant()
    print()

    openai_ok = test_ollama()
    print()
    
    # Summary
    print("📋 Setup Summary:")
    print(f"   - MongoDB Atlas: {'✅ Ready' if mongodb_ok else '❌ Failed'}")
    print(f"   - Qdrant Cloud: {'✅ Ready' if qdrant_ok else '❌ Failed'}")
    print(f"   - Ollama API: {'✅ Ready' if openai_ok else '❌ Failed'}")
    
    if all([mongodb_ok, qdrant_ok, openai_ok]):
        print("\n🎉 All services are ready! You can now start the RAG Q&A system.")
        print("Run: uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("\n⚠️ Some services failed to initialize. Please check the errors above.")

if __name__ == "__main__":
    main()