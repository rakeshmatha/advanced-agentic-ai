from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import Settings


DEFAULT_DOCUMENTS_DIR = Path(__file__).resolve().parent.parent / "rag" / "documents"
DEFAULT_VECTOR_STORE_DIR = Path(__file__).resolve().parent.parent / "rag" / ".chroma"


def load_documents(documents_dir: str | Path = DEFAULT_DOCUMENTS_DIR) -> list[Document]:
    directory = Path(documents_dir)
    documents: list[Document] = []
    for path in sorted(directory.rglob("*")):
        if path.suffix.lower() in {".md", ".txt"}:
            documents.append(
                Document(
                    page_content=path.read_text(encoding="utf-8"),
                    metadata={"source": str(path.relative_to(directory))},
                )
            )
    if not documents:
        raise ValueError(f"No .md or .txt documents found in {directory.resolve()}")
    return documents


def build_vector_store(
    settings: Settings,
    documents_dir: str | Path = DEFAULT_DOCUMENTS_DIR,
    vector_store_dir: str | Path = DEFAULT_VECTOR_STORE_DIR,
) -> Chroma:
    source_documents = load_documents(documents_dir)
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=120
    ).split_documents(source_documents)
    vector_store = Chroma(
        persist_directory=str(vector_store_dir),
        collection_name="customer_service_documents",
        embedding_function=OpenAIEmbeddings(
            api_key=settings.openai_api_key.get_secret_value()
        ),
    )
    stored_metadata = vector_store.get(include=["metadatas"]).get("metadatas", [])
    stored_sources = {
        str(metadata.get("source"))
        for metadata in stored_metadata
        if metadata and metadata.get("source")
    }
    new_chunks = [
        chunk for chunk in chunks if str(chunk.metadata.get("source")) not in stored_sources
    ]
    if new_chunks:
        vector_store.add_documents(new_chunks)
    return vector_store