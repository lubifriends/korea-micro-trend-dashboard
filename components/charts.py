"""Plotly 기반 분포/시간 차트."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


COLORS = ["#5eead4", "#60a5fa", "#fbbf24", "#f472b6", "#a78bfa", "#fb7185"]


def _style(fig, theme_mode: str):
    is_light = theme_mode == "주간"
    fig.update_layout(
        template="plotly_white" if is_light else "plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=45, b=20),
        legend_title_text="",
        font=dict(color="#334155" if is_light else "#cbd5e1"),
        hoverlabel=dict(bgcolor="#ffffff" if is_light else "#111827"),
    )
    return fig


def render_charts(df: pd.DataFrame, history: pd.DataFrame, theme_mode: str = "시스템") -> None:
    if df.empty:
        return

    left, right = st.columns(2, gap="medium")
    category_counts = df.groupby("category", as_index=False).size().rename(columns={"size": "키워드 수"})
    category_counts = category_counts.sort_values("키워드 수")
    category_fig = px.bar(
        category_counts,
        x="키워드 수",
        y="category",
        color="category",
        title="카테고리별 분포",
        color_discrete_sequence=COLORS,
        orientation="h",
    )
    category_fig.update_traces(marker_line_width=0, hovertemplate="%{y}: %{x}개<extra></extra>")
    left.plotly_chart(_style(category_fig, theme_mode), width="stretch")

    source_rows = df[["source"]].copy()
    source_rows["source"] = source_rows["source"].fillna("").str.split(" | ", regex=False)
    source_rows = source_rows.explode("source")
    source_counts = source_rows.groupby("source", as_index=False).size().rename(columns={"size": "키워드 수"})
    source_fig = px.pie(
        source_counts,
        names="source",
        values="키워드 수",
        hole=0.58,
        title="출처별 분포",
        color_discrete_sequence=COLORS,
    )
    source_fig.update_traces(textposition="inside", textinfo="percent+label")
    right.plotly_chart(_style(source_fig, theme_mode), width="stretch")

    timeline = history.copy()
    if timeline.empty:
        timeline = df.copy()
        timeline["snapshot_time"] = pd.Timestamp.now(tz="Asia/Seoul")
    timeline["snapshot_time"] = pd.to_datetime(timeline["snapshot_time"], errors="coerce")
    timeline = timeline.dropna(subset=["snapshot_time"])
    timeline["시간"] = timeline["snapshot_time"].dt.floor("10min")
    counts = timeline.groupby("시간", as_index=False)["keyword"].nunique().rename(columns={"keyword": "키워드 수"})
    time_fig = px.line(
        counts.tail(144),
        x="시간",
        y="키워드 수",
        markers=True,
        title="시간대별 포착 키워드 수 (최근 스냅샷)",
        color_discrete_sequence=["#5eead4"],
    )
    time_fig.update_traces(line_width=3, marker_size=7, fill="tozeroy", fillcolor="rgba(94,234,212,.10)")
    st.plotly_chart(_style(time_fig, theme_mode), width="stretch")
