# config.py - Updated with Resend support
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # RedStone API
    REDSTONE_API_URL = "https://api.redstone.finance/prices"
    
    # Ollama Configuration (Primary)
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    # Easy API Switch (set to True to use cloud APIs)
    USE_CLOUD_API = os.getenv("USE_CLOUD_API", "False").lower() == "true"
    
    # Cloud API Keys (for easy switching)
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Resend Email Configuration
    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "alerts@yourdomain.com")
    ENABLE_EMAIL_NOTIFICATIONS = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "True").lower() == "true"
    
    # Database
    DATABASE_URL = "sqlite:///./stonewatch.db"
    
    # Environment
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    def has_api_key(self):
        """Check if any cloud API key is available"""
        return bool(self.CLAUDE_API_KEY or self.OPENAI_API_KEY)
    
    def has_resend_key(self):
        """Check if Resend API key is available"""
        return bool(self.RESEND_API_KEY)
    
    def get_active_backend(self):
        """Get description of active backend"""
        if self.USE_CLOUD_API and self.has_api_key():
            if self.CLAUDE_API_KEY:
                return "cloud_api_claude"
            elif self.OPENAI_API_KEY:
                return "cloud_api_openai"
        return "ollama_local"
    
    def print_status(self):
        """Print current configuration status"""
        print("🔧 tokenTalk Configuration:")
        print(f"   Primary Backend: Ollama ({self.OLLAMA_URL})")
        print(f"   Cloud API Mode: {'Enabled' if self.USE_CLOUD_API else 'Disabled'}")
        print(f"   Resend Email: {'Enabled' if self.has_resend_key() else 'Disabled'}")
        print(f"   Active Backend: {self.get_active_backend()}")

settings = Settings()