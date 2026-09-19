import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")


# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # 장르 전처리: 세로막대 기호(|)로 분리된 경우 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"].astype(str).apply(lambda x: x.split("|")[0].strip())
    )

    return df


df = load_data()

st.markdown("---")

# --- 첫 번째 그래프 Section ---
st.header("1. 장르별 영화 편수 분포")

# 장르별 편수 집계
genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["장르", "편수"]

# Plotly 도넛 그래프 생성
fig1 = px.pie(
    genre_counts,
    values="편수",
    names="장르",
    title="장르별 영화 편수 비율",
    hole=0.4,  # 도넛 모양 만들기
)

# 마우스 호버 시 편수(value)와 비율(percent)이 보이도록 설정
fig1.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate="<b>장르: %{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)

st.plotly_chart(fig1, use_container_width=True)

# 그래프 1 하단 설명
st.markdown("---")
st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "박스오피스 상위권 영화 중 특정 주요 장르가 차지하는 비중과 장르별 다양성의 분포 형태를 직관적으로 파악할 수 있습니다."
)

st.write("<br><br>", unsafe_allow_html=True)

# --- 두 번째 그래프 Section ---
st.header("2. 장르 및 영화별 총 관객 수 트리맵")

# Plotly 트리맵 그래프 생성 (계층: 장르 -> 영화명, 크기: 총 관객)
fig2 = px.treemap(
    df,
    path=[px.Constant("전체"), "genre", "movieNm"],
    values="total_audi",
    title="장르 및 영화별 총 관객 수 분포",
    color="genre",
)

# 마우스 호버 시 영화명과 총 관객 수가 명확히 보이도록 설정
fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객 수: %{value:,}명<extra></extra>"
)

st.plotly_chart(fig2, use_container_width=True)

# 그래프 2 하단 설명
st.markdown("---")
st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "각 장르가 전체 관객 수에서 차지하는 비중과 해당 장르 내에서 흥행을 견인한 대표 영화들의 관객 수 기여도를 한눈에 비교할 수 있습니다."
)
