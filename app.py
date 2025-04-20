from flask import Flask, send_file, jsonify
import yfinance as yf
import csv
from io import BytesIO
import time
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.ERROR)

tickers_string = """360ONE.NS	   
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
AFFLE.NS	   
AJANTPHARM.NS	   
AKUMS.NS	   
APLLTD.NS	   
ALKEM.NS	   
ALKYLAMINE.NS	   
ALOKINDS.NS	   
ARE&M.NS	   
AMBER.NS	   
AMBUJACEM.NS	   
ANANDRATHI.NS	   
ANANTRAJ.NS	   
ANGELONE.NS	   
APARINDS.NS	   
APOLLOHOSP.NS	   
APOLLOTYRE.NS	   
APTUS.NS	   
ACI.NS	   
ASAHIINDIA.NS	   
ASHOKLEY.NS	   
ASIANPAINT.NS	   
ASTERDM.NS	   
ASTRAZEN.NS	   
ASTRAL.NS	   
ATUL.NS	   
AUROPHARMA.NS	   
AVANTIFEED.NS	   
DMART.NS	   
AXISBANK.NS	   
BASF.NS	   
BEML.NS	   
BLS.NS	   
BSE.NS	   
BAJAJ-AUTO.NS	   
BAJFINANCE.NS	   
BAJAJFINSV.NS	   
BAJAJHLDNG.NS	   
BALAMINES.NS	   
BALKRISIND.NS	   
BALRAMCHIN.NS	   
BANDHANBNK.NS	   
BANKBARODA.NS	   
BANKINDIA.NS	   
MAHABANK.NS	   
BATAINDIA.NS	   
BAYERCROP.NS	   
BERGEPAINT.NS	   
BDL.NS	   
BEL.NS	   
BHARATFORG.NS	   
BHEL.NS	   
BPCL.NS	   
BHARTIARTL.NS	   
BHARTIHEXA.NS	   
BIKAJI.NS	   
BIOCON.NS	   
BIRLACORPN.NS	   
BSOFT.NS	   
BLUEDART.NS	   
BLUESTARCO.NS	   
BBTC.NS	   
BOSCHLTD.NS	   
BRIGADE.NS	   
BRITANNIA.NS	   
MAPMYINDIA.NS	   
CCL.NS	   
CESC.NS	   
CGPOWER.NS	   
CIEINDIA.NS	   
CRISIL.NS	   
CAMPUS.NS	   
CANFINHOME.NS	   
CANBK.NS	   
CAPLIPOINT.NS	   
CGCL.NS	   
CARBORUNIV.NS	   
CASTROLIND.NS	   
CEATLTD.NS	   
CELLO.NS	   
CENTRALBK.NS	   
CDSL.NS	   
CENTURYPLY.NS	   
CERA.NS	   
CHALET.NS	   
CHAMBLFERT.NS	   
CHEMPLASTS.NS	   
CHENNPETRO.NS	   
CHOLAHLDNG.NS	   
CHOLAFIN.NS	   
CIPLA.NS	   
CUB.NS	   
CLEAN.NS	   
COALINDIA.NS	   
COCHINSHIP.NS	   
COFORGE.NS	   
COLPAL.NS	   
CAMS.NS	   
CONCORDBIO.NS	   
CONCOR.NS	   
COROMANDEL.NS	   
CRAFTSMAN.NS	   
CREDITACC.NS	   
CROMPTON.NS	   
CUMMINSIND.NS	   
CYIENT.NS	   
DLF.NS	   
DOMS.NS	   
DABUR.NS	   
DALBHARAT.NS	   
DATAPATTNS.NS	   
DEEPAKFERT.NS	   
DEEPAKNTR.NS	   
DELHIVERY.NS	   
DEVYANI.NS	   
DIVISLAB.NS	   
DIXON.NS	   
LALPATHLAB.NS	   
DRREDDY.NS	   
EIDPARRY.NS	   
EIHOTEL.NS	   
EASEMYTRIP.NS	   
EICHERMOT.NS	   
ELECON.NS	   
ELGIEQUIP.NS	   
EMAMILTD.NS	   
EMCURE.NS	   
ENDURANCE.NS	   
ENGINERSIN.NS	   
EQUITASBNK.NS	   
ERIS.NS	   
ESCORTS.NS	   
EXIDEIND.NS	   
NYKAA.NS	   
FEDERALBNK.NS	   
FACT.NS	   
FINEORG.NS	   
FINCABLES.NS	   
FINPIPE.NS	   
FSL.NS	   
FIVESTAR.NS	   
FORTIS.NS	   
GRINFRA.NS	   
GAIL.NS	   
GVT&D.NS	   
GMRAIRPORT.NS	   
GRSE.NS	   
GICRE.NS	   
GILLETTE.NS	   
GLAND.NS	   
GLAXO.NS	   
GLENMARK.NS	   
MEDANTA.NS	   
GODIGIT.NS	   
GPIL.NS	   
GODFRYPHLP.NS	   
GODREJAGRO.NS	   
GODREJCP.NS	   
GODREJIND.NS	   
GODREJPROP.NS	   
GRANULES.NS	   
GRAPHITE.NS	   
GRASIM.NS	   
GESHIP.NS	   
GRINDWELL.NS	   
GAEL.NS	   
FLUOROCHEM.NS	   
GUJGASLTD.NS	   
GMDCLTD.NS	   
GNFC.NS	   
GPPL.NS	   
GSFC.NS	   
GSPL.NS	   
HEG.NS	   
HBLENGINE.NS	   
HCLTECH.NS	   
HDFCAMC.NS	   
HDFCBANK.NS	   
HDFCLIFE.NS	   
HFCL.NS	   
HAPPSTMNDS.NS	   
HAVELLS.NS	   
HEROMOTOCO.NS	   
HSCL.NS	   
HINDALCO.NS	   
HAL.NS	   
HINDCOPPER.NS	   
HINDPETRO.NS	   
HINDUNILVR.NS	   
HINDZINC.NS	   
POWERINDIA.NS	   
HOMEFIRST.NS	   
HONASA.NS	   
HONAUT.NS	   
HUDCO.NS	   
ICICIBANK.NS	   
ICICIGI.NS	   
ICICIPRULI.NS	   
ISEC.NS	   
IDBI.NS	   
IDFCFIRSTB.NS	   
"""  # sample subset
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
