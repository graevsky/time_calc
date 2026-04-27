from __future__ import annotations

from dataclasses import dataclass
import sys

DAY_MINUTES = 24 * 60
HALF_DAY_MINUTES = 12 * 60

HELP_TEXT = """time_calc - shell time calculator

Usage:
  time_calc --help
  time_calc --sum [HHMM ...]
  time_calc --diff [HHMM ...]
  time_calc --delta [HHMM HHMM]

Options:
  -h, --help   Show this help text in English.
  -s, --sum    Sum any number of HHMM values modulo 24 hours.
  -d, --diff   Subtract each next HHMM value from the first one modulo 24 hours.
  -dt, --delta Compare exactly two HHMM values and print:
               Direct  - absolute difference in the same day
               Via 12h - difference if the route goes through a 12-hour boundary
               Via 24h - difference if the route goes through midnight

Input format:
  HHMM
  24-hour clock
  No separator

Interactive mode:
  If you do not pass times in the command line, enter one HHMM value per line.
  Type c and press Enter to calculate.
"""


class TimeCalcError(ValueError):
    """Raised when CLI input cannot be processed."""


@dataclass(frozen=True)
class ParsedArgs:
    mode: str | None
    times: list[str]
    show_help: bool = False


@dataclass(frozen=True)
class DeltaResult:
    direct: int
    via_12h: int
    via_24h: int


def parse_time(token: str) -> int:
    value = token.strip()
    if len(value) != 4 or not value.isdigit():
        raise TimeCalcError(f"Invalid time '{token}'. Expected HHMM.")

    hours = int(value[:2])
    minutes = int(value[2:])
    if hours > 23 or minutes > 59:
        raise TimeCalcError(f"Invalid time '{token}'. Expected 00:00 to 23:59.")

    return hours * 60 + minutes


def format_clock(total_minutes: int) -> str:
    normalized = total_minutes % DAY_MINUTES
    hours, minutes = divmod(normalized, 60)
    return f"{hours:02d}{minutes:02d}"


def format_duration(total_minutes: int) -> str:
    if total_minutes < 0 or total_minutes > DAY_MINUTES:
        raise TimeCalcError("Duration is out of range.")

    if total_minutes == DAY_MINUTES:
        return "2400"

    hours, minutes = divmod(total_minutes, 60)
    return f"{hours:02d}{minutes:02d}"


def parse_args(argv: list[str]) -> ParsedArgs:
    if not argv:
        return ParsedArgs(mode=None, times=[], show_help=True)

    mode: str | None = None
    times: list[str] = []

    for argument in argv:
        if argument in {"-h", "--help"}:
            return ParsedArgs(mode=None, times=[], show_help=True)

        if argument in {"-s", "--sum"}:
            mode = _assign_mode(mode, "sum", argument)
            continue

        if argument in {"-d", "--diff"}:
            mode = _assign_mode(mode, "diff", argument)
            continue

        if argument in {"-dt", "--delta"}:
            mode = _assign_mode(mode, "delta", argument)
            continue

        if argument.startswith("-"):
            raise TimeCalcError(f"Unknown argument: {argument}")

        times.append(argument)

    if mode is None:
        raise TimeCalcError("Please choose one mode: --sum, --diff, or --delta.")

    return ParsedArgs(mode=mode, times=times, show_help=False)


def _assign_mode(current_mode: str | None, next_mode: str, raw_argument: str) -> str:
    if current_mode and current_mode != next_mode:
        raise TimeCalcError(
            f"Only one mode can be used at a time. Problem argument: {raw_argument}"
        )
    return next_mode


def collect_interactive_times(
    required_count: int | None = None, input_stream: object | None = None
) -> list[int]:
    stream = sys.stdin if input_stream is None else input_stream

    if input_stream is None and hasattr(stream, "isatty") and stream.isatty():
        print("Enter times in HHMM format. Type c to calculate.")

    values: list[int] = []
    for raw_line in stream:
        token = raw_line.strip()
        if not token:
            continue

        if token.lower() == "c":
            break

        values.append(parse_time(token))
        if required_count is not None and len(values) > required_count:
            raise TimeCalcError(f"This mode accepts exactly {required_count} times.")

    if not values:
        raise TimeCalcError("No times were provided.")

    if required_count is not None and len(values) != required_count:
        raise TimeCalcError(f"This mode requires exactly {required_count} times.")

    return values


def sum_times(values: list[int]) -> int:
    if not values:
        raise TimeCalcError("At least one time is required for sum.")
    return sum(values) % DAY_MINUTES


def diff_times(values: list[int]) -> int:
    if not values:
        raise TimeCalcError("At least one time is required for diff.")

    result = values[0]
    for value in values[1:]:
        result = (result - value) % DAY_MINUTES
    return result


def delta_times(first: int, second: int) -> DeltaResult:
    direct = abs(second - first)
    via_12h = abs(HALF_DAY_MINUTES - direct)
    via_24h = DAY_MINUTES if direct == 0 else DAY_MINUTES - direct
    return DeltaResult(direct=direct, via_12h=via_12h, via_24h=via_24h)


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv

    try:
        parsed = parse_args(arguments)
        if parsed.show_help:
            print(HELP_TEXT.rstrip())
            return 0

        raw_times = parsed.times
        if raw_times:
            values = [parse_time(item) for item in raw_times]
        elif parsed.mode == "delta":
            values = collect_interactive_times(required_count=2)
        else:
            values = collect_interactive_times()

        if parsed.mode == "sum":
            print(f"Result: {format_clock(sum_times(values))}")
            return 0

        if parsed.mode == "diff":
            print(f"Result: {format_clock(diff_times(values))}")
            return 0

        if len(values) != 2:
            raise TimeCalcError("--delta requires exactly two times.")

        delta = delta_times(values[0], values[1])
        print(f"Direct: {format_duration(delta.direct)}")
        print(f"Via 12h: {format_duration(delta.via_12h)}")
        print(f"Via 24h: {format_duration(delta.via_24h)}")
        return 0
    except TimeCalcError as error:
        print(f"Error: {error}", file=sys.stderr)
        print("Use --help for usage.", file=sys.stderr)
        return 1
