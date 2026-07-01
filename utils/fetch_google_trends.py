"""Google Trends의 공개 RSS 피드를 읽습니다.

로그인 우회나 화면 크롤링을 하지 않고 공개 RSS 주소만 사용합니다.
"""

from __future__ import annotations

from email.utils import parsedate_to_datetime
from typing import Any

import feedparser
import requests


GOOGLE_TRENDS_RSS = "https://trends.google.com/trending/rss?geo=KR"


def _traffic_to_number(value: str) -> int:
    """'10K+', '500+' 같은 표시를 비교 가능한 숫자로 바꿉니다."""
    text = str(value or "0").replace(",", "").replace("+", "").strip().upper()
    multiplier = 1
    if text.endswith("K"):
        text, multiplier = text[:-1], 1_000
    elif text.endswith("M"):
        text, multiplier = text[:-1], 1_000_000
    try:
        return int(float(text) * multiplier)
    except ValueError:
        return 0


def fetch_google_trends(timeout: int = 10) -> tuple[list[dict[str, Any]], str]:
    """수집 행과 사람이 읽을 수 있는 상태 메시지를 함께 반환합니다."""
    try:
        response = requests.get(
            GOOGLE_TRENDS_RSS,
            timeout=timeout,
            headers={"User-Agent": "KoreaMicroTrendDashboard/1.0 (public RSS reader)"},
        )
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        if getattr(feed, "bozo", False) and not feed.entries:
            raise ValueError("RSS 형식을 읽지 못했습니다.")

        rows: list[dict[str, Any]] = []
        for entry in feed.entries[:30]:
            keyword = str(entry.get("title", "")).strip()
            if not keyword:
                continue

            # Google Trends RSS에 포함된 관련 뉴스가 있으면 함께 보관합니다.
            news_items = entry.get("ht_news_item", []) or entry.get("news_item", []) or []
            if isinstance(news_items, dict):
                news_items = [news_items]
            first_news = news_items[0] if news_items else {}
            # feedparser 버전에 따라 뉴스 필드가 중첩되거나 entry 바로 아래에 놓입니다.
            related_title = str(
                entry.get("ht_news_item_title", "")
                or first_news.get("ht_news_item_title", "")
                or first_news.get("title", "")
            )
            related_url = str(
                entry.get("ht_news_item_url", "")
                or first_news.get("ht_news_item_url", "")
                or first_news.get("url", "")
            )
            traffic_text = str(entry.get("ht_approx_traffic", "") or entry.get("approx_traffic", ""))

            rows.append({
                "keyword": keyword,
                "source": "Google Trends",
                "category": "기타",
                "summary": (
                    f"Google Trends 공개 RSS에서 약 {traffic_text} 검색량으로 포착되었습니다."
                    if traffic_text else "Google Trends 공개 RSS에서 급상승 검색어로 포착되었습니다."
                ),
                "related_title": related_title,
                "related_url": related_url or str(entry.get("link", "")),
                "provider_weight": min(10, _traffic_to_number(traffic_text) // 1000),
            })
        return rows, f"Google Trends {len(rows)}건 수집"
    except (requests.RequestException, ValueError, OSError) as exc:
        return [], f"Google Trends 수집 실패: {exc}"
