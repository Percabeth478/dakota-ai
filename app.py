from flask import Flask, request, jsonify, render_template, session
from groq import Groq
import os

app = Flask(__name__)

# Secret key required for sessions
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def ask_ai(message):

    if "history" not in session:
        session["history"] = [
            {"role": "system", "content": "You are Dakota, a helpful AI assistant."}
        ]

    history = session["history"]

    history.append({"role": "user", "content": message})

    if len(history) > 20:
        history = history[-20:]

    chat_completion = client.chat.completions.create(
        messages=history,
        model="llama-3.1-8b-instant"
    )

    reply = chat_completion.choices[0].message.content

    history.append({"role": "assistant", "content": reply})

    session["history"] = history

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