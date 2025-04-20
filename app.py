from flask import Flask, request, jsonify, send_file
import yfinance as yf
import csv
import os
from news_fetcher import get_news

app = Flask(__name__)

# Route to fetch stock data and show it in JSON format
@app.route('/stock')
def stock_data():
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({"error": "Ticker is required"}), 400

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        data = {
            "Symbol": ticker.replace(".NS", ""),
            "Name": info.get("longName", ""),
            "Price": info.get("currentPrice", ""),
            "Market Cap": info.get("marketCap", ""),
            "P/E": info.get("trailingPE", ""),
            "EPS": info.get("trailingEps", ""),
            "ROE": info.get("returnOnEquity", ""),
            "Sector": info.get("sector", ""),
            "News": get_news(info.get("longName", ticker))
        }
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to generate and download CSV
@app.route('/download_csv')
def download_csv():
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({"error": "Ticker is required"}), 400

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Prepare the data to be written to the CSV file
        data = [
            ['Symbol', 'Name', 'Price', 'Market Cap', 'P/E', 'EPS', 'ROE', 'Sector'],
            [ticker.replace(".NS", ""), info.get("longName", ""), info.get("currentPrice", ""),
             info.get("marketCap", ""), info.get("trailingPE", ""), info.get("trailingEps", ""),
             info.get("returnOnEquity", ""), info.get("sector", "")]
        ]

        # Create CSV file in memory or temporary location
        file_path = '/tmp/stock_fundamentals.csv'
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

        # Send the file as a download
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
