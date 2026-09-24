"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")
_MIN_FRAGMENT = 60


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_BOUNDARY.split(text) if s.strip()]


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in week 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into semantic, sentence-aware chunks tailored for campus_life.

    Milestone 4 change: the previous version only ever cut between paragraphs,
    and its "short enough to stay whole" cutoff (650 characters) and its
    per-paragraph flush target (500 characters) were both well above every
    document in this corpus (longest 549 characters, and most posts are a
    single body paragraph after the heading) — so it never actually split
    anything. This version lowers the target to SINGLE_CHUNK_LIMIT and splits
    on sentence boundaries, not just paragraph boundaries, so a single long
    paragraph can be divided too.

    Strategy:
    - Normalizes text and splits on paragraph boundaries (\n\n+).
    - Preserves heading context: if a document begins with a short heading,
      that title is attached to every chunk after it so each one stands
      independently.
    - If a document is short (<= SINGLE_CHUNK_LIMIT characters), it stays one
      coherent chunk.
    - Otherwise, every body paragraph is broken into sentences, and sentences
      are packed into chunks up to SINGLE_CHUNK_LIMIT characters.
    - Guards against small fragments: a trailing piece under 60 characters is
      merged onto the previous chunk instead of standing alone.
    """
    SINGLE_CHUNK_LIMIT = 160

    chunks: list[Chunk] = []

    for doc in documents:
        raw_text = doc.text.strip()
        if not raw_text:
            continue

        # Split into non-empty paragraphs
        paras = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
        if not paras:
            continue

        # If document is short enough to fit comfortably in a single chunk, preserve whole
        if len(raw_text) <= SINGLE_CHUNK_LIMIT:
            chunks.append(
                Chunk(
                    text=raw_text,
                    source=doc.source,
                    index=0,
                    produced_by="chunker.py::split_documents",
                )
            )
            continue

        # If there is a distinct title (short first paragraph < 60 chars), use it as header prefix
        header = ""
        body_paras = paras
        if len(paras) > 1 and len(paras[0]) < 60 and not paras[0].endswith("."):
            header = paras[0]
            body_paras = paras[1:]

        sentences: list[str] = []
        for para in body_paras:
            sentences.extend(_split_sentences(para))

        doc_chunk_idx = 0
        current_parts: list[str] = []
        current_len = 0

        for sentence in sentences:
            # If adding this sentence exceeds target size, flush current chunk
            if current_parts and (current_len + len(sentence) > SINGLE_CHUNK_LIMIT):
                chunk_body = " ".join(current_parts)
                full_text = f"{header}\n\n{chunk_body}".strip() if header else chunk_body
                chunks.append(
                    Chunk(
                        text=full_text,
                        source=doc.source,
                        index=doc_chunk_idx,
                        produced_by="chunker.py::split_documents",
                    )
                )
                doc_chunk_idx += 1
                current_parts = []
                current_len = 0

            current_parts.append(sentence)
            current_len += len(sentence)

        if current_parts:
            chunk_body = " ".join(current_parts)
            full_text = f"{header}\n\n{chunk_body}".strip() if header else chunk_body
            if current_len < _MIN_FRAGMENT and doc_chunk_idx > 0:
                # Too small to stand alone — merge onto the previous chunk.
                chunks[-1].text = f"{chunks[-1].text} {chunk_body}".strip()
            else:
                chunks.append(
                    Chunk(
                        text=full_text,
                        source=doc.source,
                        index=doc_chunk_idx,
                        produced_by="chunker.py::split_documents",
                    )
                )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))