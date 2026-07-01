"""API 키가 없어도 작동하는 한 줄 요약 도구."""

from __future__ import annotations

import re


def make_one_line_summary(keyword: str, news_title: str = "", source: str = "") -> str:
    """MVP에서는 기사 제목을 이용한 규칙 기반 요약을 사용합니다."""
    clean_title = re.sub(r"\s+", " ", news_title).strip()
    if clean_title:
        return f"'{keyword}' 관련 최신 기사: {clean_title[:100]}"
    return f"{source or '공개 피드'}에서 '{keyword}' 관심 증가가 포착되었습니다."

