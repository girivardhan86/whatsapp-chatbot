from create_vector_db import get_retriever
from memory_db import save_message

from weather import get_weather
from news import get_news

from langchain_community.tools import DuckDuckGoSearchRun
import wikipedia

from langchain_openai import ChatOpenAI

# =====================================================
# OPENROUTER LLM
# =====================================================
import os
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    temperature=0.3,
    openai_api_base="https://openrouter.ai/api/v1"
)

# =====================================================
# SEARCH TOOL
# =====================================================

search_tool = DuckDuckGoSearchRun(region="us-en")

# =====================================================
# MEMORY
# =====================================================

user_memory = {}

MAX_HISTORY = 4

# =====================================================
# BASIC MESSAGES
# =====================================================

def handle_basic_messages(query):

    q = query.lower().strip()

    if q in ["hi", "hello", "hey"]:
        return "Hello 👋 Welcome to Agneyra."

    if "thank" in q:
        return "You're welcome 😊"

    if q in ["bye", "exit"]:
        return "Goodbye 👋"

    return None

# =====================================================
# DETECT INTENT
# =====================================================

def detect_intent(query):

    q = query.lower()

    if "weather" in q:
        return "weather"

    if "news" in q:
        return "news"

    if "search" in q or "google" in q:
        return "search"

    if "who is" in q:
        return "wiki"

    return "general"

# =====================================================
# MAIN FUNCTION
# =====================================================

def get_response(query, phone_number):

    save_message(phone_number, "user", query)

    # ================= BASIC =================

    basic = handle_basic_messages(query)

    if basic:
        save_message(phone_number, "bot", basic)
        return basic

    # ================= INTENT =================

    intent = detect_intent(query)

    # ================= WEATHER =================

# ================= WEATHER =================

    if intent == "weather":

        city = (
            query.lower()
            .replace("today", "")
            .replace("weather", "")
            .replace("in", "")
            .replace("city", "")
            .strip()
        )

        if city == "":
            city = "Hyderabad"
        if city == "":
            city = "nashik"

        return get_weather(city)

    # ================= NEWS =================

    if intent == "news":

        q = query.lower()

        if "sports" in q:
            return get_news("sports")

        elif "business" in q:
            return get_news("business")

        elif "technology" in q:
            return get_news("technology")

        else:
            return get_news("general")

    # ================= GOOGLE SEARCH =================

    if intent == "search":

        try:

            result = search_tool.run(query)

            save_message(phone_number, "bot", result)

            return result

        except Exception as e:

            print("Search Error:", e)

            return "❌ Search failed"

    # ================= WIKIPEDIA =================

 # ================= WIKIPEDIA =================

    if intent == "wiki":

        try:

            search_query = query.lower().replace(
                "who is",
                ""
            ).strip()

            result = wikipedia.summary(
                search_query,
                sentences=2
            )

            save_message(
                phone_number,
                "bot",
                result
            )

            return result

        except Exception as e:

            print("Wiki Error:", e)

            return "❌ Wikipedia search failed"

    # ================= MEMORY =================

    if phone_number not in user_memory:
        user_memory[phone_number] = []

    history = user_memory[phone_number]

    history_text = "\n".join(history[-MAX_HISTORY:])

    # ================= RAG =================

    retriever = get_retriever(phone_number)

    docs = retriever.invoke(query)

    context = "\n\n".join([
        d.page_content for d in docs
    ])

    # ================= PROMPT =================

    prompt = f"""
You are Agneyra AI assistant.

Chat History:
{history_text}

Context:
{context}

Question:
{query}

Answer:
"""

    try:

        response = llm.invoke(prompt)

        if hasattr(response, "content"):
            answer = response.content
        else:
            answer = str(response)

        history.append(f"User: {query}")
        history.append(f"Assistant: {answer}")

        user_memory[phone_number] = history[-MAX_HISTORY:]

        save_message(phone_number, "bot", answer)

        return answer.strip()

    except Exception as e:

        print("LLM Error:", e)

        return "❌ Error generating response"