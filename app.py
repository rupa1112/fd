import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from SmartApi import SmartConnect
import pyotp
import requests
import traceback

app = Flask(__name__)

# Allow ONLY your Blogger URL for CORS
CORS(app, resources={r"/*": {"origins": [
    "https://5763583527682878366_24f73d2dae53a6ddc3170a5d91e05d139e40a93a.blogspot.com"
]}})

# SmartAPI credentials
api_key = os.environ.get("SMARTAPI_KEY", "your_api_key")
client_code = os.environ.get("SMARTAPI_CLIENT_CODE", "your_client_code")
pin = os.environ.get("SMARTAPI_PIN", "your_pin")
totp_secret = os.environ.get("TOTP_TOKEN")  # Must be a base32 secret

def get_auth_token():
    if not all([api_key, client_code, pin, totp_secret]):
        print("❌ Missing SmartAPI credentials or TOTP secret.")
        return None

    print(f"✅ API Key: {api_key}")
    print(f"✅ Client Code: {client_code}")
    print(f"✅ Using TOTP Secret: {totp_secret}")

    try:
        totp = pyotp.TOTP(totp_secret)
        otp = totp.now()
        print(f"🔐 Generated OTP from TOTP: {otp}")
    except Exception as e:
        print(f"❌ Error generating OTP: {e}")
        traceback.print_exc()
        return None

    try:
        smartApi = SmartConnect(api_key)
        session = smartApi.generateSession(client_code, pin, otp)
        print(f"✅ Session Response: {session}")
        jwt_token = session['data']['jwtToken']
        print(f"🔑 JWT Token: {jwt_token}")
        return jwt_token
    except Exception as e:
        print(f"❌ Error generating session: {e}")
        traceback.print_exc()
        return None

@app.route("/greeks", methods=["POST"])
def option_greeks():
    data = request.json
    name = data.get("name")
    expiry = data.get("expiry")

    print(f"📩 Received Request with name: {name}, expiry: {expiry}")

    auth_token = get_auth_token()

    if not auth_token:
        return jsonify({"error": "Authentication failed. Check logs for details."}), 401

    headers = {
        "X-PrivateKey": api_key,
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "name": name,
        "expirydate": expiry
    }

    try:
        url = "https://apiconnect.angelone.in/rest/secure/angelbroking/marketData/v1/optionGreek"
        response = requests.post(url, json=payload, headers=headers)

        print(f"🌐 Raw Response from AngelOne API: {response.text}")

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "error": "Failed to fetch data from AngelOne API",
                "status_code": response.status_code,
                "response": response.text
            }), response.status_code

    except Exception as e:
        print(f"❌ Exception during AngelOne API call: {e}")
        traceback.print_exc()
        return jsonify({"error": "Server error while contacting AngelOne API"}), 500

if __name__ == "__main__":
    app.run(debug=True)
