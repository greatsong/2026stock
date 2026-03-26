import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="주식 비교 분석", layout="wide")

st.title("📊 한국 vs 미국 주식 비교 분석 웹앱")

# 기본 종목 리스트
default_korean = ["005930.KS", "000660.KS"]  # 삼성전자, SK하이닉스
default_us = ["AAPL", "TSLA"]

st.sidebar.header("⚙️ 설정")

korean_stocks = st.sidebar.text_input(
    "한국 주식 (티커, 쉼표로 구분)",
    ",".join(default_korean)
)

us_stocks = st.sidebar.text_input(
    "미국 주식 (티커, 쉼표로 구분)",
    ",".join(default_us)
)

period = st.sidebar.selectbox(
    "기간 선택",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=3
)

normalize = st.sidebar.checkbox("📈 정규화 (시작값=100)", True)

tickers = korean_stocks.split(",") + us_stocks.split(",")

tickers = [t.strip() for t in tickers if t.strip() != ""]

if len(tickers) == 0:
    st.warning("종목을 입력하세요.")
    st.stop()

@st.cache_data
def load_data(tickers, period):
    data = yf.download(tickers, period=period)["Adj Close"]
    return data

data = load_data(tickers, period)

if data.empty:
    st.error("데이터를 불러올 수 없습니다.")
    st.stop()

# -------------------------
# 수익률 계산
# -------------------------
returns = (data.iloc[-1] / data.iloc[0] - 1) * 100
returns = returns.sort_values(ascending=False)

st.subheader("📊 수익률 비교 (%)")
st.dataframe(returns.to_frame(name="Return (%)"))

# -------------------------
# 차트
# -------------------------
st.subheader("📈 가격 비교 차트")

plot_data = data.copy()

if normalize:
    plot_data = plot_data / plot_data.iloc[0] * 100

fig, ax = plt.subplots(figsize=(10, 5))

for col in plot_data.columns:
    ax.plot(plot_data.index, plot_data[col], label=col)

ax.legend()
ax.set_title("주가 비교")
ax.set_xlabel("Date")
ax.set_ylabel("Price (Normalized)" if normalize else "Price")

st.pyplot(fig)

# -------------------------
# 개별 차트
# -------------------------
st.subheader("📉 개별 종목 차트")

selected_stock = st.selectbox("종목 선택", tickers)

fig2, ax2 = plt.subplots()

ax2.plot(data[selected_stock])
ax2.set_title(selected_stock)

st.pyplot(fig2)
