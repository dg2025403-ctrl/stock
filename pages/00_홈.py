import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="홈 (실시간 수익률)", page_icon="🏠", layout="wide")

st.markdown("""
    <style>
    .main .block-container {padding-top: 1.5rem;}
    h1 {font-size: 1.8rem !important; font-weight: 700; color: #191f28;}
    .stMetric {
        background-color: #ffffff; 
        padding: 18px; 
        border-radius: 14px; 
        border: 1px solid #e5e8eb; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }
    [data-testid="stMetricValue"] {font-size: 1.6rem !important; font-weight: 700; color: #191f28;}
    </style>
""", unsafe_allow_html=True)

st.title("🏠 홈 (실시간 수익률)")

# 조회 조건 설정
period_options = {"1개월": 30, "3개월": 90, "6개월": 180, "1년": 365, "5년": 365*5}
selected_period = st.selectbox("📅 분석 기간 선택", list(period_options.keys()), index=3)

ticker_dict = {
    "삼성전자 (KR)": "005930.KS", "SK하이닉스 (KR)": "000660.KS",
    "Apple (US)": "AAPL", "Microsoft (US)": "MSFT", "NVIDIA (US)": "NVDA", "Tesla (US)": "TSLA"
}
selected_tickers = st.multiselect("🔍 관심 종목", list(ticker_dict.keys()), default=list(ticker_dict.keys()))

if not selected_tickers:
    st.warning("⚠️ 최소 하나의 종목을 선택해 주세요.")
    st.stop()

@st.cache_data(ttl=3600)
def load_stock_data(tickers_tuple, p_key):
    data = pd.DataFrame()
    end_date = datetime.today()
    start_date = end_date - timedelta(days=period_options[p_key])
    
    for name in tickers_tuple:
        ticker = ticker_dict[name]
        try:
            df = yf.download(ticker, start=start_date, end=end_date, group_by='ticker')
            if not df.empty and 'Close' in df.columns:
                data[name] = df['Close'].squeeze()
        except:
            pass
    if not data.empty:
        data = data.ffill().bfill()
    return data

with st.spinner('실시간 주가를 가져오는 중...'):
    raw_data = load_stock_data(tuple(selected_tickers), selected_period)

if raw_data.empty:
    st.error("데이터를 가져오지 못했습니다.")
    st.stop()

normalized_data = (raw_data / raw_data.iloc[0] - 1) * 100

st.markdown("<br><h3>내 관심 종목 현황</h3>", unsafe_allow_html=True)

# 모바일 대응 자동 그리드 배치
metrics_cols = st.columns(len(selected_tickers))
for i, name in enumerate(selected_tickers):
    if name in normalized_data.columns:
        final_return = float(normalized_data[name].iloc[-1])
        current_price = float(raw_data[name].iloc[-1])
        unit = "원" if "(KR)" in name else "$"
        
        with metrics_cols[i]:
            st.metric(
                label=name, 
                value=f"{current_price:,.0f}{unit}" if unit=="원" else f"${current_price:,.2f}",
                delta=f"{final_return:+.2f}%"
            )
