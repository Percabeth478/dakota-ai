# Import necessary modules for Flask web app and Groq AI client
from flask import Flask, request, jsonify, render_template, session
from groq import Groq
import os

# Initialize Flask application
app = Flask(__name__)
# Set secret key for secure session management
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# Initialize Groq client for AI API interactions
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Define the system prompt that sets the AI's personality and behavior
SYSTEM_PROMPT = """
You are Dakota, a high school student texting casually.

You are not an AI assistant. You are just a normal person chatting.

Your personality:
- chill, slightly sarcastic sometimes
- supportive but not overly sweet
- reacts naturally (like “nah that sucks”, “wait what 😭”, “ok but lowkey…”)
- not always trying to fix everything

How you text:
- mix short + medium messages
- sometimes 1 line, sometimes a few
- don’t always ask questions
- use lowercase sometimes
- occasional slang (tbh, ngl, fr, lowkey, idk)
- small imperfections are OK

Important:
- don’t sound like a therapist or teacher
- don’t give structured advice unless needed
- don’t always try to help

Just respond like a real person texting.
"""

# Main function to handle AI chat interactions
def ask_ai(message):
    # Ensure session has necessary structures for chats and titles
    if "chats" not in session:
        session["chats"] = {}
    if "titles" not in session:
        session["titles"] = {}
    if "current_chat" not in session or session["current_chat"] is None:
        session["current_chat"] = "chat1"

    chat_id = session["current_chat"]

    # Initialize chat if it doesn't exist
    if chat_id not in session["chats"]:
        session["chats"][chat_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        session["titles"][chat_id] = "New Chat"

    history = session["chats"][chat_id]

    # Add user message to history
    history.append({"role": "user", "content": message})

    # Trim history to keep only recent messages
    if len(history) > 21:
        system_msg = history[0]
        history = [system_msg] + history[-20:]
        session["chats"][chat_id] = history

    # Generate AI response using Groq API
    chat_completion = client.chat.completions.create(
        messages=history,
        model="GPT OSS 20B"
        # optionally upgrade:
        # model="llama-3.1-70b-versatile"
    )

    # Extract reply from response
    reply = chat_completion.choices[0].message.content

    # Add AI reply to history
    history.append({"role": "assistant", "content": reply})
    session["chats"][chat_id] = history

    # Generate title for new chats
    if session["titles"].get(chat_id) == "New Chat":
        title_prompt = f"Generate a short 3-5 word chat title. No quotes, no punctuation: {message}"

        title_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": title_prompt}],
            model="GPT OSS 20B"
        )

        title = title_completion.choices[0].message.content.strip()
        title = title.replace('"', '').replace("'", "")
        title = title.rstrip(".!?")
        title = title[:40]

        session["titles"][chat_id] = title

    session.modified = True
    return reply


# ---------------- ROUTES ----------------

# Route for home page
@app.route("/")
def home():
    return render_template("index.html")


# Route to create a new chat
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
    session["titles"][chat_id] = "New Chat"
    session["current_chat"] = chat_id

    session.modified = True
    return jsonify({"chat_id": chat_id})


# Route to switch to a different chat
@app.route("/switch_chat", methods=["POST"])
def switch_chat():
    chat_id = request.json["chat_id"]
    session["current_chat"] = chat_id
    session.modified = True
    return jsonify({"status": "ok"})


# Route to send a message and get AI response
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]
    reply = ask_ai(user_message)
    return jsonify({"reply": reply})


# Route to get list of chats and their titles
@app.route("/get_chats")
def get_chats():
    return jsonify({
        "chats": list(session.get("chats", {}).keys()),
        "titles": session.get("titles", {})
    })


# Route to rename a chat
@app.route("/rename_chat", methods=["POST"])
def rename_chat():
    data = request.json
    chat_id = data["chat_id"]
    new_title = data["title"]

    if "titles" in session and chat_id in session["titles"]:
        session["titles"][chat_id] = new_title
        session.modified = True

    return jsonify({"status": "ok"})


# Route to delete a chat
@app.route("/delete_chat", methods=["POST"])
def delete_chat():
    data = request.json
    chat_id = data["chat_id"]

    if "chats" in session and chat_id in session["chats"]:
        del session["chats"][chat_id]

    if "titles" in session and chat_id in session["titles"]:
        del session["titles"][chat_id]

    # 🔥 safe fallback if all chats deleted
    if session.get("chats"):
        session["current_chat"] = next(iter(session["chats"]))
    else:
        session["current_chat"] = None

    session.modified = True
    return jsonify({"status": "ok"})


# Route to get messages for current chat
@app.route("/get_messages")
def get_messages():
    chat_id = session.get("current_chat")

    if not chat_id:
        return jsonify({"messages": []})

    history = session["chats"].get(chat_id, [])
    messages = [msg for msg in history if msg["role"] != "system"]

    return jsonify({"messages": messages})


# Google verification route
@app.route('/googlee72c3b27cedf356e.html')
def google_verify():
    return render_template('googlee72c3b27cedf356e.html')


# Run the Flask app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)