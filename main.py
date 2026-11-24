import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="다이아몬드 가격 예측 모델 (Ridge Linear Model)",
    page_icon="💎",
    layout="wide"
)

@st.cache_resource
def load_model():
    with open("model_weights.json", "r", encoding="utf-8") as f:
        return json.load(f)

model = load_model()

def predict_price(carat, cut, color, clarity, depth, table, x, y, z):
    if x <= 0 or y <= 0 or z <= 0 or carat <= 0:
        return None
    volume = x * y * z
    xy_ratio = x / y
    log_carat = np.log(carat)
    log_volume = np.log(volume)

    raw_num = [log_carat, depth, table, log_volume, xy_ratio]
    scaled_num = [(val - m) / s for val, m, s in zip(raw_num, model["means"], model["scales"])]

    # One-hot encoding (drop='first' matches index >= 1)
    ohe_vec = []
    for val, cats in zip([cut, color, clarity], model["ohe_categories"]):
        for cat in cats[1:]:
            ohe_vec.append(1.0 if val == cat else 0.0)

    base_vec = np.array(scaled_num + ohe_vec, dtype=np.float64)
    powers = np.array(model["powers"], dtype=np.int32)
    coefs = np.array(model["coefs"], dtype=np.float64)

    # Polynomial degree 2 expansion
    poly_features = np.prod(np.power(base_vec, powers), axis=1)
    log_price_pred = model["intercept"] + np.dot(poly_features, coefs)
    return float(np.exp(log_price_pred))

def estimate_dimensions(carat, cut):
    # Standard Round Brilliant estimation based on carat weight
    cut_depth_map = {
        "Ideal": 61.8,
        "Premium": 61.3,
        "Very Good": 61.9,
        "Good": 62.2,
        "Fair": 63.5
    }
    cut_table_map = {
        "Ideal": 56.0,
        "Premium": 58.0,
        "Very Good": 58.0,
        "Good": 59.0,
        "Fair": 60.0
    }
    depth = cut_depth_map[cut]
    table = cut_table_map[cut]
    # Approximate diameter d from carat (d ≈ 6.45 * carat^(1/3))
    d = 6.45 * (carat ** (1.0 / 3.0))
    x = round(d, 2)
    y = round(d * 1.002, 2)
    z = round(((x + y) / 2.0) * (depth / 100.0), 2)
    return x, y, z, depth, table

st.title("💎 다이아몬드 가격 예측 웹앱 (Linear Ridge + 2차 상호작용)")
st.markdown(
    f"정제 데이터 **53,770건** (8:2 층화 분할 — 학습 `{model['metrics']['train_rows']:,}건` / 테스트 `{model['metrics']['test_rows']:,}건`) 기반 **Model C** 추론 앱입니다."
)

# Sidebar inputs
st.sidebar.header("1. 4C 등급 및 중량 설정")
carat = st.sidebar.slider("캐럿 (Carat)", min_value=0.20, max_value=3.50, value=1.00, step=0.01)
cut = st.sidebar.selectbox("컷 등급 (Cut)", ["Ideal", "Premium", "Very Good", "Good", "Fair"], index=0)
color = st.sidebar.selectbox("컬러 등급 (Color: D 최상 ~ J 최하)", ["D", "E", "F", "G", "H", "I", "J"], index=3)
clarity = st.sidebar.selectbox("투명도 등급 (Clarity: IF 최상 ~ I1 최하)", ["IF", "VVS1", "VVS2", "VS1", "VS2", "SI1", "SI2", "I1"], index=3)

st.sidebar.header("2. 물리적 치수 (mm) 및 비율")
auto_dim = st.sidebar.checkbox("캐럿·컷 기준 표준 치수 자동 계산", value=True)
est_x, est_y, est_z, est_depth, est_table = estimate_dimensions(carat, cut)

if auto_dim:
    x, y, z, depth, table = est_x, est_y, est_z, est_depth, est_table
    st.sidebar.info(f"자동 산출 치수: x={x}mm, y={y}mm, z={z}mm | Depth={depth}%, Table={table}%")
else:
    x = st.sidebar.number_input("길이 x (mm)", min_value=0.1, max_value=15.0, value=est_x, step=0.01)
    y = st.sidebar.number_input("너비 y (mm)", min_value=0.1, max_value=15.0, value=est_y, step=0.01)
    z = st.sidebar.number_input("깊이 z (mm)", min_value=0.1, max_value=10.0, value=est_z, step=0.01)
    depth = st.sidebar.number_input("깊이 비율 Depth (%)", min_value=40.0, max_value=80.0, value=est_depth, step=0.1)
    table = st.sidebar.number_input("테이블 비율 Table (%)", min_value=40.0, max_value=95.0, value=est_table, step=0.1)

# Prediction & Guardrails
pred_usd = predict_price(carat, cut, color, clarity, depth, table, x, y, z)

if pred_usd is None:
    st.error("물리적 치수(x, y, z) 및 캐럿은 0보다 커야 합니다.")
    st.stop()

if carat > 2.50:
    st.warning(
        f"주의: 현재 입력된 {carat:.2f}ct는 학습 데이터의 99% 이상이 밀집된 구간(0.20~2.50ct)을 초과합니다. "
        "2차 다항식 선형 모델 특성상 대캐럿 구간에서는 외삽(Extrapolation)으로 인해 예측 가격이 실제보다 과대 산출될 수 있습니다."
    )

mape = model["metrics"]["mape"] / 100.0
low_bound = pred_usd * (1 - mape)
high_bound = pred_usd * (1 + mape)
price_per_carat = pred_usd / carat
volume = x * y * z

# Top KPI Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("예측 가격 (USD)", f"${pred_usd:,.2f}")
col2.metric(f"예상 오차 범위 (±{model['metrics']['mape']}%)", f"${low_bound:,.0f} ~ ${high_bound:,.0f}")
col3.metric("캐럿당 단가 ($/ct)", f"${price_per_carat:,.2f}")
col4.metric("추정 부피 (mm³)", f"{volume:,.2f}")

st.divider()

# Charts: Carat Sensitivity Curve & Grade Comparison
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("캐럿 변화에 따른 가격 민감도 곡선")
    carat_grid = np.linspace(0.20, 2.50, 47)
    prices_grid = []
    for c_val in carat_grid:
        gx, gy, gz, gdepth, gtable = estimate_dimensions(c_val, cut)
        prices_grid.append(predict_price(c_val, cut, color, clarity, gdepth, gtable, gx, gy, gz))

    fig_curve = go.Figure()
    fig_curve.add_trace(go.Scatter(
        x=carat_grid, y=prices_grid, mode="lines",
        name=f"{cut} / {color} / {clarity} 곡선",
        line=dict(color="#1f77b4", width=2.5)
    ))
    if carat <= 2.50:
        fig_curve.add_trace(go.Scatter(
            x=[carat], y=[pred_usd], mode="markers",
            name="현재 선택 스펙",
            marker=dict(color="#d62728", size=11)
        ))
    fig_curve.update_layout(
        xaxis_title="캐럿 (Carat)",
        yaxis_title="예측 가격 (USD)",
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_curve, use_container_width=True)

with right_col:
    st.subheader("동일 중량·치수 기준 투명도(Clarity)별 가격 비교")
    clarities = ["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"]
    clarity_prices = [predict_price(carat, cut, color, cl, depth, table, x, y, z) for cl in clarities]
    colors_bar = ["#d62728" if cl == clarity else "#5b84b1" for cl in clarities]

    fig_bar = go.Figure(data=[
        go.Bar(
            x=clarities,
            y=clarity_prices,
            marker_color=colors_bar,
            text=[f"${p:,.0f}" for p in clarity_prices],
            textposition="outside"
        )
    ])
    fig_bar.update_layout(
        xaxis_title="투명도 등급 (Clarity)",
        yaxis_title="예측 가격 (USD)",
        height=380,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Model Benchmark Reference
with st.expander("모델 성능 검증 지표 및 아키텍처 정보 보기", expanded=False):
    st.markdown(
        f"""
        - **알고리즘:** Ridge Regression (`alpha=10.0`) + One-Hot Encoding + 2차 다항 상호작용항(275개 피처)
        - **타겟 변환:** `log(price)` 학습 후 `exp()` 역변환
        - **테스트셋(20%, 10,754행) 평가 지표:**
          - **RMSE:** `${model['metrics']['rmse']:.2f}`
          - **MAE:** `${model['metrics']['mae']:.2f}`
          - **MAPE:** `{model['metrics']['mape']:.2f}%`
          - **결정계수 ($R^2$):** `{model['metrics']['r2']:.5f}`
        """
    )
