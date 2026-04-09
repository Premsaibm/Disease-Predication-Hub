import os
from dotenv import load_dotenv
from groq import Groq

# 1. Load environment variables
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

# 2. Initialize Client
client = None
if API_KEY:
    try:
        client = Groq(api_key=API_KEY)
    except Exception as e:
        print(f"⚠️ Groq Client Error: {e}")

def get_rule_based_response(query: str, context_disease: str) -> str:
    """Fallback logic if AI is unavailable."""
    query = query.lower()
    if "diabetes" in query or context_disease == "Diabetes":
        return "Diabetes involves high blood sugar. Please consult a doctor for a proper diagnosis."
    if "heart" in query or context_disease == "Heart":
        return "Heart disease affects cardiovascular health. A healthy diet and exercise are key."
    if "parkinson" in query or context_disease == "Parkinsons":
        return "Parkinson's is a neurodegenerative disorder. Therapy can help manage symptoms."
    return "I am your health assistant. Please ask about Diabetes, Heart Disease, or Parkinson's."

def get_ai_response(user_query: str, context_disease: str) -> str:
    """Primary logic: Uses Groq AI."""
    if not client:
        return get_rule_based_response(user_query, context_disease)

    try:
        system_prompt = f"""
        You are a helpful Medical AI Assistant.
        Context: The user is viewing the '{context_disease}' page.
        Keep answers concise (max 3 sentences). Never provide a diagnosis.
        """

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model="llama-3.3-70b-versatile", 
            temperature=0.5,
            max_tokens=150,
        )
        return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"⚠️ AI Error: {e}")
        return get_rule_based_response(user_query, context_disease)

# 👇 THIS IS THE FUNCTION main.py IS LOOKING FOR
def get_chatbot_response(user_query: str, disease: str = "General") -> str:
    """Main function called by main.py"""
    if not user_query or not user_query.strip():
        return "Hello! How can I help you today?"
    return get_ai_response(user_query, disease)