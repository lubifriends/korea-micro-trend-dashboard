"""NAVER API HUB의 공식 검색어 트렌드 API 연동.

Google에서 발견한 키워드를 네이버 검색 반응으로 교차 확인합니다. 이 API는
새 급상승어 목록을 주는 API가 아니라, 지정한 키워드의 상대 검색 추이를
연령 조건별로 반환하는 API입니다.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import requests


API_URL = "https://naverapihub.apigw.ntruss.com/search-trend/v1/search"
TEEN_AGES = ["2"]  # 공식 구간: 13~18세
TWENTIES_AGES = ["3", "4"]  # 공식 구간: 19~24세, 25~29세


def _chunks(items: list[str], size: int = 5) -> list[list[str]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def _request_age_group(
    keywords: list[str],
    ages: list[str],
    client_id: str,
    client_secret: str,
    timeout: int,
) -> dict[str, float]:
    """키워드별 최근 3일 평균 상대지수(0~100)를 반환합니다."""
    end_date = date.today()
    start_date = end_date - timedelta(days=13)
    group_names = {keyword[:20]: keyword for keyword in keywords}
    payload = {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "timeUnit": "date",
        "keywordGroups": [
            {"groupName": keyword[:20], "keywords": [keyword]}
            for keyword in keywords
        ],
        "ages": ages,
    }
    response = requests.post(
        API_URL,
        headers={
            "X-NCP-APIGW-API-KEY-ID": client_id,
            "X-NCP-APIGW-API-KEY": client_secret,
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()

    values: dict[str, float] = {}
    for result in response.json().get("results", []):
        data = result.get("data", [])[-3:]
        ratios = [float(point.get("ratio", 0) or 0) for point in data]
        title = str(result.get("title", ""))
        values[group_names.get(title, title)] = round(sum(ratios) / len(ratios), 1) if ratios else 0.0
    return values


def fetch_naver_age_reactions(
    keywords: list[str],
    client_id: str = "",
    client_secret: str = "",
    limit: int = 10,
    timeout: int = 10,
) -> tuple[list[dict[str, Any]], str]:
    """상위 키워드의 10대·20대 상대 검색지수를 조회합니다.

    연령별 호출은 각각 0~100으로 정규화되므로 두 연령의 숫자를 절대 검색량처럼
    직접 비교하면 안 됩니다. 각 연령 안에서 최근 반응이 강한지 보는 지표입니다.
    """
    if not client_id or not client_secret:
        return [], "NAVER API HUB 키 없음: 네이버 연령 반응은 표시하지 않음"

    cleaned = list(dict.fromkeys(str(keyword).strip() for keyword in keywords if str(keyword).strip()))[:limit]
    results: list[dict[str, Any]] = []
    try:
        for group in _chunks(cleaned):
            teen_values = _request_age_group(group, TEEN_AGES, client_id, client_secret, timeout)
            twenties_values = _request_age_group(group, TWENTIES_AGES, client_id, client_secret, timeout)
            for keyword in group:
                results.append({
                    "keyword": keyword,
                    "teen_index": teen_values.get(keyword, 0.0),
                    "twenties_index": twenties_values.get(keyword, 0.0),
                    "naver_period": "최근 3일 평균 상대지수",
                })
        return results, f"NAVER DataLab {len(results)}개 키워드 연령 반응 확인"
    except (requests.RequestException, ValueError, TypeError) as exc:
        return [], f"NAVER DataLab 수집 실패: {exc}"
