from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "smart_ops_knowledge"
DOC_PATH = Path("rag/docs/smart_ops_knowledge.md")

embedding_model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def load_document(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start = end - overlap

    return chunks


def get_embedding(text: str) -> list[float]:
    embedding = embedding_model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def ingest():
    text = load_document(DOC_PATH)
    chunks = split_text(text)

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    for index, chunk in enumerate(chunks):
        ids.append(f"smart_ops_knowledge_{index}")
        documents.append(chunk)
        embeddings.append(get_embedding(chunk))
        metadatas.append(
            {
                "source": str(DOC_PATH),
                "chunk_index": index,
            }
        )

    # 为了重复执行时不插入重复数据，先清空旧 collection
    try:
        existing = collection.get()
        if existing and existing.get("ids"):
            collection.delete(ids=existing["ids"])
    except Exception:
        pass

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"知识库入库完成，共 {len(chunks)} 个 chunk")


if __name__ == "__main__":
    ingest()