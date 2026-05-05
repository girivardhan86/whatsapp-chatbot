import requests

ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
APP_ID = "YOUR_APP_ID"
VERIFY_TOKEN = "agneyra_token"

# Get ngrok public URL
ngrok_data = requests.get(
    "http://127.0.0.1:4040/api/tunnels"
).json()

public_url = ngrok_data["tunnels"][0]["public_url"]

webhook_url = public_url + "/webhook"

print("Webhook URL:", webhook_url)

# Update webhook in Meta
url = f"https://graph.facebook.com/v19.0/{APP_ID}/subscriptions"

params = {
    "object": "whatsapp_business_account",
    "callback_url": webhook_url,
    "verify_token": VERIFY_TOKEN,
    "access_token": ACCESS_TOKEN
}

response = requests.post(url, params=params)

print(response.text)


