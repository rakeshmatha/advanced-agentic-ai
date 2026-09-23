from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from .config import Settings
from .rag import DEFAULT_DOCUMENTS_DIR, DEFAULT_VECTOR_STORE_DIR, build_vector_store


class CustomerServiceState(TypedDict, total=False):
    question: str
    documents: list[Document]
    answer: str
    sources: list[str]


def build_customer_service_graph(
    settings: Settings,
    documents_dir: str | Path = DEFAULT_DOCUMENTS_DIR,
    vector_store_dir: str | Path = DEFAULT_VECTOR_STORE_DIR,
):
    vector_store = build_vector_store(settings, documents_dir, vector_store_dir)
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful customer service assistant. Answer only from the provided policy context. "
                "If the context does not contain the answer, say you do not have enough information and "
                "recommend contacting a human support representative. Do not invent policies, prices, dates, "
                "or exceptions. Be concise and empathetic.\n\nPolicy context:\n{context}",
            ),
            ("human", "Customer question: {question}"),
        ]
    )
    model = ChatOpenAI(
        api_key=settings.openai_api_key.get_secret_value(),
        model=settings.model,
        temperature=0,
        max_tokens=settings.max_tokens,
    )

    def retrieve(state: CustomerServiceState) -> CustomerServiceState:
        return {"documents": retriever.invoke(state["question"])}

    def generate_answer(state: CustomerServiceState) -> CustomerServiceState:
        documents = state.get("documents", [])
        context = "\n\n".join(document.page_content for document in documents)
        response = (prompt | model).invoke(
            {"context": context, "question": state["question"]}
        )
        sources = sorted({str(document.metadata["source"]) for document in documents})
        return {"answer": str(response.content), "sources": sources}

    graph = StateGraph(CustomerServiceState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("generate_answer", generate_answer)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate_answer")
    graph.add_edge("generate_answer", END)
    return graph.compile()


def answer_question(
    question: str,
    settings: Settings,
    documents_dir: str | Path = DEFAULT_DOCUMENTS_DIR,
    vector_store_dir: str | Path = DEFAULT_VECTOR_STORE_DIR,
) -> tuple[str, list[str]]:
    result = build_customer_service_graph(
        settings, documents_dir, vector_store_dir
    ).invoke({"question": question})
    return result["answer"], result.get("sources", [])