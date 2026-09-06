from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://127.0.0.1:11434"
)

db = Chroma(
    persist_directory="knowledge_mcp/chroma_db",
    embedding_function=embeddings
)

docs = db.similarity_search(
    "blood pressure treatment threshold hypertension guideline systolic",
    k=5
)

print("RESULTS:", len(docs))

for d in docs:
    print("=" * 80)
    print(d.page_content[:500])