import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from SmartApi import SmartConnect
import pyotp
import requests

app = Flask(__name__)
# Allow ONLY your Blogger URL for CORS
CORS(app, resources={r"/*": {"origins": [
    "https://5763583527682878366_24f73d2dae53a6ddc3170a5d91e05d139e40a93a.blogspot.com"
]}})

# SmartAPI credentials
api_key = "your_api_key"
client_code = "your_client_code"
pin = "your_pin"
totp_token = os.environ.get('TOTP_TOKEN')  # Fetch the TOTP token from environment variables

def get_auth_token():
    if not totp_token:
        return jsonify({"error": "TOTP token is missing"}), 400

    # Debug log: Print the TOTP token to ensure it's correctly passed
    print(f"TOTP Token being used: {totp_token}")
    
    # Test the TOTP generation
    try:
        totp = pyotp.TOTP(totp_token)
        otp = totp.now()
        print(f"Generated OTP: {otp}")  # This prints the OTP generated from the TOTP
    except Exception as e:
        print(f"Error generating OTP: {e}")
        return jsonify({"error": "Error generating OTP"}), 500

    # Proceed to get the session token using SmartAPI
    smartApi = SmartConnect(api_key)
    session = smartApi.generateSession(client_code, pin, otp)
    return session['data']['jwtToken']

@app.route("/greeks", methods=["POST"])
def option_greeks():
    data = request.json
    name = data.get("name")
    expiry = data.get("expiry")

    auth_token = get_auth_token()

    headers = {
        "X-PrivateKey": api_key,
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "name": name,
        "expirydate": expiry
    }

    url = "https://apiconnect.angelone.in/rest/secure/angelbroking/marketData/v1/optionGreek"
    response = requests.post(url, json=payload, headers=headers)
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(debug=True)
