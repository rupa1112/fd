from flask import Flask, jsonify, send_file
import yfinance as yf
import csv
from io import BytesIO
import time
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Ticker list
tickers_string = """  
360ONE.NS	   
3MINDIA.NS	   
ABB.NS	   
ACC.NS	   
AIAENG.NS	   
APLAPOLLO.NS	   
AUBANK.NS	   
AADHARHFC.NS	   
AARTIIND.NS	   
AAVAS.NS	   
ABBOTINDIA.NS	   
ACE.NS	   
ADANIENSOL.NS	   
ADANIENT.NS	   
ADANIGREEN.NS	   
ADANIPORTS.NS	   
ADANIPOWER.NS	   
ATGL.NS	   
AWL.NS	   
ABCAPITAL.NS	   
ABFRL.NS	   
ABREL.NS	   
ABSLAMC.NS	   
AEGISLOG.NS	   
 """
stock_list = tickers_string.split()

# Function to fetch single stock data
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
        return [ticker.replace(".NS", ""), "ERROR", "", "", "", "", "", ""]

# Route to download CSV
@app.route('/download_csv')
def download_csv():
    try:
        data = [['Symbol', 'Name', 'Price', 'Market Cap', 'P/E', 'EPS', 'ROE', 'Sector']]
        
        for i, ticker in enumerate(stock_list):
            stock_data = get_stock_data(ticker)
            data.append(stock_data)
            time.sleep(0.5)  # Sleep to reduce rate-limiting risk

        # Save to BytesIO instead of a file
        output = BytesIO()
        writer = csv.writer(output)
        writer.writerows(data)
        output.seek(0)

        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='stocks_fundamentals.csv'
        )

    except Exception as e:
        logging.error(f"Error generating CSV: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
