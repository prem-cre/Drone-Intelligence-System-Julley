"""
Document chunker using LangChain text splitters.
Uses MarkdownHeaderTextSplitter for section-aware splitting,
then RecursiveCharacterTextSplitter for size-controlled sub-chunks.
"""
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

# Markdown headers to split on (preserves section hierarchy)
HEADERS_TO_SPLIT = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
]

def chunk_document(text: str, metadata: Dict[str, Any]) -> List[Document]:
    """
    Chunks a raw text document into LangChain Document objects.

    Strategy:
    1. MarkdownHeaderTextSplitter splits by #/##/### headers (section-aware).
    2. RecursiveCharacterTextSplitter sub-splits large sections (400 chars, 50 overlap).
    3. Each chunk inherits document-level metadata + section header context.
    """
    source = metadata.get("source", "document.md")
    category = metadata.get("category", "general")
    title = metadata.get("title", source)

    # Step 1: Split by markdown headers
    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT,
        strip_headers=False,
    )
    header_docs = md_splitter.split_text(text)

    # Step 2: Sub-split large sections into smaller chunks
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    final_chunks = char_splitter.split_documents(header_docs)

    # Step 3: Enrich metadata on each chunk
    result_docs = []
    for idx, doc in enumerate(final_chunks, 1):
        section = doc.metadata.get("h2") or doc.metadata.get("h1") or title
        doc.metadata.update({
            "source": source,
            "title": title,
            "section": section,
            "category": category,
            "chunk_index": idx,
        })
        result_docs.append(doc)

    return result_docs
