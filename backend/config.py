import os
from dotenv import load_dotenv, set_key, find_dotenv

# Path to .env file
ENV_FILE = find_dotenv() or os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.local')

# Load environment variables
load_dotenv(ENV_FILE)

class Config:
    """
    Centralized configuration management for the Serenity backend.
    Handles API key storage, retrieval, and persistence.
    """
    
    def __init__(self):
        self._groq_api_key = None
        self.load_api_key()
    
    def load_api_key(self):
        """Load Groq API key from environment or file."""
        # Try environment variable first
        self._groq_api_key = os.getenv('GROQ_API_KEY', '')
        
        # If not set or placeholder, try to load from .env file
        if not self._groq_api_key or self._groq_api_key == 'PLACEHOLDER_API_KEY':
            self._groq_api_key = ''
        
        print(f"[CONFIG] API Key loaded: {'[Configured]' if self._groq_api_key else '[Not configured]'}")
    
    def get_api_key(self):
        """Get the current Groq API key."""
        return self._groq_api_key
    
    def set_api_key(self, api_key):
        """
        Set and persist the Groq API key.
        Saves to .env file and updates runtime config.
        """
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        
        # Validate format (Groq keys typically start with 'gsk_')
        api_key = api_key.strip()
        
        # Save to .env file
        try:
            if os.path.exists(ENV_FILE):
                set_key(ENV_FILE, 'GROQ_API_KEY', api_key)
            else:
                # Create .env file if it doesn't exist
                with open(ENV_FILE, 'w') as f:
                    f.write(f'GROQ_API_KEY={api_key}\n')
            
            # Update runtime config
            self._groq_api_key = api_key
            os.environ['GROQ_API_KEY'] = api_key
            
            print(f"[CONFIG] API Key saved successfully")
            return True
        except Exception as e:
            print(f"[CONFIG] Error saving API key: {e}")
            raise
    
    def is_configured(self):
        """Check if API key is configured."""
        return bool(self._groq_api_key and len(self._groq_api_key) > 0)
    
    def validate_api_key(self, api_key=None):
        """
        Validate API key format.
        Returns (is_valid, message)
        """
        key = api_key if api_key else self._groq_api_key
        
        if not key:
            return False, "API key is empty"
        
        if len(key) < 20:
            return False, "API key appears too short"
        
        # Basic format check (Groq keys typically start with 'gsk_')
        if not key.startswith('gsk_'):
             return False, "API key should start with 'gsk_'"
        
        return True, "API key format looks valid"

# Global configuration instance
config = Config()
