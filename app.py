from flask import Flask
from chatbot import chatbot_bp
from Calories_Calc import calories_bp
from Plans_Generation import plans_bp

app = Flask(__name__)
app.register_blueprint(chatbot_bp)
app.register_blueprint(calories_bp)
app.register_blueprint(plans_bp)

if __name__ == "__main__":
    app.run()
