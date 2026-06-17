"""Master Sniper PRO Version 2 Streamlit application.

An educational live NSE index dashboard and stock scanner that combines
trend, momentum, volume, liquidity, and market-structure conditions into
rule-based CALL/PUT/WAIT probabilities.
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
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
}

INDEX_DESCRIPTIONS = {
    "NIFTY": "NIFTY 50 live dashboard for broader market direction.",
    "BANKNIFTY": "BANKNIFTY live dashboard for banking index momentum.",
}


@dataclass(frozen=True)
class BreakoutSignal:
    """Container for a stock breakout scan result."""

    symbol: str
    price: float
    previous_20_day_high: float
    volume_ratio: float


@dataclass(frozen=True)
class IndexDashboard:
    """Container for a Version 2 index dashboard result."""

    index: str
    last_price: float
    ema20: float
    ema50: float
    vwap: float
    rsi14: float
    volume_spike: bool
    liquidity_sweep: str
    bos: str
    choch: str
    bullish_score: int
    bearish_score: int
    call_percent: int
    put_percent: int
    sideways_percent: int
    final_verdict: str


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


def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate RSI using exponentially smoothed gains and losses."""

    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    average_gain = gains.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    average_loss = losses.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = average_gain / average_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.mask((average_loss == 0) & (average_gain > 0), 100)
    rsi = rsi.mask((average_loss == 0) & (average_gain == 0), 50)
    return rsi


def calculate_vwap(data: pd.DataFrame) -> pd.Series:
    """Calculate rolling-session VWAP from OHLCV data."""

    typical_price = (data["High"] + data["Low"] + data["Close"]) / 3
    volume = data["Volume"].astype(float)
    cumulative_volume = volume.replace(0, pd.NA).cumsum()
    return (typical_price * volume).cumsum() / cumulative_volume


def detect_liquidity_sweep(data: pd.DataFrame) -> str:
    """Detect simple latest-candle stop sweep and reclaim/rejection behaviour."""

    if len(data) < 12:
        return "None"

    latest = data.iloc[-1]
    previous = data.iloc[-11:-1]
    previous_high = float(previous["High"].max())
    previous_low = float(previous["Low"].min())

    swept_low_reclaimed = latest["Low"] < previous_low and latest["Close"] > previous_low
    swept_high_rejected = latest["High"] > previous_high and latest["Close"] < previous_high

    if swept_low_reclaimed:
        return "Bullish Sweep"
    if swept_high_rejected:
        return "Bearish Sweep"
    return "None"


def detect_market_structure(data: pd.DataFrame) -> tuple[str, str]:
    """Detect basic break of structure and change of character signals."""

    if len(data) < 24:
        return "None", "None"

    close = data["Close"].astype(float)
    recent_high = float(data["High"].iloc[-12:-2].max())
    recent_low = float(data["Low"].iloc[-12:-2].min())
    previous_close = float(close.iloc[-2])
    latest_close = float(close.iloc[-1])
    ema20 = close.ewm(span=20, adjust=False).mean()

    bos = "None"
    if latest_close > recent_high:
        bos = "Bullish BOS"
    elif latest_close < recent_low:
        bos = "Bearish BOS"

    previous_bias = "Bullish" if previous_close >= float(ema20.iloc[-2]) else "Bearish"
    current_bias = "Bullish" if latest_close >= float(ema20.iloc[-1]) else "Bearish"
    choch = "None" if previous_bias == current_bias else f"{current_bias} CHOCH"

    return bos, choch


def score_index_setup(data: pd.DataFrame, label: str) -> IndexDashboard:
    """Calculate Version 2 dashboard metrics and verdict for an index."""

    if len(data) < 55:
        raise ValueError(f"Not enough data returned for {label}")

    close = data["Close"].astype(float)
    volume = data["Volume"].astype(float)
    ema20 = close.ewm(span=20, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    vwap = calculate_vwap(data)
    rsi14 = calculate_rsi(close, 14)
    average_volume = volume.rolling(20).mean()

    latest_close = float(close.iloc[-1])
    latest_ema20 = float(ema20.iloc[-1])
    latest_ema50 = float(ema50.iloc[-1])
    latest_vwap = float(vwap.iloc[-1])
    latest_rsi = float(rsi14.iloc[-1]) if pd.notna(rsi14.iloc[-1]) else 50.0
    has_volume_spike = bool(volume.iloc[-1] > 1.5 * average_volume.iloc[-1]) if average_volume.iloc[-1] > 0 else False
    liquidity_sweep = detect_liquidity_sweep(data)
    bos, choch = detect_market_structure(data)

    bullish_score = 0
    bearish_score = 0

    bullish_score += int(latest_close > latest_ema20)
    bullish_score += int(latest_close > latest_ema50)
    bullish_score += int(latest_ema20 > latest_ema50)
    bullish_score += int(latest_close > latest_vwap)
    bullish_score += int(latest_rsi >= 55)
    bullish_score += int(has_volume_spike and close.iloc[-1] > close.iloc[-2])
    bullish_score += int(liquidity_sweep == "Bullish Sweep")
    bullish_score += int(bos == "Bullish BOS")
    bullish_score += int(choch == "Bullish CHOCH")

    bearish_score += int(latest_close < latest_ema20)
    bearish_score += int(latest_close < latest_ema50)
    bearish_score += int(latest_ema20 < latest_ema50)
    bearish_score += int(latest_close < latest_vwap)
    bearish_score += int(latest_rsi <= 45)
    bearish_score += int(has_volume_spike and close.iloc[-1] < close.iloc[-2])
    bearish_score += int(liquidity_sweep == "Bearish Sweep")
    bearish_score += int(bos == "Bearish BOS")
    bearish_score += int(choch == "Bearish CHOCH")

    total_score = bullish_score + bearish_score
    if total_score == 0:
        call_percent = put_percent = 0
        sideways_percent = 100
    else:
        call_percent = round((bullish_score / 9) * 100)
        put_percent = round((bearish_score / 9) * 100)
        sideways_percent = max(0, 100 - max(call_percent, put_percent))

    if call_percent >= 60 and bullish_score >= bearish_score + 2:
        final_verdict = "CALL"
    elif put_percent >= 60 and bearish_score >= bullish_score + 2:
        final_verdict = "PUT"
    else:
        final_verdict = "WAIT"

    return IndexDashboard(
        index=label,
        last_price=round(latest_close, 2),
        ema20=round(latest_ema20, 2),
        ema50=round(latest_ema50, 2),
        vwap=round(latest_vwap, 2),
        rsi14=round(latest_rsi, 2),
        volume_spike=has_volume_spike,
        liquidity_sweep=liquidity_sweep,
        bos=bos,
        choch=choch,
        bullish_score=bullish_score,
        bearish_score=bearish_score,
        call_percent=call_percent,
        put_percent=put_percent,
        sideways_percent=sideways_percent,
        final_verdict=final_verdict,
    )


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

    if not (latest_close > previous_high and latest_volume > 1.5 * average_volume):
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
            signal = find_breakout_signal(symbol, download_history(symbol))
            if signal:
                signals.append(signal)
        except (KeyError, ValueError, OSError, yf.exceptions.YFException):
            failed_symbols.append(symbol)

    return signals, failed_symbols


def build_index_dashboard(symbol: str, label: str, period: str = "5d", interval: str = "15m") -> IndexDashboard:
    """Build a live Version 2 index dashboard from Yahoo Finance data."""

    return score_index_setup(download_history(symbol, period=period, interval=interval), label)


def apply_dark_theme() -> None:
    """Apply mobile-friendly dark styling for Streamlit components."""

    st.markdown(
        """
        <style>
        .stApp { background: #070b12; color: #e5eefb; }
        [data-testid="stHeader"] { background: rgba(7, 11, 18, 0.85); }
        .block-container { max-width: 1180px; padding: 1.25rem 1rem 2rem; }
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #101827 0%, #0b1220 100%);
            border: 1px solid #1f2a44;
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        }
        .sniper-card {
            background: #0f172a;
            border: 1px solid #263552;
            border-radius: 20px;
            padding: 1rem;
            margin: 0.75rem 0;
        }
        .verdict {
            border-radius: 999px;
            display: inline-block;
            font-size: 1.4rem;
            font-weight: 800;
            letter-spacing: 0.08rem;
            padding: 0.45rem 1rem;
        }
        .call { background: #064e3b; color: #a7f3d0; }
        .put { background: #7f1d1d; color: #fecaca; }
        .wait { background: #3b2f0a; color: #fde68a; }
        @media (max-width: 640px) {
            .block-container { padding: 0.8rem 0.65rem 1.5rem; }
            h1 { font-size: 1.8rem !important; }
            h2, h3 { font-size: 1.25rem !important; }
            .verdict { font-size: 1.1rem; width: 100%; text-align: center; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard_card(dashboard: IndexDashboard) -> None:
    """Render a mobile-friendly dashboard card for one index."""

    verdict_class = dashboard.final_verdict.lower()
    st.markdown(f"### {dashboard.index} Live Dashboard")
    st.caption(INDEX_DESCRIPTIONS[dashboard.index])
    st.markdown(
        f'<span class="verdict {verdict_class}">Final Verdict: {dashboard.final_verdict}</span>',
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Last Price", f"{dashboard.last_price:,.2f}")
    metric_cols[1].metric("EMA20", f"{dashboard.ema20:,.2f}")
    metric_cols[2].metric("EMA50", f"{dashboard.ema50:,.2f}")
    metric_cols[3].metric("VWAP", f"{dashboard.vwap:,.2f}")

    score_cols = st.columns(5)
    score_cols[0].metric("RSI(14)", f"{dashboard.rsi14:.2f}")
    score_cols[1].metric("Bullish Score", f"{dashboard.bullish_score}/9")
    score_cols[2].metric("Bearish Score", f"{dashboard.bearish_score}/9")
    score_cols[3].metric("CALL %", f"{dashboard.call_percent}%")
    score_cols[4].metric("PUT %", f"{dashboard.put_percent}%")

    st.progress(dashboard.call_percent / 100, text=f"CALL probability: {dashboard.call_percent}%")
    st.progress(dashboard.put_percent / 100, text=f"PUT probability: {dashboard.put_percent}%")
    st.progress(dashboard.sideways_percent / 100, text=f"SIDEWAYS probability: {dashboard.sideways_percent}%")

    structure = pd.DataFrame(
        [
            {"Signal": "Volume Spike", "Status": "Yes" if dashboard.volume_spike else "No"},
            {"Signal": "Liquidity Sweep", "Status": dashboard.liquidity_sweep},
            {"Signal": "BOS", "Status": dashboard.bos},
            {"Signal": "CHOCH", "Status": dashboard.choch},
        ]
    )
    st.dataframe(structure, hide_index=True, use_container_width=True)


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


def render_live_dashboard_tab() -> None:
    """Render the Version 2 NIFTY and BANKNIFTY live dashboards."""

    st.header("⚡ Master Sniper PRO V2 Live Index Dashboards")
    st.write(
        "Combines EMA20, EMA50, VWAP, RSI(14), volume spike, liquidity sweep, BOS, "
        "and CHOCH into CALL/PUT/SIDEWAYS probabilities."
    )

    cols = st.columns([1, 1])
    period = cols[0].selectbox("Data period", ["5d", "1mo", "3mo"], index=0)
    interval = cols[1].selectbox("Candle interval", ["5m", "15m", "30m", "1h"], index=1)

    if st.button("🔍 Fetch V2 Live Dashboards", type="primary"):
        dashboards = []
        errors = []
        with st.spinner("Fetching NIFTY and BANKNIFTY live data..."):
            for label, symbol in INDEX_SYMBOLS.items():
                try:
                    dashboards.append(build_index_dashboard(symbol, label, period, interval))
                except (KeyError, ValueError, OSError, yf.exceptions.YFException) as exc:
                    errors.append(f"{label}: {exc}")

        for dashboard in dashboards:
            with st.container(border=True):
                render_dashboard_card(dashboard)

        if dashboards:
            table = pd.DataFrame([dashboard.__dict__ for dashboard in dashboards])
            st.subheader("V2 Signal Summary")
            st.dataframe(table, hide_index=True, use_container_width=True)
        if errors:
            st.warning("Some index data could not be loaded: " + " | ".join(errors))


def main() -> None:
    """Run the Streamlit app."""

    st.set_page_config(page_title="Master Sniper PRO V2", page_icon="🎯", layout="wide")
    apply_dark_theme()
    st.title("🎯 Master Sniper PRO V2")
    st.markdown("**NIFTY | BANKNIFTY | EMA20/EMA50 | VWAP | RSI | Smart Money Structure**")
    st.caption("Educational market scanner. Not financial advice.")

    tab1, tab2 = st.tabs(["⚡ Live Index Dashboards", "🚀 Swing Breakout"])
    with tab1:
        render_live_dashboard_tab()
    with tab2:
        render_breakout_tab()

    st.markdown("---")
    st.caption("Developed for Mechanical Trading | No Emotion, Only Rules 🤖")


if __name__ == "__main__":
    main()
