import faiss
import pickle
import numpy as np
from langchain.embeddings import HuggingFaceEmbeddings


#  Load FAISS index
index = faiss.read_index("articles_index.faiss")

#  Load metadata (text and chunk info)
with open("article_chunks.pkl", "rb") as f:
    data = pickle.load(f)

texts = data["texts"]
metadatas = data["metadatas"]

#  Load embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"  # Lightweight and fast
)


# Function to search the FAISS index with a query
def search_query(query: str, k: int = 5):
    query_embedding = embeddings.embed_query(query)
    query_vector = np.array([query_embedding], dtype="float32")

    # Perform similarity search
    distances, indices = index.search(query_vector, k)

    results = []
    for i in indices[0]:
        if i < len(texts):
            results.append({
                "text": texts[i],
                "metadata": metadatas[i]
            })
    return results


# Similarity search example

# query = "Tell me about ios 26 and its new features"
# results = search_query(query, k=3)

# for i, result in enumerate(results):
#     print(f"\n--- Result {i + 1} ---")
#     print(f"Title: {result['metadata'].get('title')}")
#     print(f"URL: {result['metadata'].get('url')}")
#     print(result['text']) 

