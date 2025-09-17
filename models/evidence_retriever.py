# models/evidence_retriever.py
import wikipedia
import requests
import time

# Import the google_search tool for real-time news simulation
from google_search import search as google_search_tool

class EvidenceRetriever:
    def __init__(self):
        self.wikipedia_timeout = 10
        self.news_timeout = 10 # This timeout is less relevant now but kept for consistency
        
    def get_evidence(self, keywords):
        """Retrieve evidence from multiple sources"""
        evidence = []
        
        # Get evidence from Wikipedia
        wiki_evidence = self._get_wikipedia_evidence(keywords)
        evidence.extend(wiki_evidence)
        
        # Get evidence from a simulated "real-time" news search
        # This replaces the unreliable Google News RSS feed approach
        realtime_news_evidence = self._get_realtime_news_evidence(keywords)
        evidence.extend(realtime_news_evidence)
        
        return evidence
    
    def _get_wikipedia_evidence(self, keywords):
        """Retrieve evidence from Wikipedia"""
        evidence = []
        
        try:
            # Increased search results from 3 to 5
            search_terms = ' '.join(keywords[:3])
            search_results = wikipedia.search(search_terms, results=5) # Increased results
            
            for title in search_results:
                try:
                    # Increased summary sentences from 3 to 5
                    summary = wikipedia.summary(title, sentences=5, auto_suggest=False) # Increased sentences
                    
                    evidence.append({
                        'content': summary,
                        'source': f'Wikipedia - {title}',
                        'url': f'https://en.wikipedia.org/wiki/{title.replace(" ", "_")}'
                    })
                    
                    # Allow more Wikipedia sources (e.g., up to 3 instead of 2)
                    if len(evidence) >= 3: # Increased limit
                        break
                        
                except (wikipedia.DisambiguationError, wikipedia.PageError):
                    print(f"Wikipedia disambiguation/page error for '{title}'. Skipping.")
                    continue
                    
        except Exception as e:
            print(f"Wikipedia search error: {e}")
        
        return evidence
    
    def _get_realtime_news_evidence(self, keywords):
        """
        Simulates real-time news retrieval using the google_search tool.
        This focuses on finding recent and breaking news snippets.
        """
        evidence = []
        
        try:
            # Create a search query emphasizing recency and news context
            # Adding terms like "breaking news" or "latest update" helps bias results
            query_phrases = [
                f"{' '.join(keywords)} breaking news",
                f"{' '.join(keywords)} latest update",
                f"{' '.join(keywords)} recent news article"
            ]

            # Perform multiple searches for broader coverage
            all_search_results = []
            for q_phrase in query_phrases:
                # The google_search tool provides recent results by default for news queries
                search_results_for_phrase = google_search_tool(queries=[q_phrase])
                if search_results_for_phrase and search_results_for_phrase[0].results:
                    all_search_results.extend(search_results_for_phrase[0].results)
            
            # Filter and add unique relevant snippets
            added_urls = set()
            for result in all_search_results:
                if result.snippet and result.url and result.url not in added_urls:
                    evidence.append({
                        'content': result.snippet,
                        'source': f'Real-time Web News - {result.source_title or "Unknown"}',
                        'url': result.url
                    })
                    added_urls.add(result.url)
                    if len(evidence) >= 5: # Limit total real-time news snippets
                        break
        except Exception as e:
            print(f"Real-time news search error: {e}")
            
        return evidence

