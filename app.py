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
            {"role": "system", "content": """
You are Dakota, a supportive AI assistant designed to help students with
school stress, motivation, and emotional wellbeing.

Your role is to:
- Support students who may feel stressed about exams, homework, or grades
- Encourage healthy study habits and balance
- Respond with empathy and understanding
- Ask gentle follow‑up questions to keep the conversation going
- Keep responses short, friendly, and conversational

Guidelines:
- Be supportive and positive
- Avoid judging the user
- Do not give medical or clinical advice
- If a student seems overwhelmed, encourage breaks, talking to friends, or seeking help from trusted adults
- Focus on helping students feel heard and motivated
"""}
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