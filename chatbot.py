from langchain_ollama import OllamaLLM
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from memory_db import save_message


# =====================================================
# USER SESSION STORAGE (Multi-user memory)
# =====================================================
user_sessions = {}


# =====================================================
# 1. Embedding Model
# =====================================================
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# =====================================================
# 2. Load Vector Database
# =====================================================
db = Chroma(
    persist_directory="db",
    embedding_function=embedding
)

retriever = db.as_retriever(
    search_kwargs={"k": 2}   # best for 8GB RAM
)


# =====================================================
# 3. Local LLM (Ollama)
# =====================================================
llm = OllamaLLM(
    model="tinyllama"
,
    temperature=0
)


# =====================================================
# 4. Custom Prompt (Company Behavior)
# =====================================================
prompt_template = """
You are the official AI assistant of Agneyra company.

Rules:
- Always reply in English language only.
- Answer ONLY using the provided context.
- Do NOT add extra information or assumptions.
- Keep answers short, clear, and professional.
- Maintain a polite company tone.
- If the answer is not available, reply:
  "Please contact Agneyra support for more information."
- If users ask about updates, news, or latest activities,
  suggest following Agneyra social media pages.

Context:
{context}

Question:
{question}

Answer:
"""
QA_PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)


# =====================================================
# 5. Create User-specific Chain
# =====================================================
def get_user_chain(phone_number):

    if phone_number not in user_sessions:

        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            k=4   # limit memory for 8GB RAM
        )

        user_sessions[phone_number] = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            combine_docs_chain_kwargs={"prompt": QA_PROMPT},
            return_source_documents=False
        )

    return user_sessions[phone_number]


# =====================================================
# 6. Basic Message Handler (No LLM usage)
# =====================================================
def handle_basic_messages(query):

    q = query.lower().strip()

    if q in ["hi", "hello", "hey"]:
        return "Hello 👋 Welcome to Agneyra. How can I assist you today?"

    if "thank" in q or "thanks" in q or "thank you" in q:
        return "You're welcome 😊 If you have any other questions, feel free to ask."

    if q in ["bye", "exit"]:
        return "Thank you for contacting Agneyra. Have a great day!"
    return None
def is_allowed_question(query):

    allowed_keywords = [
        "internship", "apply", "registration",
        "service", "project", "company",
        "certificate", "social", "update"
    ]

    query = query.lower()

    return any(word in query for word in allowed_keywords)

def detect_intent(query):

    q = query.lower()

    if any(word in q for word in ["hi", "hello", "hey"]):
        return "greeting"

    if "internship" in q or "apply" in q or "registration" in q:
        return "internship"

    if "service" in q or "project" in q:
        return "services"

    if "about" in q or "company" in q or "services" in q or "provide" in q:
        return "company"
    if "update" in q or "social" in q:
        return "social"

    return "general"
# =====================================================
# 7. Main Chat Function
# =====================================================
def get_response(query, phone_number):

    # Save user message
    save_message(phone_number, "user", query)

    # Reject very long messages
    if len(query) > 500:
        reply = "Please send shorter messages related to Agneyra services."
        save_message(phone_number, "bot", reply)
        return reply

    # Step 1: Handle simple greetings FIRST
    basic_reply = handle_basic_messages(query)
    if basic_reply:
        save_message(phone_number, "bot", basic_reply)
        return basic_reply

    # Step 2: Detect intent
    intent = detect_intent(query)

    # Services reply
    if intent == "services":
        reply = (
            "Agneyra provides IT services including website development, "
            "software development, AI solutions, and application development."
        )
        save_message(phone_number, "bot", reply)
        return reply

    # Company reply
    if intent == "company":
        reply = (
            "Agneyra is an IT services company providing website development, "
            "software development, AI solutions, and application development. "
            "The company focuses on industry-level projects and practical learning experiences."
        )
        save_message(phone_number, "bot", reply)
        return reply

    # Internship reply
    if intent == "internship":
        reply = (
        "To apply for an internship, visit https://agneyra.com, "
        "go to the Career section, explore internship domains, "
        "and complete the registration process.\n\n"
        "After successful registration, you will receive a confirmation email.\n\n"
        "For latest updates, follow Agneyra on:\n"
        "Instagram: https://www.instagram.com/agneyra\n"
        "Twitter (X): https://x.com/agneyra63\n"
        "LinkedIn: https://www.linkedin.com/company/agneyra"
    )
        save_message(phone_number, "bot", reply)
        return reply
    if intent == "social":
        reply = (
            "You can follow Agneyra on social media for updates:\n\n"
            "Instagram: https://www.instagram.com/agneyra\n"
            "Twitter (X): https://x.com/agneyra63\n"
            "LinkedIn: https://www.linkedin.com/company/agneyra\n\n"
            "Follow us for daily updates, announcements, and company activities."
        )
        save_message(phone_number, "bot", reply)
        return reply

    # Step 3: Reject unrelated questions (AFTER intent check)
    if not is_allowed_question(query):
        reply = (
            "I can assist only with Agneyra services, internships, "
            "certificates, and company information."
        )
        save_message(phone_number, "bot", reply)
        return reply

    # Step 4: Use AI for complex allowed questions
    qa_chain = get_user_chain(phone_number)

    result = qa_chain.invoke({"question": query})
    answer = result.get("answer") or result.get("result")

    if not answer:
        answer = "Please contact Agneyra support for more information."

    save_message(phone_number, "bot", answer)

    return answer.strip()
