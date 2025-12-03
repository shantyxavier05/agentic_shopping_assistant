"""
Script to create .env file for OpenAI API key
Run this script to create the .env file in the project root
"""
import os

def create_env_file():
    """Create .env file with OPENAI_API_KEY variable"""
    env_content = "OPENAI_API_KEY=your_api_key_here\n"
    
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    
    if os.path.exists(env_path):
        print(f".env file already exists at {env_path}")
        print("Checking if it needs updating...")
        with open(env_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        if 'OPENAI_API_KEY' in existing_content:
            print(".env file already contains OPENAI_API_KEY. No changes needed.")
            return
    
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"Created .env file at {env_path}")
        print("IMPORTANT: Replace 'your_api_key_here' with your actual OpenAI API key!")
    except Exception as e:
        print(f"Error creating .env file: {e}")

if __name__ == "__main__":
    create_env_file()

