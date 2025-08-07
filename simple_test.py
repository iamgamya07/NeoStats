#!/usr/bin/env python3
# Simple test script for banking assistant
# Good for beginners to understand the project

import os
import json
import ast
import sys

# Add the current directory to the Python path to find utils module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import reusable utilities from common_utils
from utils.common_utils import data_processor, config_validator

def test_file_structure():
    # Test 1: Check if all required files exist
    print("Testing file structure...")
    
    # List of essential files for the project
    essential_files = [
        "app.py",                    # Main application
        "build_faiss_index.py",      # Index building script
        "config/config.py",          # Configuration management
        "data/banking_documents.jsonl", # Banking knowledge base
        "models/llm.py",             # Language model integration
        "utils/rag_utils.py",        # RAG utilities
        "utils/web_search.py",       # Web search functionality
        "data/met_scraper.py",       # Data scraping script
        "requirements.txt",          # Python dependencies
        "env_template.txt",          # Environment template
        "README.md"                  # Documentation
    ]
    
    missing_files = []
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"PASS: {file_path}")
        else:
            print(f"FAIL: {file_path} - Missing!")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\nLearning: Missing {len(missing_files)} files. This might affect functionality.")
        return False
    else:
        print(f"\nSUCCESS: All {len(essential_files)} essential files are present!")
        return True

def test_banking_data():
    # Test 2: Validate banking data structure
    print("\nTesting banking data...")
    
    try:
        # Use the reusable data processor for consistent data loading and validation
        documents = data_processor.load_jsonl("data/banking_documents.jsonl")
        
        # Use the reusable data processor for comprehensive validation
        validation_results = data_processor.validate_banking_data(documents)
        
        print(f"PASS: Successfully loaded {validation_results['valid_documents']} valid banking documents")
        print(f"   Total documents: {validation_results['total_documents']}")
        print(f"   Valid documents: {validation_results['valid_documents']}")
        print(f"   Invalid documents: {validation_results['invalid_documents']}")
        
        if validation_results['missing_title'] > 0:
            print(f"   WARNING: {validation_results['missing_title']} documents missing titles")
        if validation_results['missing_content'] > 0:
            print(f"   WARNING: {validation_results['missing_content']} documents missing content")
        if validation_results['empty_content'] > 0:
            print(f"   WARNING: {validation_results['empty_content']} documents with empty content")
        
        if documents:
            # Show sample data
            sample = documents[0]
            print(f"   Sample document:")
            print(f"      Title: {sample.get('title', 'No title')[:60]}...")
            print(f"      Content: {sample.get('content', 'No content')[:80]}...")
            
            # Check data quality
            titles = [doc.get('title', '') for doc in documents]
            unique_titles = set(titles)
            print(f"   Data quality: {len(unique_titles)} unique titles out of {len(documents)} documents")
        
        return validation_results['valid_documents'] > 0
        
    except FileNotFoundError:
        print("FAIL: banking_documents.jsonl not found!")
        print("Learning: This file contains your banking knowledge base.")
        return False
    except Exception as e:
        print(f"FAIL: Error reading banking data: {e}")
        return False

def test_config_structure():
    """Test 3: Check configuration structure (Environment variables concept)"""
    print("\nTesting configuration structure...")
    
    try:
        with open("config/config.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for required environment variables
        required_vars = [
            "AZURE_CHAT_COMPLETION_API_KEY",
            "AZURE_CHAT_COMPLETION_ENDPOINT", 
            "AZURE_CHAT_COMPLETION_VERSION",
            "AZURE_CHAT_COMPLETION_DEPLOYMENT_GPT",
            "AZURE_EMBEDDING",
            "AZURE_EMBEDDING_ENDPOINT",
            "AZURE_EMBEDDING_API_KEY",
            "AZURE_EMBEDDING_VERSION"
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"FAIL: Missing configuration variables: {', '.join(missing_vars)}")
            return False
        else:
            print(f"PASS: All {len(required_vars)} required configuration variables found")
            print("Learning: These variables connect to Azure OpenAI services")
            return True
            
    except Exception as e:
        print(f"FAIL: Error checking configuration: {e}")
        return False

def test_requirements():
    """Test 4: Validate requirements.txt (Dependency management)"""
    print("\nTesting requirements.txt...")
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        # Essential packages for the project
        essential_packages = [
            "streamlit",      # Web app framework
            "openai",         # Azure OpenAI integration
            "faiss-cpu",      # Vector search
            "numpy",          # Numerical computing
            "requests",       # HTTP requests
            "beautifulsoup4", # Web scraping
            "python-dotenv"   # Environment variables
        ]
        
        missing_packages = []
        for package in essential_packages:
            if not any(package in req for req in requirements):
                missing_packages.append(package)
        
        if missing_packages:
            print(f"FAIL: Missing packages: {', '.join(missing_packages)}")
            return False
        else:
            print(f"PASS: All {len(essential_packages)} essential packages listed")
            print(f"Total packages: {len(requirements)}")
            print("Learning: These packages provide the functionality for the banking assistant")
            return True
            
    except Exception as e:
        print(f"FAIL: Error reading requirements: {e}")
        return False

def test_env_template():
    """Test 5: Check environment template (Security and configuration)"""
    print("\nTesting environment template...")
    
    try:
        with open("env_template.txt", "r") as f:
            content = f.read()
        
        # Check for required environment variables in template
        required_vars = [
            "AZURE_CHAT_COMPLETION_API_KEY",
            "AZURE_CHAT_COMPLETION_ENDPOINT",
            "AZURE_EMBEDDING_API_KEY",
            "AZURE_EMBEDDING_ENDPOINT"
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"FAIL: Missing variables in template: {', '.join(missing_vars)}")
            return False
        else:
            print(f"PASS: All {len(required_vars)} required environment variables in template")
            print("Learning: This template helps set up secure API credentials")
            return True
            
    except Exception as e:
        print(f"FAIL: Error reading env template: {e}")
        return False

def test_python_syntax():
    """Test 6: Validate Python syntax (Code quality)"""
    print("\nTesting Python syntax...")
    
    python_files = [
        "app.py",
        "build_faiss_index.py", 
        "config/config.py",
        "models/llm.py",
        "utils/rag_utils.py",
        "utils/web_search.py",
        "data/met_scraper.py"
    ]
    
    syntax_errors = []
    for file_path in python_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Try to parse the Python code
            ast.parse(content)
            print(f"PASS: {file_path} - Valid syntax")
            
        except SyntaxError as e:
            print(f"FAIL: {file_path} - Syntax error: {e}")
            syntax_errors.append(file_path)
        except Exception as e:
            print(f"FAIL: {file_path} - Error: {e}")
            syntax_errors.append(file_path)
    
    if syntax_errors:
        print(f"\nWARNING: Found syntax errors in {len(syntax_errors)} files")
        return False
    else:
        print(f"\nSUCCESS: All {len(python_files)} Python files have valid syntax!")
        print("Learning: Valid syntax ensures the code can run without errors")
        return True

def main():
    """Run all tests with educational explanations"""
    print("Enhanced Simple NeoStats Tests")
    print("=" * 50)
    print("Beginner-friendly testing with learning explanations")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("File Structure", test_file_structure),
        ("Banking Data", test_banking_data),
        ("Config Structure", test_config_structure),
        ("Requirements", test_requirements),
        ("Environment Template", test_env_template),
        ("Python Syntax", test_python_syntax)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"FAIL: {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary with learning insights
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nSUCCESS: All tests passed! Your project is well-structured.")
        print("\nNext Steps for Learning:")
        print("   1. Read the README.md to understand the project")
        print("   2. Set up your .env file with Azure OpenAI credentials")
        print("   3. Install dependencies: pip install -r requirements.txt")
        print("   4. Build the index: python3 build_faiss_index.py")
        print("   5. Run the app: streamlit run app.py")
        print("   6. Try web search: Enable 'Web Search' in the app")
        print("   7. Update data: python3 data/met_scraper.py")
    else:
        print(f"\nWARNING: {total - passed} tests failed. Review the issues above.")
        print("\nLearning Tips:")
        print("   • Check file paths and permissions")
        print("   • Ensure all required files are present")
        print("   • Verify JSON syntax in data files")
        print("   • Review Python syntax in code files")
    
    print("\nThis testing helps you understand:")
    print("   • Project structure and organization")
    print("   • Data validation and quality")
    print("   • Configuration management")
    print("   • Dependency management")
    print("   • Code quality and syntax")

if __name__ == "__main__":
    main() 