import json
import faiss
import pickle
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS 
import faiss
import numpy as np

with open("articles.json", "r") as f:
    articles = json.load(f)

print(f"Loaded {len(articles)} articles.")

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


# Step 1: Wrap articles in LangChain Document with metadata
docs = [
    Document(
        page_content=f"{article['title']}\n\n{article['text']}\n\nSource: {article['url']}",
        metadata={"title": article['title'], "url": article['url']}
    )
    for article in articles
]

# Step 2: Split documents into smaller chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=30
)
chunks = splitter.split_documents(docs)

# Optional: Add chunk IDs for traceability
for i, chunk in enumerate(chunks):
    chunk.metadata["chunk_id"] = i


# Step 3: Extract texts and metadata
texts = [chunk.page_content for chunk in chunks]
metadatas = [chunk.metadata for chunk in chunks]

# Step 4: Generate embeddings using HuggingFace
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"  # Lightweight and fast
)


texts = [chunk.page_content for chunk in chunks]
metadatas = [chunk.metadata for chunk in chunks]

vectors = embeddings.embed_documents(texts)

# Sanity check
assert len(vectors) == len(texts) == len(metadatas), "Mismatch in data lengths"

print(f"Generated {len(vectors)} embeddings of dimension {len(vectors[0])}")

# Step 6: Create and save FAISS vector store using LangChain
vectorstore = FAISS.from_texts(texts, embedding=embeddings, metadatas=metadatas)
vectorstore.save_local("faiss_store")

print("✅ FAISS vectorstore saved successfully to 'faiss_store'.")

# Step 7: Save the index and chunks for future use
index = vectorstore.index
faiss.write_index(index, "articles_index.faiss")
with open("article_chunks.pkl", "wb") as f:
    pickle.dump({"texts": texts, "metadatas": metadatas}, f)
print("✅ FAISS index and chunks saved successfully.")
