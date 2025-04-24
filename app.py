import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from SmartApi import SmartConnect
import pyotp
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": [
    "https://5763583527682878366_24f73d2dae53a6ddc3170a5d91e05d139e40a93a.blogspot.com"
]}})

# Load credentials from environment
api_key = os.environ.get("SMARTAPI_KEY")
client_code = os.environ.get("SMARTAPI_CLIENT_CODE")
pin = os.environ.get("SMARTAPI_PIN")
totp_token = os.environ.get("TOTP_TOKEN")

def get_auth_token():
    if not all([api_key, client_code, pin, totp_token]):
        print("❌ Missing SmartAPI credentials or TOTP secret.")
        return None

    try:
        totp = pyotp.TOTP(totp_token)
        otp = totp.now()
        print(f"🔑 Generated OTP: {otp}")
    except Exception as e:
        print(f"❌ OTP generation failed: {e}")
        return None

    try:
        smart_api = SmartConnect(api_key)
        session = smart_api.generateSession(client_code, pin, otp)
        jwt_token = session['data']['jwtToken']
        print("✅ Auth Token successfully fetched.")
        return jwt_token
    except Exception as e:
        print(f"❌ Auth Token fetch failed: {e}")
        return None

@app.route("/greeks", methods=["POST"])
def option_greeks():
    data = request.json
    name = data.get("name")
    expiry = data.get("expiry")
    print(f"📩 Received Request with name: {name}, expiry: {expiry}")

    token = get_auth_token()
    if not token:
        return jsonify({"error": "Authentication failed"}), 401

    headers = {
        "Authorization": f"Bearer {token}",
        "X-PrivateKey": api_key,
        "X-ClientCode": client_code,
        "Content-Type": "application/json"
    }

    payload = {
        "name": name,
        "expirydate": expiry
    }

    url = "https://apiconnect.angelone.in/rest/secure/angelbroking/marketData/v1/optionGreek"
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"📨 Raw Response from AngelOne API: {response.text}")

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "error": "Failed to fetch data from AngelOne API",
                "status_code": response.status_code,
                "response": response.text
            }), response.status_code

    except Exception as e:
        print(f"❌ Request error: {e}")
        return jsonify({"error": "Request failed"}), 500

@app.route("/", methods=["GET"])
def home():
    return "✅ AngelOne Greeks API is running."

if __name__ == "__main__":
    app.run(debug=True)
