"""Google News의 공개 RSS 검색 결과로 관련 기사를 보강합니다."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote_plus

import feedparser
import requests


def _plain_text(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", str(value or "")).replace("&nbsp;", " ").strip()


def fetch_news_for_keyword(keyword: str, timeout: int = 8) -> tuple[list[dict[str, Any]], str]:
    """키워드 하나당 최신 기사 최대 3개만 가져와 호출 부담을 줄입니다."""
    url = (
        "https://news.google.com/rss/search?"
        f"q={quote_plus(keyword)}&hl=ko&gl=KR&ceid=KR:ko"
    )
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "KoreaMicroTrendDashboard/1.0 (public RSS reader)"},
        )
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        rows: list[dict[str, Any]] = []
        for entry in feed.entries[:3]:
            title = _plain_text(entry.get("title", ""))
            rows.append({
                "title": title,
                "url": str(entry.get("link", "")),
                "summary": _plain_text(entry.get("summary", ""))[:180],
            })
        return rows, f"뉴스 {len(rows)}건"
    except (requests.RequestException, OSError) as exc:
        return [], f"뉴스 수집 실패: {exc}"


def enrich_with_news(rows: list[dict[str, Any]], limit: int = 10) -> tuple[list[dict[str, Any]], str]:
    """상위 키워드만 뉴스로 보강해 수동 갱신 시간을 짧게 유지합니다."""
    enriched = [dict(row) for row in rows]
    success_count = 0
    for row in enriched[:limit]:
        news, _ = fetch_news_for_keyword(str(row.get("keyword", "")))
        if not news:
            continue
        success_count += 1
        first = news[0]
        row["source"] = " | ".join(dict.fromkeys([str(row.get("source", "")), "Google News"]))
        row["related_title"] = first["title"]
        row["related_url"] = first["url"]
        row["summary"] = f"관련 최신 기사: {first['title']}"
    return enriched, f"Google News {success_count}개 키워드 보강"

