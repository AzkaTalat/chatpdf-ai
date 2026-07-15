import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")


def ask_pdf(vector_store, question):
    """
    Answer questions using the uploaded PDF.
    """

    docs = vector_store.similarity_search(question, k=4)

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
You are a helpful AI assistant.

Answer ONLY from the PDF content below.

If the answer is not available, reply:

"I couldn't find that information in the uploaded PDF."

PDF Context:
{context}

Question:
{question}

Answer:
"""

    response = model.generate_content(prompt)

    return response.text


def generate_quiz(vector_store):
    """
    Generate an interactive quiz in JSON format.
    """

    docs = vector_store.similarity_search("", k=20)

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
You are an expert teacher.

Using ONLY the PDF below, generate EXACTLY 10 multiple choice questions.

Return ONLY valid JSON.

Format:

[
    {{
        "question":"Question here",
        "options":[
            "Option A",
            "Option B",
            "Option C",
            "Option D"
        ],
        "answer":"Correct Option",
        "explanation":"One line explanation"
    }}
]

Rules:
- Return ONLY JSON.
- No markdown.
- No ```json.
- No extra text.
- Exactly 10 questions.

PDF:

{context}
"""

    response = model.generate_content(prompt)

    quiz_text = response.text.strip()

    # Remove markdown if Gemini accidentally returns it
    quiz_text = quiz_text.replace("```json", "")
    quiz_text = quiz_text.replace("```", "")
    quiz_text = quiz_text.strip()

    try:
        quiz = json.loads(quiz_text)
        return quiz

    except Exception as e:
        print("Quiz JSON Error:", e)
        print(quiz_text)
        return []