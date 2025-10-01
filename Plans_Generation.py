from flask import Blueprint, request, jsonify
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv


load_dotenv()

plans_bp = Blueprint("plans", __name__)


try:
    api_key = os.getenv("Plans_API")
    if not api_key:
        raise ValueError("API key 'Plans_API' not found in environment variables.")
    genai.configure(api_key=api_key)

    
    SYSTEM_INSTRUCTION = (
        "You are a fitness and nutrition plan generator for a test environment. "
        "Your sole purpose is to return valid, well-formed JSON that strictly adheres to the provided schema. "
        "Do not include any explanatory text, markdown formatting, or anything outside of the JSON structure. "
        "The JSON response MUST contain two top-level keys: 'nutrition' and 'workout'. "
        "Rules for the JSON structure:"
        "- Both 'nutrition' and 'workout' must be objects."
        "- The keys for these objects must be strings from 'day 1' through 'day 7'."
        "- Each day in 'nutrition' must have an array of meal objects. A meal object is {\"meal\": \"breakfast\", \"food\": \"oats\"}."
        "- Each day in 'workout' must have an array of exercise objects. An exercise object is {\"exercise\": \"bench press\", \"sets\": 3, \"reps\": 10}. The values for 'sets' and 'reps' MUST strictly be integers. For reps until failure (e.g., 'as many as possible'), use the integer 0."
        "- For rest days, the workout array should be exactly: [{\"exercise\": \"rest\"}]."
        "- All keys within the JSON must be lowercase."
        "- Do not return null values or empty objects. If a day has no plan, omit it."
        "Example of a valid response format:\n"
        "{"
        "  \"nutrition\": {"
        "    \"day 1\": ["
        "      {\"meal\": \"breakfast\", \"food\": \"eggs with spinach\"},"
        "      {\"meal\": \"lunch\", \"food\": \"chicken salad\"}"
        "    ]"
        "  },"
        "  \"workout\": {"
        "    \"day 1\": ["
        "      {\"exercise\": \"push-ups\", \"sets\": 3, \"reps\": 15},"
        "      {\"exercise\": \"squats\", \"sets\": 3, \"reps\": 12}"
        "    ]"
        "  }"
        "}"
    )

    model = genai.GenerativeModel(
        "gemini-2.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )

except (ValueError, Exception) as e:
    print(f"Error initializing Generative AI Model: {e}")
    model = None


@plans_bp.route("/api/generate-plan", methods=["POST"])
def generate_plan():
    """
    Generates a 7-day fitness and nutrition plan based on user input.
    The AI model is configured to return a strict JSON schema.
    """
    if not model:
        return jsonify({"status": "error", "details": "AI model not initialized"}), 503

    try:
        data = request.json
        weight = data.get("weight")
        height = data.get("height")
        goal = data.get("goal")
        culture = data.get("culture")

        if not all([weight, height, goal, culture]):
            return jsonify({"status": "error", "details": "Missing weight, height, goal, or culture"}), 400

        user_prompt = (
            "Based on the user profile below, generate a complete 7-day plan in JSON format. The plan MUST include BOTH a 'workout' section and a 'nutrition' section.\n"
            "User Profile:\n"
            f"- Weight: {weight} kg\n"
            f"- Height: {height} cm\n"
            f"- Goal: {goal}\n"
            f"- Cultural food preference: {culture}\n"
        )

        response = model.generate_content(
            user_prompt,
            generation_config={"response_mime_type": "application/json"}
        )

        raw_text = (response.text or "").strip()

        if not raw_text:
            return jsonify({
                "status": "error",
                "details": "AI model returned an empty response."
            }), 500

        
        plan_json = json.loads(raw_text)
        
        
        plan_json["status"] = "success"

        return jsonify(plan_json)

    except json.JSONDecodeError:
        
        return jsonify({
            "status": "error",
            "details": "AI model returned invalid JSON.",
            "raw_response": raw_text
        }), 500
    except Exception as e:
        
        return jsonify({"status": "error", "details": str(e)}), 500
