import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정 (넓은 화면 모드)
st.set_page_config(page_title="박스오피스 데이터 분석", layout="wide")

# App 제목
st.title("🎬 영화 박스오피스 데이터 분석")

# -------------------------------------------------------------------
# [1. 데이터 불러오기]
# @st.cache_data를 사용해 매번 새로 받아오지 않고 캐싱(임시 저장)합니다.
# -------------------------------------------------------------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    data = pd.read_csv(url)
    
    # [2. 날짜 전처리]
    # 결측치(빈 데이터)가 포함된 행 삭제
    data = data.dropna()
    
    # '기준일자' 컬럼을 datetime 형식으로 변환
    data['기준일자'] = pd.to_datetime(data['기준일자'])
    
    # 기준일자 오름차순 정렬
    data = data.sort_values(by='기준일자')
    
    return data

# 데이터 로드 실행
df = load_data()

# -------------------------------------------------------------------
# [3. 영화 선택 기능]
# 누적관객수가 가장 높은 순서대로 영화 목록 정리 후 사이드바에 배치
# -------------------------------------------------------------------
# 영화별 최대 누적관객수를 구해 내림차순 정렬
movie_order = (
    df.groupby('영화명')['누적관객수']
    .max()
    .sort_values(ascending=False)
    .index
    .tolist()
)

# 사이드바에서 영화 선택
st.sidebar.header("설정")
selected_movie = st.sidebar.selectbox("영화 선택 (누적관객수 순)", movie_order)

# 선택한 영화의 데이터만 필터링
movie_df = df[df['영화명'] == selected_movie]

# -------------------------------------------------------------------
# [첫 번째 구역] 일별 관객 수 추이 (선 그래프)
# -------------------------------------------------------------------
st.header("1. 일별 관객 수 추이")

# 선택한 영화의 기준일자별 해당일관객수 Plotly 선 그래프
fig1 = px.line(
    movie_df, 
    x='기준일자', 
    y='해당일관객수',
    title=f"'{selected_movie}' 일별 관객수 변화",
    labels={'기준일자': '날짜', '해당일관객수': '관객 수(명)'},
    markers=True  # 데이터 지점에 점 표시
)

# 그래프 화면에 출력
st.plotly_chart(fig1, use_container_width=True)

# 그래프 설명문
st.caption("💡 **이 그래프로 알 수 있는 것:** 개봉 후 일자별 관객수의 증감 추이와 흥행 피크 시점을 확인할 수 있습니다.")

st.divider()  # 구역 구분선

# -------------------------------------------------------------------
# [두 번째 구역] 누적 관객 수 추이 (영역 차트)
# -------------------------------------------------------------------
st.header("2. 누적 관객 수 추이")

# 선택한 영화의 기준일자별 누적관객수 Plotly 영역 차트(Area Chart)
fig2 = px.area(
    movie_df,
    x='기준일자',
    y='누적관객수',
    title=f"'{selected_movie}' 누적 관객수 성장 추이",
    labels={'기준일자': '날짜', '누적관객수': '누적 관객 수(명)'}
)

# 그래프 화면에 출력
st.plotly_chart(fig2, use_container_width=True)

# 그래프 설명문
st.caption("💡 **이 그래프로 알 수 있는 것:** 시간이 지남에 따라 전체 관객수가 얼마나 지속적으로 증가하고 축적되었는지 확인할 수 있습니다.")

st.divider()  # 구역 구분선

# -------------------------------------------------------------------
# 앞으로 추가할 그래프를 위한 예시 구역
# -------------------------------------------------------------------
st.header("3. 추가 분석 구역 (예정)")
st.info("📌 추후 새로운 분석 그래프가 이곳에 추가될 예정입니다.")
st.caption("💡 **이 그래프로 알 수 있는 것:** (추후 추가될 그래프 분석 결과 문구 자리)")
