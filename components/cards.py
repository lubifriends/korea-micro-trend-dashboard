"""전광판 스타일 키워드 카드."""

from __future__ import annotations

import html
from urllib.parse import urlparse

import pandas as pd
import streamlit as st


STATUS_CLASS = {"신규": "new", "상승": "up", "관찰": "watch", "하락": "down"}
CATEGORY_CLASS = {
    "사회": "cat-blue", "경제": "cat-amber", "기술": "cat-violet",
    "스포츠": "cat-green", "연예": "cat-pink", "문화": "cat-orange",
    "생활": "cat-cyan", "기타": "cat-slate",
}


def _safe_url(value: object) -> str:
    url = str(value or "").split(" | ")[0].strip()
    return url if urlparse(url).scheme in {"http", "https"} else ""


def _number(value: object) -> float:
    number = pd.to_numeric(value, errors="coerce")
    return 0.0 if pd.isna(number) else float(number)


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
            category_class = CATEGORY_CLASS.get(str(row.get("category", "기타")), "cat-slate")
            status = str(row.get("status", "관찰"))
            status_class = STATUS_CLASS.get(status, "watch")
            url = _safe_url(row.get("related_url", ""))
            teen_index = _number(row.get("teen_index", 0))
            twenties_index = _number(row.get("twenties_index", 0))
            naver_html = ""
            if teen_index > 0 or twenties_index > 0:
                naver_html = f"""
                  <div class="age-signals">
                    <span>10대 <b>{teen_index:.1f}</b></span>
                    <span>20대 <b>{twenties_index:.1f}</b></span>
                    <small>NAVER 상대지수</small>
                  </div>
                """
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
                      <div class="score-row">
                        <div class="score">{float(row.get('score', 0)):.1f}<small> / 100</small></div>
                        <div class="score-track"><i style="width:{min(100, float(row.get('score', 0)))}%"></i></div>
                      </div>
                      <p>{summary}</p>
                      {naver_html}
                      <div class="meta">
                        <span class="category {category_class}">{category}</span>
                        <span>{source}</span>
                      </div>
                      {link_html}
                    </article>
                    """,
                    unsafe_allow_html=True,
                )
