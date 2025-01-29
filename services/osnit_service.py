from langchain.agents import initialize_agent, Tool
from langchain.tools import tool
from langchain_openai import OpenAI
import requests

# Define API-based tools for OSINT tasks
@tool
def search_linkedin_via_google(query: str) -> str:
    """Search LinkedIn profiles using Google Custom Search API."""
    try:
        api_key = "AIzaSyD7C8K7cRFCerB8MR_51_GkU2fF-H7gus8"
        cx = "53193da46052742c1"
        url = f"https://www.googleapis.com/customsearch/v1?q=site:linkedin.com+{query}&key={api_key}&cx={cx}"
        response = requests.get(url)
        data = response.json()
        links = [item['link'] for item in data.get('items', []) if 'linkedin.com/in/' in item['link']]
        return f"Found LinkedIn profiles: {links}" if links else "No LinkedIn profiles found."
    except Exception as e:
        return f"Error occurred while searching LinkedIn: {str(e)}"

@tool
def search_email_with_hunterio(query: str) -> str:
    """Search email addresses using Hunter.io API."""
    try:
        api_key = "5d38862b24ec80f86381de9280f45cd0c64a99f6"
        url = f"https://api.hunter.io/v2/email-finder?domain={query}&api_key={api_key}"
        response = requests.get(url)
        data = response.json()
        email = data.get('data', {}).get('email')
        return f"Found email: {email}" if email else "No email found."
    except Exception as e:
        return f"Error occurred while searching emails: {str(e)}"

@tool
def search_phone_numbers_via_google(query: str) -> str:
    """Search phone numbers using Google Custom Search API."""
    try:
        api_key = "YOUR_GOOGLE_CUSTOM_SEARCH_API_KEY"
        cx = "YOUR_SEARCH_ENGINE_ID"
        url = f"https://www.googleapis.com/customsearch/v1?q=phone+number+{query}&key={api_key}&cx={cx}"
        response = requests.get(url)
        data = response.json()
        snippets = [item['snippet'] for item in data.get('items', [])]
        numbers = [word for snippet in snippets for word in snippet.split() if word.isdigit() and len(word) >= 10]
        return f"Found phone numbers: {numbers}" if numbers else "No phone numbers found."
    except Exception as e:
        return f"Error occurred while searching phone numbers: {str(e)}"

# Initialize the LangChain agent with the tools
llm = OpenAI(temperature=0)
tools = [search_linkedin_via_google, search_email_with_hunterio, search_phone_numbers_via_google]
osint_agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

# Example usage
if __name__ == "__main__":
    query = "Pradeep Khandwala"
    print("Starting OSINT agent...\n")
    result = osint_agent.run(f"Find LinkedIn profiles, email addresses, and phone numbers for {query}.")
    print(result)
