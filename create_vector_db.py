from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


loader = TextLoader("company_data.txt", encoding="utf-8")
documents = loader.load()

text_splitter = CharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=30
)

docs = text_splitter.split_documents(documents)

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma.from_documents(
    docs,
    embedding,
    persist_directory="db"
)

db.persist()

print("✅ Vector DB created successfully")
