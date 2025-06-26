import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Load Environment Variables ---
os.environ["GOOGLE_API_KEY"] = "AIzaSyAYAv_S_yYXxBy17UK-EfqlLTUivsJpi5w"
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    print("GOOGLE_API_KEY missing from environment.")
    exit()

# --- Initialize Models ---
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.load_local(
    folder_path="faiss_store",
    embeddings=embedding_model,
    allow_dangerous_deserialization=True
)

# --- Helper: Truncate content nicely ---
def truncate(text, max_chars=800):
    if len(text) <= max_chars:
        return text
    last_period = text.rfind(".", 0, max_chars)
    return text[:last_period + 1] if last_period != -1 else text[:max_chars] + "..."



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

Avoid making things up. Never speculate. Please respond using Markdown formatting for links, headings, and lists when you can.

Context:
{context}

Question: {question}

Answer:

(— Powered by ChaturAI 🧠, crafted with ❤️ by Prateek Mandaliya)
"""
)

# --- Set up LLM ---
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
    max_output_tokens=1024
)

# --- Main Loop ---
while True:
    query = input("\nEnter your question (or type 'exit'): ").strip()
    if query.lower() == "exit":
        break
    if not query:
        continue

    print("🔍 Searching...")
    retrieved = vectorstore.similarity_search_with_relevance_scores(query, k=5)

    # Relevance cutoff for inline source embedding
    TOP_SOURCE_THRESHOLD = 0.2
    context_parts = []

    for doc, score in retrieved:
        content = truncate(doc.page_content)
        url = doc.metadata.get("url")
        title = doc.metadata.get("title", "Source")

        # Attach inline URL only for highly relevant sources
        if score < TOP_SOURCE_THRESHOLD and url:
            content += f"\n\n(Source: [{title}]({url}))"

        context_parts.append(content)

    context = "\n\n---\n\n".join(context_parts)

    final_prompt = prompt_template.format(context=context, question=query)

    try:
        print("\n🤔 Thinking...")
        response = llm.invoke(final_prompt)
        print("\n📢 Answer:\n", response.content.strip())
    except Exception as e:
        print(f"\n❌ Error: {e}")

print("\n👋 Goodbye!")
