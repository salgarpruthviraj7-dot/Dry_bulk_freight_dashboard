"""Data loading, cleaning and indicator calculations (pandas only)."""
import numpy as np
import pandas as pd

VESSELS = ["Capesize", "Panamax", "Supramax"]
ALL_SERIES = ["BDI"] + VESSELS

# Accepts many header spellings from different data sources
ALIASES = {
    "date": "Date", "day": "Date", "time": "Date",
    "bdi": "BDI", "baltic dry index": "BDI", "price": "BDI", "close": "BDI", "value": "BDI",
    "bci": "Capesize", "capesize": "Capesize", "cape": "Capesize",
    "bpi": "Panamax", "panamax": "Panamax",
    "bsi": "Supramax", "supramax": "Supramax",
}


def generate_demo_data(start="2018-01-01", end=None, seed=42) -> pd.DataFrame:
    """Synthetic, BDI-like data for testing. NOT real market data."""
    end = end or pd.Timestamp.today().normalize()
    dates = pd.bdate_range(start, end)
    rng = np.random.default_rng(seed)
    n = len(dates)
    t = np.arange(n)
    cycle = 1 + 0.35 * np.sin(2 * np.pi * t / 520) + 0.15 * np.sin(2 * np.pi * t / 130)

    def walk(scale, vol):
        steps = rng.normal(0, vol, n).cumsum()
        return scale * cycle * np.exp(steps - steps.mean()) 

    cape = np.clip(walk(2200, 0.012), 300, 12000)
    pana = np.clip(walk(1500, 0.008), 300, 6000)
    supra = np.clip(walk(1100, 0.006), 300, 4500)
    bdi = (0.4 * cape + 0.3 * pana + 0.3 * supra).round(0)
    return pd.DataFrame({"Date": dates, "BDI": bdi, "Capesize": cape.round(0),
                         "Panamax": pana.round(0), "Supramax": supra.round(0)})


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns, parse dates/numbers, drop duplicates, fill gaps."""
    df = df.copy()
    df.columns = [ALIASES.get(str(c).strip().lower(), str(c).strip()) for c in df.columns]
    if "Date" not in df.columns:
        raise ValueError("CSV must contain a date column (Date / Day / Time).")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=False)
    df = df.dropna(subset=["Date"])

    present = [c for c in ALL_SERIES if c in df.columns]
    if not present:
        raise ValueError("No BDI / Capesize / Panamax / Supramax column found.")

    for c in present:  # handle '1,234' and '1.2K' style values
        s = df[c].astype(str).str.replace(",", "", regex=False).str.strip()
        s = s.str.replace("K", "e3", regex=False)
        df[c] = pd.to_numeric(s, errors="coerce")

    df = df[["Date"] + present]
    df = df.drop_duplicates(subset="Date", keep="last").sort_values("Date")
    df = df.set_index("Date")
    df[present] = df[present].ffill().bfill()          # missing values
    return df.reset_index()


def pct_change_over(series: pd.Series, days: int):
    """% change between latest value and value `days` calendar days earlier."""
    s = series.dropna()
    if s.empty:
        return None
    target = s.index[-1] - pd.Timedelta(days=days)
    prior = s[s.index <= target]
    if prior.empty or prior.iloc[-1] == 0:
        return None
    return (s.iloc[-1] / prior.iloc[-1] - 1) * 100


def key_indicators(df: pd.DataFrame, col: str) -> dict:
    s = df.set_index("Date")[col].dropna()
    return {
        "latest": s.iloc[-1],
        "latest_date": s.index[-1],
        "weekly": pct_change_over(s, 7),
        "monthly": pct_change_over(s, 30),
        "high": s.max(), "high_date": s.idxmax(),
        "low": s.min(), "low_date": s.idxmin(),
    }


def add_moving_averages(df: pd.DataFrame, col: str, windows=(7, 30)) -> pd.DataFrame:
    out = df[["Date", col]].copy()
    for w in windows:
        out[f"MA{w}"] = out[col].rolling(w, min_periods=1).mean()
    return out


def volatility_summary(df: pd.DataFrame, cols) -> pd.DataFrame:
    rows = []
    for c in cols:
        s = df[c].dropna()
        daily_ret = s.pct_change().dropna()
        rows.append({
            "Series": c,
            "Average": s.mean(),
            "Std Dev": s.std(),
            "Min": s.min(),
            "Max": s.max(),
            "Range": s.max() - s.min(),
            "Coeff. of Variation (%)": s.std() / s.mean() * 100 if s.mean() else np.nan,
            "Daily Volatility (%)": daily_ret.std() * 100,
        })
    return pd.DataFrame(rows).round(2)
