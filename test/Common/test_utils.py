import time
import pytest
from src.Common.utils import parse_boolean, print_timings


# ---------------------------------------------------------------------------
# parse_boolean
# ---------------------------------------------------------------------------

class TestParseBoolean:
    # String truthy values
    def test_lowercase_true(self):
        assert parse_boolean("true") is True

    def test_uppercase_true(self):
        assert parse_boolean("TRUE") is True

    def test_mixed_case_true(self):
        assert parse_boolean("True") is True

    def test_french_vrai(self):
        assert parse_boolean("vrai") is True

    def test_french_vrai_uppercase(self):
        assert parse_boolean("VRAI") is True

    # String falsy values
    def test_lowercase_false(self):
        assert parse_boolean("false") is False

    def test_uppercase_false(self):
        assert parse_boolean("FALSE") is False

    def test_arbitrary_string_returns_false(self):
        assert parse_boolean("yes") is False

    def test_empty_string_returns_false(self):
        assert parse_boolean("") is False

    def test_random_string_returns_false(self):
        assert parse_boolean("oui") is False

    # Bool passthrough
    def test_bool_true_passthrough(self):
        assert parse_boolean(True) is True

    def test_bool_false_passthrough(self):
        assert parse_boolean(False) is False


# ---------------------------------------------------------------------------
# print_timings
# ---------------------------------------------------------------------------

class TestPrintTimings:
    def test_decorator_returns_function_result(self):
        @print_timings
        def add(a, b):
            return a + b

        assert add(2, 3) == 5

    def test_decorator_preserves_return_value_for_none(self):
        @print_timings
        def do_nothing():
            return None

        assert do_nothing() is None

    def test_decorator_passes_args_and_kwargs(self):
        @print_timings
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        assert greet("World", greeting="Hi") == "Hi, World!"

    def test_decorator_prints_function_name(self, capsys):
        @print_timings
        def my_function():
            return 42

        my_function()
        captured = capsys.readouterr()
        assert "my_function" in captured.out

    def test_decorator_prints_timing(self, capsys):
        @print_timings
        def quick():
            pass

        quick()
        captured = capsys.readouterr()
        assert "executed in" in captured.out
