from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

conversation_history = ""

def ask_ai(message):
    global conversation_history

    conversation_history += f"User: {message}\nDakota: "

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": conversation_history,
            "stream": False
        }
    )

    reply = response.json()["response"]
    conversation_history += reply + "\n"

    return reply


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]
    reply = ask_ai(user_message)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)