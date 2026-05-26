import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

# 1. Load PDF
loader = PyPDFLoader("../sample_data/sample.pdf")
documents = loader.load()

print(f"Loaded pages: {len(documents)}")

# 2. Split PDF text into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = text_splitter.split_documents(documents)

print(f"Created chunks: {len(chunks)}")

# 3. Convert chunks into embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=api_key
)

# 4. Store embeddings in FAISS vector database
vector_store = FAISS.from_documents(chunks, embeddings)

# 5. Ask user question
question = input("Ask a question from the PDF: ")

# 6. Retrieve most relevant chunks
retrieved_docs_with_scores = vector_store.similarity_search_with_score(question, k=5)

# Lower score = more similar in FAISS
score_threshold = 1.0

filtered_docs = [
    doc for doc, score in retrieved_docs_with_scores
    if score <= score_threshold
]

if not filtered_docs:
    print("\n=== FINAL ANSWER ===\n")
    if "I don't know" in answer:
        st.warning("Answer not found in the uploaded document")
    else:
        st.success(answer)
    print("I don't know based on the document.")
    exit()

    

context = "\n\n".join([doc.page_content for doc in filtered_docs])


# 7. Send context + question to Gemini

prompt = f"""
You are a helpful AI assistant.

STRICT RULES:
- Answer ONLY from the provided context
- If the answer is not in the context, say: "I don't know based on the document"
- Do NOT make up information

CONTEXT:
{context}

QUESTION:
{question}

Answer clearly and concisely:
"""

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=prompt
)

if not context.strip():
    print("\n=== FINAL ANSWER ===\n")
    print("I don't know based on the document.")
    exit()

print("\n=== FINAL ANSWER ===\n")
print(response.text)