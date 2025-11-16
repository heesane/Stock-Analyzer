from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from getpass import getpass
from typing import Iterable, List, Sequence

from stock_analyzer.services.exporters import (
    CsvExporter,
    Exporter,
    JsonExporter,
    MySQLExporter,
    PostgresExporter,
)
from stock_analyzer.services.language import LanguagePack, get_language

from .analysis import analyze_ticker
from .report import render_cli_report
from .banner import show_welcome_message, show_interactive_help
from .streaming import stream_print, print_instant
from .menu import select_export_format

COMMANDS = {"analyze", "interactive", "i", "export"}
DEFAULT_BENCHMARK = "SPY"
DEFAULT_REL_WINDOW = 60


@dataclass
class AppContext:
    lang: LanguagePack
    benchmark: str
    relative_window: int


def _split_command_list(value: str) -> set[str]:
    return {item.strip().lower() for item in value.split(",") if item.strip()}


def _command_list(context: AppContext, key: str) -> set[str]:
    raw = context.lang.t(key)
    if raw == key:
        return set()
    return _split_command_list(raw)


def _message_or_default(lang: LanguagePack, key: str, default: str) -> str:
    value = lang.t(key)
    return default if value == key else value


def _build_context(
    lang_code: str | None,
    *,
    benchmark: str | None = None,
    relative_window: int | None = None,
) -> AppContext:
    lang = get_language(lang_code)
    default_benchmark = _message_or_default(lang, "cli.defaults.benchmark", DEFAULT_BENCHMARK)
    default_window_raw = _message_or_default(
        lang, "cli.defaults.relative_window", str(DEFAULT_REL_WINDOW)
    )
    try:
        default_window = int(default_window_raw)
    except ValueError:
        default_window = DEFAULT_REL_WINDOW
    bench_value = (benchmark or default_benchmark or DEFAULT_BENCHMARK).upper()
    window_value = relative_window or default_window
    return AppContext(lang=lang, benchmark=bench_value, relative_window=window_value)


def _extract_option(argv: Sequence[str] | None, name: str) -> str | None:
    if not argv:
        return None
    for idx, value in enumerate(argv):
        if value == name and idx + 1 < len(argv):
            return argv[idx + 1]
    return None


def _extract_int_option(argv: Sequence[str] | None, name: str) -> int | None:
    value = _extract_option(argv, name)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _strip_known_global_options(argv: Sequence[str] | None) -> list[str]:
    if not argv:
        return []
    known = {"--lang", "--benchmark", "--backtest"}
    result: list[str] = []
    skip_next = False
    for idx, value in enumerate(argv):
        if skip_next:
            skip_next = False
            continue
        if value in known:
            skip_next = True
            continue
        result.append(value)
    return result


def _user_prompt(context: AppContext) -> str:
    return context.lang.t("cli.prompt.user")


def assistant_stream(context: AppContext, text: str, delay: float = 0.005) -> None:
    prefix = context.lang.t("cli.prompt.assistant")
    stream_print(f"{prefix}{text}", delay=delay)


def _add_analysis_options(parser: argparse.ArgumentParser, lang: LanguagePack) -> None:
    parser.add_argument(
        "--benchmark",
        help=lang.t("cli.parser.option.benchmark"),
    )
    parser.add_argument(
        "--backtest",
        type=int,
        help=lang.t("cli.parser.option.backtest"),
    )


def build_parser(context: AppContext) -> argparse.ArgumentParser:
    lang = context.lang
    parser = argparse.ArgumentParser(
        prog=lang.t("cli.parser.prog"),
        description=lang.t("cli.parser.description"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=lang.t("cli.parser.epilog"),
    )
    parser.add_argument("--lang", default=lang.code, help=lang.t("cli.parser.option.lang"))

    subparsers = parser.add_subparsers(dest="command", help=lang.t("cli.parser.subcommands_help"))

    analyze_parser = subparsers.add_parser(
        "analyze",
        help=lang.t("cli.parser.analyze.help"),
        description=lang.t("cli.parser.analyze.description"),
    )
    analyze_parser.add_argument(
        "tickers",
        nargs="*",
        help=lang.t("cli.parser.analyze.tickers"),
    )
    analyze_parser.add_argument(
        "--export",
        dest="exports",
        action="append",
        choices=["json", "csv", "mysql", "postgres"],
        help=lang.t("cli.parser.analyze.export"),
    )
    analyze_parser.add_argument("--json-path", help=lang.t("cli.parser.analyze.json_path"))
    analyze_parser.add_argument("--csv-path", help=lang.t("cli.parser.analyze.csv_path"))
    _add_analysis_options(analyze_parser, lang)

    interactive_parser = subparsers.add_parser(
        "interactive",
        aliases=["i"],
        help=lang.t("cli.parser.interactive.help"),
        description=lang.t("cli.parser.interactive.description"),
    )
    _add_analysis_options(interactive_parser, lang)

    export_parser = subparsers.add_parser(
        "export",
        help=lang.t("cli.parser.export.help"),
        description=lang.t("cli.parser.export.description"),
    )
    export_parser.add_argument(
        "tickers",
        nargs="+",
        help=lang.t("cli.parser.export.tickers"),
    )
    export_parser.add_argument(
        "--format",
        "-f",
        dest="exports",
        action="append",
        choices=["json", "csv", "mysql", "postgres"],
        required=True,
        help=lang.t("cli.parser.export.format"),
    )
    export_parser.add_argument("--json-path", help=lang.t("cli.parser.export.json_path"))
    export_parser.add_argument("--csv-path", help=lang.t("cli.parser.export.csv_path"))
    _add_analysis_options(export_parser, lang)

    for subparser in [analyze_parser, export_parser]:
        subparser.add_argument("--mysql-host", default="localhost")
        subparser.add_argument("--mysql-port", type=int, default=3306)
        subparser.add_argument("--mysql-user", default="root")
        subparser.add_argument("--mysql-password")
        subparser.add_argument("--mysql-database")
        subparser.add_argument("--mysql-table", default="stock_analysis")
        subparser.add_argument("--postgres-host", default="localhost")
        subparser.add_argument("--postgres-port", type=int, default=5432)
        subparser.add_argument("--postgres-user", default="postgres")
        subparser.add_argument("--postgres-password")
        subparser.add_argument("--postgres-database")
        subparser.add_argument("--postgres-table", default="stock_analysis")
        subparser.add_argument("--postgres-schema")

    return parser


def parse_args(argv: list[str] | None, context: AppContext) -> argparse.Namespace:
    parser = build_parser(context)
    return parser.parse_args(argv)


def prompt_ticker(context: AppContext) -> str:
    lang = context.lang
    prompt = f"\n{_user_prompt(context)}"
    help_inputs = _command_list(context, "cli.commands.help")
    quit_inputs = _command_list(context, "cli.commands.quit")

    try:
        ticker_input = input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print_instant("\n")
        return ""

    lowered = ticker_input.lower()
    if lowered in help_inputs:
        show_interactive_help(lang)
        return prompt_ticker(context)
    if lowered in quit_inputs:
        return ""
    if not ticker_input:
        print_instant()
        assistant_stream(context, lang.t("cli.prompt.confirm_exit"))
        return ""

    ticker = ticker_input.upper()
    command_display = lang.t("cli.prompt.analyze_command", ticker=ticker)
    print_instant(f"{_user_prompt(context)}{command_display}")
    assistant_stream(context, lang.t("cli.prompt.analyzing", ticker=ticker))
    print_instant()
    return ticker


def prompt_export_option(context: AppContext) -> str:
    return select_export_format(context.lang.code if hasattr(context.lang, "code") else "en")


def build_mysql_exporter_prompt(lang: LanguagePack) -> MySQLExporter:
    host = input(lang.t("prompt_mysql_host")).strip() or "localhost"
    port_input = input(lang.t("prompt_mysql_port")).strip()
    port = int(port_input) if port_input else 3306
    user = input(lang.t("prompt_mysql_user")).strip() or "root"
    password = getpass(lang.t("prompt_mysql_password"))
    database = input(lang.t("prompt_mysql_database")).strip()
    if not database:
        raise ValueError(lang.t("error_missing_option", flag="MySQL database"))
    table = input(lang.t("prompt_mysql_table")).strip() or "stock_analysis"
    return MySQLExporter(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        table=table,
    )


def build_postgres_exporter_prompt(lang: LanguagePack) -> PostgresExporter:
    host = input(lang.t("prompt_postgres_host")).strip() or "localhost"
    port_input = input(lang.t("prompt_postgres_port")).strip()
    port = int(port_input) if port_input else 5432
    user = input(lang.t("prompt_postgres_user")).strip() or "postgres"
    password = getpass(lang.t("prompt_postgres_password"))
    database = input(lang.t("prompt_postgres_database")).strip()
    if not database:
        raise ValueError(lang.t("error_missing_option", flag="PostgreSQL database"))
    schema = input(lang.t("prompt_postgres_schema")).strip() or None
    table = input(lang.t("prompt_postgres_table")).strip() or "stock_analysis"
    return PostgresExporter(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        schema=schema,
        table=table,
    )


def handle_interactive_export_flow(summary: dict, context: AppContext) -> None:
    default_stem = f"{summary['ticker']}_{summary['latest_date']}"
    lang = context.lang
    affirmatives = _command_list(context, "cli.export.affirmative_inputs")

    while True:
        choice = prompt_export_option(context)
        if not choice or choice == "skip":
            assistant_stream(context, lang.t("cli.export.skip"))
            break
        try:
            if choice == "json":
                default_path = f"exports/{default_stem}.json"
                assistant_stream(context, lang.t("cli.export.default_path", path=default_path))
                path_prompt = lang.t("cli.export.path_prompt")
                path = input(f"{_user_prompt(context)}{path_prompt}").strip() or default_path
                exporter: Exporter = JsonExporter(path)
            elif choice == "csv":
                default_path = "exports/analysis_log.csv"
                assistant_stream(context, lang.t("cli.export.default_path", path=default_path))
                path_prompt = lang.t("cli.export.path_prompt")
                path = input(f"{_user_prompt(context)}{path_prompt}").strip() or default_path
                exporter = CsvExporter(path)
            elif choice == "mysql":
                assistant_stream(context, lang.t("cli.export.mysql_prompt"))
                exporter = build_mysql_exporter_prompt(lang)
            elif choice == "postgres":
                assistant_stream(context, lang.t("cli.export.postgres_prompt"))
                exporter = build_postgres_exporter_prompt(lang)
            else:
                assistant_stream(context, lang.t("cli.export.unknown_format", format=choice))
                assistant_stream(context, lang.t("cli.export.unknown_hint"))
                continue

            assistant_stream(context, lang.t("cli.export.saving", format=choice.upper()))
            exporter.export(summary)
            assistant_stream(context, lang.t("cli.export.success", format=choice.upper()))
        except Exception as exc:  # noqa: BLE001
            assistant_stream(context, lang.t("cli.export.error", error=exc))
        else:
            prompt_more = lang.t("cli.export.more")
            again = input(f"{_user_prompt(context)}{prompt_more}").strip().lower()
            if again and again not in affirmatives:
                assistant_stream(context, lang.t("cli.export.done"))
                break


def _require_option(value: str | None, flag: str, lang: LanguagePack) -> str:
    if value:
        return value
    raise ValueError(lang.t("error_missing_option", flag=flag))


def build_mysql_exporter_from_args(args: argparse.Namespace, lang: LanguagePack) -> MySQLExporter:
    database = _require_option(args.mysql_database, "--mysql-database", lang)
    return MySQLExporter(
        host=args.mysql_host or "localhost",
        port=args.mysql_port or 3306,
        user=args.mysql_user or "root",
        password=args.mysql_password or "",
        database=database,
        table=args.mysql_table or "stock_analysis",
    )


def build_postgres_exporter_from_args(args: argparse.Namespace, lang: LanguagePack) -> PostgresExporter:
    database = _require_option(args.postgres_database, "--postgres-database", lang)
    return PostgresExporter(
        host=args.postgres_host or "localhost",
        port=args.postgres_port or 5432,
        user=args.postgres_user or "postgres",
        password=args.postgres_password or "",
        database=database,
        table=args.postgres_table or "stock_analysis",
        schema=args.postgres_schema or None,
    )


def build_exporters_from_args(
    summary: dict, args: argparse.Namespace, lang: LanguagePack
) -> list[tuple[str, Exporter]]:
    formats = args.exports or []
    exporters: list[tuple[str, Exporter]] = []
    if not formats:
        return exporters

    default_stem = f"{summary['ticker']}_{summary['latest_date']}"
    for fmt in formats:
        if fmt == "json":
            path = args.json_path or f"exports/{default_stem}.json"
            exporters.append(("json", JsonExporter(path)))
        elif fmt == "csv":
            path = args.csv_path or "exports/analysis_log.csv"
            exporters.append(("csv", CsvExporter(path)))
        elif fmt == "mysql":
            exporters.append(("mysql", build_mysql_exporter_from_args(args, lang)))
        elif fmt == "postgres":
            exporters.append(("postgres", build_postgres_exporter_from_args(args, lang)))
    return exporters


def run_configured_exports(summary: dict, args: argparse.Namespace, lang: LanguagePack) -> bool:
    try:
        exporters = build_exporters_from_args(summary, args, lang)
    except Exception as exc:  # noqa: BLE001
        print(lang.t("configured_export_prepare_error", error=exc))
        return False

    for label, exporter in exporters:
        try:
            exporter.export(summary)
            print(lang.t("configured_export_success", label=label.upper()))
        except Exception as exc:  # noqa: BLE001
            print(lang.t("configured_export_error", label=label.upper(), error=exc))
    return bool(exporters)


def process_ticker(
    ticker: str, args: argparse.Namespace, context: AppContext, interactive_exports: bool
) -> None:
    lang = context.lang
    try:
        assistant_stream(context, lang.t("cli.process.fetching"))
        summary = analyze_ticker(
            ticker,
            lang,
            benchmark_symbol=context.benchmark,
            relative_window=context.relative_window,
            backtest_days=getattr(args, "backtest", None),
        )
        assistant_stream(context, lang.t("cli.process.analyzing"))
        print_instant()
    except Exception as exc:  # noqa: BLE001
        print_instant()
        assistant_stream(context, lang.t("cli.process.error"))
        assistant_stream(context, lang.t("cli.process.error_detail", error=exc))
        assistant_stream(context, lang.t("cli.process.hint"))
        print_instant()
        return

    print_instant()
    print_instant()
    render_cli_report(summary, lang)
    print_instant()
    print_instant()

    exported = run_configured_exports(summary, args, lang)
    if interactive_exports and not exported:
        handle_interactive_export_flow(summary, context)


def interactive_loop(context: AppContext, args: argparse.Namespace) -> None:
    lang = context.lang
    exit_inputs = _command_list(context, "cli.interactive.exit_inputs")

    try:
        show_welcome_message(lang)

        while True:
            ticker = prompt_ticker(context)
            if not ticker:
                print_instant()
                assistant_stream(context, lang.t("cli.interactive.goodbye1"))
                assistant_stream(context, lang.t("cli.interactive.goodbye2"))
                print_instant()
                break

            process_ticker(ticker, args, context, interactive_exports=True)

            print_instant()

            try:
                again = input(
                    f"{_user_prompt(context)}{lang.t('cli.interactive.continue_prompt')}"
                ).strip().lower()
            except (KeyboardInterrupt, EOFError):
                print_instant("\n")
                again = "n"

            if again in exit_inputs:
                print_instant()
                assistant_stream(context, lang.t("cli.interactive.farewell1"))
                assistant_stream(context, lang.t("cli.interactive.farewell2"))
                assistant_stream(context, lang.t("cli.interactive.farewell3"))
                print_instant()
                break
            print_instant()
    except KeyboardInterrupt:
        print_instant("\n")
        assistant_stream(context, lang.t("cli.interactive.goodbye1"))
        assistant_stream(context, lang.t("cli.interactive.goodbye2"))
        print_instant()


def non_interactive_loop(
    tickers: Iterable[str], args: argparse.Namespace, context: AppContext
) -> None:
    if not args.exports:
        print(context.lang.t("configured_export_warning_no_export"))
    for ticker in tickers:
        process_ticker(ticker, args, context, interactive_exports=False)


def main(argv: list[str] | None = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    lang_code = _extract_option(argv, "--lang")
    benchmark_override = _extract_option(argv, "--benchmark")
    backtest_override = _extract_int_option(argv, "--backtest")
    context = _build_context(lang_code, benchmark=benchmark_override)

    try:
        if argv and any(opt in argv for opt in ("--help", "-h")):
            parser = build_parser(context)
            parser.parse_args(argv)
            return

        command_probe = _strip_known_global_options(argv)
        if not command_probe or command_probe[0] not in COMMANDS:
            args = argparse.Namespace(
                command="interactive",
                lang=context.lang.code,
                exports=None,
                json_path=None,
                csv_path=None,
                benchmark=None,
                backtest=backtest_override,
            )
            interactive_loop(context, args)
            return

        args = parse_args(argv, context)
        context = _build_context(args.lang, benchmark=args.benchmark)

        if not args.command:
            parser = build_parser(context)
            parser.print_help()
            return

        if args.command in ("interactive", "i"):
            interactive_loop(context, args)
            return

        if args.command == "analyze":
            tickers: List[str] = [t.upper() for t in (args.tickers or []) if t]
            if tickers:
                non_interactive_loop(tickers, args, context)
            else:
                interactive_loop(context, args)
            return

        if args.command == "export":
            tickers = [t.upper() for t in args.tickers if t]
            if not tickers:
                print(context.lang.t("cli.error.ticker_required"))
                return
            non_interactive_loop(tickers, args, context)
            return
    except KeyboardInterrupt:
        print_instant("\n")
        assistant_stream(context, context.lang.t("cli.exit"))
        print_instant()
        sys.exit(0)
