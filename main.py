import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="토스 스타일 주식 분석기",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 토스 감성의 깔끔한 CSS 스타일 적용
st.markdown("""
    <style>
    .main .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    h1 {font-size: 2.2rem !important; font-weight: 700; color: #191f28;}
    h2 {font-size: 1.6rem !important; font-weight: 700; color: #191f28;}
    h3 {font-size: 1.2rem !important; font-weight: 600; color: #4e5968;}
    p {color: #4e5968; font-size: 1rem;}
    </style>
""", unsafe_allow_html=True)

st.title("💸 토스 스타일 주식 분석기")
st.markdown("""
안녕하세요! 토스증권 앱처럼 깔끔하고 보기 편하게 만든 한·미 주요 주식 수익률 비교 서비스입니다.

**왼쪽 사이드바 메뉴**를 통해 원하는 화면으로 쏙쏙 이동해 보세요!
* **🏠 홈 (실시간 수익률):** 선택한 관심 종목들의 현재가와 기간 내 총 수익률을 토스 카드로 확인합니다.
* **📈 수익률 비교 차트:** 여러 종목의 주가 상승 곡선을 한눈에 겹쳐서 비교합니다.
* **📄 상세 데이터:** 날짜별 정확한 주가 수치를 표 형태로 확인하고 다운로드합니다.
""")

st.info("💡 모바일이나 화면이 작아 왼쪽 메뉴가 보이지 않는다면, 왼쪽 상단의 '>' 모양 버튼을 눌러 메뉴창을 열어주세요.")
