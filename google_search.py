# google_search.py

class SearchResult:
    def __init__(self, snippet, url, source_title=None):
        self.snippet = snippet
        self.url = url
        self.source_title = source_title

class SearchResponse:
    def __init__(self, results):
        self.results = results

def search(queries, num_results=3):
    """Mock search function returning dummy data for testing."""
    responses = []
    for query in queries:
        dummy_results = [
            SearchResult(
                snippet=f"This is a mock snippet for query '{query}' - result {i+1}.",
                url=f"https://example.com/{query.replace(' ', '_')}/{i}",
                source_title="Mock News Source"
            )
            for i in range(num_results)
        ]
        responses.append(SearchResponse(results=dummy_results))
    return responses
