from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from google import genai
from pydantic import BaseModel
from backend.agents.router_agent import classify_intent
from backend.prompts.prompt_builder import build_prompt
#from fastapi import HTTPException


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Create .env file in this folder.")

app = FastAPI()

# Allow frontend access (important later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage
vector_store = None

# Load embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=api_key
)

client = genai.Client(api_key=api_key)
class QuestionRequest(BaseModel):
    question: str
    chat_history: list = []


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global vector_store

    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = text_splitter.split_documents(documents)

    vector_store = FAISS.from_documents(chunks, embeddings)

    return {"message": "PDF uploaded and processed successfully"}

class QuestionRequest(BaseModel):
    question: str
    chat_history: list = []


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    global vector_store
    
    
    question = request.question
    chat_history = request.chat_history

    if vector_store is None:
        return {"error": "No document uploaded yet"}
    
    docs_with_scores = vector_store.similarity_search_with_score(question, k=5)
    intent = classify_intent(question)

    score_threshold = 1.0

    filtered_docs = [
        doc for doc, score in docs_with_scores
        if score <= score_threshold
    ]

    if not filtered_docs:
        return {
            "answer": "I don't know based on the document.",
            "context": ""
            }
    if intent == "summarize":
        task_instruction = "Summarize the document context clearly in bullet points."
    elif intent == "extract_key_points":
        task_instruction = "Extract the most important key points from the context."
    elif intent == "generate_interview_questions":
        task_instruction = "Generate interview questions and answers based only on the context."
    else:
        task_instruction = "Answer the user's question based only on the context."


    # context = "\n\n".join([doc.page_content for doc in filtered_docs])
    context = "\n\n".join([
    f"Source Page: {doc.metadata.get('page', 'unknown')}\n{doc.page_content}"
    for doc in filtered_docs
])

#     prompt = f"""
# You are an Agentic RAG Assistant.

# CHAT HISTORY:
# {chat_history}

# AGENT TASK:
# {task_instruction}

# STRICT RULES:
# - Use ONLY the provided context
# - If the answer is not present, say: "I don't know based on the document"
# - Do NOT make up information
# - Mention source page if available

# CONTEXT:
# {context}

# USER QUESTION:
# {question}

# FINAL ANSWER:
# """
    prompt = build_prompt(
    chat_history=chat_history,
    task_instruction=task_instruction,
    context=context,
    question=question
)

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        print(response)   ## debug purpose 

        answer_text = ""
        if hasattr(response, "text") and response.text:
             answer_text = response.text.strip()
        else:
             answer_text = "Model returned empty response."
        
        return {
            "answer": answer_text,
            "context": context[:1000]  # limit size for UI
            }



        # return {
        #     "answer": response.text.strip(),
        #     "context": context[:1000]   # limit size for UI
        #     }
        
    except Exception as e:
        return {
            "answer": "The AI model is temporarily unavailable. Please try again in a few seconds.",
            "error": str(e)
        }