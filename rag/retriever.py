import chromadb
from sentence_transformers import SentenceTransformer


CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "smart_ops_knowledge"

embedding_model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def get_embedding(text: str) -> list[float]:
    embedding = embedding_model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def search_knowledge_base(query: str, top_k: int = 3) -> list[dict]:
    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    contexts = []

    for doc, meta, distance in zip(documents, metadatas, distances):
        contexts.append(
            {
                "text": doc,
                "source": meta.get("source"),
                "chunk_index": meta.get("chunk_index"),
                "distance": distance,
            }
        )

    return contexts