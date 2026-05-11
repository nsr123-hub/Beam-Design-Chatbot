import os
from flask import Flask, request, jsonify, render_template
from chatbot import process_user_message

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
app = Flask(
    __name__,
    template_folder=os.path.join(base_dir, "templates"),
    static_folder=os.path.join(base_dir, "static"),
)

# ==========================================
# FRONTEND PAGE
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")

# ==========================================
# CHAT API
# ==========================================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    user_message = data.get("message")

    response = process_user_message(user_message)

    return jsonify(response)

# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)