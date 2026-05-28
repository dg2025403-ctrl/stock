import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="한·미 주요 주식 수익률 비교 (Max 버전)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 모바일 최적화 스타일
st.markdown("""
    <style>
    .main .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    h1 {font-size: 1.8rem !important;}
    h3 {font-size: 1.3rem !important;}
    .stMetric {background-color: #f8f9fa; padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);}
    [data-testid="stMetricValue"] {font-size: 1.4rem !important;}
    </style>
""", unsafe_allow_html=True)

st.title("📊 한·미 주요 주식 수익률 비교 앱")
st.caption("스마트폰과 PC 어디서나 상장 이후 전체 기간까지 안전하게 비교해 보세요!")

# 2. 분석 조건 설정
st.subheader("⚙️ 분석 조건 설정")
col_period, col_bench = st.columns([1, 1])

with col_period:
    # '전체 기간(Max)' 옵션을 새로 추가했습니다!
    period_options = {
        "1개월": 30, 
        "3개월": 90, 
        "6개월": 180, 
        "1년": 365, 
        "5년": 365*5, 
        "올해(YTD)": "YTD", 
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

# 4. 안 걸리고 안전하게 데이터를 가져오는 핵심 함수 (캐싱 및 예외 처리)
@st.cache_data(ttl=86400)  # 하루(24시간) 동안 데이터를 저장해두고 재사용 (차단 방지 핵심)
def load_stock_data(tickers_tuple, period_key):
    """
    스트림릿 캐싱을 적용하여 사용자가 같은 기간을 조회할 때는 
    야후 서버에 다시 요청하지 않고 저장된 데이터를 즉시 보여줍니다.
    """
    data = pd.DataFrame()
    
    # 기간 설정 처리
    if period_key == "max":
        # 상장 이후 전체 데이터를 가져옵니다.
        for name in tickers_tuple:
            ticker = ticker_dict[name]
            # 전체 데이터를 긁어올 때 에러가 나면 패스하도록 안전장치 가동
            try:
                df = yf.download(ticker, period="max")
                if not df.empty and 'Close' in df.columns:
                    data[name] = df['Close']
            except Exception as e:
                st.warning(f"⚠️ {name} 데이터를 가져오는 중 오류 발생: {e}")
    else:
        # 특정 기간만 계산해서 가져오기
        end_date = datetime.today()
        if period_key == "YTD":
            start_date = datetime(end_date.year, 1, 1)
        else:
            start_date = end_date - timedelta(days=period_options[period_key])
            
        for name in tickers_tuple:
            ticker = ticker_dict[name]
            try:
                df = yf.download(ticker, start=start_date, end=end_date)
                if not df.empty and 'Close' in df.columns:
                    data[name] = df['Close']
            except Exception as e:
                pass
                
    # 데이터가 비어있는 행(휴일 등)을 깔끔하게 정리
    data = data.ffill().bfill()
    return data

# 스트림릿 캐싱을 위해 리스트를 튜플 형태로 변환하여 전달합니다.
with st.spinner('안전하게 데이터를 불러오는 중... (전체 기간 선택 시 최대 5~10초 소요)'):
    raw_data = load_stock_data(tuple(selected_tickers), selected_period)

if raw_data.empty:
    st.error("데이터를 불러오지 못했습니다. 종목을 다시 확인해 주세요.")
    st.stop()

# 누적 수익률 계산 (시작점 기준 0%로 정규화)
normalized_data = (raw_data / raw_data.iloc[0] - 1) * 100

# 5. 종목별 최종 누적 수익률 표시 (그리드 레이아웃)
st.markdown("---")
st.subheader("🔥 종목별 최종 누적 수익률")

metrics_cols = st.columns(len(selected_tickers))
for i, name in enumerate(selected_tickers):
    if name in normalized_data.columns:
        final_return = normalized_data[name].iloc[-1]
        if isinstance(final_return, pd.Series):
            final_return = final_return.iloc[0]
        
        current_price = raw_data[name].iloc[-1]
        if isinstance(current_price, pd.Series):
            current_price = current_price.iloc[0]
            
        unit = "원" if "(KR)" in name else "$"
        
        with metrics_cols[i]:
            st.metric(
                label=name, 
                value=f"{current_price:,.0f}{unit}" if unit=="원" else f"${current_price:,.2f}",
                delta=f"{final_return:+.2f}%"
            )

# 6. 반응형 차트 그리기
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
    margin=dict(l=20, r=20, t=20, b=20),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.3,
        xanchor="center",
        x=0.5
    ),
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

# 7. 데이터 표 다운로드 섹션
with st.expander("📄 상세 데이터 표 보기"):
    st.dataframe(raw_data.style.format(formatter="{:,.2f}"), use_container_width=True)
