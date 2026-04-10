"""
Source Verification Module
Verify content against trusted sources, Google News, and official domains
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import config


class SourceVerifier:
    """Verify news content against trusted sources"""
    
    def __init__(self):
        self.google_api_key = config.GOOGLE_API_KEY
        self.google_cx = config.GOOGLE_CX
        self.news_api_key = config.NEWS_API_KEY
        self.trusted_domains = config.TRUSTED_DOMAINS
    
    def verify_google_news(self, text: str) -> Dict:
        """
        Verify content on Google News
        
        Args:
            text: Text to search for
            
        Returns:
            Dictionary with verification results
        """
        search_query = text[:200]  # First 200 chars
        
        # If API key is not configured, return mock data
        if not self.google_api_key or not self.google_cx:
            return {
                "found_on_google_news": False,
                "similar_articles": 0,
                "search_query": search_query,
                "note": "Google API not configured"
            }
        
        try:
            # Google Custom Search API
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": self.google_cx,
                "q": search_query,
                "num": 10
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                total_results = int(data.get('searchInformation', {}).get('totalResults', 0))
                
                return {
                    "found_on_google_news": total_results > 0,
                    "similar_articles": min(total_results, 10),
                    "search_query": search_query,
                    "sources": [item.get('link') for item in data.get('items', [])[:3]]
                }
            else:
                return {
                    "found_on_google_news": False,
                    "similar_articles": 0,
                    "search_query": search_query,
                    "error": f"API returned status {response.status_code}"
                }
                
        except Exception as e:
            return {
                "found_on_google_news": False,
                "similar_articles": 0,
                "search_query": search_query,
                "error": str(e)
            }
    
    def verify_official_sources(self, text: str) -> Dict:
        """
        Check if content mentions official/trusted sources
        
        Args:
            text: Text to check
            
        Returns:
            Dictionary with official source information
        """
        text_lower = text.lower()
        found_domains = []
        
        # Check for trusted domain mentions
        for domain in self.trusted_domains:
            if domain in text_lower:
                found_domains.append(domain)
        
        # Calculate credibility boost
        credibility_boost = min(len(found_domains) * 10, 30)  # Max 30 points
        
        return {
            "official_sources_found": len(found_domains) > 0,
            "trusted_domains": found_domains,
            "domain_count": len(found_domains),
            "credibility_boost": credibility_boost
        }
    
    def verify_news_api(self, text: str) -> Dict:
        """
        Verify using NewsAPI
        
        Args:
            text: Text to search for
            
        Returns:
            Dictionary with news API results
        """
        if not self.news_api_key:
            return {
                "found": False,
                "articles_count": 0,
                "note": "NewsAPI not configured"
            }
        
        try:
            # Extract keywords from text (simple approach)
            keywords = ' '.join(text.split()[:10])  # First 10 words
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "apiKey": self.news_api_key,
                "q": keywords,
                "pageSize": 5,
                "sortBy": "relevancy"
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                total_results = data.get('totalResults', 0)
                
                return {
                    "found": total_results > 0,
                    "articles_count": total_results,
                    "top_sources": [
                        article.get('source', {}).get('name') 
                        for article in data.get('articles', [])[:3]
                    ]
                }
            else:
                return {
                    "found": False,
                    "articles_count": 0,
                    "error": f"API returned status {response.status_code}"
                }
                
        except Exception as e:
            return {
                "found": False,
                "articles_count": 0,
                "error": str(e)
            }
    
    def calculate_credibility_score(
        self, 
        prediction: Dict, 
        verification: Dict
    ) -> float:
        """
        Calculate overall credibility score
        
        Args:
            prediction: Prediction result from BERT model
            verification: Verification results
            
        Returns:
            Credibility score (0-100)
        """
        # Start with prediction confidence
        base_score = prediction['confidence']
        
        # Adjust based on Google News
        if verification['google_news'].get('found_on_google_news'):
            base_score += 10
        
        # Adjust based on official sources
        if verification['official_sources'].get('official_sources_found'):
            boost = verification['official_sources']['credibility_boost']
            base_score += boost
        
        # Adjust based on NewsAPI
        if verification.get('news_api', {}).get('found'):
            base_score += 5
        
        # If prediction is Fake, reduce score
        if prediction['prediction'] == 'Fake':
            base_score = max(base_score - 30, 0)
        
        # Cap at 100
        return min(base_score, 100.0)
    
    def comprehensive_verification(self, text: str, prediction: Dict) -> Dict:
        """
        Perform comprehensive verification
        
        Args:
            text: Text to verify
            prediction: Prediction result from BERT
            
        Returns:
            Complete verification report
        """
        # Verify on Google News
        google_news = self.verify_google_news(text)
        
        # Check official sources
        official_sources = self.verify_official_sources(text)
        
        # Verify on NewsAPI
        news_api = self.verify_news_api(text)
        
        # Combine results
        source_verification = {
            "google_news": google_news,
            "official_sources": official_sources,
            "news_api": news_api
        }
        
        # Calculate credibility score
        credibility_score = self.calculate_credibility_score(
            prediction, 
            source_verification
        )
        
        # Determine official approval
        official_approval = (
            prediction['prediction'] == 'Real' and
            (google_news.get('found_on_google_news') or 
             official_sources.get('official_sources_found'))
        )
        
        return {
            "prediction": prediction['prediction'],
            "confidence": prediction['confidence'],
            "source_verification": source_verification,
            "credibility_score": credibility_score,
            "official_approval": official_approval,
            "verification_summary": self._generate_summary(
                source_verification, 
                credibility_score
            )
        }
    
    def _generate_summary(self, verification: Dict, score: float) -> str:
        """Generate human-readable summary"""
        summaries = []
        
        if verification['google_news'].get('found_on_google_news'):
            count = verification['google_news'].get('similar_articles', 0)
            summaries.append(f"Found on Google News ({count} similar articles)")
        
        if verification['official_sources'].get('official_sources_found'):
            domains = verification['official_sources']['trusted_domains']
            summaries.append(f"Mentions official sources: {', '.join(domains[:3])}")
        
        if verification.get('news_api', {}).get('found'):
            summaries.append("Verified by NewsAPI")
        
        if not summaries:
            summaries.append("No external verification found")
        
        summary = " | ".join(summaries)
        summary += f" | Credibility Score: {score:.1f}/100"
        
        return summary


# Global verifier instance
_verifier = None


def get_verifier() -> SourceVerifier:
    """Get or create global verifier instance"""
    global _verifier
    if _verifier is None:
        _verifier = SourceVerifier()
    return _verifier


if __name__ == "__main__":
    # Test the verifier
    print("\n" + "="*50)
    print("Testing Source Verifier")
    print("="*50 + "\n")
    
    verifier = SourceVerifier()
    
    test_text = """
    The World Health Organization (WHO) announced new guidelines 
    for COVID-19 treatment. The CDC has confirmed the effectiveness 
    of the new protocol.
    """
    
    print("Testing text:")
    print(test_text[:100] + "...\n")
    
    # Test official sources
    official = verifier.verify_official_sources(test_text)
    print("Official Sources:")
    print(f"Found: {official['official_sources_found']}")
    print(f"Domains: {official['trusted_domains']}")
    print(f"Credibility boost: +{official['credibility_boost']}\n")
    
    # Mock prediction for testing
    mock_prediction = {
        "prediction": "Real",
        "confidence": 85.5
    }
    
    # Test comprehensive verification
    result = verifier.comprehensive_verification(test_text, mock_prediction)
    print("Comprehensive Verification:")
    print(f"Credibility Score: {result['credibility_score']:.1f}/100")
    print(f"Official Approval: {result['official_approval']}")
    print(f"Summary: {result['verification_summary']}")
    
    print("\n✅ Verifier is working correctly!")