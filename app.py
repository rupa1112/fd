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

@app.route("/top_gainers_losers", methods=["POST"])
def get_top_gainers_losers():
    data = request.json
    datatype = data.get("datatype")
    expirytype = data.get("expirytype")

    if not datatype or not expirytype:
        return jsonify({"error": "Missing 'datatype' or 'expirytype' in request"}), 400

    auth_token_response = get_auth_token()
    if isinstance(auth_token_response, tuple):
        return auth_token_response
    jwt_token = auth_token_response

    if not jwt_token:
        return jsonify({"error": "Could not retrieve auth token"}), 500

    headers = {
        "X-PrivateKey": api_key,
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "datatype": datatype,
        "expirytype": expirytype
    }
    print(f"📤 Sending payload for top gainers/losers: {payload}")

    url = "https://apiconnect.angelone.in/rest/secure/angelbroking/marketData/v1/gainersLosers"

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"🔄 Response Status from AngelOne (Gainers/Losers): {response.status_code}")
        print(f"🧾 Raw Response from AngelOne (Gainers/Losers): {response.text}")
        print(f"Headers from AngelOne Response (Gainers/Losers): {response.headers}") # Log the headers

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "error": "Failed to fetch top gainers/losers data",
                "status_code": response.status_code,
                "response": response.text,
                "headers": dict(response.headers) # Include headers in the error response
            }), response.status_code

    except Exception as e:
        print(f"❌ Exception during top gainers/losers request: {e}")
        return jsonify({"error": "Internal Server Error during top gainers/losers fetch", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
