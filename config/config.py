import os
from dotenv import load_dotenv
# Import reusable utilities from common_utils
from utils.common_utils import config_validator

# Load environment variables
load_dotenv()

AZURE_CHAT_COMPLETION_API_KEY = "3NGVhi0oYwUv1JYWBNb0jLmBPGdWr4v9Rpgbd1RiRhfMLGCXU9uLJQQJ99BFACHYHv6XJ3w3AAAAACOGDOpG"
AZURE_CHAT_COMPLETION_ENDPOINT = "https://danch-mblxhvnj-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview"
AZURE_CHAT_COMPLETION_VERSION = "2025-01-01-preview"
AZURE_CHAT_COMPLETION_DEPLOYMENT_GPT = "gpt-4o"

# Azure OpenAI Embedding Config
AZURE_EMBEDDING = "text-embedding-3-large"
AZURE_EMBEDDING_ENDPOINT = "https://gpt-dan1.openai.azure.com/openai/deployments/text-embedding-3-large/embeddings?api-version=2023-05-15"
AZURE_EMBEDDING_API_KEY = "7d1TMPfx2WbUr9x643MMGqKpE2L6O3iYNf8IVAoxxWGCK2xzORPqJQQJ99BFACYeBjFXJ3w3AAABACOGGM82"
AZURE_EMBEDDING_VERSION = "2023-05-15"

def validate_config():
    """
    Validate that all required environment variables are set using reusable config validator.
    
    Raises:
        ValueError: If any required variable is missing
    """
    required_var_names = [
        "AZURE_CHAT_COMPLETION_API_KEY",
        "AZURE_CHAT_COMPLETION_ENDPOINT", 
        "AZURE_CHAT_COMPLETION_VERSION",
        "AZURE_CHAT_COMPLETION_DEPLOYMENT_GPT",
        "AZURE_EMBEDDING",
        "AZURE_EMBEDDING_ENDPOINT",
        "AZURE_EMBEDDING_API_KEY",
        "AZURE_EMBEDDING_VERSION",
    ]
    
    # Use the reusable config validator for consistent validation across the project
    validation_results = config_validator.validate_env_variables(required_var_names)
    missing_vars = [var for var, is_set in validation_results.items() if not is_set]
    
    if missing_vars:
        raise ValueError(
            f"The following environment variables are not set: {', '.join(missing_vars)}. "
            "Please check your .env file or environment variables."
        )

# Only validatinh this module if it's imported directly (not when imported by other modules)
if __name__ == "__main__":
    validate_config()
    print("All Azure OpenAI configuration variables are set correctly.")
