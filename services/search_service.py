import os
from typing import Dict, Any
from duckduckgo_search import DDGS

class AISearchTools:
    def __init__(self):
        """
        Initialize search tools with DuckDuckGo and local LLM.
        
        Args:
            local_llm_model (str, optional): Local LLM model name. Defaults to 'llama2'.
        """
        # Initialize DuckDuckGo search
        self.ddgs = DDGS()
    
    def get_organization_website(self, organization_name: str) -> Dict[str, Any]:
        """
        Find the website for a given organization using web search.
        
        Args:
            organization_name (str): Name of the company or school
        
        Returns:
            Dict[str, Any]: Search results for the organization
        """
        try:
            search_query = f"{organization_name} official website"
            results = list(self.ddgs.text(search_query, max_results=3))
            
            return {
                "query": search_query,
                "results": [
                    {
                        "title": result['title'],
                        "url": result['href'],
                        "snippet": result['body']
                    } for result in results
                ]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_person_details(self, full_name: str) -> Dict[str, Any]:
        """
        Retrieve professional details for a given person.
        
        Args:
            full_name (str): Full name of the person
        
        Returns:
            Dict[str, Any]: Professional information search results
        """
        try:
            # Search for person's professional information
            search_query = f"{full_name} professional profile LinkedIn"
            results = list(self.ddgs.text(search_query, max_results=3))
            
            return {
                "query": search_query,
                "results": [
                    {
                        "title": result['title'],
                        "url": result['href'],
                        "snippet": result['body']
                    } for result in results
                ]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def advanced_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Perform an advanced search with additional context.
        
        Args:
            query (str): Search query
            max_results (int, optional): Maximum number of results. Defaults to 5.
        
        Returns:
            Dict[str, Any]: Comprehensive search results
        """
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            
            return {
                "query": query,
                "results": [
                    {
                        "title": result['title'],
                        "url": result['href'],
                        "snippet": result['body']
                    } for result in results
                ]
            }
        except Exception as e:
            return {"error": str(e)}

search_service = AISearchTools()