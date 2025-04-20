import logging
import yfinance as yf
from flask import Flask, jsonify, send_file
import csv
from io import StringIO

app = Flask(__name__)

# Stock tickers as a space-separated string
tickers_string = """
MANAPPURAM.NS      
MRPL.NS      
MANKIND.NS      
MARICO.NS      
MARUTI.NS      
MASTEK.NS      
MFSL.NS      
MAXHEALTH.NS      
MAZDOCK.NS      
METROBRAND.NS      
METROPOLIS.NS      
MINDACORP.NS      
MSUMI.NS      
MOTILALOFS.NS      
MPHASIS.NS      
MCX.NS      
MUTHOOTFIN.NS      
NATCOPHARM.NS      
NBCC.NS      
NCC.NS      
NHPC.NS      
NLCINDIA.NS      
NMDC.NS      
NSLNISP.NS      
NTPC.NS      
NH.NS      
NATIONALUM.NS      
NAVINFLUOR.NS      
NESTLEIND.NS      
NETWEB.NS      
NETWORK18.NS      
NEWGEN.NS      
NAM-INDIA.NS      
NUVAMA.NS      
NUVOCO.NS      
OBEROIRLTY.NS      
ONGC.NS      
OIL.NS      
OLECTRA.NS      
PAYTM.NS      
OFSS.NS      
POLICYBZR.NS      
PCBL.NS      
PIIND.NS      
PNBHOUSING.NS      
PNCINFRA.NS      
PTCIL.NS      
PVRINOX.NS      
PAGEIND.NS      
PATANJALI.NS      
PERSISTENT.NS      
PETRONET.NS      
PFIZER.NS      
PHOENIXLTD.NS      
PIDILITIND.NS      
PEL.NS      
PPLPHARMA.NS      
POLYMED.NS      

"""

# Split the string into a list of tickers
stock_list = tickers_string.split()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Function to fetch data for a single stock
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return [
            ticker.replace(".NS", ""),  # Clean up NSE ticker symbols
            info.get("longName", "N/A"),
            info.get("currentPrice", "N/A"),
            info.get("marketCap", "N/A"),
            info.get("trailingPE", "N/A"),
            info.get("trailingEps", "N/A"),
            info.get("returnOnEquity", "N/A"),
            info.get("sector", "N/A")
        ]
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {e}")
        return [ticker, "Error", str(e)]

# Route to generate and download CSV for all stocks
@app.route('/download_csv')
def download_csv():
    try:
        # Prepare the data for all stocks
        data = [['Symbol', 'Name', 'Price', 'Market Cap', 'P/E', 'EPS', 'ROE', 'Sector']]  # CSV header
        
        for ticker in stock_list:
            stock_data = get_stock_data(ticker)
            data.append(stock_data)

        # Create in-memory CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerows(data)

        # Seek to the beginning of the StringIO buffer
        output.seek(0)

        # Send the CSV file for download
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name='stock_data.csv')

    except Exception as e:
        logging.error(f"Error generating CSV: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
