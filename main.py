from flask import Flask
from dotenv import load_dotenv


from Plans_Generation import plans_bp
from Calories_Calc import calories_bp
from chatbot import chatbot_bp



load_dotenv()
import os
print("Plans_API:", os.getenv("Plans_API"))
print("calories_API:", os.getenv("calories_API"))
print("Chatbot_API:", os.getenv("Chatbot_API"))

app = Flask(__name__)


app.register_blueprint(plans_bp)
app.register_blueprint(calories_bp)
app.register_blueprint(chatbot_bp)

if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=5000, debug=True)
