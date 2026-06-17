# Master Sniper PRO V2

Master Sniper PRO V2 is a dark-theme Streamlit market-scanner dashboard for educational, rule-based analysis of NSE stocks and Indian indices. Version 2 adds dedicated live dashboards for NIFTY and BANKNIFTY with trend, momentum, volume, liquidity, and market-structure scoring.

> **Disclaimer:** This project is for learning and market research only. It is not financial advice. Always validate data and signals independently before making trading decisions.

## Version 2 Features

- **NIFTY Live Dashboard**
  - Fetches Yahoo Finance data for `^NSEI`.
  - Displays Last Price, EMA20, EMA50, VWAP, and RSI(14).
  - Produces Bullish Score, Bearish Score, CALL %, PUT %, SIDEWAYS %, and a final CALL / PUT / WAIT verdict.
- **BANKNIFTY Live Dashboard**
  - Fetches Yahoo Finance data for `^NSEBANK`.
  - Uses the same Version 2 scoring engine as NIFTY.
- **Technical Indicator Engine**
  - EMA20 trend filter.
  - EMA50 trend filter.
  - VWAP intraday value filter.
  - RSI(14) momentum filter.
  - Volume Spike detection using latest volume versus 1.5× the 20-candle average.
- **Smart Money / Market Structure Signals**
  - Liquidity Sweep detection for latest-candle high/low sweeps and reclaim/rejection behaviour.
  - BOS (Break of Structure) detection against recent swing ranges.
  - CHOCH (Change of Character) detection using EMA20 bias changes.
- **Probability Output**
  - Bullish Score and Bearish Score out of 9 rules.
  - CALL %, PUT %, and SIDEWAYS %.
  - Final Verdict: `CALL`, `PUT`, or `WAIT`.
- **Mobile-Friendly Dark UI**
  - Wide desktop layout with responsive cards.
  - Mobile CSS refinements for smaller screens.
  - Dark card styling for metrics, scores, and final verdicts.
- **Swing Breakout Scanner**
  - Keeps the original configurable Yahoo Finance stock scanner.
  - Looks for closes above the previous 20-day high.
  - Requires current volume to be greater than 1.5× the 20-day average volume.
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

1. Open the **Live Index Dashboards** tab.
2. Select the data period and candle interval.
3. Click **Fetch V2 Live Dashboards**.
4. Review each NIFTY and BANKNIFTY dashboard:
   - EMA20, EMA50, VWAP, RSI(14)
   - Volume Spike
   - Liquidity Sweep
   - BOS
   - CHOCH
   - Bullish Score / Bearish Score
   - CALL %, PUT %, SIDEWAYS %
   - Final Verdict: CALL / PUT / WAIT
5. Open the **Swing Breakout** tab to scan selected NSE equity symbols for 20-day breakout setups.

## Scoring Rules

Each live index dashboard evaluates nine bullish and nine bearish conditions:

| Component | Bullish Rule | Bearish Rule |
| --- | --- | --- |
| EMA20 | Price above EMA20 | Price below EMA20 |
| EMA50 | Price above EMA50 | Price below EMA50 |
| EMA Trend | EMA20 above EMA50 | EMA20 below EMA50 |
| VWAP | Price above VWAP | Price below VWAP |
| RSI(14) | RSI at or above 55 | RSI at or below 45 |
| Volume Spike | Spike on green candle | Spike on red candle |
| Liquidity Sweep | Low sweep with reclaim | High sweep with rejection |
| BOS | Close breaks recent swing high | Close breaks recent swing low |
| CHOCH | Bias flips bullish | Bias flips bearish |

The app converts these scores into CALL %, PUT %, and SIDEWAYS %. It returns `CALL` or `PUT` only when directional probability is at least 60% and the directional score leads by at least two points; otherwise it returns `WAIT`.

## Project Structure

```text
.
├── app.py            # Streamlit application, indicator engine, and dashboards
├── requirements.txt  # Python dependencies
└── README.md         # Setup, usage, and scoring guide
```

## Notes

- Symbols must be valid Yahoo Finance tickers. NSE equities generally use the `.NS` suffix.
- Live market data availability, delay, and quality depend on Yahoo Finance and `yfinance`.
- Intraday Yahoo Finance availability can vary by interval and market session.
- If a symbol or index fails to load, the app continues processing the remaining dashboards or symbols and reports the failed item.
