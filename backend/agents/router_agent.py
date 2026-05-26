def classify_intent(question: str):
    q = question.lower()

    if "summary" in q or "summarize" in q:
        return "summarize"

    if "key points" in q or "important points" in q:
        return "extract_key_points"

    if "interview questions" in q or "questions from this" in q:
        return "generate_interview_questions"

    return "question_answer" 