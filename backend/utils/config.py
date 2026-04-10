"""
Configuration Management
Load environment variables and application settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Application Configuration"""
    
    # Model Configuration
    MODEL_PATH = os.getenv('MODEL_PATH', './model/fake_news_bert_model')
    MAX_LENGTH = int(os.getenv('MAX_LENGTH', '512'))
    
    # API Keys
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    GOOGLE_CX = os.getenv('GOOGLE_CX', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    
    # Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '8000'))
    
    # File Upload Configuration
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '10485760'))  # 10MB
    ALLOWED_EXTENSIONS = ['pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png']
    
    # CORS Configuration
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    
    # Text Processing
    MIN_TEXT_LENGTH = 10
    MAX_TEXT_CHARS = 2048
    
    # Prediction Thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.85
    LOW_CONFIDENCE_THRESHOLD = 0.60
    
    # Official Sources for Verification
    TRUSTED_DOMAINS = [
        'who.int',
        'cdc.gov',
        'gov.in',
        'pib.gov.in',
        'bbc.com',
        'reuters.com',
        'apnews.com',
        'government.uk',
        'nih.gov',
        'un.org'
    ]
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        # Check if model path exists
        model_path = Path(cls.MODEL_PATH)
        if not model_path.exists():
            print(f"Warning: Model path does not exist: {cls.MODEL_PATH}")
            return False
        
        print("✅ Configuration validated successfully")
        return True
    
    @classmethod
    def get_summary(cls) -> dict:
        """Get configuration summary"""
        return {
            "model_path": cls.MODEL_PATH,
            "max_length": cls.MAX_LENGTH,
            "host": cls.HOST,
            "port": cls.PORT,
            "max_file_size_mb": cls.MAX_FILE_SIZE / (1024 * 1024),
            "allowed_extensions": cls.ALLOWED_EXTENSIONS,
            "has_google_api_key": bool(cls.GOOGLE_API_KEY),
            "has_news_api_key": bool(cls.NEWS_API_KEY),
            "trusted_domains_count": len(cls.TRUSTED_DOMAINS)
        }


# Create a singleton instance
config = Config()


if __name__ == "__main__":
    print("Configuration Summary:")
    print("=" * 50)
    
    summary = Config.get_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    print("=" * 50)
    Config.validate()