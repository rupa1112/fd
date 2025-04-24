from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import Flask, request, jsonify
from SmartApi import SmartConnect
import pyotp
import requests

app = Flask(__name__)

# SmartAPI credentials
api_key = "your_api_key"
client_code = "your_client_code"
pin = "your_pin"
totp_token = "your_totp_token"

def get_auth_token():
    smartApi = SmartConnect(api_key)
    otp = pyotp.TOTP(totp_token).now()
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
