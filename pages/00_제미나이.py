import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 페이지 기본 설정
st.set_page_config(page_title="한/미 주식 비교 분석", page_icon="📈", layout="wide")

st.title("📈 한국 & 미국 주요 주식 비교 분석 웹앱")
st.markdown("한국과 미국의 주요 주식들의 **기간별 누적 수익률**을 한눈에 비교해 보세요.")

# 종목 딕셔너리 (한국 주식은 .KS(코스피) 또는 .KQ(코스닥)를 붙여야 yfinance에서 인식합니다)
TICKERS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "현대차": "053800.KS",
    "NAVER": "035420.KS",
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "NVIDIA": "NVDA",
    "S&P 500 (ETF)": "SPY"
}

# --- 사이드바 설정 ---
st.sidebar.header("⚙️ 분석 설정")

# 1. 날짜 선택
end_date = datetime.today()
start_date = end_date - timedelta(days=365) # 기본값: 1년 전

selected_start = st.sidebar.date_input("시작일", start_date)
selected_end = st.sidebar.date_input("종료일", end_date)

# 2. 종목 선택
selected_names = st.sidebar.multiselect(
    "비교할 종목을 선택하세요",
    options=list(TICKERS.keys()),
    default=["삼성전자", "Apple", "NVIDIA", "S&P 500 (ETF)"]
)

# --- 데이터 가져오기 함수 (캐싱 적용) ---
@st.cache_data
def load_data(tickers, start, end):
    df = pd.DataFrame()
    for name, ticker in tickers.items():
        data = yf.download(ticker, start=start, end=end, progress=False)
        if not data.empty:
            # 종가를 기준으로 데이터 병합
            df[name] = data['Close']
    return df

# --- 메인 화면 로직 ---
if not selected_names:
    st.warning("👈 사이드바에서 최소 한 개 이상의 종목을 선택해 주세요.")
else:
    # 선택된 종목만 필터링해서 데이터 로드
    selected_tickers = {name: TICKERS[name] for name in selected_names}
    
    with st.spinner('주식 데이터를 불러오는 중입니다...'):
        raw_df = load_data(selected_tickers, selected_start, selected_end)
    
    if raw_df.empty:
        st.error("선택한 기간의 데이터를 불러올 수 없습니다.")
    else:
        # 결측치 처리 (앞의 데이터로 채우기)
        raw_df = raw_df.ffill().dropna()

        # 1. 누적 수익률 계산 (시작일 종가 기준 % 변화율)
        # 공식: (현재가 / 시작가 - 1) * 100
        returns_df = (raw_df / raw_df.iloc[0] - 1) * 100

        # 데이터프레임 구조 변경 (Plotly 시각화를 위함)
        returns_df_melted = returns_df.reset_index().melt(id_vars='Date', var_name='종목', value_name='수익률(%)')

        # --- 차트 그리기 ---
        st.subheader("📊 누적 수익률 비교 차트")
        fig = px.line(
            returns_df_melted, 
            x='Date', 
            y='수익률(%)', 
            color='종목',
            hover_data={"Date": "|%Y-%m-%d"}
        )
        fig.update_layout(
            xaxis_title="날짜",
            yaxis_title="누적 수익률 (%)",
            hovermode="x unified", # 마우스를 올렸을 때 같은 날짜의 데이터를 한 번에 보여줌
            legend_title="선택된 종목"
        )
        # 기준선(0%) 추가
        fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
        
        st.plotly_chart(fig, use_container_width=True)

        # --- 요약 데이터 표 ---
        st.subheader("📝 기간 내 요약 데이터")
        
        # 시작가, 현재가, 수익률 계산
        summary_data = {
            "종목": selected_names,
            "시작가": raw_df.iloc[0].values,
            "최근가": raw_df.iloc[-1].values,
            "수익률(%)": returns_df.iloc[-1].values
        }
        summary_df = pd.DataFrame(summary_data)
        
        # 보기 좋게 포맷팅
        st.dataframe(
            summary_df.style.format({
                "시작가": "{:,.2f}",
                "최근가": "{:,.2f}",
                "수익률(%)": "{:,.2f}%"
            }).background_gradient(subset=["수익률(%)"], cmap="RdYlGn"), 
            use_container_width=True
        )
