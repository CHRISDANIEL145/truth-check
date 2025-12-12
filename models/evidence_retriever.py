# models/evidence_retriever.py
import wikipedia
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote_plus


class EvidenceRetriever:
    def __init__(self):
        self.wikipedia_timeout = 10
        self.max_evidence_sources = 10
        self.trusted_domains = [
            'reuters.com', 'apnews.com', 'bbc.com', 'nature.com',
            'science.org', 'who.int', 'cdc.gov', 'nasa.gov', 
            'wikipedia.org', '.gov', '.edu'
        ]
        
    def get_evidence(self, keywords):
        """Retrieve evidence from multiple sources with credibility scoring"""
        evidence = []
        
        # Get evidence from Wikipedia (most reliable)
        wiki_evidence = self._get_wikipedia_evidence(keywords)
        evidence.extend(wiki_evidence)
        
        # Get evidence from web search (using Google Custom Search as fallback)
        web_evidence = self._get_web_search_evidence(keywords)
        evidence.extend(web_evidence)
        
        # Sort by credibility score and return top sources
        evidence.sort(key=lambda x: x.get('credibility_score', 0.0), reverse=True)
        
        return evidence[:10]
    
    def _assign_credibility_score(self, source_type, url):
        """Assign credibility scores based on source type and domain"""
        if 'wikipedia.org' in url:
            return 0.95
        elif any(url.endswith(gov) for gov in ['.gov', '.gov/']):
            return 0.92
        elif any(url.endswith(edu) for edu in ['.edu', '.edu/']):
            return 0.88
        elif any(trusted in url for trusted in ['reuters.com', 'apnews.com', 'bbc.com']):
            return 0.85
        elif any(sci in url for sci in ['nature.com', 'science.org', 'ncbi.nlm.nih.gov']):
            return 0.90
        elif source_type == 'wikipedia':
            return 0.95
        elif source_type == 'academic':
            return 0.88
        elif source_type == 'government':
            return 0.92
        elif source_type == 'news_trusted':
            return 0.80
        else:
            return 0.60
    
    def _get_wikipedia_evidence(self, keywords):
        """Retrieve evidence from Wikipedia"""
        evidence = []
        
        try:
            search_terms = ' '.join(keywords[:4])
            search_results = wikipedia.search(search_terms, results=5)
            
            for title in search_results:
                try:
                    summary = wikipedia.summary(title, sentences=7, auto_suggest=False)
                    url = f'https://en.wikipedia.org/wiki/{title.replace(" ", "_")}'
                    
                    evidence.append({
                        'content': summary,
                        'source': f'Wikipedia - {title}',
                        'url': url,
                        'credibility_score': self._assign_credibility_score('wikipedia', url),
                        'source_type': 'wikipedia'
                    })
                    
                    if len(evidence) >= 3:
                        break
                        
                except (wikipedia.DisambiguationError, wikipedia.PageError):
                    continue
                    
        except Exception as e:
            print(f"Wikipedia search error: {e}")
        
        return evidence
    
    def _get_web_search_evidence(self, keywords):
        """Retrieve evidence from web search using SearXNG metasearch"""
        evidence = []
        
        try:
            query = ' '.join(keywords[:5])
            
            # Method 1: Try DuckDuckGo Lite (more reliable)
            ddg_results = self._search_duckduckgo_lite(query)
            evidence.extend(ddg_results)
            
            # Method 2: If DuckDuckGo fails, use direct scraping with Google
            if len(evidence) < 3:
                google_results = self._search_google_scrape(query)
                evidence.extend(google_results)
            
        except Exception as e:
            print(f"Web search error: {e}")
        
        return evidence[:5]
    
    def _search_duckduckgo_lite(self, query):
        """Search using DuckDuckGo Lite (HTML version, more stable)"""
        results = []
        
        try:
            url = "https://lite.duckduckgo.com/lite/"
            data = {"q": query}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.post(url, data=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all result rows
                result_table = soup.find_all('tr')
                
                for row in result_table[:10]:
                    try:
                        link = row.find('a', class_='result-link')
                        snippet_td = row.find('td', class_='result-snippet')
                        
                        if link and snippet_td:
                            result_url = link.get('href', '')
                            title = link.get_text(strip=True)
                            snippet = snippet_td.get_text(strip=True)
                            
                            if result_url and snippet:
                                results.append({
                                    'content': snippet,
                                    'source': f'Web - {title}',
                                    'url': result_url,
                                    'credibility_score': self._assign_credibility_score('web', result_url),
                                    'source_type': 'web'
                                })
                                
                                if len(results) >= 3:
                                    break
                    except:
                        continue
                        
        except Exception as e:
            print(f"DuckDuckGo Lite error: {e}")
        
        return results
    
    def _search_google_scrape(self, query):
        """Search using Google scraping (fallback method)"""
        results = []
        
        try:
            url = f"https://www.google.com/search?q={quote_plus(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find search results
                search_results = soup.find_all('div', class_='g')
                
                for result in search_results[:5]:
                    try:
                        link = result.find('a')
                        snippet_div = result.find('div', class_=['VwiC3b', 'lEBKkf'])
                        
                        if link and snippet_div:
                            result_url = link.get('href', '')
                            title = result.find('h3')
                            title_text = title.get_text(strip=True) if title else 'Unknown'
                            snippet = snippet_div.get_text(strip=True)
                            
                            if result_url.startswith('http') and snippet:
                                results.append({
                                    'content': snippet,
                                    'source': f'Web - {title_text}',
                                    'url': result_url,
                                    'credibility_score': self._assign_credibility_score('web', result_url),
                                    'source_type': 'web'
                                })
                                
                                if len(results) >= 3:
                                    break
                    except:
                        continue
                        
        except Exception as e:
            print(f"Google scrape error: {e}")
        
        return results
