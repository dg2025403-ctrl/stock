import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 페이지 기본 설정 (반응형 및 다크모드 대응을 위해 가로 폭을 자동으로 맞춤)
st.set_page_config(
    page_title="한·미 주요 주식 수익률 비교",
    page_icon="📈",
    layout="wide",  # 와이드 모드로 설정해야 PC와 모바일 모두에서 레이아웃이 유연하게 조절됩니다.
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS로 모바일 화면 최적화 (글자 크기 및 여백 조정)
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
st.caption("스마트폰과 PC 어디서나 실시간(종가 기준)으로 수익률을 비교해 보세요!")

# 2. 사이드바 / 상단 컨트롤러 (모바일에서는 상단 배치됨)
st.subheader("⚙️ 분석 조건 설정")
col_period, col_bench = st.columns([1, 1])

with col_period:
    period_options = {"1개월": 30, "3개월": 90, "6개월": 180, "1년": 365, "올해(YTD)": "YTD"}
    selected_period = st.selectbox("📅 분석 기간 선택", list(period_options.keys()), index=1)

# 기간 계산
end_date = datetime.today()
if selected_period == "올해(YTD)":
    start_date = datetime(end_date.year, 1, 1)
else:
    start_date = end_date - timedelta(days=period_options[selected_period])

# 3. 비교할 주식 종목 정의 (한국/미국 대표 주식)
# 한국 종목은 뒤에 .KS, .KQ 필요
ticker_dict = {
    "삼성전자 (KR)": "005930.KS",
    "SK하이닉스 (KR)": "000660.KS",
    "Apple (US)": "AAPL",
    "Microsoft (US)": "MSFT",
    "NVIDIA (US)": "NVDA",
    "Tesla (US)": "TSLA"
}

# 멀티셀렉트로 사용자가 종목을 뺐다 넣었다 할 수 있게 구현
selected_tickers = st.multiselect(
    "🔍 비교할 종목 선택", 
    list(ticker_dict.keys()), 
    default=list(ticker_dict.keys())
)

if not selected_tickers:
    st.warning("⚠️ 최소 하나의 종목을 선택해 주세요!")
    st.stop()

# 4. 데이터 로드 및 수익률 계산 (캐싱 적용으로 속도 향상)
@st.cache_data(ttl=3600)  # 1시간 동안 데이터 캐싱
def load_data(tickers, start, end):
    data = pd.DataFrame()
    for name in tickers:
        ticker = ticker_dict[name]
        df = yf.download(ticker, start=start, end=end)
        if not df.empty:
            # yfinance 최신 버전의 MultiIndex 대응을 위해 Close 가격만 안전하게 추출
            if 'Close' in df.columns:
                data[name] = df['Close']
    return data

with st.spinner('실시간 주가 데이터를 가져오는 중...'):
    raw_data = load_data(selected_tickers, start_date, end_date)

if raw_data.empty:
    st.error("데이터를 불러오지 못했습니다. 선택한 기간이나 종목을 확인해 주세요.")
    st.stop()

# 누적 수익률 계산 (시작일 기준 0%부터 얼마나 올랐는지 계산)
# $ \text{수익률} = \left( \frac{\text{현재가}}{\text{시작 주가}} - 1 \right) \times 100 $
normalized_data = (raw_data / raw_data.iloc[0] - 1) * 100

# 5. 대시보드 화면 구성
st.markdown("---")
st.subheader("🔥 종목별 최종 누적 수익률")

# 모바일 환경을 고려하여 그리드(컬럼) 배치 (종목이 많으면 자동으로 줄바꿈됨)
metrics_cols = st.columns(len(selected_tickers))
for i, name in enumerate(selected_tickers):
    if name in normalized_data.columns:
        final_return = normalized_data[name].iloc[-1]
        # 값이 단일 시리즈나 스칼라가 되도록 처리
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

st.markdown("---")
st.subheader("📈 수익률 추이 비교 차트")

# Plotly를 활용한 반응형 선그래프 생성
fig = go.Figure()
for name in selected_tickers:
    if name in normalized_data.columns:
        fig.add_trace(go.Scatter(
            x=normalized_data.index, 
            y=normalized_data[name], 
            mode='lines', 
            name=name
        ))

# 차트 레이아웃 설정 (모바일에서 여백 최소화 및 범례 아래로 이동)
fig.update_layout(
    xaxis_title="날짜",
    yaxis_title="수익률 (%)",
    hovermode="x unified",
    margin=dict(l=20, r=20, t=20, b=20),
    legend=dict(
        orientation="h",       # 범례를 가로로 배치
        yanchor="bottom",
        y=-0.3,                # 차트 아래쪽에 배치하여 모바일 가로폭 확보
        xanchor="center",
        x=0.5
    ),
    template="plotly_white"
)

# use_container_width=True 가 모바일/PC 화면 크기에 맞춰 그래프를 자동으로 늘였다 줄였다 해줍니다.
st.plotly_chart(fig, use_container_width=True)

# 6. 데이터 표 제공
with st.expander("📄 상세 데이터 표 보기"):
    st.dataframe(raw_data.style.format(formatter="{:,.2f}"), use_container_width=True)
