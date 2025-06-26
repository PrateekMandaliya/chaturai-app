import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from sklearn.metrics.pairwise import cosine_similarity



os.environ["GOOGLE_API_KEY"] = "AIzaSyAYAv_S_yYXxBy17UK-EfqlLTUivsJpi5w"
load_dotenv()

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# --- Load FAISS Vectorstore ---
vectorstore = FAISS.load_local(
    folder_path="faiss_store",
    embeddings=embedding_model,
    allow_dangerous_deserialization=True
)

# --- Truncate function ---
def truncate(text, max_chars=800):
    if len(text) <= max_chars:
        return text
    return text[:text.rfind(".", 0, max_chars)+1]  # Ends cleanly

# --- Define Prompt Template ---
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a helpful assistant named **ChaturAI**, developed with love by Prateek Mandaliya.

If the context below is relevant, use it to answer the question.
If it doesn't contain enough relevant info, feel free to say so politely and rely on your general knowledge — but **don’t make things up**.

- Be accurate, and concise.
- Do not hallucinate or speculate.
- Use bullet points only when necessary.
- If you don’t know something, say so naturally.

Context:
{context}

Question: {question}

Answer:

(— Powered by ChaturAI 🧠, crafted with ❤️ by Prateek Mandaliya)
"""
)


# --- Set up LLM ---
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # or gemini-1.5-pro
    temperature=0.3,
    max_output_tokens=1024
)



while True:
    query = input("\nEnter your question (or type 'exit'): ").strip()
    if query.lower() == "exit":
        break

    # Set up the retriever with a relevance threshold
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    retrieved_docs = retriever.invoke(query)

    # Optional filtering based on keyword presence (helps remove marginally relevant docs)
    def is_relevant(doc: Document, query: str) -> bool:
        return any(word in doc.page_content.lower() for word in query.lower().split())

    filtered_docs = [doc for doc in retrieved_docs if is_relevant(doc, query)]

    # Truncate content if needed and construct context
    if filtered_docs:
        context = "\n\n".join([truncate(doc.page_content) for doc in filtered_docs])
        final_prompt = prompt_template.format(context=context, question=query)
    else:
        # No context found – switch to fallback prompt
        final_prompt = f"""
    You are ChaturAI, a helpful assistant developed with love by Prateek.

    The user asked: "{query}"

    Unfortunately, I couldn’t find any relevant context to support this query.
    Rely only on your general knowledge to answer it.

    - Be accurate, concise, and polite.
    - Do not hallucinate or speculate.
    - Use bullet points only if necessary.

    Answer:

    (— Powered by ChaturAI 🧠, crafted with ❤️ by Prateek)
    """

    # Invoke the model
    response = llm.invoke(final_prompt)

    # Print the answer
    print("\n📢 Answer:\n", response.content)

    # Show sources only if they were used
    if filtered_docs:
        print("\n📚 Sources:")
        for doc in filtered_docs:
            title = doc.metadata.get("title", "Untitled")
            url = doc.metadata.get("url", "No URL")
            print(f"- {title} → {url}")