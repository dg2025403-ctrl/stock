import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="수익률 비교 차트", page_icon="📈", layout="wide")

st.title("📈 수익률 비교 차트")

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
                series_data = df['Close'].squeeze()
                if isinstance(series_data, pd.DataFrame):
                    series_data = series_data.iloc[:, 0]
                data[name] = series_data
        except:
            pass
    if not data.empty:
        data = data.ffill().bfill()
        data.index = pd.to_datetime(data.index).date
    return data

with st.spinner('차트 데이터를 그리는 중...'):
    raw_data = load_stock_data(tuple(selected_tickers), selected_period)

if raw_data.empty:
    st.error("데이터를 가져오지 못했습니다.")
    st.stop()

normalized_data = (raw_data / raw_data.iloc[0] - 1) * 100

fig = go.Figure()
for name in selected_tickers:
    if name in normalized_data.columns:
        fig.add_trace(go.Scatter(x=normalized_data.index, y=normalized_data[name], mode='lines', name=name))

fig.update_layout(
    xaxis_title="날짜", yaxis_title="수익률 (%)", hovermode="x unified",
    margin=dict(l=15, r=15, t=15, b=15),
    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
    template="plotly_white"
)
st.plotly_chart(fig, use_container_width=True)
