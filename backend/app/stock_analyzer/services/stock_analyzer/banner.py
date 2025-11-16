"""Conversational welcome banner"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stock_analyzer.services.language import LanguagePack

from .streaming import print_instant, stream_print

FRAME_WIDTH = 78
FRAME_BODY = FRAME_WIDTH - 4
FRAME_COLOR = "\033[38;5;141m"
FRAME_TITLE = "Stock Analyzer · Interactive Assistant"
USER_LINE = "\033[38;5;111mYou\033[0m      > "
ASSISTANT_LINE = "\033[38;5;213mAssistant\033[0m  > "


def _pad(text: str) -> str:
    clean = (text or "")[:FRAME_BODY]
    return clean.ljust(FRAME_BODY)


def _assistant_frame(lines: list[str]) -> None:
    title_fill = "─" * (FRAME_WIDTH - len(FRAME_TITLE) - 5)
    header = f"╭─ {FRAME_TITLE} {title_fill}╮"
    footer = f"╰{'─' * (FRAME_WIDTH - 2)}╯"
    print_instant(f"{FRAME_COLOR}{header}\033[0m")
    for line in lines:
        print_instant(f"{FRAME_COLOR}│\033[0m {_pad(line)} {FRAME_COLOR}│\033[0m")
    print_instant(f"{FRAME_COLOR}{footer}\033[0m")


def show_banner() -> None:
    """Display assistant-styled frame"""
    lines = [
        "Realtime streaming equity briefings with export shortcuts.",
        "Conversational streaming UX for equity analysis.",
    ]
    _assistant_frame(lines)
    print_instant()


def show_welcome_message(lang: "LanguagePack") -> None:
    """Display conversational onboarding"""
    show_banner()

    lang_code = lang.code if hasattr(lang, "code") else "ko"
    messages = {
        "ko": {
            "dialogue": [
                ("assistant", "무엇을 도와드릴까요? 티커를 알려주시면 분석을 시작할게요."),
                ("you", "analyze AAPL"),
                ("assistant", "AAPL의 MACD·RSI·채널·확률을 실시간으로 정리해드릴게요."),
                ("you", "analyze 005930.KS"),
                ("assistant", "삼성전자 같은 국내 종목도 같은 포맷으로 보고해요."),
                ("assistant", "결과는 JSON, CSV, DB로도 내보낼 수 있습니다."),
            ],
            "shortcuts_title": "단축 명령어",
            "shortcuts": [
                ("/help", "사용법 보기"),
                ("/quit", "즉시 종료"),
                ("Enter", "빈 입력 시 종료"),
            ],
        },
        "en": {
            "dialogue": [
                ("assistant", "What can I help you with? Tell me a ticker to analyze."),
                ("you", "analyze AAPL"),
                ("assistant", "I'll stream MACD, RSI, channel, and probability for AAPL."),
                ("you", "analyze MSFT"),
                ("assistant", "Global tickers share the same summary format."),
                ("assistant", "You can also export the report as JSON, CSV, or DB rows."),
            ],
            "shortcuts_title": "Shortcuts",
            "shortcuts": [
                ("/help", "Show usage"),
                ("/quit", "Exit immediately"),
                ("Enter", "Blank input exits"),
            ],
        },
    }

    msg = messages.get(lang_code, messages["ko"])

    for speaker, text in msg["dialogue"]:
        label = USER_LINE if speaker == "you" else ASSISTANT_LINE
        stream_print(f"{label}{text}", delay=0.003)

    print_instant()
    stream_print(msg["shortcuts_title"], delay=0.003)
    for cmd, desc in msg["shortcuts"]:
        stream_print(f"   {cmd:<10} {desc}", delay=0.003)
    print_instant()
    print_instant("  " + "─" * 68)
    print_instant()


def show_interactive_help(lang: "LanguagePack") -> None:
    """Display help message in interactive mode"""
    print_instant()
    print_instant("  " + "═" * 68)

    lang_code = lang.code if hasattr(lang, 'code') else "ko"

    messages = {
        "ko": {
            "title": "  📚 \033[1m도움말이 필요하셨군요! 제가 도와드릴게요.\033[0m",
            "usage_title": "  💬 \033[1m기본 사용법\033[0m",
            "usage_text": "     티커 심볼만 입력하시면 바로 분석이 시작됩니다!",
            "examples_title": "  ✨ \033[1m예시\033[0m",
            "examples": [
                ("AAPL", "→ 애플 주식 분석"),
                ("TSLA", "→ 테슬라 주식 분석"),
                ("005930.KS", "→ 삼성전자 분석"),
                ("MSFT", "→ 마이크로소프트 분석"),
            ],
            "commands_title": "  🎯 \033[1m특별 명령어\033[0m",
            "commands": [
                ("/help", "→ 이 도움말 다시 보기"),
                ("/quit 또는 /exit", "→ 프로그램 종료하기"),
                ("엔터만 누르기", "→ 프로그램 종료하기"),
            ],
            "tip_title": "  💡 \033[1mTip\033[0m",
            "tips": [
                "     분석 결과는 실시간으로 스트리밍되어 타이핑되듯이 표시됩니다.",
                "     분석 후 JSON, CSV, 데이터베이스 등으로 저장할 수 있어요!",
            ]
        },
        "en": {
            "title": "  📚 \033[1mLet me help you!\033[0m",
            "usage_title": "  💬 \033[1mBasic Usage\033[0m",
            "usage_text": "     Just enter a ticker symbol to start analysis!",
            "examples_title": "  ✨ \033[1mExamples\033[0m",
            "examples": [
                ("AAPL", "→ Analyze Apple stock"),
                ("TSLA", "→ Analyze Tesla stock"),
                ("GOOGL", "→ Analyze Google stock"),
                ("MSFT", "→ Analyze Microsoft stock"),
            ],
            "commands_title": "  🎯 \033[1mSpecial Commands\033[0m",
            "commands": [
                ("/help", "→ Show this help again"),
                ("/quit or /exit", "→ Exit the program"),
                ("Press Enter", "→ Exit the program"),
            ],
            "tip_title": "  💡 \033[1mTip\033[0m",
            "tips": [
                "     Analysis results are streamed in real-time like typing.",
                "     You can save results to JSON, CSV, or databases!",
            ]
        }
    }

    msg = messages.get(lang_code, messages["ko"])

    stream_print(msg["title"], delay=0.005)
    print_instant()

    stream_print(msg["usage_title"], delay=0.003)
    print_instant()
    stream_print(msg["usage_text"], delay=0.003)
    print_instant()

    stream_print(msg["examples_title"], delay=0.003)
    print_instant()
    for cmd, desc in msg["examples"]:
        stream_print(f"     \033[1;36m{cmd:<15}\033[0m {desc}", delay=0.003)

    print_instant()
    stream_print(msg["commands_title"], delay=0.003)
    print_instant()

    for cmd, desc in msg["commands"]:
        stream_print(f"     \033[1;33m{cmd:<20}\033[0m {desc}", delay=0.003)

    print_instant()
    stream_print(msg["tip_title"], delay=0.003)
    for tip in msg["tips"]:
        stream_print(tip, delay=0.003)
    print_instant()
    print_instant("  " + "═" * 68)
    print_instant()
