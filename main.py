import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

st.divider()  # 구역 구분선

# -------------------------------------------------------------------
# [네 번째 구역] 전체 박스오피스 일별 관객수 합계 및 7일 이동평균선
# -------------------------------------------------------------------
st.header("4. 전체 박스오피스 일별 관객수 추이 및 7일 이동평균")

# 1. 기준일자별 TOP10 영화의 해당일관객수 총합 계산
daily_total = df.groupby('기준일자')['해당일관객수'].sum().reset_index()

# 2. 7일 이동평균 계산 (rolling window 사용, 초기 결측값은 min_periods=1로 처리)
daily_total['7일_이동평균'] = daily_total['해당일관객수'].rolling(window=7, min_periods=1).mean()

# 3. Plotly Graph Objects를 이용해 원본 선과 이동평균 선을 겹쳐서 작성
fig4 = go.Figure()

# 원본 일별 관객수 (연한 색상, 반투명)
fig4.add_trace(go.Scatter(
    x=daily_total['기준일자'],
    y=daily_total['해당일관객수'],
    mode='lines',
    name='일별 총 관객수',
    line=dict(color='lightskyblue', width=1.5),
    opacity=0.6
))

# 7일 이동평균선 (진한 색상, 두껍게)
fig4.add_trace(go.Scatter(
    x=daily_total['기준일자'],
    y=daily_total['7일_이동평균'],
    mode='lines',
    name='7일 이동평균',
    line=dict(color='firebrick', width=3)
))

# 그래프 레이아웃 설정
fig4.update_layout(
    title="전체 박스오피스 일별 관객수 합계 및 7일 이동평균 추이",
    xaxis_title="날짜",
    yaxis_title="관객 수(명)",
    legend_title="구분",
    hovermode="x unified"  # 마우스 커서 위치의 x축 값을 일괄 표시
)

# 그래프 화면에 출력
st.plotly_chart(fig4, use_container_width=True)

# 그래프 설명문
st.caption("💡 **이 그래프로 알 수 있는 것:** 주말/평일 변동에 따른 일별 변동성을 완화한 7일 이동평균선을 통해 전체 영화 시장의 장기적인 관객수 증감 흐름과 성수기/비성수기 추세를 명확하게 파악할 수 있습니다.")

st.divider()  # 구역 구분선

# -------------------------------------------------------------------
# [다섯 번째 구역] 월별 전체 관객수 합계 (막대 그래프)
# -------------------------------------------------------------------
st.header("5. 월별 전체 관객수 합계")

# 1. '기준일자'에서 '연-월(YYYY-MM)' 형태의 컬럼 생성
daily_total['연월'] = daily_total['기준일자'].dt.strftime('%Y-%m')

# 2. 월(연월) 단위로 그룹화하여 해당일관객수 총합 계산
monthly_total = daily_total.groupby('연월')['해당일관객수'].sum().reset_index()

# 3. Plotly Express를 활용한 월별 막대 그래프 생성
fig5 = px.bar(
    monthly_total,
    x='연월',
    y='해당일관객수',
    title="월별 박스오피스 전체 관객수 합계",
    labels={'연월': '월(Year-Month)', '해당일관객수': '총 관객 수(명)'},
    text_auto='.2s'  # 막대 상단에 간략화된 수치 표시 (예: 1.5M)
)

# X축을 문자열 카테고리 형태로 고정하여 월 순서가 유지되도록 설정
fig5.update_xaxes(type='category')

# 그래프 화면에 출력
st.plotly_chart(fig5, use_container_width=True)

# 그래프 설명문
st.caption("💡 **이 그래프로 알 수 있는 것:** 월 단위 총 관객수 비교를 통해 어느 달에 극장가 이용객이 집중되었는지 월별 성수기 및 비성수기 규모를 명확히 비교할 수 있습니다.")
