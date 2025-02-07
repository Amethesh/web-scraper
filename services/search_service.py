import os
from typing import Dict, Any
from serpapi import GoogleSearch



class AISearchTools:
    def __init__(self):
        """
        Initialize search tools with Google Search via SerpAPI.
        
        Requires the SERPAPI_API_KEY environment variable to be set.
        """
        self.api_key = os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY not set in environment variables.")
    
    def get_organization_website(self, organization_name: str) -> Dict[str, Any]:
        """
        Find the website for a given organization using Google Search.
        
        Args:
            organization_name (str): Name of the company or school.
        
        Returns:
            Dict[str, Any]: Search results for the organization.
        """
        try:
            search_query = f"{organization_name} official website"
            params = {
                "engine": "google",
                "q": search_query,
                "num": 3,
                "api_key": self.api_key
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            organic_results = results.get("organic_results", [])
            formatted_results = [
                {
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                }
                for result in organic_results
            ]
            return {"query": search_query, "results": formatted_results}
        except Exception as e:
            return {"error": str(e)}
    
    def get_person_details(self, full_name: str) -> Dict[str, Any]:
        """
        Retrieve professional details for a given person using Google Search.
        
        Args:
            full_name (str): Full name of the person.
        
        Returns:
            Dict[str, Any]: Professional information search results.
        """
        try:
            search_query = f"{full_name} professional profile LinkedIn"
            params = {
                "engine": "google",
                "q": search_query,
                "num": 3,
                "api_key": self.api_key
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            organic_results = results.get("organic_results", [])
            formatted_results = [
                {
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                }
                for result in organic_results
            ]
            return {"query": search_query, "results": formatted_results}
        except Exception as e:
            return {"error": str(e)}
    
    def advanced_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Perform an advanced search with additional context using Google Search.
        
        Args:
            query (str): Search query.
            max_results (int, optional): Maximum number of results. Defaults to 5.
        
        Returns:
            Dict[str, Any]: Comprehensive search results.
        """
        try:
            params = {
                "engine": "google",
                "q": query,
                "num": max_results,
                "api_key": self.api_key
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            organic_results = results.get("organic_results", [])
            formatted_results = [
                {
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                }
                for result in organic_results
            ]
            return {"query": query, "results": formatted_results}
        except Exception as e:
            return {"error": str(e)}

# Create an instance of the service.
search_service = AISearchTools()
