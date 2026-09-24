"""Day 2: RAG system with LangChain + FAISS + OpenAI (matches notebook 4).

Mirrors `Day2/1 RAG continued/4 RAG_system_using_LangChain_and_OpenAI.ipynb`:
load documents, split into chunks, embed with OpenAI, store/search in FAISS,
then answer questions grounded in the retrieved chunks.

    source ./activate
    rag --chat
    rag "Can I return an unopened item?"
"""

from __future__ import annotations

import argparse
from pathlib import Path
from time import perf_counter

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from common.config import settings

DOCS_DIR = Path(__file__).resolve().parent / "docs"


def load_documents(docs_dir: Path = DOCS_DIR) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(docs_dir.rglob("*")):
        if path.name.lower() == "readme.md":
            continue
        suffix = path.suffix.lower()
        if suffix in {".md", ".txt"}:
            documents.append(
                Document(
                    page_content=path.read_text(encoding="utf-8"),
                    metadata={"source": path.name},
                )
            )
        elif suffix == ".pdf":
            reader = PdfReader(str(path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            documents.append(Document(page_content=text, metadata={"source": path.name}))
    if not documents:
        raise ValueError(f"No .md/.txt/.pdf documents found in {docs_dir}")
    return documents


def build_vector_store(docs_dir: Path = DOCS_DIR) -> FAISS:
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=120
    ).split_documents(load_documents(docs_dir))
    embeddings = OpenAIEmbeddings(
        api_key=settings.openai_api_key.get_secret_value(),
        model="text-embedding-3-small",
    )
    return FAISS.from_documents(chunks, embeddings)


def _doc_names(docs_dir: Path = DOCS_DIR) -> list[str]:
    names = []
    for path in sorted(docs_dir.rglob("*")):
        if path.name.lower() == "readme.md":
            continue
        if path.suffix.lower() in {".md", ".txt", ".pdf"}:
            names.append(path.name)
    return names


def answer_question(
    question: str,
    vector_store: FAISS | None = None,
    docs_dir: Path = DOCS_DIR,
) -> tuple[str, list[str]]:
    store = vector_store or build_vector_store(docs_dir)
    retriever = store.as_retriever(search_kwargs={"k": 4})
    documents = retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in documents)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. Answer only from the provided context. "
                "If the context does not contain the answer, say you do not have enough "
                "information. Be concise.\n\nContext:\n{context}",
            ),
            ("human", "Question: {question}"),
        ]
    )
    model = ChatOpenAI(
        api_key=settings.openai_api_key.get_secret_value(),
        model=settings.model,
        temperature=0,
        max_tokens=settings.max_tokens,
    )
    response = (prompt | model).invoke({"context": context, "question": question})
    sources = sorted({str(doc.metadata.get("source")) for doc in documents})
    return str(response.content), sources


def _print_answer(answer: str, sources: list[str], elapsed: float) -> None:
    print(f"bot> {answer}")
    print(f"     [retrieved from: {', '.join(sources)} | {elapsed:.2f}s]")
    print()


def chat_repl() -> None:
    print("=" * 70)
    print(f"Day 2 RAG chat (model: {settings.model} | store: FAISS)")
    print("=" * 70)
    print("Ask questions about the documents. Each turn:")
    print("  1) your question is embedded")
    print("  2) FAISS finds the closest chunks (k=4)")
    print("  3) the model answers ONLY from those chunks")
    print("  4) sources = which files the chunks came from")
    print("If a question is not in the docs, it should say it does not know.")
    print()
    indexed = _doc_names()
    print(f"Indexed files: {', '.join(indexed) if indexed else '(none)'}")
    print()
    print("Try this:")
    print('  1) "Can I return an unopened item?"')
    print('  2) "What if my item arrived damaged?"')
    print('  3) "How many vacation days do I get?"   (not in the docs -> should refuse)')
    print()
    print("Commands: /exit quits.")
    print("-" * 70)
    print("Building FAISS index (one time)...", flush=True)
    store = build_vector_store()
    print("Ready. Ask a question.\n")
    while True:
        try:
            question = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question == "/exit":
            break
        started_at = perf_counter()
        answer, sources = answer_question(question, vector_store=store)
        _print_answer(answer, sources, perf_counter() - started_at)


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 2 RAG lab (LangChain + FAISS)")
    parser.add_argument("--chat", action="store_true", help="interactive Q&A over docs/")
    parser.add_argument("question", nargs="*", help="one-shot question (skip chat)")
    args = parser.parse_args()
    question = " ".join(args.question).strip()

    if question and not args.chat:
        started_at = perf_counter()
        answer, sources = answer_question(question)
        print(f"Model: {settings.model} | Vector store: FAISS")
        print(f"Time taken: {perf_counter() - started_at:.2f} seconds\n")
        print(answer)
        print("\nSources:")
        for source in sources:
            print(f"- {source}")
        return

    chat_repl()


if __name__ == "__main__":
    main()
