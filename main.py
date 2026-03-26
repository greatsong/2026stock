import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MARKET LENS | 글로벌 주식 비교",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@300;400;600;700&family=Noto+Sans+KR:wght@300;400;700&display=swap');

:root {
    --bg:        #070d12;
    --bg2:       #0d1821;
    --bg3:       #111f2e;
    --accent:    #00ff88;
    --accent2:   #00c4ff;
    --accent3:   #ff4d6d;
    --text:      #c8d6e5;
    --text-dim:  #5e7a96;
    --border:    #1a3a55;
    --glow:      0 0 18px rgba(0,255,136,0.25);
    --glow2:     0 0 18px rgba(0,196,255,0.2);
}

html, body, [class*="css"] {
    font-family: 'Rajdhani', 'Noto Sans KR', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text);
}

/* hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* ── Header ── */
.site-header {
    display: flex;
    align-items: baseline;
    gap: 16px;
    padding: 0.6rem 0 1.6rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.6rem;
}
.site-logo {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.75rem;
    color: var(--accent);
    letter-spacing: 4px;
    text-shadow: var(--glow);
}
.site-sub {
    font-size: 0.9rem;
    color: var(--text-dim);
    letter-spacing: 2px;
    text-transform: uppercase;
}
.live-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
    animation: blink 1.4s infinite;
    margin-left: 6px;
    vertical-align: middle;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.2} }

/* ── Metric cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 12px;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 16px;
    position: relative;
    overflow: hidden;
    transition: border-color .2s;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--accent);
}
.metric-card.us::before  { background: var(--accent2); }
.metric-card.neg::before { background: var(--accent3); }
.metric-card:hover { border-color: var(--accent); }

.mc-ticker {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-dim);
    letter-spacing: 2px;
    margin-bottom: 4px;
}
.mc-price {
    font-size: 1.4rem;
    font-weight: 700;
    color: #fff;
    line-height: 1.1;
}
.mc-change {
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 4px;
}
.mc-name {
    font-size: 0.72rem;
    color: var(--text-dim);
    margin-top: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.pos { color: var(--accent); }
.neg { color: var(--accent3); }
.neu { color: var(--text-dim); }

/* ── Section labels ── */
.section-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--text-dim);
    border-left: 3px solid var(--accent);
    padding-left: 10px;
    margin-bottom: 12px;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stRadio label {
    color: var(--text) !important;
    font-weight: 600;
    letter-spacing: 1px;
}

/* ── Table ── */
.return-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
}
.return-table th {
    background: var(--bg3);
    color: var(--text-dim);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 2px;
    padding: 8px 12px;
    text-align: right;
    border-bottom: 1px solid var(--border);
}
.return-table th:first-child { text-align: left; }
.return-table td {
    padding: 8px 12px;
    border-bottom: 1px solid rgba(26,58,85,0.5);
    color: var(--text);
    text-align: right;
}
.return-table td:first-child { text-align: left; font-weight: 600; }
.return-table tr:hover td { background: rgba(255,255,255,0.03); }

/* ── Plotly container ── */
.chart-wrap {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 4px;
    margin-bottom: 1rem;
}

/* ── Scrollable table wrapper ── */
.table-scroll {
    overflow-x: auto;
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 4px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Stock universe ────────────────────────────────────────────────────────────
KR_STOCKS = {
    "삼성전자":   "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "현대차":     "005380.KS",
    "POSCO홀딩스":"005490.KS",
    "카카오":     "035720.KS",
    "네이버(NAVER)":"035420.KS",
    "셀트리온":   "068270.KS",
    "기아":       "000270.KS",
    "KB금융":     "105560.KS",
    "신한지주":   "055550.KS",
    "LG화학":     "051910.KS",
    "삼성SDI":    "006400.KS",
    "하나금융지주":"086790.KS",
    "코스피 지수": "^KS11",
    "코스닥 지수": "^KQ11",
}

US_STOCKS = {
    "Apple":       "AAPL",
    "Microsoft":   "MSFT",
    "NVIDIA":      "NVDA",
    "Amazon":      "AMZN",
    "Alphabet":    "GOOGL",
    "Meta":        "META",
    "Tesla":       "TSLA",
    "Berkshire B": "BRK-B",
    "JPMorgan":    "JPM",
    "S&P 500 ETF": "SPY",
    "Nasdaq ETF":  "QQQ",
    "TSMC":        "TSM",
    "Samsung ADR": "SSNLF",
    "Eli Lilly":   "LLY",
    "Broadcom":    "AVGO",
}

PERIOD_MAP = {
    "1개월":  "1mo",
    "3개월":  "3mo",
    "6개월":  "6mo",
    "1년":    "1y",
    "2년":    "2y",
    "5년":    "5y",
}

INTERVAL_MAP = {
    "1mo": "1d",
    "3mo": "1d",
    "6mo": "1d",
    "1y":  "1d",
    "2y":  "1wk",
    "5y":  "1wk",
}

# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_price(ticker: str, period: str) -> pd.Series:
    interval = INTERVAL_MAP.get(period, "1d")
    df = yf.download(ticker, period=period, interval=interval,
                     auto_adjust=True, progress=False)
    if df.empty:
        return pd.Series(dtype=float)
    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return close.dropna()


@st.cache_data(ttl=300, show_spinner=False)
def fetch_info(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        return {
            "price":   getattr(info, "last_price", None),
            "prev":    getattr(info, "previous_close", None),
            "high52":  getattr(info, "year_high", None),
            "low52":   getattr(info, "year_low", None),
            "mktcap":  getattr(info, "market_cap", None),
        }
    except Exception:
        return {}


def pct(a, b):
    if a is None or b is None or b == 0:
        return None
    return (a - b) / b * 100


def fmt_pct(v):
    if v is None:
        return "—"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.2f}%"


def fmt_price(v, ticker):
    if v is None:
        return "—"
    if ".KS" in ticker or ".KQ" in ticker or "^KS" in ticker or "^KQ" in ticker:
        return f"₩{v:,.0f}"
    return f"${v:,.2f}"


def color_cls(v):
    if v is None:
        return "neu"
    return "pos" if v >= 0 else "neg"


def card_cls(v):
    if v is None:
        return ""
    return "" if v >= 0 else " neg"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    period_label = st.selectbox("📅 조회 기간", list(PERIOD_MAP.keys()), index=3)
    period = PERIOD_MAP[period_label]

    st.markdown("---")
    st.markdown("**🇰🇷 한국 종목 선택**")
    kr_selected = st.multiselect(
        "한국 종목",
        list(KR_STOCKS.keys()),
        default=["삼성전자", "SK하이닉스", "현대차", "코스피 지수"],
        label_visibility="collapsed",
    )

    st.markdown("**🇺🇸 미국 종목 선택**")
    us_selected = st.multiselect(
        "미국 종목",
        list(US_STOCKS.keys()),
        default=["Apple", "NVIDIA", "Tesla", "S&P 500 ETF"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    chart_type = st.radio(
        "📊 차트 유형",
        ["수익률 비교 (정규화)", "가격 추이", "캔들차트 (단일 종목)"],
    )

    if chart_type == "캔들차트 (단일 종목)":
        all_names = kr_selected + us_selected
        candle_target = st.selectbox("캔들 종목 선택", all_names if all_names else ["—"])

    show_volume = st.checkbox("거래량 표시", value=False)
    show_ma = st.checkbox("이동평균선 (20/60일)", value=True)

    st.markdown("---")
    st.markdown(
        "<small style='color:#5e7a96'>데이터: Yahoo Finance · yfinance<br>5분마다 자동 갱신</small>",
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%Y.%m.%d  %H:%M")
st.markdown(f"""
<div class="site-header">
  <span class="site-logo">MARKET LENS</span>
  <span class="site-sub">글로벌 주식 비교 대시보드</span>
  <span style="margin-left:auto;font-family:'Share Tech Mono',monospace;font-size:0.78rem;color:#5e7a96">
    {now_str}<span class="live-dot"></span>
  </span>
</div>
""", unsafe_allow_html=True)

# ── Build selected list ───────────────────────────────────────────────────────
selected_all = (
    [(n, KR_STOCKS[n], "kr") for n in kr_selected] +
    [(n, US_STOCKS[n],  "us") for n in us_selected]
)

if not selected_all:
    st.warning("사이드바에서 종목을 하나 이상 선택해주세요.")
    st.stop()

# ── Metric cards ──────────────────────────────────────────────────────────────
with st.spinner("시세 데이터 불러오는 중…"):
    infos = {ticker: fetch_info(ticker) for _, ticker, _ in selected_all}

st.markdown('<div class="section-label">현재 시세</div>', unsafe_allow_html=True)
cols = st.columns(min(len(selected_all), 6))

for idx, (name, ticker, mkt) in enumerate(selected_all):
    inf = infos[ticker]
    price = inf.get("price")
    prev  = inf.get("prev")
    chg   = pct(price, prev)
    cc    = color_cls(chg)
    mc    = "us" if mkt == "us" else ""
    if chg is not None and chg < 0:
        mc += " neg"

    with cols[idx % min(len(selected_all), 6)]:
        st.markdown(f"""
        <div class="metric-card {mc.strip()}">
          <div class="mc-ticker">{ticker}</div>
          <div class="mc-price">{fmt_price(price, ticker)}</div>
          <div class="mc-change {cc}">{fmt_pct(chg)}</div>
          <div class="mc-name">{name}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Fetch price series ────────────────────────────────────────────────────────
st.markdown("")
with st.spinner("차트 데이터 수집 중…"):
    price_data: dict[str, pd.Series] = {}
    for name, ticker, _ in selected_all:
        s = fetch_price(ticker, period)
        if not s.empty:
            price_data[name] = s

if not price_data:
    st.error("데이터를 불러올 수 없습니다. 종목을 다시 선택해보세요.")
    st.stop()

# ── Plotly theme helper ───────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#0d1821",
    plot_bgcolor="#070d12",
    font=dict(family="Rajdhani, Noto Sans KR, sans-serif", color="#c8d6e5", size=12),
    legend=dict(bgcolor="#0d1821", bordercolor="#1a3a55", borderwidth=1,
                font=dict(size=11)),
    hovermode="x unified",
    margin=dict(l=12, r=12, t=36, b=12),
)

AXIS_STYLE = dict(gridcolor="#1a3a55", showgrid=True, zeroline=False)
XAXIS_STYLE = dict(gridcolor="#1a3a55", showgrid=True, zeroline=False,
                   rangeslider_visible=False)

KR_COLORS = ["#00ff88","#00e07a","#00c06a","#00a05a","#00805a",
             "#00604a","#00403a","#00202a"]
US_COLORS = ["#00c4ff","#00aaee","#0090dd","#0076cc","#005cbb",
             "#0042aa","#002899","#000e88"]


def get_color(name, mkt):
    kr_names = [n for n, _, m in selected_all if m == "kr"]
    us_names = [n for n, _, m in selected_all if m == "us"]
    if mkt == "kr":
        i = kr_names.index(name) if name in kr_names else 0
        return KR_COLORS[i % len(KR_COLORS)]
    else:
        i = us_names.index(name) if name in us_names else 0
        return US_COLORS[i % len(US_COLORS)]


# ── Chart ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">차트</div>', unsafe_allow_html=True)

def make_ma(series, w):
    return series.rolling(w, min_periods=1).mean()

# ─ 1. Normalized return chart ─
if chart_type == "수익률 비교 (정규화)":
    fig = go.Figure()
    for name, ticker, mkt in selected_all:
        if name not in price_data:
            continue
        s = price_data[name]
        normed = (s / s.iloc[0] - 1) * 100
        color = get_color(name, mkt)
        fig.add_trace(go.Scatter(
            x=normed.index, y=normed.values,
            name=name, mode="lines",
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>수익률: %{{y:.2f}}%<extra></extra>",
        ))

    fig.add_hline(y=0, line_dash="dot", line_color="#5e7a96", line_width=1)
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=f"수익률 비교 (기준=0%, {period_label})", font=dict(size=14, color="#00ff88")),
        height=480,
    )
    fig.update_xaxes(**XAXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE, ticksuffix="%")
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─ 2. Price chart ─
elif chart_type == "가격 추이":
    # kr and us on separate y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for name, ticker, mkt in selected_all:
        if name not in price_data:
            continue
        s = price_data[name]
        color = get_color(name, mkt)
        secondary = (mkt == "us")
        fig.add_trace(
            go.Scatter(
                x=s.index, y=s.values,
                name=name, mode="lines",
                line=dict(color=color, width=2),
                hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:,.2f}}<extra></extra>",
            ),
            secondary_y=secondary,
        )
        if show_ma and len(s) >= 20:
            fig.add_trace(
                go.Scatter(
                    x=s.index, y=make_ma(s, 20).values,
                    name=f"{name} MA20", mode="lines",
                    line=dict(color=color, width=1, dash="dot"),
                    opacity=0.5,
                    hoverinfo="skip", showlegend=False,
                ),
                secondary_y=secondary,
            )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=f"가격 추이 ({period_label}) | 🇰🇷 좌축(₩)  🇺🇸 우축($)", font=dict(size=14, color="#00c4ff")),
        height=480,
    )
    fig.update_xaxes(**XAXIS_STYLE)
    fig.update_yaxes(title_text="KRW (₩)", secondary_y=False,
                     gridcolor="#1a3a55", showgrid=True, zeroline=False)
    fig.update_yaxes(title_text="USD ($)", secondary_y=True,
                     gridcolor="#1a3a55", showgrid=False, zeroline=False)
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─ 3. Candle chart ─
elif chart_type == "캔들차트 (단일 종목)":
    if "candle_target" in locals() and candle_target and candle_target != "—":
        ticker = KR_STOCKS.get(candle_target) or US_STOCKS.get(candle_target)
        mkt = "kr" if candle_target in KR_STOCKS else "us"
        interval = INTERVAL_MAP.get(period, "1d")

        @st.cache_data(ttl=300, show_spinner=False)
        def fetch_ohlcv(t, p, iv):
            df = yf.download(t, period=p, interval=iv, auto_adjust=True, progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            return df.dropna()

        ohlcv = fetch_ohlcv(ticker, period, interval)
        color = get_color(candle_target, mkt)

        rows = 2 if show_volume else 1
        row_h = [0.75, 0.25] if show_volume else [1]
        fig = make_subplots(rows=rows, cols=1, row_heights=row_h, shared_xaxes=True,
                            vertical_spacing=0.03)

        fig.add_trace(go.Candlestick(
            x=ohlcv.index,
            open=ohlcv["Open"], high=ohlcv["High"],
            low=ohlcv["Low"],   close=ohlcv["Close"],
            increasing_line_color="#00ff88",
            decreasing_line_color="#ff4d6d",
            name=candle_target,
        ), row=1, col=1)

        if show_ma and len(ohlcv) >= 20:
            for w, c in [(20, "#ffcc00"), (60, "#ff7700")]:
                if len(ohlcv) >= w:
                    ma = ohlcv["Close"].rolling(w).mean()
                    fig.add_trace(go.Scatter(
                        x=ohlcv.index, y=ma,
                        name=f"MA{w}", mode="lines",
                        line=dict(color=c, width=1.5),
                    ), row=1, col=1)

        if show_volume and "Volume" in ohlcv.columns:
            vol_colors = [
                "#00ff88" if ohlcv["Close"].iloc[i] >= ohlcv["Open"].iloc[i] else "#ff4d6d"
                for i in range(len(ohlcv))
            ]
            fig.add_trace(go.Bar(
                x=ohlcv.index, y=ohlcv["Volume"],
                name="거래량", marker_color=vol_colors, showlegend=False,
            ), row=2, col=1)

        fig.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(text=f"{candle_target} ({ticker}) 캔들차트 — {period_label}", font=dict(size=14, color=color)),
            height=520,
        )
        fig.update_xaxes(gridcolor="#1a3a55", showgrid=True, zeroline=False,
                         rangeslider_visible=False)
        fig.update_yaxes(gridcolor="#1a3a55", showgrid=True, zeroline=False)
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ── Return table ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">수익률 비교 테이블</div>', unsafe_allow_html=True)

RETURN_PERIODS = [("1mo","1개월"), ("3mo","3개월"), ("6mo","6개월"),
                  ("1y","1년"), ("2y","2년")]

@st.cache_data(ttl=300, show_spinner=False)
def get_return(ticker, period):
    s = fetch_price(ticker, period)
    if len(s) < 2:
        return None
    return (s.iloc[-1] / s.iloc[0] - 1) * 100

rows_data = []
with st.spinner("수익률 계산 중…"):
    for name, ticker, mkt in selected_all:
        inf = infos[ticker]
        row = {"종목": name, "시장": "🇰🇷" if mkt == "kr" else "🇺🇸"}
        for p_key, p_label in RETURN_PERIODS:
            row[p_label] = get_return(ticker, p_key)
        hi52 = inf.get("high52")
        lo52 = inf.get("low52")
        pr   = inf.get("price")
        row["52주 고점대비"] = pct(pr, hi52) if hi52 else None
        rows_data.append(row)

df_table = pd.DataFrame(rows_data)

# Build HTML table
cols_show = ["종목", "시장"] + [p for _, p in RETURN_PERIODS] + ["52주 고점대비"]
header_html = "".join(f"<th>{c}</th>" for c in cols_show)

body_html = ""
for _, row in df_table.iterrows():
    cells = f"<td>{row['종목']}</td><td>{row['시장']}</td>"
    for _, p_label in RETURN_PERIODS:
        v = row[p_label]
        cc = color_cls(v)
        cells += f'<td class="{cc}">{fmt_pct(v)}</td>'
    v52 = row["52주 고점대비"]
    cc52 = color_cls(v52)
    cells += f'<td class="{cc52}">{fmt_pct(v52)}</td>'
    body_html += f"<tr>{cells}</tr>"

table_html = f"""
<div class="table-scroll">
  <table class="return-table">
    <thead><tr>{header_html}</tr></thead>
    <tbody>{body_html}</tbody>
  </table>
</div>
"""
st.markdown(table_html, unsafe_allow_html=True)

# ── Correlation heatmap (if ≥ 2 stocks) ──────────────────────────────────────
if len(price_data) >= 2:
    st.markdown("")
    st.markdown('<div class="section-label">수익률 상관관계</div>', unsafe_allow_html=True)

    # Align on common index
    all_series = []
    for name, s in price_data.items():
        ret = s.pct_change().dropna()
        ret.name = name
        all_series.append(ret)
    df_ret = pd.concat(all_series, axis=1).dropna()

    if df_ret.shape[0] > 5:
        corr = df_ret.corr()
        labels = corr.columns.tolist()

        colorscale = [
            [0.0,  "#ff4d6d"],
            [0.5,  "#0d1821"],
            [1.0,  "#00ff88"],
        ]
        fig_corr = go.Figure(go.Heatmap(
            z=corr.values,
            x=labels, y=labels,
            colorscale=colorscale,
            zmin=-1, zmax=1,
            text=np.round(corr.values, 2),
            texttemplate="%{text}",
            textfont=dict(size=11),
            hovertemplate="%{x} × %{y}: %{z:.2f}<extra></extra>",
        ))
        fig_corr.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(text="일별 수익률 상관계수", font=dict(size=14, color="#00c4ff")),
            height=max(320, 60 * len(labels)),
        )
        fig_corr.update_xaxes(side="bottom", tickfont=dict(size=10),
                              gridcolor="#1a3a55", showgrid=False, zeroline=False)
        fig_corr.update_yaxes(autorange="reversed", tickfont=dict(size=10),
                              gridcolor="#1a3a55", showgrid=False, zeroline=False)
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_corr, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:2.5rem;padding-top:1rem;border-top:1px solid #1a3a55;
            text-align:center;font-size:0.75rem;color:#5e7a96;letter-spacing:1px;">
  MARKET LENS &nbsp;·&nbsp; Data by Yahoo Finance &nbsp;·&nbsp;
  투자 참고용이며 투자 권유가 아닙니다
</div>
""", unsafe_allow_html=True)
