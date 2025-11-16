import os
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner

# Load environment variables at module import time
_dotenv_path = "/home/ed/kaggle/recipe/.env"
if os.path.exists(_dotenv_path):
    load_dotenv(dotenv_path=_dotenv_path)

# Load model configuration from environment variables with defaults
DEFAULT_LLM = os.getenv("DEFAULT_LLM", "gemini-2.0-flash")
DEFAULT_REASONING_LLM = os.getenv("DEFAULT_REASONING_LLM", "gemini-2.5-flash")

def load_environment_variables():
    """
    Load environment variables from a .env file located at /home/ed/kaggle/recipe/.env

    Note: Environment variables are now loaded automatically at module import time.
    This function is kept for backward compatibility.
    """
    # Use the specific .env file path
    dotenv_path = "/home/ed/kaggle/recipe/.env"

    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
        print(f"Loaded environment variables from: {dotenv_path}")
    else:
        print(f"Warning: .env file not found at {dotenv_path}. Ensure it's in the correct location.")

def create_session(runner: InMemoryRunner, session_id: str, user_id: str, state=None):
    """
    Create a new session using the provided runner.
    
    :param runner: The InMemoryRunner instance to use for session creation.
    :param session_id: The ID of the session to create.
    :param user_id: The ID of the user for whom the session is created.
    """
    import asyncio
    print(f"Creating session: {session_id} for user: {user_id} on app: {runner.app_name}")
    
    try:
        asyncio.run(runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
            state=state or {}
        ))
        print("Session created successfully.")
    except Exception as e:
        print(f"Error creating session: {e}")
        exit()