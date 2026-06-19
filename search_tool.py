from tavily import TavilyClient

API_KEY="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"

client = TavilyClient(api_key=API_KEY)

def search_web(query):

    try:
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=5
        )

        results = response.get("results", [])

        if not results:
            return "No results found."

        answer = "🌐 Web Search Results:\n\n"

        for i, r in enumerate(results, start=1):

            title = r.get("title", "No title")
            content = r.get("content", "")

            answer += f"{i}. {title}\n"
            answer += f"{content[:150]}...\n\n"

        return answer

    except Exception as e:
        print("Search Error:", e)
        return "❌ Search failed"