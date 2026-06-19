import requests


NEWS_API_KEY="615f2982d3d6472980befc10a5695877"

def get_news(topic="technology"):

    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={topic}&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    )

    try:

        response = requests.get(url)

        data = response.json()

        print(data)

        if data["status"] != "ok":
            return "❌ Unable to fetch news"

        articles = data.get("articles", [])

        if len(articles) == 0:
            return "❌ No news found"

        news_text = f"📰 {topic.title()} News:\n\n"

        for i, article in enumerate(articles[:5], start=1):

            title = article.get("title", "No title")

            source = article["source"]["name"]

            news_text += (
                f"{i}. {title}\n"
                f"Source: {source}\n\n"
            )

        return news_text

    except Exception as e:

        print("News Error:", e)

        return "❌ Unable to fetch news"