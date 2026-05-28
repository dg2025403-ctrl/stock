import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="한·미 주요 주식 수익률 비교",
    page_icon="📈",
    layout="wide"
)

st.title("📊 한·미 주요 주식 수익률 비교 앱")

# 2. 분석 조건 설정
st.subheader("⚙️ 분석 조건 설정")
col_period, _ = st.columns([1, 1])

with col_period:
    period_options = {
        "1개월": 30, 
        "3개월": 90, 
        "6개월": 180, 
        "1년": 365, 
        "5년": 365*5, 
        "상장 이후 전체(Max)": "max"
    }
    selected_period = st.selectbox("📅 분석 기간 선택", list(period_options.keys()), index=3)

# 3. 주식 종목 정의
ticker_dict = {
    "삼성전자 (KR)": "005930.KS",
    "SK하이닉스 (KR)": "000660.KS",
    "Apple (US)": "AAPL",
    "Microsoft (US)": "MSFT",
    "NVIDIA (US)": "NVDA",
    "Tesla (US)": "TSLA"
}

selected_tickers = st.multiselect(
    "🔍 비교할 종목 선택", 
    list(ticker_dict.keys()), 
    default=list(ticker_dict.keys())
)

if not selected_tickers:
    st.warning("⚠️ 최소 하나의 종목을 선택해 주세요!")
    st.stop()

# 4. 가장 초기 형태의 직관적인 데이터 가져오기 함수
@st.cache_data(ttl=3600)  # 1시간 동안 결과 캐싱 (서버 차단 방지)
def load_stock_data(tickers_tuple, period_key):
    data = pd.DataFrame()
    
    # [A] 상장 이후 전체(Max)를 가져오는 경우
    if period_key == "상장 이후 전체(Max)":
        for name in tickers_tuple:
            ticker = ticker_dict[name]
            try:
                df = yf.download(ticker, period="max")
                if not df.empty:
                    # 옛날 방식 그대로 Close 데이터만 추출
                    data[name] = df['Close']
            except:
                pass
                
    # [B] 일반 기간(1개월, 1년 등)을 가져오는 경우
    else:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=period_options[period_key])
        for name in tickers_tuple:
            ticker = ticker_dict[name]
            try:
                df = yf.download(ticker, start=start_date, end=end_date)
                if not df.empty:
                    data[name] = df['Close']
            except:
                pass
                
    # 휴장일 빈칸 메우기
    if not data.empty:
        data = data.ffill().bfill()
    return data

# 데이터 로드 실행
with st.spinner('야후 파이낸스에서 데이터를 가져오는 중...'):
    raw_data = load_stock_data(tuple(selected_tickers), selected_period)

# 데이터가 완전히 비어있는지 확인
if raw_data.empty:
    st.error("데이터를 불러오지 못했습니다. 야후 서버 연결이 원활하지 않거나 IP가 일시 차단되었을 수 있습니다. 잠시 후 다시 시도하거나 앱을 재부팅(Reboot) 해주세요.")
    st.stop()

# 누적 수익률 계산 (시작점 기준 0%로 정규화)
normalized_data = (raw_data / raw_data.iloc[0] - 1) * 100

# 5. 종목별 최종 누적 수익률 표시
st.markdown("---")
st.subheader("🔥 종목별 최종 누적 수익률")

metrics_cols = st.columns(len(selected_tickers))
for i, name in enumerate(selected_tickers):
    if name in normalized_data.columns:
        final_return = normalized_data[name].iloc[-1]
        current_price = raw_data[name].iloc[-1]
        unit = "원" if "(KR)" in name else "$"
        
        with metrics_cols[i]:
            st.metric(
                label=name, 
                value=f"{current_price:,.0f}{unit}" if unit=="원" else f"${current_price:,.2f}",
                delta=f"{final_return:+.2f}%"
            )

# 6. 수익률 추이 비교 차트
st.markdown("---")
st.subheader("📈 수익률 추이 비교 차트")

fig = go.Figure()
for name in selected_tickers:
    if name in normalized_data.columns:
        fig.add_trace(go.Scatter(
            x=normalized_data.index, 
            y=normalized_data[name], 
            mode='lines', 
            name=name
        ))

fig.update_layout(
    xaxis_title="날짜",
    yaxis_title="수익률 (%)",
    hovermode="x unified",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

# 7. 상세 데이터 표
with st.expander("📄 상세 데이터 표 보기"):
    st.dataframe(raw_data, use_container_width=True)
