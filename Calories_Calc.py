from flask import Blueprint, Flask, request, jsonify
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

calories_bp = Blueprint("calories", __name__)
GOOGLE_API_KEY2 = os.getenv("calories_API")

if not GOOGLE_API_KEY2:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

genai.configure(api_key=GOOGLE_API_KEY2)


GEMINI_VISION_MODEL = "gemini-2.5-flash"


@calories_bp.route('/api/analyze-meal-image', methods=['POST'])
def analyze_meal_image():
    if 'mealImage' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files['mealImage']
    image_data = image_file.read()

    try:
        nutrition_info = call_gemini_vision(image_data)
        return jsonify({"status": "success", "mealAnalysis": nutrition_info}), 200
    except Exception as e:
        print(f"Error analyzing meal image: {e}")
        return jsonify({"status": "error", "details": str(e)}), 500


def call_gemini_vision(image_data):
    vision_model = genai.GenerativeModel(GEMINI_VISION_MODEL)

    vision_prompt = """
    Analyze the food items in this image. For each item, estimate:
    - name
    - estimated serving size in grams
    - approximate calories
    - protein in grams
    - carbs in grams
    - fat in grams

    Output ONLY valid JSON in this format:
    {
        "items": [
        {
            "name": "chicken breast",
            "estimatedServingG": 150,
            "calories": 250,
            "proteinG": 30,
            "carbsG": 0,
            "fatG": 5
        }
        ],
        "totalCalories": 250,
        "totalProtein": 30,
        "totalCarbs": 0,
        "totalFat": 5
    }
    """

    response = vision_model.generate_content(
        [vision_prompt, {"mime_type": "image/jpeg", "data": image_data}]
    )

    raw_text = response.text.strip() if response.text else ""

    if not raw_text:
        raise ValueError("Gemini returned empty response.")

    
    if raw_text.startswith("```") and raw_text.endswith("```"):
        raw_text = "\n".join(raw_text.split("\n")[1:-1])

    try:
        nutrition_data = json.loads(raw_text)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON from Gemini: {raw_text}")

    return nutrition_data
