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
    hole=0.4,
)

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

fig2 = px.treemap(
    df,
    path=[px.Constant("전체"), "genre", "movieNm"],
    values="total_audi",
    title="장르 및 영화별 총 관객 수 분포",
    color="genre",
)

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

st.write("<br><br>", unsafe_allow_html=True)

# --- 세 번째 그래프 Section ---
st.header("3. 총 관객 수 분포 히스토그램")

# Plotly 히스토그램 생성
fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    title="영화별 총 관객 수 분포",
    labels={"total_audi": "총 관객 수(명)"},
)

fig3.update_traces(
    hovertemplate="관객 수 구간: %{x:,}명<br>영화 수: %{y}편<extra></extra>"
)

st.plotly_chart(fig3, use_container_width=True)

# 최다 관객 영화 정보 동적 추출
top_movie = df.loc[df["total_audi"].idxmax()]
top_movie_name = top_movie["movieNm"]
top_movie_audi = top_movie["total_audi"]

# 그래프 3 하단 설명
st.markdown("---")
st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    f"• **밀집 구간**: 대부분의 영화가 약 200만 명 이하의 상대적으로 하위 관객 수 구간에 몰려 있는 오른쪽으로 긴 꼬리를 가진 분포 형태를 보입니다.<br>"
    f"• **최다 관객 영화**: 이 기간 동안 가장 많은 관객을 동원한 1위 영화는 **'{top_movie_name}'**(총 {top_movie_audi:,}명)입니다.",
    unsafe_allow_html=True,
)
