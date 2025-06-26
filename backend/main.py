import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# --- Load env variables ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("❌ GOOGLE_API_KEY not set in the environment!")

# --- FastAPI app ---
app = FastAPI()

# Allow CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to actual frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Schema ---
class Query(BaseModel):
    question: str

# --- Load Vectorstore ---
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.load_local(
    folder_path="faiss_store",
    embeddings=embedding_model,
    allow_dangerous_deserialization=True
)

# --- Prompt Template ---
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a clever, witty yet funny assistant named **ChaturAI**, developed with love by Prateek Mandaliya.
The context contains **recent major news across technology, business, science, and world affairs** — use it carefully to support your response.

Your answers are:
- Accurate and based on provided context **if** available.
- Based on general knowledge **if** context is insufficient.
- Concise with sufficient detail to be helpful.
- Occasionally witty, but never at the cost of clarity.

📌 If specific source links are present in the context **and** they are highly relevant to the user's question (e.g., title closely matches query), mention them inline naturally (e.g., *"according to Yahoo News"*) with the link.  
❌ Do *not* mention sources if the question seems to rely on general knowledge or the context is unrelated.

Avoid making things up. Never speculate.

Context:
{context}

Question: {question}

Answer:

(— Powered by ChaturAI 🧠, crafted with ❤️ by Prateek Mandaliya)
"""
)

# --- Gemini LLM setup ---
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
    max_output_tokens=1024
)

# --- Truncator ---
def truncate(text, max_chars=800):
    if len(text) <= max_chars:
        return text
    last_period = text.rfind(".", 0, max_chars)
    return text[:last_period + 1] if last_period != -1 else text[:max_chars] + "..."

# --- /ask endpoint ---
@app.post("/ask")
async def ask(query: Query):
    search_results = vectorstore.similarity_search_with_relevance_scores(query.question, k=5)
    context_parts = []

    for doc, score in search_results:
        content = truncate(doc.page_content)
        url = doc.metadata.get("url")
        title = doc.metadata.get("title", "Source")

        if score < 0.2 and url:
            content += f"\n\n(Source: [{title}]({url}))"

        context_parts.append(content)

    context = "\n\n---\n\n".join(context_parts)
    prompt = prompt_template.format(context=context, question=query.question)

    try:
        response = llm.invoke(prompt)
        return {"answer": response.content.strip()}
    except Exception as e:
        return {"error": str(e)}
