"""중복 키워드 병합과 설명 가능한 트렌드 점수 계산."""

from __future__ import annotations

import math
import re
from collections import Counter
from datetime import datetime
from typing import Any

import pandas as pd


# 필요에 따라 여기에 일반어/스팸 표현을 추가할 수 있습니다.
GENERIC_OR_SPAM_WORDS = {
    "뉴스", "오늘", "실시간", "무료", "추천", "광고", "이벤트", "클릭", "대박"
}

CATEGORY_RULES = {
    "연예": ["영화", "드라마", "배우", "가수", "아이돌", "콘서트", "예능", "뮤직"],
    "스포츠": ["축구", "야구", "농구", "배구", "선수", "경기", "월드컵", "올림픽"],
    "경제": ["주가", "증시", "환율", "금리", "부동산", "코스피", "코스닥", "비트코인"],
    "기술": ["AI", "인공지능", "애플", "삼성", "갤럭시", "로봇", "반도체", "게임"],
    "사회": ["날씨", "장마", "태풍", "교통", "교육", "사건", "정책", "선거"],
}


def normalize_keyword(value: Any) -> str:
    """공백/기호 차이 때문에 같은 키워드가 중복되는 일을 줄입니다."""
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text.casefold()


def guess_category(keyword: str, context: str = "") -> str:
    haystack = f"{keyword} {context}".casefold()
    for category, words in CATEGORY_RULES.items():
        if any(word.casefold() in haystack for word in words):
            return category
    return "기타"


def _split_values(value: Any, separator: str = " | ") -> list[str]:
    if pd.isna(value) or not str(value).strip():
        return []
    return [item.strip() for item in str(value).split(separator) if item.strip()]


def _unique_join(values: list[Any], separator: str = " | ") -> str:
    items: list[str] = []
    for value in values:
        items.extend(_split_values(value, separator))
    return separator.join(dict.fromkeys(items))


def _to_timestamp(value: Any, fallback: pd.Timestamp) -> pd.Timestamp:
    timestamp = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(timestamp):
        return fallback
    return timestamp.tz_convert("Asia/Seoul")


def _safe_number(value: Any, fallback: float = 0.0) -> float:
    """빈칸이나 NaN이 들어와도 숫자 변환 오류를 내지 않습니다."""
    number = pd.to_numeric(value, errors="coerce")
    return fallback if pd.isna(number) else float(number)


def merge_and_score(new_rows: list[dict[str, Any]], previous: pd.DataFrame | None = None) -> pd.DataFrame:
    """새 수집 결과를 합치고 0~100점 점수 및 상태를 계산합니다."""
    now = pd.Timestamp.now(tz="Asia/Seoul")
    previous = previous.copy() if previous is not None else pd.DataFrame()
    previous_by_key = {
        normalize_keyword(row.get("keyword")): row
        for row in previous.to_dict("records")
        if normalize_keyword(row.get("keyword"))
    }

    groups: dict[str, list[dict[str, Any]]] = {}
    for row in new_rows:
        key = normalize_keyword(row.get("keyword"))
        if key:
            groups.setdefault(key, []).append(row)

    results: list[dict[str, Any]] = []
    for key, rows in groups.items():
        old = previous_by_key.get(key, {})
        keyword = str(rows[0].get("keyword", "")).strip()
        sources = _unique_join([row.get("source", "") for row in rows])
        urls = _unique_join([row.get("related_url", "") for row in rows])
        titles = _unique_join([row.get("related_title", "") for row in rows])
        summaries = [str(row.get("summary", "")).strip() for row in rows if row.get("summary")]
        contexts = " ".join(titles + " " + " ".join(summaries))

        first_seen = _to_timestamp(old.get("first_seen"), now) if old else now
        last_seen = now
        old_count = int(_safe_number(old.get("sighting_count", 0)))
        sighting_count = old_count + max(1, len(rows))
        source_count = max(1, len(_split_values(sources)))
        age_hours = max(0.0, (now - first_seen).total_seconds() / 3600)

        # 각 항목을 따로 저장해 상세 화면에서 점수 근거를 보여 줍니다.
        freshness_score = max(0.0, 35.0 - min(age_hours, 48.0) * 0.7)
        multi_source_score = min(25.0, max(0, source_count - 1) * 12.5)
        link_score = 15.0 if urls else 0.0
        repeat_score = min(20.0, math.log2(sighting_count + 1) * 5.0)
        age_penalty = min(25.0, max(0.0, age_hours - 12.0) * 0.55)
        spam_penalty = 20.0 if key in {word.casefold() for word in GENERIC_OR_SPAM_WORDS} else 0.0
        raw_score = 15 + freshness_score + multi_source_score + link_score + repeat_score
        score = round(max(0.0, min(100.0, raw_score - age_penalty - spam_penalty)), 1)

        previous_score = _safe_number(old.get("score", score), score)
        if not old:
            status = "신규"
        elif score >= previous_score + 3:
            status = "상승"
        elif score <= previous_score - 3:
            status = "하락"
        else:
            status = "관찰"

        category_candidates = [str(row.get("category", "")).strip() for row in rows]
        category_candidates = [value for value in category_candidates if value and value != "기타"]
        category = Counter(category_candidates).most_common(1)[0][0] if category_candidates else guess_category(keyword, contexts)
        summary = summaries[0] if summaries else f"{sources or '공개 피드'}에서 새롭게 포착된 키워드입니다."

        results.append({
            "keyword": keyword,
            "score": score,
            "previous_score": round(previous_score, 1),
            "status": status,
            "source": sources or "공개 RSS",
            "category": category,
            "first_seen": first_seen.isoformat(),
            "last_seen": last_seen.isoformat(),
            "summary": summary,
            "related_title": titles,
            "related_url": urls,
            "sighting_count": sighting_count,
            "source_count": source_count,
            "freshness_score": round(freshness_score, 1),
            "multi_source_score": round(multi_source_score, 1),
            "link_score": round(link_score, 1),
            "repeat_score": round(repeat_score, 1),
            "age_penalty": round(age_penalty, 1),
            "spam_penalty": round(spam_penalty, 1),
            "score_reason": (
                f"기본 15 + 최신성 {freshness_score:.1f} + 다중출처 {multi_source_score:.1f} "
                f"+ 링크 {link_score:.1f} + 반복 {repeat_score:.1f} "
                f"- 경과시간 {age_penalty:.1f} - 일반어/스팸 {spam_penalty:.1f}"
            ),
        })

    return pd.DataFrame(results).sort_values("score", ascending=False).reset_index(drop=True) if results else pd.DataFrame()
