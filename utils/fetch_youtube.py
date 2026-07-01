"""YouTube 인기 동영상 수집기.

키가 없으면 sample_data의 YouTube 행을 사용하므로 앱은 계속 실행됩니다.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
import requests


API_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CATEGORIES = {
    "1": "연예", "2": "생활", "10": "연예", "17": "스포츠",
    "20": "기술", "22": "생활", "23": "연예", "24": "연예",
    "25": "사회", "26": "생활", "27": "사회", "28": "기술",
}


def _sample_youtube_rows(sample_path: Path | None) -> list[dict[str, Any]]:
    if not sample_path or not sample_path.exists():
        return []
    try:
        sample = pd.read_csv(sample_path, encoding="utf-8-sig")
        sample = sample[sample["source"].astype(str).str.contains("YouTube", na=False)]
        return sample.to_dict("records")
    except (OSError, UnicodeError, pd.errors.ParserError, KeyError):
        return []


def fetch_youtube_trends(
    api_key: str | None = None,
    sample_path: Path | None = None,
    timeout: int = 10,
) -> tuple[list[dict[str, Any]], str]:
    api_key = api_key or os.getenv("YOUTUBE_API_KEY", "")
    if not api_key:
        rows = _sample_youtube_rows(sample_path)
        return rows, f"YouTube 키 없음: 샘플 {len(rows)}건 사용"

    try:
        response = requests.get(
            API_URL,
            params={
                "part": "snippet,statistics",
                "chart": "mostPopular",
                "regionCode": "KR",
                "maxResults": 10,
                "key": api_key,
            },
            timeout=timeout,
        )
        response.raise_for_status()
        rows: list[dict[str, Any]] = []
        for item in response.json().get("items", []):
            snippet = item.get("snippet", {})
            title = str(snippet.get("title", "")).strip()
            if not title:
                continue
            rows.append({
                # MVP에서는 영상 제목을 키워드 후보로 사용합니다.
                # 다음 버전에서는 형태소 분석으로 핵심 명사를 추출할 수 있습니다.
                "keyword": title[:60],
                "source": "YouTube",
                "category": YOUTUBE_CATEGORIES.get(str(snippet.get("categoryId", "")), "기타"),
                "summary": f"한국 YouTube 인기 동영상: {title}",
                "related_title": title,
                "related_url": f"https://www.youtube.com/watch?v={item.get('id', '')}",
                "provider_weight": int(item.get("statistics", {}).get("viewCount", 0) or 0),
            })
        return rows, f"YouTube 인기 영상 {len(rows)}건 수집"
    except (requests.RequestException, ValueError, OSError) as exc:
        rows = _sample_youtube_rows(sample_path)
        return rows, f"YouTube 수집 실패, 샘플 {len(rows)}건 사용: {exc}"
