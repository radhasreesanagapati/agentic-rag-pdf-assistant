import streamlit as st
import requests

st.title("📄 RAG PDF Chatbot")

BACKEND_URL = "http://127.0.0.1:8000"

if "history" not in st.session_state:
    st.session_state.history = []

if st.button("Clear Chat"):
    st.session_state.history = []

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_file:
    if st.button("Process PDF"):
        try:
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf"
                )
            }

            with st.spinner("Processing PDF..."):
                res = requests.post(
                    f"{BACKEND_URL}/upload",
                    files=files,
                    timeout=120
                )

            if res.status_code == 200:
                st.success("PDF uploaded successfully!")
            else:
                st.error(f"Upload failed: {res.status_code}")

        except requests.exceptions.ConnectionError:
            st.error("Backend is not running. Please start FastAPI on port 8000.")

question = st.text_input("Ask a question:")

if st.button("Ask"):
    if question:
        try:
            payload = {
                      "question": question,
                      "chat_history": st.session_state.history
                      }
            with st.spinner("Thinking..."):
                res = requests.post(
                f"{BACKEND_URL}/ask",
                json=payload,
                timeout=60
                )

            if res.status_code == 200:
                data = res.json()
                answer = data.get("answer", "No answer returned")
                context = data.get("context", "")
                st.session_state.history.append(("user", question, ""))
                st.session_state.history.append(("bot", answer, context))
                
            else:
                st.error(f"Backend error: {res.status_code}")

        except requests.exceptions.ConnectionError:
            st.error("Backend is not running. Please start FastAPI on port 8000.")

        except requests.exceptions.Timeout:
                st.error("Request timed out. Please try again.")

        except Exception as e:
            st.error(f"Unexpected error: {e}")

st.write("### Chat History")

for role, msg, ctx in st.session_state.history:
    if role == "user":
        st.write("👤 **You:**", msg)

    else:  # bot
        if "I don't know" in msg:
            st.warning("🤖 Answer not found in the uploaded document.")
        else:
            st.write("🤖 **Bot:**", msg)

            if ctx:
                with st.expander("📚 See retrieved context"):
                    st.write(ctx)