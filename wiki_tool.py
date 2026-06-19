import wikipedia
import requests
def wiki_search(query):

    try:

        result = wikipedia.summary(query, sentences=3)

        return result

    except Exception:

        return "❌ No Wikipedia result found"