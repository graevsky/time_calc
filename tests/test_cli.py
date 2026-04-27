from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from time_calc.cli import (
    DeltaResult,
    delta_times,
    diff_times,
    format_clock,
    format_duration,
    parse_args,
    parse_time,
    sum_times,
)


class TimeCalcTests(unittest.TestCase):
    def test_parse_time_accepts_valid_value(self) -> None:
        self.assertEqual(parse_time("2359"), 23 * 60 + 59)

    def test_parse_time_rejects_invalid_hour(self) -> None:
        with self.assertRaises(ValueError):
            parse_time("2460")

    def test_parse_args_supports_delta_short_flag(self) -> None:
        parsed = parse_args(["-dt", "1000", "2330"])
        self.assertEqual(parsed.mode, "delta")
        self.assertEqual(parsed.times, ["1000", "2330"])

    def test_sum_wraps_across_midnight(self) -> None:
        result = sum_times([parse_time("2320"), parse_time("0050")])
        self.assertEqual(format_clock(result), "0010")

    def test_diff_wraps_across_midnight(self) -> None:
        result = diff_times([parse_time("0020"), parse_time("0110")])
        self.assertEqual(format_clock(result), "2310")

    def test_delta_reports_all_modes(self) -> None:
        result: DeltaResult = delta_times(parse_time("1000"), parse_time("2330"))
        self.assertEqual(format_duration(result.direct), "1330")
        self.assertEqual(format_duration(result.via_12h), "0130")
        self.assertEqual(format_duration(result.via_24h), "1030")

    def test_delta_same_times_can_show_full_cycle(self) -> None:
        result = delta_times(parse_time("0830"), parse_time("0830"))
        self.assertEqual(format_duration(result.direct), "0000")
        self.assertEqual(format_duration(result.via_12h), "1200")
        self.assertEqual(format_duration(result.via_24h), "2400")


if __name__ == "__main__":
    unittest.main()
