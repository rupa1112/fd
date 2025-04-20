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

        price = info.get("currentPrice", 0)
        market_cap = info.get("marketCap", 0)
        trailing_pe = info.get("trailingPE", 0)
        eps = info.get("trailingEps", 0)
        roe = info.get("returnOnEquity", 0)
        sector = info.get("sector", "")

        # Format market cap in Indian Crores
        market_cap_crore = round(market_cap / 1e7, 2)  # 1 crore = 10^7

        return [
            ticker.replace(".NS", ""),
            info.get("longName", ""),
            round(price, 2),
            f"{market_cap_crore} Cr",  # Example: 1256.78 Cr
            round(trailing_pe, 2) if trailing_pe else "—",
            round(eps, 2) if eps else "—",
            f"{round(roe * 100, 2)}%" if roe else "—",
            sector
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
