import logging
from openai import AzureOpenAI
from config.config import (
    AZURE_CHAT_COMPLETION_API_KEY, 
    AZURE_CHAT_COMPLETION_ENDPOINT, 
    AZURE_CHAT_COMPLETION_VERSION, 
    AZURE_CHAT_COMPLETION_DEPLOYMENT_GPT, 
    validate_config
)

# Initialize Azure OpenAI client with error handling
def get_azure_client():
    """
    Get Azure OpenAI client with proper error handling.
    
    Returns:
        AzureOpenAI: Configured client or None if configuration is invalid
    """
    try:
        # Validate configuration
        validate_config()
        
        return AzureOpenAI(
            api_key=AZURE_CHAT_COMPLETION_API_KEY,
            api_version=AZURE_CHAT_COMPLETION_VERSION,
            azure_endpoint=AZURE_CHAT_COMPLETION_ENDPOINT
        )
    except Exception as e:
        logging.error(f"Failed to initialize Azure OpenAI client: {e}")
        return None

def generate_llm(prompt: str, mode: str = "detailed", stream: bool = False) -> str:
    """
    Generate LLM response using Azure OpenAI API.
    
    Args:
        prompt (str): The input prompt
        mode (str): Response mode - "concise" or "detailed"
        stream (bool): Whether to stream the response
        
    Returns:
        str: Generated response or error message
    """

    # Validating the configuration
    client = get_azure_client()
    if client is None:
        return "Error: Azure OpenAI configuration is invalid. Please check your .env file and ensure all required variables are set."

    try:

        #Prompt for when concise is selected
        if mode == "concise":
            system_prompt = (
                "You are a helpful AI assistant specializing in Indian banking, finance, and regulations. "
                "Respond concisely and clearly."
            )
        else:
            #Prompt for when detailed is selected
            system_prompt = (
                "You are a helpful AI assistant specializing in Indian banking, finance, and regulations. "
                "Provide detailed and comprehensive answers including examples and context where appropriate."
            )

        response = client.chat.completions.create(
            model=AZURE_CHAT_COMPLETION_DEPLOYMENT_GPT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1024,
            stream=stream
        )

        if stream:
            full_response = ""
            for chunk in response:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
            return full_response.strip()

        return response.choices[0].message.content.strip()

    except Exception as e:
        logging.exception("LLM generation failed")
        return f"Error from LLM: {str(e)}"
