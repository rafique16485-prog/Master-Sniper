"""Master Sniper PRO Streamlit application.

A simple market-scanner dashboard for educational analysis of NSE symbols.
It uses Yahoo Finance data through yfinance and calculates rule-based signals
for breakout, volume, EMA, and VWAP conditions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd
import streamlit as st
import yfinance as yf


DEFAULT_SYMBOLS = [
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "INFY.NS",
    "SBIN.NS",
    "RVNL.NS",
    "POLYCAB.NS",
    "BHEL.NS",
    "TRENT.NS",
    "PFC.NS",
    "RECLTD.NS",
    "HAL.NS",
    "SUZLON.NS",
    "IREDA.NS",
    "IRFC.NS",
    "ZOMATO.NS",
    "INDIGO.NS",
    "DLF.NS",
    "BSE.NS",
    "CDSL.NS",
    "MAZDOCK.NS",
    "BEL.NS",
    "SJVN.NS",
    "NHPC.NS",
]

INDEX_SYMBOLS = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
}


@dataclass(frozen=True)
class BreakoutSignal:
    """Container for a stock breakout scan result."""

    symbol: str
    price: float
    previous_20_day_high: float
    volume_ratio: float


@st.cache_data(ttl=300, show_spinner=False)
def download_history(symbol: str, period: str = "60d", interval: str = "1d") -> pd.DataFrame:
    """Download historical OHLCV data for a symbol."""

    data = yf.download(
        symbol,
        period=period,
        interval=interval,
        progress=False,
        auto_adjust=False,
        threads=False,
    )
    if data.empty:
        return data

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return data.dropna(how="all")


def parse_symbols(raw_symbols: str) -> list[str]:
    """Parse comma/newline separated symbols, preserving user order."""

    symbols = [item.strip().upper() for item in raw_symbols.replace("\n", ",").split(",")]
    return [symbol for symbol in symbols if symbol]


def find_breakout_signal(symbol: str, data: pd.DataFrame) -> BreakoutSignal | None:
    """Return a signal when price breaks the prior 20-day high on strong volume."""

    if len(data) < 25 or not {"Close", "Volume"}.issubset(data.columns):
        return None

    close = data["Close"].astype(float)
    volume = data["Volume"].astype(float)
    previous_high = close.rolling(20).max().shift(1).iloc[-1]
    average_volume = volume.rolling(20).mean().iloc[-1]
    latest_close = close.iloc[-1]
    latest_volume = volume.iloc[-1]

    if pd.isna(previous_high) or pd.isna(average_volume) or average_volume <= 0:
        return None

    is_breakout = latest_close > previous_high
    has_institutional_volume = latest_volume > 1.5 * average_volume

    if not (is_breakout and has_institutional_volume):
        return None

    return BreakoutSignal(
        symbol=symbol.replace(".NS", ""),
        price=round(float(latest_close), 2),
        previous_20_day_high=round(float(previous_high), 2),
        volume_ratio=round(float(latest_volume / average_volume), 2),
    )


def scan_breakouts(symbols: Iterable[str]) -> tuple[list[BreakoutSignal], list[str]]:
    """Scan symbols and return matching signals plus symbols that failed to load."""

    signals: list[BreakoutSignal] = []
    failed_symbols: list[str] = []

    for symbol in symbols:
        try:
            data = download_history(symbol)
            signal = find_breakout_signal(symbol, data)
            if signal:
                signals.append(signal)
        except (KeyError, ValueError, OSError, yf.exceptions.YFException):
            failed_symbols.append(symbol)

    return signals, failed_symbols


def build_index_snapshot(symbol: str, label: str) -> dict[str, str | float]:
    """Build a compact index momentum snapshot using 9-EMA and VWAP."""

    data = download_history(symbol, period="5d", interval="15m")
    if len(data) < 10:
        raise ValueError(f"Not enough data returned for {label}")

    typical_price = (data["High"] + data["Low"] + data["Close"]) / 3
    cumulative_volume = data["Volume"].replace(0, pd.NA).cumsum()
    vwap = (typical_price * data["Volume"]).cumsum() / cumulative_volume
    ema_9 = data["Close"].ewm(span=9, adjust=False).mean()

    last_close = float(data["Close"].iloc[-1])
    last_ema = float(ema_9.iloc[-1])
    last_vwap = float(vwap.iloc[-1])
    trend = "Bullish" if last_close > last_ema and last_close > last_vwap else "Neutral/Bearish"

    return {
        "Index": label,
        "Last Price": round(last_close, 2),
        "9 EMA": round(last_ema, 2),
        "VWAP": round(last_vwap, 2),
        "Signal": trend,
    }


def render_breakout_tab() -> None:
    """Render the swing-breakout scanner tab."""

    st.header("🔥 20-Day Breakout + Institutional Volume")
    st.write(
        "Scans selected NSE symbols for a close above the previous 20-day high with "
        "volume greater than 1.5× the 20-day average."
    )

    raw_symbols = st.text_area(
        "Symbols to scan",
        value=", ".join(DEFAULT_SYMBOLS),
        help="Use Yahoo Finance symbols, separated by commas or new lines.",
        height=120,
    )

    if st.button("🚀 Scan Institutional Setup", type="primary"):
        symbols = parse_symbols(raw_symbols)
        if not symbols:
            st.error("Please enter at least one symbol.")
            return

        with st.spinner(f"Scanning {len(symbols)} symbols..."):
            signals, failed_symbols = scan_breakouts(symbols)

        if signals:
            st.success(f"🔥 {len(signals)} breakout setup(s) found.")
            st.dataframe(pd.DataFrame([signal.__dict__ for signal in signals]), use_container_width=True)
        else:
            st.warning("No symbols currently match the breakout rules. Capital safe! 🛡️")

        if failed_symbols:
            st.info("Could not load data for: " + ", ".join(failed_symbols))


def render_momentum_tab() -> None:
    """Render the index momentum tab."""

    st.header("⚡ 9-EMA + VWAP Sniper (Index)")
    st.write("Fetches 15-minute index data and compares last price with 9-EMA and VWAP.")

    if st.button("🔍 Fetch Live Index Data", type="primary"):
        snapshots = []
        errors = []
        with st.spinner("Fetching index data..."):
            for label, symbol in INDEX_SYMBOLS.items():
                try:
                    snapshots.append(build_index_snapshot(symbol, label))
                except (KeyError, ValueError, OSError, yf.exceptions.YFException) as exc:
                    errors.append(f"{label}: {exc}")

        if snapshots:
            st.dataframe(pd.DataFrame(snapshots), use_container_width=True)
        if errors:
            st.warning("Some index data could not be loaded: " + " | ".join(errors))


def main() -> None:
    """Run the Streamlit app."""

    st.set_page_config(page_title="Master Sniper PRO", page_icon="🎯", layout="centered")
    st.title("🎯 Master Sniper PRO")
    st.markdown("**Tracking: Smart Money Flows | 9-EMA Crossover | VWAP**")
    st.caption("Educational market scanner. Not financial advice.")

    tab1, tab2 = st.tabs(["🚀 Swing Breakout", "⚡ Live Momentum"])
    with tab1:
        render_breakout_tab()
    with tab2:
        render_momentum_tab()

    st.markdown("---")
    st.caption("Developed for Mechanical Trading | No Emotion, Only Rules 🤖")


if __name__ == "__main__":
    main()
