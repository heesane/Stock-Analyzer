from __future__ import annotations

import unicodedata

from stock_analyzer.services.language import LanguagePack, LANGUAGE_KO

from .utils import format_number, format_percent
from .streaming import stream_print, print_instant


def _macd_bias_text(macd_val: float | None, signal_val: float | None, lang: LanguagePack) -> str:
    if macd_val is not None and signal_val is not None:
        if macd_val > signal_val:
            return lang.t("macd_bias_up")
        if macd_val < signal_val:
            return lang.t("macd_bias_down")
    return lang.t("macd_bias_flat")


def _rsi_state_text(rsi_val: float | None, lang: LanguagePack) -> str:
    if rsi_val is None:
        return lang.t("rsi_state_na")
    if rsi_val >= 70:
        return lang.t("rsi_state_overbought", value=format_number(rsi_val))
    if rsi_val <= 30:
        return lang.t("rsi_state_oversold", value=format_number(rsi_val))
    return lang.t("rsi_state_neutral", value=format_number(rsi_val))


def _translate_channel_label(label: str, lang: LanguagePack) -> str:
    return lang.t(f"channel_label_{label}")


def _translate_channel_trend(trend: str, lang: LanguagePack) -> str:
    return lang.t(f"channel_trend_{trend}")


def _translate_channel_position(position: str, lang: LanguagePack) -> str:
    return lang.t(f"channel_position_{position}")


PANEL_WIDTH = 70
PANEL_BODY = PANEL_WIDTH - 4
FRAME_COLOR = "\033[38;5;141m"
PANEL_TITLE = "Stock Analyzer"


def _display_width(char: str) -> int:
    if unicodedata.east_asian_width(char) in {"W", "F"}:
        return 2
    return 1


def _wrap_with_indent(text: str) -> list[str]:
    if text is None:
        return [""]
    stripped = text.rstrip("\n")
    if not stripped:
        return [""]
    indent_len = len(stripped) - len(stripped.lstrip(" "))
    indent = " " * indent_len
    content = stripped.lstrip(" ")
    width = max(PANEL_BODY - indent_len, 20)

    lines: list[str] = []
    current = ""
    current_width = 0

    for char in content:
        if char == "\n":
            lines.append(indent + current)
            current = ""
            current_width = 0
            continue
        char_width = _display_width(char)
        if current and current_width + char_width > width:
            lines.append(indent + current)
            current = char
            current_width = char_width
        else:
            current += char
            current_width += char_width

    if current:
        lines.append(indent + current)
    return lines or [indent]


def _assistant_panel(lines: list[str]) -> None:
    fill = "─" * (PANEL_WIDTH - len(PANEL_TITLE) - 5)
    header = f"╭─ {PANEL_TITLE} {fill}╮"
    footer = f"╰{'─' * (PANEL_WIDTH - 2)}╯"
    print_instant(f"{FRAME_COLOR}{header}\033[0m")
    for line in lines:
        for wrapped in _wrap_with_indent(line):
            padded = wrapped.ljust(PANEL_BODY)
            stream_print(
                f"{FRAME_COLOR}│\033[0m {padded} {FRAME_COLOR}│\033[0m",
                delay=0.002,
            )
    print_instant(f"{FRAME_COLOR}{footer}\033[0m")
    print_instant()


def render_cli_report(summary: dict, lang: LanguagePack | None = None) -> None:
    lang = lang or LANGUAGE_KO
    macd_vals = summary["macd"]
    latest_price = summary["latest_close"]
    macd_val = macd_vals["macd"]
    signal_val = macd_vals["signal"]
    hist_val = macd_vals["hist"]
    rsi_val = summary["rsi"]

    macd_bias = _macd_bias_text(macd_val, signal_val, lang)
    rsi_state = _rsi_state_text(rsi_val, lang)

    analysis_lines = [
        f"• {lang.t('label_ticker')}: {summary['ticker']}",
        f"• {lang.t('label_reference_date')}: {summary['latest_date']}",
        f"• {lang.t('label_close')}: {summary['latest_close']:.2f} USD",
    ]
    signal_lines = [
        f"• {lang.t('label_macd')}: {format_number(macd_val)}",
        f"• {lang.t('label_signal')}: {format_number(signal_val)}",
        f"• {lang.t('label_histogram')}: {format_number(hist_val)}",
        f"• {lang.t('label_rsi')}: {format_number(rsi_val)}",
    ]

    lines: list[str] = []

    def add_section(title: str, entries: list[str]) -> None:
        if not entries:
            return
        lines.append(f"[{title}]")
        lines.extend(entries)
        lines.append("")

    signal_title = lang.messages.get("heading_signal_board") or lang.t("heading_indicators")
    add_section(lang.t("heading_analysis"), analysis_lines)
    add_section(signal_title, signal_lines)

    decision = summary["decision"]
    decision_lines = [
        f"{decision['action']}",
        f"  {decision['rationale']}",
    ]
    add_section(lang.t("decision_prefix"), decision_lines)

    indicator_lines = [
        lang.t("macd_summary", bias=macd_bias),
        lang.t("rsi_summary", state=rsi_state),
        lang.t(
            "sma_summary",
            sma20=format_number(summary["moving_averages"]["sma20"]),
            sma50=format_number(summary["moving_averages"]["sma50"]),
        ),
        lang.t(
            "volume_summary",
            latest=format_number(summary["volume"]["latest"]),
            avg20=format_number(summary["volume"]["avg20"]),
        ),
    ]
    add_section(lang.t("heading_indicators"), indicator_lines)

    relative_info = summary.get("relative_performance")
    if relative_info:
        label = lang.t(relative_info.get("label_key", "relative_label_neutral"))
        alpha_display = format_percent(relative_info.get("alpha_pct"), digits=1)
        ticker_return = format_percent(relative_info.get("ticker_return"), digits=1)
        benchmark_return = format_percent(relative_info.get("benchmark_return"), digits=1)
        relative_lines = [
            lang.t(
                "relative_summary",
                benchmark=relative_info["benchmark"],
                window=relative_info["window_days"],
                label=label,
                alpha=alpha_display,
            ),
            lang.t(
                "relative_returns",
                ticker=ticker_return,
                benchmark=benchmark_return,
            ),
        ]
        add_section(lang.t("heading_relative_performance"), relative_lines)

    risk_info = summary.get("risk")
    if risk_info:
        risk_lines = [
            lang.t(
                "risk_metric_line",
                label=lang.t("risk_vol_30"),
                value=format_percent(risk_info.get("vol_30d"), digits=1),
            ),
            lang.t(
                "risk_metric_line",
                label=lang.t("risk_vol_60"),
                value=format_percent(risk_info.get("vol_60d"), digits=1),
            ),
            lang.t(
                "risk_metric_line",
                label=lang.t("risk_mdd_180"),
                value=format_percent(risk_info.get("mdd_180d"), digits=1),
            ),
            lang.t(
                "risk_metric_line",
                label=lang.t("risk_atr"),
                value=format_number(risk_info.get("atr")),
            ),
            lang.t(
                "risk_metric_line",
                label=lang.t("risk_stop_loss"),
                value=format_number(risk_info.get("stop_loss_price")),
            ),
            lang.t(
                "risk_level_line",
                label=lang.t(risk_info.get("risk_level_key", "risk_level_unknown")),
            ),
        ]
        add_section(lang.t("heading_risk"), risk_lines)

    scorecard = summary.get("scorecard")
    if scorecard:
        score_lines: list[str] = ["• " + lang.t(
            "score_total_line",
            score=scorecard["total_score"],
            rating=lang.t(scorecard["rating_label_key"]),
        )]
        for indicator in scorecard["indicators"]:
            value_display = indicator.get("display") or lang.t("data_unavailable")
            note = lang.t("score_data_missing") if indicator.get("data_missing") else ""
            score_lines.append(
                "  "
                + lang.t(
                    "score_indicator_line",
                    label=lang.t(indicator["label_key"]),
                    value=value_display,
                    score=indicator["score"],
                    weight=indicator["weight"],
                    note=note,
                )
            )
        for category in scorecard["category_scores"]:
            score_lines.append(
                "    "
                + lang.t(
                    "score_category_line",
                    label=lang.t(category["label_key"]),
                    score=category["score"],
                )
            )
        add_section(lang.t("heading_scorecard"), score_lines)

    probability = summary.get("probability")
    if probability:
        confidence = lang.t(probability["confidence_key"])
        prob_lines = ["• " + lang.t(
            "prob_summary",
            bullish=format_percent(probability["bullish"]),
            bearish=format_percent(probability["bearish"]),
            confidence=confidence,
        )]
        total_weight = probability.get("weight_sum") or sum(
            comp.get("weight", 0.0) for comp in probability.get("breakdown", [])
        )
        for comp in probability.get("breakdown", []):
            weight_ratio = (
                comp["weight"] / total_weight if total_weight else comp["weight"]
            )
            prob_lines.append(
                "  "
                + lang.t(
                    "prob_component_line",
                    label=lang.t(comp["label_key"]),
                    score=format_percent(comp["score"]),
                    weight=format_percent(weight_ratio, digits=0),
                )
            )
        prob_lines.append("  " + lang.t("probability_note"))
        add_section(lang.t("heading_probability"), prob_lines)

    channel_lines: list[str] = []
    if summary["channels"]:
        for info in summary["channels"]:
            slope_perc = info["slope"] / latest_price * 100 if latest_price else float("nan")
            label = _translate_channel_label(info["label"], lang)
            trend = _translate_channel_trend(info["trend"], lang)
            position = _translate_channel_position(info["position"], lang)
            channel_lines.append(
                lang.t(
                    "channel_entry",
                    label=label,
                    window=info["lookback"],
                    trend=trend,
                    slope=info["slope"],
                    slope_perc=slope_perc,
                    position=position,
                )
            )
            channel_lines.append(
                "  "
                + lang.t(
                    "channel_range",
                    upper=format_number(info["channel_upper"]),
                    lower=format_number(info["channel_lower"]),
                )
            )
    else:
        channel_lines.append(lang.t("channel_none"))

    sr_info = summary["support_resistance"]
    if sr_info:
        channel_lines.append(
            "  "
            + lang.t(
                "support_line",
                window=sr_info["window"],
                price=format_number(sr_info["support"]),
                date=sr_info["support_date"],
            )
        )
        channel_lines.append(
            "  "
            + lang.t(
                "resistance_line",
                window=sr_info["window"],
                price=format_number(sr_info["resistance"]),
                date=sr_info["resistance_date"],
            )
        )
    else:
        channel_lines.append("  " + lang.t("support_none"))

    add_section(lang.t("heading_channels"), channel_lines)

    if lines and not lines[-1].strip():
        lines.pop()
    lines.append("")
    lines.append(lang.t("final_note"))

    _assistant_panel(lines)

    backtest = summary.get("backtest")
    if backtest:
        bt_lines = [
            lang.t(
                "backtest_summary",
                days=backtest["lookback_days"],
                ticker_return=format_percent(backtest.get("ticker_return"), digits=1),
                benchmark_return=format_percent(backtest.get("benchmark_return"), digits=1),
            ),
            lang.t(
                "backtest_alpha",
                benchmark=backtest["benchmark"],
                alpha=format_percent(backtest.get("alpha_pct"), digits=1),
            ),
            lang.t(
                "backtest_win_rate",
                win_rate=format_percent(backtest.get("win_rate"), digits=1),
            ),
            lang.t("backtest_note"),
        ]
        _assistant_panel(bt_lines)
