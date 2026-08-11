from unittest import result

from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def tavily_search(query):

    response=tavily_client.search(
        query,
        max_results=5,
    )
    results = []

    for index, i in enumerate(response['results'], start=1):
        title = i.get('title', 'unknown')
        url = i.get('url', '')
        content = i.get('content', '').strip()

        if len(content) > 300:
            content = content[:300].rsplit(" ", 1)[0] + "..."

        results.append(
            f"Result {index}:\n"
            f"Title: {title}\n"
            f"URL: {url}\n"
            f"Content: {content}"
        )

    return "\n\n".join(results)