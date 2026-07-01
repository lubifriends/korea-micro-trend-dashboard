"""Korea Micro Trend Dashboard - Streamlit 메인 실행 파일."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from components.cards import render_trend_cards
from components.charts import render_charts
from components.filters import render_filters
from utils.fetch_google_trends import fetch_google_trends
from utils.fetch_news import enrich_with_news
from utils.fetch_youtube import fetch_youtube_trends
from utils.scoring import merge_and_score
from utils.storage import SAMPLE_PATH, append_history, bootstrap_from_sample, load_history, save_current


load_dotenv()  # 로컬의 .env 파일을 읽습니다. 파일이 없어도 오류가 나지 않습니다.
st.set_page_config(page_title="Korea Micro Trend Dashboard", page_icon="📡", layout="wide")


def get_secret(name: str) -> str:
    """Cloud의 Secrets를 우선 사용하고, 로컬에서는 .env를 사용합니다."""
    try:
        return str(st.secrets.get(name, "") or os.getenv(name, ""))
    except (FileNotFoundError, KeyError):
        return os.getenv(name, "")


def refresh_data(previous: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """수동 갱신 버튼이 실행하는 전체 수집 흐름입니다."""
    messages: list[str] = []
    google_rows, google_status = fetch_google_trends()
    messages.append(google_status)

    if google_rows:
        google_rows, news_status = enrich_with_news(google_rows, limit=10)
        messages.append(news_status)

    youtube_api_key = get_secret("YOUTUBE_API_KEY")
    youtube_rows, youtube_status = fetch_youtube_trends(
        api_key=youtube_api_key,
        sample_path=SAMPLE_PATH,
    )
    messages.append(youtube_status)
    collected = google_rows + youtube_rows

    # 네트워크가 모두 실패해도 샘플 데이터 덕분에 빈 화면이 되지 않습니다.
    if not collected or (not google_rows and not youtube_api_key):
        sample = bootstrap_from_sample()
        messages.append("모든 외부 수집이 실패하여 전체 샘플 데이터를 표시합니다.")
        return sample, messages

    scored = merge_and_score(collected, previous)
    if scored.empty:
        return bootstrap_from_sample(), messages + ["가공 결과가 없어 샘플 데이터를 표시합니다."]
    save_current(scored)
    append_history(scored)
    return scored, messages


def format_korean_time(value: object) -> str:
    timestamp = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(timestamp):
        return "아직 없음"
    return timestamp.tz_convert("Asia/Seoul").strftime("%Y-%m-%d %H:%M:%S KST")


st.markdown(
    """
    <style>
      :root { color-scheme: dark; }
      .stApp { background: radial-gradient(circle at 15% 0%, #12243c 0, #07111f 35%, #050914 100%); }
      .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp label { color: #e8f0f7; }
      [data-testid="stSidebar"] { background: #08111f; border-right: 1px solid #1d334d; }
      .block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1500px; }
      .hero { border: 1px solid #1f3b53; border-radius: 22px; padding: 1.35rem 1.5rem;
              background: linear-gradient(135deg, rgba(19,45,68,.92), rgba(7,15,29,.92));
              box-shadow: 0 18px 55px rgba(0,0,0,.28); margin-bottom: 1rem; }
      .hero-kicker { color: #5eead4; font-size: .78rem; font-weight: 800; letter-spacing: .16em; }
      .hero h1 { color:#f8fafc; margin: .25rem 0; font-size: clamp(1.8rem, 4vw, 3.2rem); letter-spacing: -.04em; }
      .hero p { color: #9fb2c7; margin: 0; }
      .live-dot { display:inline-block; width:8px; height:8px; margin-right:7px; border-radius:50%; background:#34d399;
                  box-shadow:0 0 14px #34d399; }
      .trend-card { min-height: 285px; padding: 1.25rem; margin: .4rem 0 .9rem; border-radius: 18px;
                    background: linear-gradient(155deg, rgba(18,35,55,.96), rgba(8,17,31,.98));
                    border: 1px solid #203c55; box-shadow: 0 12px 32px rgba(0,0,0,.22); }
      .card-top { display:flex; justify-content:space-between; align-items:center; }
      .rank { color:#5eead4; font-weight:900; font-size:1.1rem; letter-spacing:.08em; }
      .status { padding:.25rem .55rem; border-radius:999px; font-size:.75rem; font-weight:800; }
      .status.new { color:#07111f; background:#5eead4; } .status.up { color:#062312; background:#4ade80; }
      .status.watch { color:#2a1800; background:#fbbf24; } .status.down { color:#fff; background:#f43f5e; }
      .trend-card h3 { color:#f8fafc; margin:.8rem 0 .1rem; font-size:1.45rem; line-height:1.25; }
      .score { color:#f8fafc; font-size:2.6rem; font-weight:900; line-height:1; }
      .score small { color:#71869d; font-size:.8rem; font-weight:600; }
      .trend-card p { color:#b6c5d4; min-height:3.2rem; line-height:1.55; }
      .meta { display:flex; gap:.45rem; flex-wrap:wrap; color:#8fa5ba; font-size:.78rem; margin-bottom:.8rem; }
      .meta span { border:1px solid #28445f; border-radius:999px; padding:.22rem .48rem; }
      .meta .category { color:#93c5fd; border-color:#315b85; }
      .card-link { color:#5eead4 !important; text-decoration:none; font-weight:750; }
      .card-link.muted { color:#66788a !important; }
      div[data-testid="stMetric"] { background:#0d1a2b; border:1px solid #1f3b53; padding:1rem; border-radius:15px; }
      @media (max-width: 640px) { .block-container { padding:1rem .8rem 3rem; } .hero { padding:1rem; } .trend-card { min-height:auto; } }
    </style>
    """,
    unsafe_allow_html=True,
)


if "trend_data" not in st.session_state:
    st.session_state.trend_data = bootstrap_from_sample()
if "collection_messages" not in st.session_state:
    st.session_state.collection_messages = ["앱 시작 완료 · 갱신 버튼을 누르면 공개 피드를 확인합니다."]

data: pd.DataFrame = st.session_state.trend_data
latest_time = data["last_seen"].max() if not data.empty and "last_seen" in data else None
st.markdown(
    f"""
    <section class="hero">
      <div class="hero-kicker"><span class="live-dot"></span>KOREA · MICRO SIGNAL BOARD</div>
      <h1>Korea Micro Trend Dashboard</h1>
      <p>10~30분 단위의 작은 관심 변화를 공개 RSS와 공식 API로 모아 보는 실용형 전광판</p>
    </section>
    """,
    unsafe_allow_html=True,
)

top_left, top_middle, top_right = st.columns([1.2, 1.2, 1])
top_left.metric("마지막 갱신", format_korean_time(latest_time))
top_middle.metric("현재 키워드", f"{len(data):,}개")
with top_right:
    if st.button("🔄 지금 수동 갱신", type="primary", width="stretch"):
        with st.spinner("공개 피드와 API를 확인하고 있습니다…"):
            refreshed, messages = refresh_data(data)
            st.session_state.trend_data = refreshed
            st.session_state.collection_messages = messages
        st.rerun()

with st.expander("전체 수집 상태", expanded=False):
    for message in st.session_state.collection_messages:
        icon = "⚠️" if "실패" in message else "✅"
        st.write(f"{icon} {message}")
    st.caption("YouTube API 키가 없을 때는 샘플 영상이 표시됩니다. 네이버 데이터랩은 다음 버전의 연결 자리만 준비되어 있습니다.")

filtered, _ = render_filters(data)
st.subheader("⚡ 지금 뜨는 급상승 키워드")
render_trend_cards(filtered)

st.divider()
st.subheader("📊 트렌드 구성")
render_charts(filtered, load_history())

st.divider()
st.subheader("🔬 키워드 상세")
if filtered.empty:
    st.info("상세 정보를 볼 키워드가 없습니다.")
else:
    selected_keyword = st.selectbox("자세히 볼 키워드", filtered["keyword"].astype(str).tolist())
    detail = filtered[filtered["keyword"].astype(str) == selected_keyword].iloc[0]
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("트렌드 점수", f"{float(detail.get('score', 0)):.1f}")
    d2.metric("상태", str(detail.get("status", "관찰")))
    d3.metric("누적 발견", f"{int(float(detail.get('sighting_count', 1)))}회")
    d4.metric("동시 출처", f"{int(float(detail.get('source_count', 1)))}개")
    st.write(str(detail.get("summary", "설명이 없습니다.")))
    st.write(f"**최초 발견:** {format_korean_time(detail.get('first_seen'))}")
    st.write(f"**마지막 발견:** {format_korean_time(detail.get('last_seen'))}")
    st.write(f"**출처:** {detail.get('source', '-')}")
    st.info(f"점수 계산 근거 · {detail.get('score_reason', '샘플 데이터의 예시 점수입니다.')}")
    titles = str(detail.get("related_title", "")).split(" | ")
    urls = str(detail.get("related_url", "")).split(" | ")
    if any(title.strip() for title in titles):
        st.markdown("**관련 뉴스·영상**")
        for index, title in enumerate(titles):
            if not title.strip():
                continue
            url = urls[index] if index < len(urls) else ""
            st.markdown(f"- [{title}]({url})" if url.startswith("http") else f"- {title}")

st.caption("공개 RSS와 공식 API만 사용합니다 · CSV 기반 MVP · 표시 내용은 투자·의료·법률 조언이 아닙니다.")
