from flask import Flask, send_file, jsonify
import yfinance as yf
import csv
from io import BytesIO
import time
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.ERROR)

tickers_string = """ABREL.NS USHAMART.NS VGUARD.NS VIPIND.NS DBREALTY.NS VTL.NS ECLERX.NS"""  # sample subset
stock_list = tickers_string.split()

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return [
            ticker.replace(".NS", ""),
            info.get("longName", ""),
            info.get("currentPrice", ""),
            info.get("marketCap", ""),
            info.get("trailingPE", ""),
            info.get("trailingEps", ""),
            info.get("returnOnEquity", ""),
            info.get("sector", "")
        ]
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {e}")
        return [ticker.replace(".NS", ""), "Error", "", "", "", "", "", ""]

@app.route('/download_csv')
def download_csv():
    try:
        buffer = BytesIO()
        writer = csv.writer(buffer := BytesIO())
        header = ['Symbol', 'Name', 'Price', 'Market Cap', 'P/E', 'EPS', 'ROE', 'Sector']
        rows = [header]

        for i, ticker in enumerate(stock_list):
            rows.append(get_stock_data(ticker))
            time.sleep(1.5)  # Slow down to avoid Yahoo rate-limiting

        # Write CSV as text and encode to bytes
        text_buffer = "\n".join([",".join(map(str, row)) for row in rows])
        buffer.write(text_buffer.encode('utf-8'))
        buffer.seek(0)

        return send_file(buffer, mimetype='text/csv', download_name='stocks_fundamentals.csv', as_attachment=True)

    except Exception as e:
        logging.error(f"Error generating CSV: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "Welcome to the Stock Fundamentals API!"

if __name__ == '__main__':
    app.run(debug=True)
