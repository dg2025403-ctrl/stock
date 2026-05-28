import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="상세 데이터", page_icon="📄", layout="wide")

st.markdown("""
    <style>
    .main .block-container {padding-top: 1.5rem;}
    h1 {font-size: 1.8rem !important; font-weight: 700; color: #191f28;}
    </style>
""", unsafe_allow_html=True)

st.title("📄 상세 데이터")

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
        data.index = pd.to_datetime(data.index).date
    return data

with st.spinner('장부를 정리하는 중...'):
    raw_data = load_stock_data(tuple(selected_tickers), selected_period)

if raw_data.empty:
    st.error("데이터를 가져오지 못했습니다.")
    st.stop()

# 금액 포맷팅을 적용한 깔끔한 표 노출
st.dataframe(raw_data.style.format(formatter="{:,.2f}"), use_container_width=True)

# CSV 파일 추출 및 다운로드 단추
csv = raw_data.to_csv().encode('utf-8')
st.download_button(
    label="📥 데이터 다운로드 (CSV)",
    data=csv,
    file_name=f"stock_data_{datetime.today().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)
