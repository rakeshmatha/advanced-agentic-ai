from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import Settings


DEFAULT_DOCUMENTS_DIR = Path(__file__).resolve().parent.parent / "documents"
DEFAULT_VECTOR_STORE_DIR = Path(__file__).resolve().parent.parent / ".chroma"


def load_documents(documents_dir: str | Path = DEFAULT_DOCUMENTS_DIR) -> list[Document]:
    directory = Path(documents_dir)
    documents: list[Document] = []

    for path in sorted(directory.rglob("*")):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
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
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    chunks = splitter.split_documents(source_documents)
    embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key.get_secret_value())

    vector_store = Chroma(
        persist_directory=str(vector_store_dir),
        collection_name="project_documents",
        embedding_function=embeddings,
    )
    if vector_store._collection.count() == 0:
        vector_store.add_documents(chunks)
    return vector_store


def answer_question(
    question: str,
    settings: Settings,
    documents_dir: str | Path = DEFAULT_DOCUMENTS_DIR,
    vector_store_dir: str | Path = DEFAULT_VECTOR_STORE_DIR,
) -> tuple[str, list[str]]:
    vector_store = build_vector_store(settings, documents_dir, vector_store_dir)
    retrieved_documents = vector_store.as_retriever(search_kwargs={"k": 4}).invoke(question)
    context = "\n\n".join(document.page_content for document in retrieved_documents)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer using only the supplied context. If the answer is not in the context, say you do not know.\n\nContext:\n{context}",
            ),
            ("human", "{question}"),
        ]
    )
    response = (prompt | ChatOpenAI(
        api_key=settings.openai_api_key.get_secret_value(),
        model=settings.model,
        temperature=0,
    )).invoke({"context": context, "question": question})
    sources = sorted({str(document.metadata["source"]) for document in retrieved_documents})
    return response.content, sources