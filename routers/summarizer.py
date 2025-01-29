from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from services.ai_service import ai_chat_service
from services.scraper_service import scraper_service
from urllib.parse import urlparse
from services.new_url_extractor import url_extractor
from services.search_service import search_service
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/summarize")
async def summarize_links(request: Request):
    """
    Takes a user question and a URL, extracts all links from the URL, 
    and streams the most relevant link using AI.
    """
    try:
        data = await request.json()
        question = data.get("question")
        url = data.get("url")

        if not question or not url:
            raise HTTPException(status_code=400, detail="Both 'question' and 'url' are required.")

        # Extract URLs
        # extracted_urls = scraper_service.extract_urls(url)
        # extracted_urls = url_extractor.extract_urls(url)
        search_query = await ai_chat_service.compress_user_query(question, name=url)
        search_query = json.loads(search_query)
        query_text = search_query["response"]
        query_text = query_text.strip('"\'')  # Remove both single and double quotes

        print(query_text)
        search_result = search_service.advanced_search(query_text, max_results=5)
        logger.info(search_result)
        print(search_result)
        # needed_urls = json.loads(needed_urls_str)
        # print("Needed links Type", type(needed_urls))
        # print("Needed links:", needed_urls["response"])
        
        # if all(bool(urlparse(link).scheme) and bool(urlparse(link).netloc) for link in needed_urls["response"]):
        # text, links = scraper_service.scrape_page_info(needed_urls["response"])
        # markdown_output = scraper_service.write_to_markdown(text, links)
        # result = ai_chat_service.ai_chat_response(question, markdown_output)

        # print(markdown_output)
        return search_result
        # return StreamingResponse(result, media_type="text/plain")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
