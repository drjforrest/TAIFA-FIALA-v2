#!/usr/bin/env python3
"""
Test script to verify Pinecone Assistant configuration
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not PINECONE_API_KEY:
    print("❌ PINECONE_API_KEY not found in environment variables")
    exit(1)

def test_assistant_connection():
    """Test basic assistant connection"""
    try:
        # Initialize Pinecone client
        pc = Pinecone(api_key=PINECONE_API_KEY)
        print("✅ Pinecone client initialized")
        
        # Try to get assistant
        assistant = pc.assistant.Assistant(assistant_name="ai-innovations")
        print("✅ Assistant 'ai-innovations' connected")
        
        # Test basic chat
        msg = Message(content="Hello, are you working?")
        resp = assistant.chat(messages=[msg])
        print(f"✅ Assistant response: {resp['message']['content']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Assistant test failed: {e}")
        return False

def test_file_upload():
    """Test file upload capability"""
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        assistant = pc.assistant.Assistant(assistant_name="ai-innovations")
        
        # Create a test file
        test_content = """
        African AI Research Sample
        
        Title: Machine Learning Applications in African Healthcare
        Authors: Dr. Kwame Nkrumah, Dr. Wangari Maathai
        Institution: University of Ghana, University of Nairobi
        
        Abstract: This paper explores the application of machine learning 
        techniques to address healthcare challenges in rural African communities.
        We developed a diagnostic tool using deep learning to identify common
        diseases from symptoms reported via mobile phones.
        
        Keywords: machine learning, healthcare, Africa, mobile health, diagnostics
        """
        
        with open("/tmp/test_research.txt", "w") as f:
            f.write(test_content)
        
        # Upload test file
        response = assistant.upload_file(
            file_path="/tmp/test_research.txt",
            timeout=30
        )
        
        print(f"✅ File upload successful: {response}")
        
        # Clean up
        os.unlink("/tmp/test_research.txt")
        
        return True
        
    except Exception as e:
        print(f"❌ File upload test failed: {e}")
        return False

def test_rag_query():
    """Test RAG query after file upload"""
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        assistant = pc.assistant.Assistant(assistant_name="ai-innovations")
        
        # Ask about uploaded content
        msg = Message(content="What healthcare applications are mentioned in the uploaded documents?")
        resp = assistant.chat(messages=[msg])
        
        print(f"✅ RAG query successful: {resp['message']['content']}")
        return True
        
    except Exception as e:
        print(f"❌ RAG query failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Pinecone Assistant Configuration...")
    print("=" * 50)
    
    # Test 1: Basic connection
    print("\n1. Testing assistant connection...")
    if test_assistant_connection():
        print("✅ Assistant is properly configured")
    else:
        print("❌ Assistant configuration issue")
        exit(1)
    
    # Test 2: File upload
    print("\n2. Testing file upload...")
    if test_file_upload():
        print("✅ File upload working")
    else:
        print("❌ File upload issue")
    
    # Test 3: RAG query
    print("\n3. Testing RAG query...")
    if test_rag_query():
        print("✅ RAG functionality working")
    else:
        print("❌ RAG query issue")
    
    print("\n" + "=" * 50)
    print("🎯 Assistant testing complete!")