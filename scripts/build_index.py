"""Load corpus, chunk, embed, and save the local NumPy index."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.chunker import chunk_documents
from backend.document_loader import load_corpus
from backend.embeddings import embed_texts
from backend.vector_store import save_index


def main() -> None:
    pdf_path = ROOT / "corpus" / "medical_exemption.pdf"
    if not pdf_path.exists():
        from scripts.generate_pdf import generate_pdf

        generate_pdf(pdf_path)

    print("Loading corpus...")
    documents = load_corpus()
    print(f"Loaded {len(documents)} section documents.")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks. Embedding with all-MiniLM-L6-v2...")
    embeddings = embed_texts([chunk["text"] for chunk in chunks])
    save_index(chunks, embeddings)
    print(f"Saved index to {ROOT / 'data'} ({embeddings.shape[0]} vectors).")


if __name__ == "__main__":
    main()
