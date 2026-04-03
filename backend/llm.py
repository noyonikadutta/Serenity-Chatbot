from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from config import config

# Load environment variables
load_dotenv()

# -------------------------------------------------------------
# GROQ API CONFIGURATION
# -------------------------------------------------------------
# Groq uses OpenAI-compatible API
# Base URL: https://api.groq.com/openai/v1
# Model: llama3-70b-8192

def get_groq_client():
    """
    Creates and returns a Groq API client.
    Uses the API key from config module.
    """
    api_key = config.get_api_key()
    
    if not api_key:
        raise ValueError("Groq API key not configured. Please set it via the frontend settings.")
    
    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

# Model configuration
# Model configuration
MODEL_NAME = "llama-3.3-70b-versatile"

def extract_metadata(user_input):
    """
    Calls Groq to extract structured metadata (facts, emotions, topics) 
    from the user's input in STRICT JSON format.
    """
    system_prompt = """
    You are a backend analysis engine for a therapy chatbot.
    Analyze the following user input and return JSON ONLY.
    
    Structure:
    {
      "facts": {
        "name": null or string (if mentioned),
        "age": null or string (if mentioned),
        "preferences": ["pref1", "pref2"] (extract array)
      },
      "emotion": "sad | anxious | happy | stressed | neutral | angry",
      "topics": ["topic1", "topic2"],
      "memory_worthy": true | false (is there a new fact?),
      "entity": null or string (dominant entity mentioned like 'Mom', 'Boss'),
      "intent": "question | statement | emotional"
    }
    """

    try:
        client = get_groq_client()
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"USER INPUT: {user_input}\n\nAnalyze this and return only JSON."}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=500
        )
        
        # Parse JSON response
        text = response.choices[0].message.content.strip()
        print(f"[LLM] Raw Extraction: {text}")
        return json.loads(text)
        
    except Exception as e:
        print(f"[LLM] Extraction Error: {e}")
        # Return fallback empty structure
        return {
            "facts": {"name": None, "age": None, "preferences": []},
            "emotion": "neutral",
            "topics": [],
            "memory_worthy": False,
            "entity": None,
            "intent": "statement"
        }

def generate_response(user_input, context_str):
    """
    Generates a therapeutic response using the explicit context provided.
    Does NOT use internal model memory of the conversation history.
    It relies entirely on the 'context_str' we build from our manual memory.
    """
    system_prompt = f"""
    You are Serenity, an empathetic, professional therapist chatbot.
    
    CRITICAL INSTRUCTION:
    Use the following MEMORY CONTEXT to answer. 
    If the user's name is in the context, use it naturally.
    Reflect on the 'Dominant Emotion' in the context.
    Refer to 'Recent Topics' if relevant.
    
    MEMORY CONTEXT:
    {context_str}
    
    Respond warmly, concisely, and supportively. 
    Do not mention "I see from my memory" or "My database shows". 
    Just speak naturally.
    """

    try:
        client = get_groq_client()
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"[LLM] Generation Error: {e}")
        if "401" in str(e) or "authentication" in str(e).lower():
            return "I'm having trouble connecting (Invalid API Key). Please check your Groq API key in settings."
        elif "429" in str(e):
            return "I'm feeling a bit overwhelmed right now (Rate Limit). Please give me a moment and try again."
        return "I'm listening. Please go on."

def test_api_connection():
    """
    Tests the Groq API connection.
    Returns (success: bool, message: str)
    """
    try:
        client = get_groq_client()
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": "Say 'OK' if you can hear me."}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        return True, f"Connection successful! Groq responded: {result}"
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "authentication" in error_msg.lower():
            return False, "Authentication failed. Please check your API key."
        elif "404" in error_msg:
            return False, "Model not found. Please verify the model name."
        else:
            return False, f"Connection failed: {error_msg}"
