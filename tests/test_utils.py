from unittest.mock import patch

import pytest

from mm_cryptocurrency.utils import random_str_choice


class TestRandomStrChoice:
    """Test cases for the random_str_choice function."""

    def test_returns_none_when_source_is_none(self):
        """Should return None when source is None."""
        result = random_str_choice(None)
        assert result is None

    def test_returns_string_when_source_is_string(self):
        """Should return the same string when source is a string."""
        test_string = "hello"
        result = random_str_choice(test_string)
        assert result == test_string

    def test_returns_string_when_source_is_empty_string(self):
        """Should return empty string when source is empty string."""
        result = random_str_choice("")
        assert result == ""

    def test_returns_none_when_source_is_empty_list(self):
        """Should return None when source is an empty list."""
        result = random_str_choice([])
        assert result is None

    def test_returns_none_when_source_is_empty_tuple(self):
        """Should return None when source is an empty tuple."""
        result = random_str_choice(())
        assert result is None

    def test_returns_single_item_from_single_element_list(self):
        """Should return the single item when list has one element."""
        test_list = ["only_item"]
        result = random_str_choice(test_list)
        assert result == "only_item"

    def test_returns_single_item_from_single_element_tuple(self):
        """Should return the single item when tuple has one element."""
        test_tuple = ("only_item",)
        result = random_str_choice(test_tuple)
        assert result == "only_item"

    @patch("random.choice")
    def test_calls_random_choice_for_multiple_items_list(self, mock_choice):
        """Should call random.choice when list has multiple items."""
        test_list = ["item1", "item2", "item3"]
        mock_choice.return_value = "item2"

        result = random_str_choice(test_list)

        mock_choice.assert_called_once_with(test_list)
        assert result == "item2"

    @patch("random.choice")
    def test_calls_random_choice_for_multiple_items_tuple(self, mock_choice):
        """Should call random.choice when tuple has multiple items."""
        test_tuple = ("item1", "item2", "item3")
        mock_choice.return_value = "item3"

        result = random_str_choice(test_tuple)

        mock_choice.assert_called_once_with(test_tuple)
        assert result == "item3"

    def test_returns_item_from_list_multiple_calls(self):
        """Should return items from the list (integration test)."""
        test_list = ["apple", "banana", "cherry"]
        results = set()

        # Run multiple times to check randomness
        for _ in range(100):
            result = random_str_choice(test_list)
            assert result in test_list
            results.add(result)

        # With 100 calls, we should get at least 2 different results
        # (this could theoretically fail but extremely unlikely)
        assert len(results) >= 2

    def test_type_hints_compliance(self):
        """Test that function works with different sequence types."""
        # Test with different sequence types
        assert random_str_choice(["a", "b"]) in ["a", "b"]
        assert random_str_choice(("a", "b")) in ["a", "b"]
        assert random_str_choice(range(0)) is None  # empty range

    def test_works_with_unicode_strings(self):
        """Should work correctly with unicode strings."""
        unicode_list = ["🎉", "🚀", "🌟"]
        result = random_str_choice(unicode_list)
        assert result in unicode_list

        unicode_string = "🎯"
        result = random_str_choice(unicode_string)
        assert result == unicode_string

    def test_works_with_long_strings(self):
        """Should work correctly with long strings."""
        long_string = "a" * 1000
        result = random_str_choice(long_string)
        assert result == long_string

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (None, None),
            ("", ""),
            ("single", "single"),
            ([], None),
            ((), None),
            (["one"], "one"),
            (("one",), "one"),
        ],
    )
    def test_parametrized_cases(self, test_input, expected):
        """Parametrized test for various edge cases."""
        result = random_str_choice(test_input)
        if expected is None:
            assert result is None
        else:
            assert result == expected
