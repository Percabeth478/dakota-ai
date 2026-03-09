from flask import Flask, request, jsonify, render_template
from groq import Groq
import os

app = Flask(__name__)

# Create Groq client using the API key from environment variables
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

conversation_history = ""


def ask_ai(message):
    global conversation_history

    conversation_history += f"User: {message}\nDakota: "

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": conversation_history}
        ],
        model="llama-3.1-8b-instant"
    )

    reply = chat_completion.choices[0].message.content

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