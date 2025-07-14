# tools/functions.py

import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Load environment variables from .env file
load_dotenv()

# --- Tool 1: Web Search using Tavily AI ---
# tools/functions.py

# ... (keep other imports and functions) ...

def web_search(query: str) -> str:
    """
    Uses the Tavily AI API to perform a web search.
    Returns a concise summary of search results AND the source URLs.
    """
    print(f"TOOL: Performing web search for: '{query}'")
    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": os.getenv("TAVILY_API_KEY"),
                "query": query,
                "search_depth": "basic",
                "include_answer": True, # Get a summary answer
                "include_raw_content": False,
                "max_results": 5,
            },
        )
        response.raise_for_status()
        data = response.json()
        
        # --- THIS IS THE NEW PART ---
        # Format the output to be highly informative for the agent
        summary = data.get("answer", "No summary answer found.")
        
        results = data.get("results", [])
        sources = "\n".join([f"- {res['title']}: {res['url']}" for res in results])
        
        if not sources:
            return f"Summary: {summary}\n\nNo sources found."

        return f"Summary: {summary}\n\nSources:\n{sources}"

    except Exception as e:
        return f"Error performing web search: {e}"

# --- Tool 2: Web Scraper using Playwright ---
def web_scraper(url: str) -> str:
    """
    Fetches the content of a URL using a headless browser (Playwright).
    Returns the textual content of the page.
    """
    print(f"TOOL: Scraping URL: {url}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            html_content = page.content()
            browser.close()

            # Use BeautifulSoup to extract clean text
            soup = BeautifulSoup(html_content, "html.parser")
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            
            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = "\n".join(chunk for chunk in chunks if chunk)
            
            # Return a manageable chunk of text
            return clean_text[:4000] # Return the first 4000 characters to not overload the context
    except Exception as e:
        return f"Error scraping URL {url}: {e}"

# --- Tool 3: The Finish Tool ---
def finish(answer: str) -> str:
    """
    Use this tool to provide the final answer when you have found the best price.
    The input should be a complete sentence summarizing the findings.
    """
    print(f"TOOL: Finishing with answer: '{answer}'")
    return answer