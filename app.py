from flask import Flask, request, render_template, redirect
from chatbot import get_response
import requests
import queue
import threading
from memory_db import init_db, save_message, get_chat_history, get_all_users
import os
import sqlite3
from create_vector_db import (
    ingest_file,
    ingest_image,
    ingest_url
)
from weather import get_weather
from news import get_news
# ================= CONFIG =================

# ================= INIT =================
message_queue = queue.Queue()
app = Flask(__name__)
init_db()

# ================= ADMIN PANEL =================
@app.route("/admin")
def admin():
    phone = request.args.get("phone")

    users = get_all_users()
    if not phone and users:
        phone = users[0][0]

    messages = get_chat_history(phone) if phone else []

    return render_template(
        "admin.html",
        all_users=users,
        messages=messages,
        phone=phone
    )

# ================= HOME =================
@app.route("/")
def home():
    return "Agneyra WhatsApp AI Bot Running ✅"

# ================= WEBHOOK VERIFY =================
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge
    return "Verification failed", 403

# ================= RECEIVE MESSAGE =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Incoming:", data)

    try:
        value = data["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return "ok", 200

        msg = value["messages"][0]
        sender = msg["from"]

        # ================= TEXT =================
        if msg["type"] == "text":
            message = msg["text"]["body"]
            message_queue.put((sender, "text", message))

        # ================= IMAGE =================
        elif msg["type"] == "image":
            image_id = msg["image"]["id"]
            message_queue.put((sender, "image", image_id))

        # ================= DOCUMENT =================
        elif msg["type"] == "document":
            doc_id = msg["document"]["id"]
            filename = msg["document"].get("filename", "file")

            message_queue.put((sender, "document", (doc_id, filename)))

        else:
            return "ok", 200

    except Exception as e:
        print("Webhook Error:", e)

    return "ok", 200

def download_media(media_id, filename):
    url = f"https://graph.facebook.com/v19.0/{media_id}"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    res = requests.get(url, headers=headers).json()
    media_url = res.get("url")

    if not media_url:
        return None

    file_data = requests.get(media_url, headers=headers).content

    os.makedirs("uploads", exist_ok=True)
    filepath = f"uploads/{filename}"

    with open(filepath, "wb") as f:
        f.write(file_data)

    return filepath

# ================= SEND TEXT =================
def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print("Send:", response.json())

        # Save bot message
        save_message(to, "bot", message)

    except Exception as e:
        print("Send Error:", e)

# ================= SEND IMAGE =================
def send_image(to, filepath):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    upload_url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/media"

    try:
        with open(filepath, 'rb') as f:
            files = {'file': (os.path.basename(filepath), f, 'image/jpeg')}
            data = {"messaging_product": "whatsapp"}

            upload = requests.post(upload_url, headers=headers, files=files, data=data)
            media_id = upload.json().get("id")

        if not media_id:
            print("Upload failed")
            return

        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "image",
            "image": {"id": media_id}
        }

        requests.post(url, headers=headers, json=payload)

    except Exception as e:
        print("Image Error:", e)

# ================= SEND DOCUMENT =================
def send_document(to, filepath):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    upload_url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/media"

    try:
        with open(filepath, 'rb') as f:
            files = {'file': (filepath, f, 'application/pdf')}
            data = {"messaging_product": "whatsapp"}

            upload = requests.post(upload_url, headers=headers, files=files, data=data)
            media_id = upload.json().get("id")

        if not media_id:
            print("Upload failed")
            return

        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "document",
            "document": {
                "id": media_id,
                "caption": "🎓 Your Certificate"
            }
        }

        requests.post(url, headers=headers, json=payload)

    except Exception as e:
        print("Document Error:", e)

# ================= PROCESS QUEUE =================
def process_messages():
    while True:
        sender, msg_type, content = message_queue.get()

        try:
            print(f"{msg_type.upper()} from {sender}: {content}")

            # ================= TEXT =================
            if msg_type == "text":

                save_message(sender, "user", content)

                # URL detection
                if "http" in content:
                    ingest_url(content, sender)
                    send_whatsapp_message(sender, "✅ URL processed. Ask questions now.")
                    message_queue.task_done()
                    continue

                # AI response
                reply = get_response(content, sender)
                send_whatsapp_message(sender, reply)

            # ================= IMAGE =================
            elif msg_type == "image":

                filepath = download_media(content, f"{sender}.jpg")

                if filepath:
                    ingest_image(filepath, sender)
                    send_whatsapp_message(sender, "✅ Image processed. Ask questions now.")

            # ================= DOCUMENT =================
            elif msg_type == "document":

                media_id, filename = content
                filepath = download_media(media_id, filename)

                if filepath:
                    ingest_file(filepath, sender)
                    send_whatsapp_message(sender, "✅ File processed. Ask questions now.")

        except Exception as e:
            print("Processing Error:", e)

        message_queue.task_done()


# ================= RUN =================
if __name__ == "__main__":
    threading.Thread(target=process_messages, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)