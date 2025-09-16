from flask import Blueprint, request, jsonify
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv


load_dotenv()

plans_bp = Blueprint("plans", __name__)


genai.configure(api_key=os.getenv("Plans_API"))
model = genai.GenerativeModel("gemini-1.5-flash")

@plans_bp.route("/api/generate-plan", methods=["POST"])
def generate_plan():
    try:
        data = request.json
        weight = data.get("weight")
        height = data.get("height")
        goal = data.get("goal")
        culture = data.get("culture")

        if not weight or not height or not goal or not culture:
            return jsonify({"status": "error", "details": "Missing weight, height, goal, or culture"}), 400

        system_instruction = (
            "You are generating fictional example fitness and nutrition plans for testing a fitness app. "
            "Always return ONLY valid JSON. "
            "Do not add explanations or text outside JSON. "
            "Meals must reflect the user's culture. "
        )

        user_prompt = f"""
        Create a fictional 1-week workout and nutrition plan as JSON.
        User:
        - Weight: {weight} kg
        - Height: {height} cm
        - Goal: {goal}
        - Culture: {culture}
        """

        
        response = model.generate_content(
            system_instruction + "\n" + user_prompt,
            generation_config={"response_mime_type": "application/json"}
        )

        raw_text = (response.text or "").strip()

        if not raw_text:
            fallback = {
                "user": {"weight": weight, "height": height, "goal": goal, "culture": culture},
                "week_plan": [
                    {
                        "day": "Monday",
                        "workouts": [{"exercise": "Push-ups", "sets": 3, "reps": 15}],
                        "meals": [{"meal": "Breakfast", "food": "Eggs with bread"}]
                    }
                ]
            }
            return jsonify({"plan": fallback, "status": "success"})

        try:
            plan_json = json.loads(raw_text)
        except json.JSONDecodeError:
            return jsonify({
                "status": "error",
                "details": "Gemini returned invalid JSON.",
                "raw_text": raw_text
            }), 500

        return jsonify({"plan": plan_json, "status": "success"})

    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500
