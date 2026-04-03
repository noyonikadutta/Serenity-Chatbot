import sys
import os
import traceback

# Add backend directory to path to allow imports to work as if running from backend
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    import llm
    print(f"Testing Grok API connectivity with model: {llm.MODEL_NAME}")
    
    success, message = llm.test_api_connection()
    
    if success:
        print("\n[SUCCESS] Grok API is communicating!")
        print(f"Details: {message}")
    else:
        print("\n[FAILURE] Could not connect to Grok.")
        print(f"Error: {message}")

except Exception as e:
    print(f"\nERROR: Unexpected script error!")
    print(f"Error Message: {e}")
    traceback.print_exc()
