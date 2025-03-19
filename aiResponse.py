import os
import traceback
import google.generativeai as genai

def geminiResponse(message):
    """
    Send a message to Google's Gemini API and return the response.
    
    Uses Gemini 2.0 Flash model specifically.
    
    Args:
        message (str): The message to send to Gemini.
        
    Returns:
        str: The text response from Gemini.
    """
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        
        print(f"API key found: {bool(api_key)}")
        
        if not api_key:
            try:
                from dotenv import load_dotenv
                load_dotenv()
                api_key = os.environ.get("GEMINI_API_KEY")
                print(f"API key loaded from .env: {bool(api_key)}")
            except ImportError:
                print("dotenv module not found")
        
        if not api_key:
            raise ValueError("API key not found. Please set the GEMINI_API_KEY environment variable or enter it in the web interface.")
        
        genai.configure(api_key=api_key)
        
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(message)

            if hasattr(response, 'text'):
                return response.text
            else:
                print(f"Unexpected response format: {type(response)}")
                return str(response)
                
        except Exception as list_error:
            print(f"Error listing models: {str(list_error)}")
            raise
            
    except Exception as e:
        print(f"Error in geminiResponse: {str(e)}")
        print(traceback.format_exc())
        return f"Error: {str(e)}\n\nTry running: pip install --upgrade google-generativeai"