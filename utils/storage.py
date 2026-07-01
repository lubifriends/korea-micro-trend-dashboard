"""CSV 저장소.

앱의 다른 부분은 이 파일의 함수만 호출합니다. 나중에 Supabase를 사용할 때
함수 이름과 반환 형식을 유지한 채 내부 구현만 교체하면 됩니다.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
CURRENT_PATH = DATA_DIR / "trends.csv"
HISTORY_PATH = DATA_DIR / "history.csv"
SAMPLE_PATH = ROOT_DIR / "sample_data" / "sample_trends.csv"


def _read_csv(path: Path) -> pd.DataFrame:
    """CSV가 없거나 손상되어도 앱이 멈추지 않게 빈 표를 반환합니다."""
    try:
        if path.exists() and path.stat().st_size > 0:
            return pd.read_csv(path, encoding="utf-8-sig")
    except (OSError, UnicodeError, pd.errors.ParserError):
        pass
    return pd.DataFrame()


def load_current() -> pd.DataFrame:
    return _read_csv(CURRENT_PATH)


def load_sample() -> pd.DataFrame:
    return _read_csv(SAMPLE_PATH)


def load_history() -> pd.DataFrame:
    return _read_csv(HISTORY_PATH)


def save_current(df: pd.DataFrame) -> None:
    """현재 TOP 목록을 UTF-8 CSV로 안전하게 교체합니다."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary_path = CURRENT_PATH.with_suffix(".tmp")
    df.to_csv(temporary_path, index=False, encoding="utf-8-sig")
    temporary_path.replace(CURRENT_PATH)


def append_history(df: pd.DataFrame, keep_rows: int = 5000) -> None:
    """시간대 차트용 스냅샷을 누적하되 파일이 무한히 커지지 않게 제한합니다."""
    if df.empty:
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    columns = ["snapshot_time", "keyword", "category", "source", "score"]
    snapshot = df.copy()
    snapshot["snapshot_time"] = pd.Timestamp.now(tz="Asia/Seoul").isoformat()
    for column in columns:
        if column not in snapshot.columns:
            snapshot[column] = ""
    combined = pd.concat([load_history(), snapshot[columns]], ignore_index=True)
    combined.tail(keep_rows).to_csv(HISTORY_PATH, index=False, encoding="utf-8-sig")


def bootstrap_from_sample() -> pd.DataFrame:
    """첫 실행 시 API가 없어도 샘플로 바로 화면을 보여 줍니다."""
    current = load_current()
    if not current.empty:
        return current
    sample = load_sample()
    if not sample.empty:
        save_current(sample)
        append_history(sample)
    return sample

