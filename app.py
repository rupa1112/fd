from flask import Flask, jsonify, send_file
import yfinance as yf
import csv

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
POLYCAB.NS	   
POONAWALLA.NS	   
PFC.NS	   
POWERGRID.NS	   
PRAJIND.NS	   
PRESTIGE.NS	   
PGHH.NS	   
PNB.NS	   
QUESS.NS	   
RRKABEL.NS	   
RBLBANK.NS	   
RECLTD.NS	   
RHIM.NS	   
RITES.NS	   
RADICO.NS	   
RVNL.NS	   
RAILTEL.NS	   
RAINBOW.NS	   
RAJESHEXPO.NS	   
RKFORGE.NS	   
RCF.NS	   
RATNAMANI.NS	   
RTNINDIA.NS	   
RAYMOND.NS	   
REDINGTON.NS	   
RELIANCE.NS	   
ROUTE.NS	   
SBFC.NS	   
SBICARD.NS	   
SBILIFE.NS	   
SJVN.NS	   
SKFINDIA.NS	   
SRF.NS	   
SAMMAANCAP.NS	   
MOTHERSON.NS	   
SANOFI.NS	   
SAPPHIRE.NS	   
SAREGAMA.NS	   
SCHAEFFLER.NS	   
SCHNEIDER.NS	   
SCI.NS	   
SHREECEM.NS	   
RENUKA.NS	   
SHRIRAMFIN.NS	   
SHYAMMETL.NS	   
SIEMENS.NS	   
SIGNATURE.NS	   
SOBHA.NS	   
SOLARINDS.NS	   
SONACOMS.NS	   
SONATSOFTW.NS	   
STARHEALTH.NS	   
SBIN.NS	   
SAIL.NS	   
SWSOLAR.NS	   
SUMICHEM.NS	   
SPARC.NS	   
SUNPHARMA.NS	   
SUNTV.NS	   
SUNDARMFIN.NS	   
SUNDRMFAST.NS	   
SUPREMEIND.NS	   
SUVENPHAR.NS	   
SUZLON.NS	   
SWANENERGY.NS	   
SYNGENE.NS	   
SYRMA.NS	   
TBOTEK.NS	   
TVSMOTOR.NS	   
TVSSCS.NS	   
TANLA.NS	   
TATACHEM.NS	   
TATACOMM.NS	   
TCS.NS	   
TATACONSUM.NS	   
TATAELXSI.NS	   
TATAINVEST.NS	   
TATAMOTORS.NS	   
TATAPOWER.NS	   
TATASTEEL.NS	   
TATATECH.NS	   
TTML.NS	   
TECHM.NS	   
TECHNOE.NS	   
TEJASNET.NS	   
NIACL.NS	   
RAMCOCEM.NS	   
THERMAX.NS	   
TIMKEN.NS	   
TITAGARH.NS	   
TITAN.NS	   
TORNTPHARM.NS	   
TORNTPOWER.NS	   
TRENT.NS	   
TRIDENT.NS	   
TRIVENI.NS	   
TRITURBINE.NS	   
TIINDIA.NS	   
UCOBANK.NS	   
UNOMINDA.NS	   
UPL.NS	   
UTIAMC.NS	   
UJJIVANSFB.NS	   
ULTRACEMCO.NS	   
UNIONBANK.NS	   
UBL.NS	   
UNITDSPR.NS	   
USHAMART.NS	   
VGUARD.NS	   
VIPIND.NS	   
DBREALTY.NS	   
VTL.NS	   
ECLERX.NS	   
	 

"""

# Split the string into a list of tickers
stock_list = tickers_string.split()

# Function to fetch data for a single stock
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
        return [ticker, str(e)]  # In case of error, return the error message instead

# Route to generate and download CSV for all stocks
@app.route('/download_csv')
def download_csv():
    try:
        # Prepare the data for all stocks
        data = [['Symbol', 'Name', 'Price', 'Market Cap', 'P/E', 'EPS', 'ROE', 'Sector']]  # CSV header
        
        for ticker in stock_list:
            stock_data = get_stock_data(ticker)
            data.append(stock_data)

        # Create CSV file in memory or temporary location
        file_path = '/tmp/stocks_fundamentals.csv'
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

        # Send the file as a download
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
