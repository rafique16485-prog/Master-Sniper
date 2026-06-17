# Master Sniper PRO

Master Sniper PRO is a Streamlit market-scanner dashboard for educational, rule-based analysis of NSE stocks and Indian indices.

> **Disclaimer:** This project is for learning and market research only. It is not financial advice. Always validate data and signals independently before making trading decisions.

## Features

- **Swing Breakout Scanner**
  - Scans configurable Yahoo Finance symbols.
  - Looks for closes above the previous 20-day high.
  - Requires current volume to be greater than 1.5× the 20-day average volume.
- **Index Momentum Dashboard**
  - Fetches 15-minute NIFTY 50 and BANK NIFTY data.
  - Calculates 9-EMA and VWAP.
  - Shows a simple bullish vs neutral/bearish trend label.
- **Configurable Symbol Input**
  - Edit the symbol list directly in the app using comma-separated or newline-separated Yahoo Finance tickers.
- **Caching**
  - Uses Streamlit caching with a five-minute TTL to reduce repeated market-data requests.

## Requirements

- Python 3.10 or newer
- Internet access for Yahoo Finance data

## Run Locally

1. Clone or open this repository.

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:

   On macOS/Linux:

   ```bash
   source .venv/bin/activate
   ```

   On Windows PowerShell:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the app:

   ```bash
   streamlit run app.py
   ```

6. Open the local URL shown by Streamlit, usually <http://localhost:8501>.

## How to Use

1. Open the **Swing Breakout** tab.
2. Review or edit the Yahoo Finance symbols in the text box.
3. Click **Scan Institutional Setup**.
4. Open the **Live Momentum** tab.
5. Click **Fetch Live Index Data** to load index EMA/VWAP snapshots.

## Project Structure

```text
.
├── app.py            # Streamlit application and scanner logic
├── requirements.txt  # Python dependencies
└── README.md         # Setup and usage guide
```

## Notes

- Symbols must be valid Yahoo Finance tickers. NSE equities generally use the `.NS` suffix.
- Market data availability, delay, and quality depend on Yahoo Finance and `yfinance`.
- If a symbol fails to load, the app continues scanning the remaining symbols and reports the failed tickers.
