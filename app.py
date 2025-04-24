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
api_key = os.environ.get("SMARTAPI_KEY")  # Ensure the API key is fetched from env variables
client_code = os.environ.get("CLIENT_CODE")  # Fetch client code from environment
pin = os.environ.get("PIN")  # Fetch PIN from environment
totp_token = os.environ.get('TOTP_TOKEN')  # Fetch the TOTP token from environment variables

def get_auth_token():
    if not totp_token or not api_key or not client_code or not pin:
        return jsonify({"error": "Missing required credentials (API Key, Client Code, PIN, TOTP token)"}), 400

    try:
        totp = pyotp.TOTP(totp_token)
        otp = totp.now()
        print(f"Generated OTP: {otp}")  # Log the OTP for debugging purposes
    except Exception as e:
        print(f"Error generating OTP: {e}")
        return jsonify({"error": "Error generating OTP"}), 500

    smartApi = SmartConnect(api_key)
    try:
        # Attempt to generate the session using provided credentials
        session = smartApi.generateSession(client_code, pin, otp)
        auth_token = session['data']['jwtToken']
        print("Auth Token successfully fetched")
        return auth_token
    except Exception as e:
        print(f"Error fetching auth token: {e}")
        return jsonify({"error": "Failed to fetch auth token"}), 500

@app.route("/greeks", methods=["POST"])
def option_greeks():
    data = request.json
    name = data.get("name")
    expiry = data.get("expiry")

    # Fetch the auth token for the API request
    auth_token = get_auth_token()

    # Check if auth_token is valid
    if isinstance(auth_token, tuple):
        return auth_token  # Return error response if auth_token is invalid

    headers = {
        "X-PrivateKey": api_key,
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "name": name,
        "expirydate": expiry
    }

    url = "https://apiconnect.angelbroking.in/rest/secure/angelbroking/marketData/v1/optionGreek"
    try:
        # Make the API request to AngelOne
        response = requests.post(url, json=payload, headers=headers)
        print(f"Raw Response from AngelOne API: {response.text}")

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            print(f"Error fetching data: {response.text}")
            return jsonify({"error": "Failed to fetch data from AngelOne API", "status_code": response.status_code, "response": response.text}), response.status_code
    except Exception as e:
        print(f"Error in API request: {e}")
        return jsonify({"error": "Error making request to AngelOne API"}), 500

if __name__ == "__main__":
    app.run(debug=True)
