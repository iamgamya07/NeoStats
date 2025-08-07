#!/usr/bin/env python3
"""
Simple Test Script for Banking Assistant
Basic tests for intern-level understanding
"""

import os
import json

def main():
    """Run basic tests for the banking assistant."""
    print("Simple Banking Assistant Tests")
    print("=" * 40)
    
    # Test 1: Check if main files exist
    print("\nChecking project files...")
    files_to_check = [
        "app.py",
        "config/config.py", 
        "data/banking_documents.jsonl",
        "models/llm.py",
        "utils/rag_utils.py",
        "requirements.txt"
    ]
    
    all_files_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"PASS: {file_path}")
        else:
            print(f"FAIL: {file_path} - Missing!")
            all_files_exist = False
    
    # Test 2: Check banking data
    print("\nChecking banking data...")
    try:
        with open("data/banking_documents.jsonl", "r", encoding="utf-8") as f:
            documents = []
            for line in f:
                try:
                    doc = json.loads(line.strip())
                    documents.append(doc)
                except json.JSONDecodeError:
                    continue
        
        print(f"PASS: Found {len(documents)} banking documents")
        if documents:
            print(f"   Sample: {documents[0].get('title', 'No title')[:50]}...")
    except Exception as e:
        print(f"FAIL: Error reading banking data: {e}")
        all_files_exist = False
    
    # Test 3: Check requirements
    print("\nChecking requirements...")
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read().strip().split("\n")
        print(f"PASS: Found {len(requirements)} required packages")
        print(f"   Includes: {', '.join(requirements[:3])}...")
    except Exception as e:
        print(f"FAIL: Error reading requirements: {e}")
        all_files_exist = False
    
    # Summary
    print("\n" + "=" * 40)
    if all_files_exist:
        print("SUCCESS: All basic tests passed!")
        print("Next steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Set up .env file with Azure OpenAI credentials")
        print("   3. Run: streamlit run app.py")
    else:
        print("WARNING: Some issues found. Please check the errors above.")
    
    print("\nTIP: For detailed testing, run: python3 simple_test.py")

if __name__ == "__main__":
    main() 