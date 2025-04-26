import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from SmartApi import SmartConnect
import pyotp
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": [
    "https://www.niftyfifty.in"
]}})

# SmartAPI credentials from environment variables
api_key = os.environ.get("SMARTAPI_KEY")
client_code = os.environ.get("CLIENT_CODE")
pin = os.environ.get("PIN")
totp_token = os.environ.get('TOTP_TOKEN')
print(f"API Key: {api_key}, Client Code: {client_code}, PIN: {pin}, TOTP Token: {totp_token}")

def get_auth_token():
    if not totp_token or not api_key or not client_code or not pin:
        print("❌ Missing required credentials")
        return jsonify({"error": "Missing required credentials (API Key, Client Code, PIN, TOTP token)"}), 400

    try:
        totp = pyotp.TOTP(totp_token)
        otp = totp.now()
        print(f"Generated OTP: {otp}")
    except Exception as e:
        print(f"❌ Error generating OTP: {e}")
        return jsonify({"error": "Error generating OTP"}), 500

    try:
        smartApi = SmartConnect(api_key=api_key)
        print("Attempting to generate session...")
        session = smartApi.generateSession(client_code, pin, otp)
        print(f"Session API Response: {session}")

        if "data" in session and "jwtToken" in session["data"]:
            auth_token = session['data']['jwtToken']
            print("✅ Auth Token fetched successfully:", auth_token[:20] + "...") # Print first 20 chars for brevity
            return auth_token
        else:
            print("❌ Session response missing jwtToken:", session)
            return jsonify({"error": "Invalid session response", "details": session}), 500

    except Exception as e:
        print(f"❌ Error in generateSession(): {e}")
        return jsonify({"error": "Failed to fetch auth token", "details": str(e)}), 500


    try:
        smartApi = SmartConnect(api_key=api_key)
        session = smartApi.generateSession(client_code, pin, otp)

        if "data" in session and "jwtToken" in session["data"]:
            auth_token = session['data']['jwtToken']
            print("✅ Auth Token fetched successfully")
            return auth_token
        else:
            print("❌ Session response missing jwtToken:", session)
            return jsonify({"error": "Invalid session response", "details": session}), 500

    except Exception as e:
        print(f"❌ Error in generateSession(): {e}")
        return jsonify({"error": "Failed to fetch auth token", "details": str(e)}), 500

@app.route("/greeks", methods=["POST"])
def option_greeks():
    data = request.json
    print(f"📥 Received data: {data}")
    name = data.get("name")
    expiry = data.get("expirydate")

    if not name or not expiry:
        print("❌ Missing 'name' or 'expirydate' in request")
        return jsonify({"error": "Missing 'name' or 'expirydate' in request"}), 400

    auth_token_response = get_auth_token()
    if isinstance(auth_token_response, tuple):
        return auth_token_response
    jwt_token = auth_token_response # Now this directly holds the JWT string

    if jwt_token: # Check if we successfully got the token
        print(f"✅ Using raw jwtToken for greeks request: {jwt_token[:20]}...")
        headers = {
            "X-PrivateKey": api_key,
            "Authorization": f"{jwt_token}", # Removed "Bearer " prefix as per last attempt
            "Content-Type": "application/json"
        }
    else:
        print("❌ Could not retrieve auth token for greeks request")
        return jsonify({"error": "Could not retrieve auth token for greeks request"}), 500


    payload = {
        "name": name,
        "expirydate": expiry
    }

    url = "https://apiconnect.angelone.in/rest/secure/angelbroking/marketData/v1/optionGreek" # Ensure correct URL

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"🔄 Response Status from AngelOne: {response.status_code}")
        print(f"🧾 Raw Response from AngelOne: {response.text}")

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "error": "Failed to fetch data from AngelOne API",
                "status_code": response.status_code,
                "response": response.text
            }), response.status_code

    except Exception as e:
        print(f"❌ Exception during API request: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
