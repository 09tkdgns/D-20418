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
# [세 번째 구역] 장기 흥행(20일 이상 차트인) Top 5 영화 누적 관객 수 비교
# -------------------------------------------------------------------
st.header("3. 장기 흥행 상위 5개 영화 누적 관객 수 비교")

# 1. 영화별 차트 진입 일수(데이터 등장 횟수) 계산
movie_days = df.groupby('영화명')['기준일자'].count()

# 2. 20일 이상 등장한 영화들만 필터링
movies_over_20days = movie_days[movie_days >= 20].index

# 3. 20일 이상 등장한 영화 중에서 최대 누적관객수 기준 내림차순 정렬 후 상위 5개 추출
top5_longterm_movies = (
    df[df['영화명'].isin(movies_over_20days)]
    .groupby('영화명')['누적관객수']
    .max()
    .sort_values(ascending=False)
    .head(5)
    .index
    .tolist()
)

# 4. 상위 5개 영화 데이터만 필터링
top5_df = df[df['영화명'].isin(top5_longterm_movies)]

# 5. 다중 선 그래프 생성
fig3 = px.line(
    top5_df,
    x='기준일자',
    y='누적관객수',
    color='영화명',  # 영화별 색상 및 범례 분리
    title="TOP 10 차트 20일 이상 유지 영화 중 상위 5개작 누적 관객수 추이",
    labels={'기준일자': '날짜', '누적관객수': '누적 관객 수(명)', '영화명': '영화 제목'}
)

# 그래프 화면에 출력
st.plotly_chart(fig3, use_container_width=True)

# 그래프 설명문
st.caption("💡 **이 그래프로 알 수 있는 것:** 20일 이상 장기 흥행한 영화들 간의 누적 관객수 축적 속도와 최종 흥행 규모를 한눈에 비교할 수 있습니다.")
