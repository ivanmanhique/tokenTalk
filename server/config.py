# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # RedStone API
    REDSTONE_API_URL = "https://api.redstone.finance/prices"
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Database
    DATABASE_URL = "sqlite:///./stonewatch.db"
    
    # Environment
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    def validate_openai_key(self):
        """Validate that OpenAI API key is set"""
        if not self.OPENAI_API_KEY:
            print("⚠️  WARNING: OPENAI_API_KEY not set. Using fallback parsing.")
            return False
        return True


settings = Settings()