"""Dry Bulk Freight Dashboard  -  run with:  streamlit run app.py"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_utils import (ALL_SERIES, VESSELS, add_moving_averages, clean_data,
                        generate_demo_data, key_indicators, volatility_summary)

st.set_page_config(page_title="Dry Bulk Freight Dashboard", page_icon="🚢", layout="wide")

# ---------------------------------------------------------------- data loading
@st.cache_data
def load_csv(file) -> pd.DataFrame:
    return clean_data(pd.read_csv(file))

@st.cache_data
def load_demo() -> pd.DataFrame:
    return clean_data(generate_demo_data())

st.sidebar.title("🚢 Filters")
uploaded = st.sidebar.file_uploader("Upload freight CSV", type="csv",
    help="Columns: Date, BDI, Capesize, Panamax, Supramax (names are flexible).")
try:
    if uploaded is not None:
        data, using_demo = load_csv(uploaded), False
    else:
        data, using_demo = load_demo(), True
except Exception as e:
    st.error(f"Could not read the file: {e}")
    st.stop()

available = [c for c in ALL_SERIES if c in data.columns]

# --------------------------------------------------------------------- filters
min_d, max_d = data["Date"].min().date(), data["Date"].max().date()
date_range = st.sidebar.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
if not (isinstance(date_range, tuple) and len(date_range) == 2):
    st.info("Select both a start and an end date.")
    st.stop()

primary = st.sidebar.selectbox("Main series (cards & trend)", available)
compare = st.sidebar.multiselect("Vessel classes to compare",
    [v for v in VESSELS if v in data.columns],
    default=[v for v in VESSELS if v in data.columns])
ma_windows = st.sidebar.multiselect("Moving averages (days)", [7, 30, 90], default=[7, 30])

mask = (data["Date"].dt.date >= date_range[0]) & (data["Date"].dt.date <= date_range[1])
view = data.loc[mask].reset_index(drop=True)
if view.empty:
    st.warning("No data in the selected range.")
    st.stop()

# ----------------------------------------------------------------------- header
st.title("Dry Bulk Freight Dashboard")
st.caption("Interactive analysis of Baltic Dry Index and vessel-class freight trends")
if using_demo:
    st.warning("Showing **synthetic demo data** (not real market data). "
               "Upload a real CSV in the sidebar.")

# --------------------------------------------------------------- overview cards
st.subheader(f"Overview: {primary}")
ind = key_indicators(data, primary)          # latest/weekly/monthly use full history
sel = key_indicators(view, primary)          # high/low use selected period
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Latest", f"{ind['latest']:,.0f}", help=f"As of {ind['latest_date']:%d %b %Y}")
c2.metric("Weekly change", "n/a" if ind["weekly"] is None else f"{ind['weekly']:+.2f}%",
          delta=None if ind["weekly"] is None else f"{ind['weekly']:.2f}%")
c3.metric("Monthly change", "n/a" if ind["monthly"] is None else f"{ind['monthly']:+.2f}%",
          delta=None if ind["monthly"] is None else f"{ind['monthly']:.2f}%")
c4.metric("Period high", f"{sel['high']:,.0f}", help=f"{sel['high_date']:%d %b %Y}")
c5.metric("Period low", f"{sel['low']:,.0f}", help=f"{sel['low_date']:%d %b %Y}")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Trend", "⚖️ Vessel comparison", "📊 Volatility", "🗂 Data"])

# ------------------------------------------------------------------------ trend
with tab1:
    ma = add_moving_averages(view, primary, tuple(ma_windows))
    fig = go.Figure()
    fig.add_scatter(x=ma["Date"], y=ma[primary], name=primary, line=dict(width=1.5))
    for w in ma_windows:
        fig.add_scatter(x=ma["Date"], y=ma[f"MA{w}"], name=f"{w}-day MA", line=dict(dash="dot"))
    fig.update_layout(height=450, hovermode="x unified", xaxis_title="Date",
                      yaxis_title="Index points", legend=dict(orientation="h", y=1.1))
    fig.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------- comparison
with tab2:
    if not compare:
        st.info("Pick at least one vessel class in the sidebar.")
    else:
        fig = go.Figure()
        for v in compare:
            fig.add_scatter(x=view["Date"], y=view[v], name=v)
        fig.update_layout(height=420, hovermode="x unified", yaxis_title="Index points",
                          legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Rebased to 100 at start of period** (fair comparison of movement)")
        fig2 = go.Figure()
        for v in compare:
            fig2.add_scatter(x=view["Date"], y=view[v] / view[v].iloc[0] * 100, name=v)
        fig2.update_layout(height=350, hovermode="x unified", yaxis_title="Rebased (start = 100)",
                           legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig2, use_container_width=True)

# ------------------------------------------------------------------- volatility
with tab3:
    vol = volatility_summary(view, available)
    st.dataframe(vol, use_container_width=True, hide_index=True)
    fig = go.Figure(go.Bar(x=vol["Series"], y=vol["Daily Volatility (%)"]))
    fig.update_layout(height=320, yaxis_title="Std dev of daily % change")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Higher daily volatility = larger day-to-day swings. "
               "Kavussanos (1996) found Capesize to be the most volatile class.")

# ------------------------------------------------------------------------- data
with tab4:
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.download_button("⬇ Download filtered data (CSV)",
                       view.to_csv(index=False).encode("utf-8"),
                       file_name="freight_filtered.csv", mime="text/csv")
