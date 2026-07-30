import os
import io
from typing import Dict, Any
from langchain_core.documents import Document
from scripts.preprocess_data import chunk_text, RAW_DIR
from rag.vector_store import add_documents

def extract_pdf_text_and_tables(content_bytes: bytes) -> str:
    """
    Extracts text and table structures from PDF bytes using pypdf.
    Formats tabular data into clean Markdown tables for RAG vector indexing.
    """
    import pypdf
    reader = pypdf.PdfReader(io.BytesIO(content_bytes))
    extracted_pages = []
    
    for page_num, page in enumerate(reader.pages, 1):
        raw_page_text = page.extract_text() or ""
        lines = raw_page_text.split("\n")
        formatted_lines = []
        
        in_table = False
        table_rows = []
        
        for line in lines:
            stripped = line.strip()
            # Detect tab-separated or multi-space separated columns (likely table rows)
            if "  " in stripped and len(stripped.split()) >= 3:
                cols = [c.strip() for c in stripped.split("  ") if c.strip()]
                if len(cols) >= 2:
                    markdown_row = "| " + " | ".join(cols) + " |"
                    if not in_table:
                        in_table = True
                        header_sep = "| " + " | ".join(["---"] * len(cols)) + " |"
                        formatted_lines.append(markdown_row)
                        formatted_lines.append(header_sep)
                    else:
                        formatted_lines.append(markdown_row)
                    continue
            
            in_table = False
            formatted_lines.append(stripped)
            
        page_content = f"--- Page {page_num} ---\n" + "\n".join(formatted_lines)
        extracted_pages.append(page_content)
        
    return "\n\n".join(extracted_pages)


def ingest_document(file_name: str, content: bytes) -> Dict[str, Any]:
    """
    Saves uploaded file to data/raw, extracts text & tables, chunks content, and seeds ChromaDB.
    """
    os.makedirs(RAW_DIR, exist_ok=True)
    file_path = os.path.join(RAW_DIR, file_name)
    
    with open(file_path, "wb") as f:
        f.write(content)
        
    # PDF vs Text/Markdown parsing
    if file_name.lower().endswith(".pdf"):
        text_content = extract_pdf_text_and_tables(content)
    else:
        text_content = content.decode("utf-8", errors="ignore")
        
    raw_chunks = chunk_text(text_content, chunk_size=500, overlap=50)
    
    docs = []
    for idx, chunk in enumerate(raw_chunks, 1):
        docs.append(
            Document(
                page_content=f"Document: {file_name}\n{chunk}",
                metadata={
                    "source": file_name,
                    "title": f"{file_name} (Chunk {idx})",
                    "category": "pdf_document" if file_name.endswith(".pdf") else "user_uploaded",
                    "chunk_index": idx,
                }
            )
        )
        
    if docs:
        add_documents(docs)
        
    return {
        "status": "success",
        "file_name": file_name,
        "chunks_indexed": len(docs),
        "message": f"Successfully parsed text & tables from '{file_name}' and indexed {len(docs)} chunks into ChromaDB."
    }
