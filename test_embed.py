from langchain_ollama import OllamaEmbeddings

emb = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://127.0.0.1:11434"
)

x = emb.embed_query("hypertension")

print(len(x))