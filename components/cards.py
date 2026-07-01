"""전광판 스타일 키워드 카드."""

from __future__ import annotations

import html
from urllib.parse import urlparse

import pandas as pd
import streamlit as st


STATUS_CLASS = {"신규": "new", "상승": "up", "관찰": "watch", "하락": "down"}


def _safe_url(value: object) -> str:
    url = str(value or "").split(" | ")[0].strip()
    return url if urlparse(url).scheme in {"http", "https"} else ""


def render_trend_cards(df: pd.DataFrame) -> None:
    """두 열 카드가 모바일에서는 자동으로 한 열로 접힙니다."""
    if df.empty:
        st.info("선택한 조건에 맞는 키워드가 없습니다. 사이드바 필터를 넓혀 보세요.")
        return

    for start in range(0, len(df), 2):
        columns = st.columns(2, gap="medium")
        for offset, column in enumerate(columns):
            index = start + offset
            if index >= len(df):
                continue
            row = df.iloc[index]
            rank = index + 1
            keyword = html.escape(str(row.get("keyword", "")))
            summary = html.escape(str(row.get("summary", "")))
            source = html.escape(str(row.get("source", "")))
            category = html.escape(str(row.get("category", "기타")))
            status = str(row.get("status", "관찰"))
            status_class = STATUS_CLASS.get(status, "watch")
            url = _safe_url(row.get("related_url", ""))
            link_html = (
                f'<a class="card-link" href="{html.escape(url)}" target="_blank" rel="noopener">관련 링크 ↗</a>'
                if url else '<span class="card-link muted">링크 준비 중</span>'
            )
            with column:
                st.markdown(
                    f"""
                    <article class="trend-card">
                      <div class="card-top">
                        <span class="rank">#{rank:02d}</span>
                        <span class="status {status_class}">{html.escape(status)}</span>
                      </div>
                      <h3>{keyword}</h3>
                      <div class="score">{float(row.get('score', 0)):.1f}<small> / 100</small></div>
                      <p>{summary}</p>
                      <div class="meta">
                        <span class="category">{category}</span>
                        <span>{source}</span>
                      </div>
                      {link_html}
                    </article>
                    """,
                    unsafe_allow_html=True,
                )

