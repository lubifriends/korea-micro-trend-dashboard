"""Korea Micro Trend Dashboard - Streamlit 메인 앱."""

from __future__ import annotations

import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from components.cards import render_trend_cards
from components.charts import render_charts
from components.filters import render_filters
from utils.fetch_google_trends import fetch_google_trends
from utils.fetch_naver_datalab import fetch_naver_age_reactions
from utils.fetch_news import enrich_with_news
from utils.scoring import merge_and_score, normalize_keyword
from utils.storage import (
    append_history,
    load_live_current,
    load_live_history,
    load_sample,
    save_current,
)


load_dotenv()
st.set_page_config(page_title="Korea Micro Trend Dashboard", page_icon="📡", layout="wide")


def get_secret(name: str) -> str:
    """Cloud에서는 Secrets, 로컬에서는 .env 값을 읽습니다."""
    try:
        return str(st.secrets.get(name, "") or os.getenv(name, ""))
    except (FileNotFoundError, KeyError):
        return os.getenv(name, "")


def naver_credentials() -> tuple[str, str]:
    """새 NAVER API HUB 키를 우선하고 기존 개발자센터 키도 호환합니다."""
    client_id = get_secret("NAVER_API_HUB_CLIENT_ID") or get_secret("NAVER_CLIENT_ID")
    client_secret = get_secret("NAVER_API_HUB_CLIENT_SECRET") or get_secret("NAVER_CLIENT_SECRET")
    return client_id, client_secret


def refresh_data(previous: pd.DataFrame) -> tuple[pd.DataFrame, list[str], bool]:
    """실데이터만 수집합니다. 실패해도 샘플을 섞거나 저장하지 않습니다."""
    messages: list[str] = []
    google_rows, google_status = fetch_google_trends()
    messages.append(google_status)

    if not google_rows:
        messages.append("실데이터 수집 실패: 기존 실데이터를 유지합니다.")
        return previous, messages, False

    google_rows, news_status = enrich_with_news(google_rows, limit=10)
    messages.append(news_status)

    client_id, client_secret = naver_credentials()
    naver_rows, naver_status = fetch_naver_age_reactions(
        [str(row.get("keyword", "")) for row in google_rows],
        client_id=client_id,
        client_secret=client_secret,
        limit=10,
    )
    messages.append(naver_status)

    # 네이버 데이터는 새 키워드를 만드는 대신 Google에서 발견한 키워드를 보강합니다.
    naver_by_keyword = {normalize_keyword(row["keyword"]): row for row in naver_rows}
    for row in google_rows:
        reaction = naver_by_keyword.get(normalize_keyword(row.get("keyword")))
        if not reaction:
            continue
        row.update(reaction)
        sources = [item.strip() for item in str(row.get("source", "")).split(" | ") if item.strip()]
        row["source"] = " | ".join(dict.fromkeys(sources + ["NAVER DataLab"]))

    scored = merge_and_score(google_rows, previous)
    if scored.empty:
        messages.append("가공 결과가 없어 기존 실데이터를 유지합니다.")
        return previous, messages, False

    scored["data_mode"] = "live"
    save_current(scored)
    append_history(scored)
    return scored, messages, True


def format_korean_time(value: object) -> str:
    timestamp = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(timestamp):
        return "아직 수집 전"
    return timestamp.tz_convert("Asia/Seoul").strftime("%m월 %d일 %H:%M KST")


def safe_number(value: object) -> float:
    number = pd.to_numeric(value, errors="coerce")
    return 0.0 if pd.isna(number) else float(number)


def reaction_text(value: object) -> str:
    number = safe_number(value)
    if number >= 65:
        return f"강함 · {number:.1f}"
    if number >= 25:
        return f"반응 · {number:.1f}"
    if number > 0:
        return f"낮음 · {number:.1f}"
    return "데이터 없음"


def theme_styles(mode: str) -> str:
    dark = """
      --bg:#060a12; --bg-soft:#0a1220; --panel:#0d1726; --panel-2:#111e30;
      --text:#edf4fb; --muted:#91a3b8; --border:#203650; --accent:#5eead4;
      --accent-2:#60a5fa; --shadow:rgba(0,0,0,.32); --input:#0b1422;
    """
    light = """
      --bg:#f3f6fb; --bg-soft:#eaf0f8; --panel:#ffffff; --panel-2:#f8fafc;
      --text:#132033; --muted:#607188; --border:#d7e0ec; --accent:#0f9f91;
      --accent-2:#2563eb; --shadow:rgba(30,60,95,.12); --input:#ffffff;
    """
    variables = light if mode == "주간" else dark
    system_override = f"@media (prefers-color-scheme: light) {{ .stApp {{ {light} }} }}" if mode == "시스템" else ""
    return f"""
    <style>
      .stApp {{ {variables} color-scheme:{'light' if mode == '주간' else 'dark'};
        background:
          radial-gradient(circle at 12% -10%, color-mix(in srgb, var(--accent-2) 16%, transparent), transparent 31%),
          radial-gradient(circle at 88% 5%, color-mix(in srgb, var(--accent) 10%, transparent), transparent 27%),
          var(--bg); color:var(--text); }}
      {system_override}
      .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp label {{ color:var(--text); }}
      [data-testid="stSidebar"] {{ background:color-mix(in srgb, var(--bg-soft) 96%, transparent); border-right:1px solid var(--border); }}
      [data-testid="stSidebar"] * {{ color:var(--text); }}
      header[data-testid="stHeader"] {{ background:color-mix(in srgb, var(--bg) 94%, transparent); }}
      [data-testid="stSegmentedControl"] button {{ background:var(--panel-2)!important; color:var(--text)!important; border-color:var(--border)!important; }}
      [data-testid="stSegmentedControl"] button[aria-pressed="true"] {{ background:color-mix(in srgb,var(--accent) 28%,var(--panel))!important; }}
      [data-baseweb="select"] > div, [data-baseweb="input"] > div {{ background:var(--input); border-color:var(--border); }}
      .block-container {{ padding-top:1.4rem; padding-bottom:4rem; max-width:1480px; }}
      .hero {{ position:relative; overflow:hidden; padding:1.65rem 1.8rem; border:1px solid var(--border); border-radius:24px;
        background:linear-gradient(135deg, color-mix(in srgb, var(--panel-2) 96%, var(--accent-2)), var(--panel));
        box-shadow:0 24px 70px var(--shadow); margin-bottom:1rem; }}
      .hero::after {{ content:""; position:absolute; width:260px; height:260px; right:-80px; top:-140px; border-radius:50%;
        background:var(--accent); filter:blur(10px); opacity:.10; }}
      .hero-top {{ display:flex; align-items:center; justify-content:space-between; gap:1rem; }}
      .hero-kicker {{ color:var(--accent); font-size:.76rem; font-weight:850; letter-spacing:.16em; }}
      .mode-pill {{ color:var(--muted); background:var(--bg-soft); border:1px solid var(--border); border-radius:999px; padding:.32rem .68rem; font-size:.72rem; }}
      .hero h1 {{ color:var(--text); margin:.35rem 0 .25rem; font-size:clamp(2rem,4.4vw,3.55rem); letter-spacing:-.055em; line-height:1.02; }}
      .hero p {{ color:var(--muted); margin:.65rem 0 0; max-width:780px; line-height:1.6; }}
      .live-dot {{ display:inline-block; width:8px; height:8px; margin-right:7px; border-radius:50%; background:#34d399; box-shadow:0 0 14px #34d399; }}
      .sample-banner, .empty-banner {{ border-radius:16px; padding:.85rem 1rem; margin:.6rem 0 1rem; line-height:1.5; }}
      .sample-banner {{ color:#7c2d12; background:#fff7ed; border:1px solid #fdba74; }}
      .empty-banner {{ color:var(--text); background:var(--panel); border:1px dashed var(--border); }}
      div[data-testid="stMetric"] {{ background:linear-gradient(145deg,var(--panel),var(--panel-2)); border:1px solid var(--border);
        padding:1rem 1.05rem; border-radius:17px; box-shadow:0 10px 30px var(--shadow); }}
      div[data-testid="stMetric"] label {{ color:var(--muted)!important; }}
      .trend-card {{ min-height:335px; padding:1.25rem; margin:.35rem 0 .9rem; border-radius:20px;
        background:linear-gradient(155deg,var(--panel-2),var(--panel)); border:1px solid var(--border);
        box-shadow:0 14px 38px var(--shadow); transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease; }}
      .trend-card:hover {{ transform:translateY(-3px); border-color:color-mix(in srgb,var(--accent) 55%,var(--border)); box-shadow:0 20px 48px var(--shadow); }}
      .card-top {{ display:flex; justify-content:space-between; align-items:center; }}
      .rank {{ color:var(--accent); font-weight:900; font-size:1.05rem; letter-spacing:.1em; }}
      .status {{ padding:.27rem .6rem; border-radius:999px; font-size:.72rem; font-weight:850; }}
      .status.new {{ color:#073b35; background:#5eead4; }} .status.up {{ color:#063a1d; background:#4ade80; }}
      .status.watch {{ color:#4a2c00; background:#fbbf24; }} .status.down {{ color:#fff; background:#f43f5e; }}
      .trend-card h3 {{ color:var(--text); margin:.9rem 0 .25rem; font-size:1.45rem; line-height:1.25; letter-spacing:-.02em; }}
      .score {{ color:var(--text); font-size:2.55rem; font-weight:900; line-height:1; }}
      .score small {{ color:var(--muted); font-size:.75rem; font-weight:650; }}
      .score-track {{ height:5px; border-radius:999px; background:var(--bg-soft); margin:.65rem 0 .25rem; overflow:hidden; }}
      .score-track i {{ display:block; height:100%; border-radius:999px; background:linear-gradient(90deg,var(--accent-2),var(--accent)); }}
      .trend-card p {{ color:var(--muted); min-height:3.1rem; line-height:1.55; font-size:.92rem; }}
      .age-signals {{ display:flex; gap:.45rem; align-items:center; flex-wrap:wrap; margin:.55rem 0 .8rem; }}
      .age-signals span {{ color:var(--muted); background:var(--bg-soft); border:1px solid var(--border); padding:.28rem .5rem; border-radius:9px; font-size:.76rem; }}
      .age-signals b {{ color:var(--accent); }} .age-signals small {{ color:var(--muted); font-size:.68rem; }}
      .meta {{ display:flex; gap:.4rem; flex-wrap:wrap; color:var(--muted); font-size:.74rem; margin-bottom:.8rem; }}
      .meta span {{ border:1px solid var(--border); border-radius:999px; padding:.24rem .5rem; }}
      .category.cat-blue {{ color:#60a5fa; }} .category.cat-amber {{ color:#f59e0b; }} .category.cat-violet {{ color:#a78bfa; }}
      .category.cat-green {{ color:#34d399; }} .category.cat-pink {{ color:#f472b6; }} .category.cat-orange {{ color:#fb923c; }}
      .category.cat-cyan {{ color:#22d3ee; }} .category.cat-slate {{ color:var(--muted); }}
      .card-link {{ color:var(--accent)!important; text-decoration:none; font-weight:800; }} .card-link:hover {{ text-decoration:underline; }}
      .card-link.muted {{ color:var(--muted)!important; }}
      [data-testid="stExpander"], [data-testid="stExpander"] details, [data-testid="stExpander"] summary {{ background:var(--panel)!important; border-color:var(--border); border-radius:14px; }}
      hr {{ border-color:var(--border)!important; }}
      @media (max-width:640px) {{ .block-container {{ padding:1rem .75rem 3rem; }} .hero {{ padding:1.15rem; }}
        .hero-top {{ align-items:flex-start; flex-direction:column; gap:.5rem; }} .trend-card {{ min-height:auto; }} }}
    </style>
    """


# 테마와 샘플은 사용자가 명시적으로 선택합니다.
st.sidebar.markdown("### ⚙️ 화면 설정")
theme_mode = st.sidebar.segmented_control(
    "화면 모드",
    options=["시스템", "주간", "야간"],
    default="시스템",
    key="theme_mode",
    help="시스템은 브라우저/운영체제의 밝기 설정을 따릅니다.",
)
theme_mode = theme_mode or "시스템"
sample_preview = st.sidebar.toggle(
    "샘플 데이터 미리보기",
    value=False,
    key="sample_preview",
    help="직접 켰을 때만 샘플을 별도 표시합니다. 실데이터와 섞이지 않습니다.",
)
st.markdown(theme_styles(theme_mode), unsafe_allow_html=True)


if "trend_data" not in st.session_state:
    st.session_state.trend_data = load_live_current()
if "collection_messages" not in st.session_state:
    st.session_state.collection_messages = ["실데이터 대기 중 · 수동 갱신 버튼을 눌러 주세요."]
if "last_refresh_ok" not in st.session_state:
    st.session_state.last_refresh_ok = False

live_data: pd.DataFrame = st.session_state.trend_data
if sample_preview:
    data = load_sample().copy()
    if not data.empty:
        data["data_mode"] = "sample"
        naver_mask = data["source"].fillna("").astype(str).str.contains("NAVER DataLab")
        data["teen_index"] = 0.0
        data["twenties_index"] = 0.0
        data.loc[naver_mask, "teen_index"] = (pd.to_numeric(data.loc[naver_mask, "score"], errors="coerce") * 0.72).round(1)
        data.loc[naver_mask, "twenties_index"] = (pd.to_numeric(data.loc[naver_mask, "score"], errors="coerce") * 0.88).round(1)
        data["naver_period"] = "샘플 상대지수"
else:
    data = live_data

latest_time = data["last_seen"].max() if not data.empty and "last_seen" in data else None
mode_label = "SAMPLE PREVIEW" if sample_preview else ("LIVE DATA" if not data.empty else "WAITING FOR DATA")
st.markdown(
    f"""
    <section class="hero">
      <div class="hero-top">
        <div class="hero-kicker"><span class="live-dot"></span>KOREA · MICRO SIGNAL BOARD</div>
        <span class="mode-pill">{mode_label} · {theme_mode} 모드</span>
      </div>
      <h1>Korea Micro Trend Dashboard</h1>
      <p>공개 RSS에서 포착한 한국 급상승 신호를 Google News로 설명하고, NAVER DataLab의 10대·20대 상대 반응으로 교차 확인합니다.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

if sample_preview:
    st.markdown(
        '<div class="sample-banner">⚠️ <b>샘플 미리보기입니다.</b> 실제 수집 결과와 섞이거나 저장되지 않습니다. '
        '실데이터를 보려면 왼쪽의 “샘플 데이터 미리보기”를 끄세요.</div>',
        unsafe_allow_html=True,
    )
elif data.empty:
    st.markdown(
        '<div class="empty-banner">아직 저장된 실데이터가 없습니다. 아래 <b>실데이터 수동 갱신</b>을 누르면 Google 공개 RSS부터 수집합니다.</div>',
        unsafe_allow_html=True,
    )

client_id, client_secret = naver_credentials()
naver_connected = bool(client_id and client_secret)
average_score = safe_number(data["score"].mean()) if not data.empty and "score" in data else 0.0
naver_count = 0
if not data.empty and "teen_index" in data and "twenties_index" in data:
    naver_count = int(((pd.to_numeric(data["teen_index"], errors="coerce").fillna(0) > 0) |
                       (pd.to_numeric(data["twenties_index"], errors="coerce").fillna(0) > 0)).sum())

k1, k2, k3, k4 = st.columns(4)
k1.metric("마지막 실데이터 갱신", format_korean_time(latest_time) if (latest_time and not sample_preview) else ("샘플" if sample_preview else "수집 전"))
k2.metric("표시 키워드", f"{len(data):,}개")
k3.metric("평균 트렌드 점수", f"{average_score:.1f}")
k4.metric("NAVER 연령 반응", f"{naver_count}개", "API 연결됨" if naver_connected else "키 미설정", delta_color="off")

refresh_col, note_col = st.columns([1, 2.4], vertical_alignment="center")
with refresh_col:
    refresh_clicked = st.button(
        "↻ 실데이터 수동 갱신",
        type="primary",
        width="stretch",
        disabled=sample_preview,
        help="샘플 미리보기를 끄면 사용할 수 있습니다." if sample_preview else None,
    )
with note_col:
    st.caption("Google Trends → Google News 보강 → NAVER DataLab 연령 반응 → 중복 병합·점수 계산 순서로 처리합니다.")

if refresh_clicked:
    with st.spinner("공개 RSS와 NAVER API HUB를 확인하고 있습니다…"):
        refreshed, messages, success = refresh_data(live_data)
        st.session_state.trend_data = refreshed
        st.session_state.collection_messages = messages
        st.session_state.last_refresh_ok = success
    st.rerun()

with st.expander("수집 상태와 데이터 출처", expanded=not bool(data.size)):
    for message in st.session_state.collection_messages:
        icon = "⚠️" if "실패" in message or "없음" in message else "✓"
        st.write(f"{icon} {message}")
    st.caption("샘플은 왼쪽에서 직접 켠 미리보기에서만 사용됩니다. 실데이터 CSV와 시간 기록에는 저장되지 않습니다.")

filtered, _ = render_filters(data)
st.subheader("지금 뜨는 급상승 키워드")
render_trend_cards(filtered)

st.divider()
st.subheader("트렌드 구성")
history = pd.DataFrame() if sample_preview else load_live_history()
render_charts(filtered, history, theme_mode)

st.divider()
st.subheader("키워드 상세")
if filtered.empty:
    st.info("표시할 실데이터가 없습니다. 샘플 미리보기를 켜거나 실데이터를 갱신해 주세요.")
else:
    selected_keyword = st.selectbox("자세히 볼 키워드", filtered["keyword"].astype(str).tolist())
    detail = filtered[filtered["keyword"].astype(str) == selected_keyword].iloc[0]
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("트렌드 점수", f"{safe_number(detail.get('score')):.1f}")
    d2.metric("상태", str(detail.get("status", "관찰")))
    d3.metric("누적 발견", f"{int(safe_number(detail.get('sighting_count', 1)))}회")
    d4.metric("동시 출처", f"{int(safe_number(detail.get('source_count', 1)))}개")

    n1, n2 = st.columns(2)
    n1.metric("NAVER 10대 반응", reaction_text(detail.get("teen_index")))
    n2.metric("NAVER 20대 반응", reaction_text(detail.get("twenties_index")))
    st.caption("NAVER 수치는 최근 3일 평균 상대지수입니다. 연령별 절대 검색량이나 두 연령 간 직접 비교값이 아닙니다.")

    st.write(str(detail.get("summary", "설명이 없습니다.")))
    st.write(f"**최초 발견:** {format_korean_time(detail.get('first_seen'))}")
    st.write(f"**마지막 발견:** {format_korean_time(detail.get('last_seen'))}")
    st.write(f"**출처:** {detail.get('source', '-')}")
    st.info(f"점수 계산 근거 · {detail.get('score_reason', '샘플 미리보기 점수입니다.')}")

    titles = str(detail.get("related_title", "")).split(" | ")
    urls = str(detail.get("related_url", "")).split(" | ")
    if any(title.strip() for title in titles):
        st.markdown("**관련 뉴스**")
        for index, title in enumerate(titles):
            if not title.strip():
                continue
            url = urls[index] if index < len(urls) else ""
            st.markdown(f"- [{title}]({url})" if url.startswith("http") else f"- {title}")

st.caption("공개 RSS와 공식 API만 사용 · 실데이터/샘플 완전 분리 · NAVER 지수는 상대 검색 추이 · 투자·의료·법률 조언이 아님")
