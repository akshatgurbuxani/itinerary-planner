import google.generativeai as genai
import streamlit as st

def get_response(msg):


    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

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
    # get_response(f"Based on the user's interest in {user_preference}, recommend an event from the following list:\n{events_text}\n\nWhich event would you recommend!")

    print(get_response("Hello"))