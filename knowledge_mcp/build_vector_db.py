import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = PROJECT_ROOT / "RAG" / "guidelines"
DB_DIR = PROJECT_ROOT / "knowledge_mcp" / "chroma_db"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

documents = []

for pdf in PDF_DIR.glob("*.pdf"):

    print("Loading:", pdf)

    loader = PyPDFLoader(str(pdf))

    docs = loader.load()

    print("Pages:", len(docs))

    documents.extend(docs)

print("TOTAL PAGES:", len(documents))

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(documents)

print("TOTAL CHUNKS:", len(chunks))

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url=OLLAMA_BASE_URL
)

db = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=str(DB_DIR)
)

print("DONE")