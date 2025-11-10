"""
Configuration file for API keys.
This file should be added to .gitignore if you hardcode keys here.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Option 1: Use environment variables (RECOMMENDED)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Option 2: Hardcode keys here (NOT RECOMMENDED - only for local development)
# Uncomment and add your keys if you want to hardcode them:
# PINECONE_API_KEY = "your-pinecone-key-here"
GEMINI_API_KEY = "AIzaSyCh8DJyc-l0iHxwIRqMQujEXCOUN1_6g28"

# Validation
if not PINECONE_API_KEY:
    print("WARNING: PINECONE_API_KEY not found!")
    
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found!")
