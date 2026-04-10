"""
Text Processing Utilities
Clean and preprocess text for BERT model
"""

import re
from typing import Optional


def clean_text(text: str) -> str:
    """
    Clean and preprocess text for BERT
    
    Args:
        text: Raw input text
        
    Returns:
        Cleaned text string
    """
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove mentions and hashtags (keep the word)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#', '', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def truncate_text(text: str, max_chars: int = 2048) -> str:
    """
    Truncate text to maximum character limit
    BERT supports max 512 tokens ≈ 2048 characters
    
    Args:
        text: Input text
        max_chars: Maximum characters (default 2048)
        
    Returns:
        Truncated text
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars]


def validate_text(text: str, min_length: int = 10) -> tuple[bool, Optional[str]]:
    """
    Validate input text
    
    Args:
        text: Input text to validate
        min_length: Minimum required length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text:
        return False, "Text cannot be empty"
    
    if not isinstance(text, str):
        return False, "Text must be a string"
    
    cleaned = clean_text(text)
    
    if len(cleaned) < min_length:
        return False, f"Text too short. Minimum {min_length} characters required"
    
    return True, None


def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    """
    Extract top keywords from text (simple implementation)
    
    Args:
        text: Input text
        top_n: Number of keywords to extract
        
    Returns:
        List of keywords
    """
    # Simple word frequency approach
    words = text.lower().split()
    
    # Remove common stopwords
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'was', 
                 'are', 'were', 'been', 'be', 'have', 'has', 'had'}
    
    words = [w for w in words if w not in stopwords and len(w) > 3]
    
    # Count frequency
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, freq in sorted_words[:top_n]]


def get_text_stats(text: str) -> dict:
    """
    Get statistics about text
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with text statistics
    """
    words = text.split()
    sentences = text.split('.')
    
    return {
        "character_count": len(text),
        "word_count": len(words),
        "sentence_count": len([s for s in sentences if s.strip()]),
        "average_word_length": sum(len(w) for w in words) / len(words) if words else 0,
        "contains_url": bool(re.search(r'http\S+|www\S+', text)),
        "contains_email": bool(re.search(r'\S+@\S+', text))
    }


if __name__ == "__main__":
    # Test the functions
    sample_text = """
    BREAKING NEWS!!! Scientists discover SHOCKING truth about vaccines! 
    Visit www.fakenews.com for more info. Contact us at fake@news.com
    #FakeNews #Shocking @BreakingNews
    """
    
    print("Original text:")
    print(sample_text)
    print("\nCleaned text:")
    print(clean_text(sample_text))
    print("\nText stats:")
    print(get_text_stats(sample_text))
    print("\nKeywords:")
    print(extract_keywords(sample_text))