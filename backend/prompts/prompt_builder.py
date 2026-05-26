def build_prompt(chat_history, task_instruction, context, question):

    prompt = f"""
You are an Agentic RAG Assistant.

CHAT HISTORY:
{chat_history}

AGENT TASK:
{task_instruction}

STRICT RULES:
- Use ONLY the provided context
- If the answer is not present, say: "I don't know based on the document"
- Do NOT make up information
- Mention source page if available

CONTEXT:
{context}

USER QUESTION:
{question}

FINAL ANSWER:
"""

    return prompt