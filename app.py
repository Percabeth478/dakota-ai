from flask import Flask, request, jsonify, render_template, session
from groq import Groq
import os

app = Flask(__name__)

# Secret key required for sessions
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are Dakota, a teen-style support chatbot for students.

Talk casually and naturally, like a real teen texting.
Use light slang sometimes (tbh, ngl, fr), but don’t overdo it.

Vary your responses:
- Sometimes short, sometimes a bit longer
- Sometimes one message, sometimes split into a few if it feels natural

Don’t always ask a follow-up question — only when it makes sense.

You can occasionally make small typos or informal phrasing, but keep it readable.

Avoid sounding robotic, structured, or overly helpful.
Sound like a real person just chatting and trying to help.
"""

def ask_ai(message):

    if "chats" not in session:
        session["chats"] = {}

    if "titles" not in session:
        session["titles"] = {}

    if "current_chat" not in session:
        chat_id = "chat1"
        session["current_chat"] = chat_id

    chat_id = session["current_chat"]

    if chat_id not in session["chats"]:
        session["chats"][chat_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    if chat_id not in session["titles"]:
        session["titles"][chat_id] = "New Chat"

    history = session["chats"][chat_id]

    history.append({"role": "user", "content": message})

    if len(history) > 21:
        system_msg = history[0]
        session["chats"][chat_id] = [system_msg] + history[-20:]
        history = session["chats"][chat_id]

    chat_completion = client.chat.completions.create(
        messages=history,
        model="llama-3.1-8b-instant"
    )

    # only generate title ONCE
    if len(history) == 2 and session["titles"].get(chat_id) == "New Chat":
        title_prompt = f"Generate a short 3-5 word chat title. No quotes, no punctuation: {message}"

        title_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": title_prompt}],
        model="llama-3.1-8b-instant"
        )

        title = title_completion.choices[0].message.content.strip()

        # clean it
        title = title.replace('"', '').replace("'", "")
        title = title.rstrip(".!?")
        title = title[:40]

        session["titles"][chat_id] = title

        reply = chat_completion.choices[0].message.content

        history.append({"role": "assistant", "content": reply})
        session["chats"][chat_id] = history

        return reply

# Backend routes

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/new_chat", methods=["POST"])
def new_chat():
    if "chats" not in session:
        session["chats"] = {}
    if "titles" not in session:
        session["titles"] = {}

    chat_id = f"chat{len(session['chats']) + 1}"

    session["chats"][chat_id] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    session["titles"][chat_id] = "New Chat"  # temporary title

    session["current_chat"] = chat_id

    return jsonify({"chat_id": chat_id})

@app.route("/switch_chat", methods=["POST"])
def switch_chat():
    chat_id = request.json["chat_id"]
    session["current_chat"] = chat_id
    return jsonify({"status": "ok"})

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]
    reply = ask_ai(user_message)
    return jsonify({"reply": reply})

@app.route("/get_chats")
def get_chats():
    if "chats" not in session:
        return jsonify({"chats": []})

    return jsonify({
        "chats": list(session["chats"].keys()),
        "titles": session.get("titles", {})
    })

@app.route("/rename_chat", methods=["POST"])
def rename_chat():
    data = request.json
    chat_id = data["chat_id"]
    new_title = data["title"]

    if "titles" in session and chat_id in session["titles"]:
        session["titles"][chat_id] = new_title

    return jsonify({"status": "ok"})

@app.route("/get_messages")
def get_messages():
    chat_id = session.get("current_chat")
    if not chat_id:
        return jsonify({"messages": []})

    history = session["chats"].get(chat_id, [])

    # remove system message
    messages = [msg for msg in history if msg["role"] != "system"]

    return jsonify({"messages": messages})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)