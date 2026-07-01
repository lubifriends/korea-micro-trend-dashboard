"""사이드바 필터 UI."""

from __future__ import annotations

import pandas as pd
import streamlit as st


SORT_OPTIONS = {
    "트렌드 점수 높은 순": ("score", False),
    "최근 발견 순": ("last_seen", False),
    "최초 발견 순": ("first_seen", False),
    "키워드 가나다순": ("keyword", True),
}


def render_filters(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    st.sidebar.header("🔎 전광판 필터")
    if df.empty:
        return df, 20

    categories = sorted(df["category"].dropna().astype(str).unique().tolist())
    selected_categories = st.sidebar.multiselect(
        "카테고리",
        categories,
        default=categories,
        help="보고 싶은 주제 분야만 남깁니다.",
    )

    # 한 키워드에 출처가 여러 개면 ' | '로 연결되어 있습니다.
    source_values: set[str] = set()
    for value in df["source"].fillna("").astype(str):
        source_values.update(item.strip() for item in value.split(" | ") if item.strip())
    sources = sorted(source_values)
    selected_sources = st.sidebar.multiselect(
        "출처",
        sources,
        default=sources,
        help="Google Trends, Google News, NAVER DataLab 같은 수집 출처입니다.",
    )

    sort_label = st.sidebar.selectbox("정렬 기준", list(SORT_OPTIONS))
    top_n = st.sidebar.slider("TOP N", min_value=5, max_value=20, value=20, step=5)

    category_mask = df["category"].astype(str).isin(selected_categories)
    source_mask = df["source"].fillna("").astype(str).apply(
        lambda value: any(source in value.split(" | ") for source in selected_sources)
    )
    filtered = df[category_mask & source_mask].copy()
    sort_column, ascending = SORT_OPTIONS[sort_label]
    if sort_column in ("last_seen", "first_seen"):
        filtered[sort_column] = pd.to_datetime(filtered[sort_column], errors="coerce")
    filtered = filtered.sort_values(sort_column, ascending=ascending).head(top_n)
    return filtered.reset_index(drop=True), top_n
