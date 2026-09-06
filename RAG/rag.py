from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

DB_PATH = "RAG/chroma_db"


def build_db():

    docs = []

    files = [
        "RAG/guidelines/Hypertension guideline.pdf",
        "RAG/guidelines/Diabetes guideline.pdf",
        "RAG/guidelines/Heart Failure guideline.pdf"
    ]

    for file in files:

        loader = PyPDFLoader(file)

        docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(docs)

    Chroma.from_documents(
        chunks,
        embedding,
        persist_directory=DB_PATH
    )

    print("RAG database created.")


def search_guidelines(condition):

    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embedding
    )

    docs = db.similarity_search(
        condition,
        k=3
    )

    return "\n".join(
        [d.page_content for d in docs]
    )