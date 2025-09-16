from flask import Blueprint, request, jsonify
import os
import google.generativeai as genai
import json
from dotenv import load_dotenv

load_dotenv()

chatbot_bp = Blueprint("chatbot", __name__)


GOOGLE_API_KEY = os.getenv("Chatbot_API")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")


genai.configure(api_key=GOOGLE_API_KEY)
GEMINI_FLASH_MODEL = "gemini-2.5-flash"


@chatbot_bp.route('/api/chatbot', methods=['POST'])
def chatbot_query():
    user_data = request.json
    if not user_data or 'message' not in user_data:
        return jsonify({"error": "Missing 'message' in request body"}), 400

    user_message = user_data['message']

    try:
        bot_response = call_gemini_chatbot(user_message)
        return jsonify(bot_response), 200
    except Exception as e:
        print(f"Error with Gemini chatbot: {e}")
        return jsonify({"error": "Failed to get chatbot response", "details": str(e)}), 500


import json

def call_gemini_chatbot(user_message):
    """
    Sends the user's message to the Gemini API with a system instruction
    and returns a structured JSON response.
    """
    model = genai.GenerativeModel(GEMINI_FLASH_MODEL)

    system_instruction = (
        "You are a helpful fitness and nutrition assistant. "
        "Provide concise, structured, and accurate advice strictly about "
        "fitness, nutrition, exercise, and healthy lifestyle. "
        "Output ONLY valid JSON in the format: {\"message\": \"<your advice here>\"}.\n\n"
    )

    contents = [
        {"role": "user", "parts": [{"text": system_instruction + user_message}]}
    ]

    response = model.generate_content(
        contents,
        generation_config={"temperature": 0.7, "max_output_tokens": 2048} 
    )

    if not response.candidates:
        raise ValueError("Gemini returned an empty response with no candidates.")

    candidate = response.candidates[0]
    if not candidate.content or not candidate.content.parts:
        raise ValueError("Gemini returned empty content or parts.")

    json_text = ""
    for part in candidate.content.parts:
        if part.text:
            json_text += part.text

    if not json_text.strip():
        raise ValueError("Gemini returned empty text in its response.")

    try:
        start_index = json_text.find('{')
        end_index = json_text.rfind('}') + 1
        
        if start_index != -1 and end_index != 0 and end_index > start_index:
            extracted_json = json_text[start_index:end_index]
            advice_json = json.loads(extracted_json)
        else:
            raise ValueError(f"Could not find a valid JSON object in the response. Response text: {json_text}")

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid or truncated JSON from Gemini: {extracted_json}. Details: {e}")

    return advice_json

