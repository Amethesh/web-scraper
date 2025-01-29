SUMMARIZER_PROMPT = """
You are an AI assistant. Your task is to help users find the most relevant link to their question from a given list of URLs.

Question: {question}

Here are the URLs:
{urls}

Based on the question, provide the most relevant link only
"""
CHAT_PROMPT = """
You are an AI assistant. Your task is to analyze the following question and use the provided website's information to extract any relevant details or answers the question in an MARKDOWN.

Question: {question}
Website Information: {info}

Response:
1. **Answer to the question:**
2. **Overview or summary of the data:**
3. **Relevant link and pdfs files:** (if any)
"""
QUERY_COMPRESS_PROMPT = """
You are an AI assistant. Your task is to create and return an optimized search query for DuckDuckGo based on the given question and the name of the company or organization.

Question: {question}
Company/Organization Name: {name}

Create a search query that will yield the most relevant results on DuckDuckGo:
RETURN ONLY THE SEARCH QUERY
"""
