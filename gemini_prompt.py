import os
import google.generativeai as genai
from dotenv import load_dotenv

def get_response(msg):

    load_dotenv()

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    # Create the model
    generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    )

    chat_session = model.start_chat(history=[])

    response = chat_session.send_message(msg)

    return response.text



if __name__ == "__main__":
    user_preference = {}
    get_response(f"Based on the user's interest in {user_preference}, recommend an event from the following list:\n{events_text}\n\nWhich event would you recommend!")

