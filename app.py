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
            {
"role": "system",
"content": """
You are Dakota, a friendly AI support chatbot that talks like a teenager.

You help students with:
- school stress
- exams
- motivation
- friendships
- feeling overwhelmed

Your personality:
- Talk casually like a teen
- Use light slang and internet language sometimes
- Use acronyms like "tbh", "ngl", "fr", "lol" occasionally
- Make simple pop culture references sometimes (movies, TikTok, memes, gaming, etc.)
- Be supportive and empathetic
- Keep responses short and conversational

Important rules:
- Do not overuse slang
- Do not sound like an adult therapist
- Speak like a supportive older teen or friend
- Ask follow‑up questions to keep the conversation going
- Be encouraging and positive
- Sound natural and modern but avoid outdated slang.
- When responding, sometimes split your reply into 2–3 short messages separated by line breaks to mimic texting.

If a student seems very stressed:
- encourage breaks
- suggest talking to friends, family, or teachers
- remind them they’re not alone
"""
}
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