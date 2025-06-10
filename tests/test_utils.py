import tempfile
from pathlib import Path

import pytest

from mm_cryptocurrency import read_items_from_file


class TestReadItemsFromFile:
    """Tests for the read_items_from_file function."""

    def test_successful_reading(self) -> None:
        """Test reading valid files with different content."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "test.txt"

            # Test simple case
            test_file.write_text("item1\nitem2\nitem3")
            result = read_items_from_file(test_file, lambda x: len(x) > 0)
            assert result == ["item1", "item2", "item3"]

            # Test with validation (only items starting with 'item')
            result = read_items_from_file(test_file, lambda x: x.startswith("item"))
            assert result == ["item1", "item2", "item3"]

    def test_lowercase_option(self) -> None:
        """Test the lowercase parameter functionality."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "test.txt"
            test_file.write_text("UPPER\nMixed\nlower")

            # Without lowercase
            result = read_items_from_file(test_file, lambda _: True)
            assert result == ["UPPER", "Mixed", "lower"]

            # With lowercase
            result = read_items_from_file(test_file, lambda _: True, lowercase=True)
            assert result == ["upper", "mixed", "lower"]

    def test_empty_lines_handling(self) -> None:
        """Test that empty lines are skipped."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "test.txt"
            test_file.write_text("item1\n\n\nitem2\n\nitem3\n")

            result = read_items_from_file(test_file, lambda _: True)
            assert result == ["item1", "item2", "item3"]

    def test_whitespace_handling(self) -> None:
        """Test that leading/trailing whitespace is stripped."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "test.txt"
            test_file.write_text("  item1  \n\titem2\t\n item3 ")

            result = read_items_from_file(test_file, lambda _: True)
            assert result == ["item1", "item2", "item3"]

    def test_validation_errors_with_line_numbers(self) -> None:
        """Test validation errors include line numbers."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "test.txt"
            test_file.write_text("valid1\ninvalid\nvalid2")

            # Validator that rejects 'invalid'
            def validator(item: str) -> bool:
                return item != "invalid"

            with pytest.raises(ValueError) as exc_info:
                read_items_from_file(test_file, validator)

            error_msg = str(exc_info.value)
            assert "line 2" in error_msg
            assert "invalid" in error_msg
            assert str(test_file) in error_msg

    def test_validation_errors_with_empty_lines(self) -> None:
        """Test that line numbers account for skipped empty lines."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "test.txt"
            test_file.write_text("valid1\n\n\ninvalid\nvalid2")

            def validator(item: str) -> bool:
                return item != "invalid"

            with pytest.raises(ValueError) as exc_info:
                read_items_from_file(test_file, validator)

            error_msg = str(exc_info.value)
            assert "line 4" in error_msg  # Should be line 4, not 2

    def test_missing_file_error(self) -> None:
        """Test error when file doesn't exist."""
        non_existent = Path("/tmp/nonexistent_file.txt")

        with pytest.raises(ValueError) as exc_info:
            read_items_from_file(non_existent, lambda _: True)

        error_msg = str(exc_info.value)
        assert "is not a file" in error_msg
        assert str(non_existent) in error_msg

    def test_directory_instead_of_file(self) -> None:
        """Test error when path points to directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            dir_path = Path(tmp_dir)

            with pytest.raises(ValueError) as exc_info:
                read_items_from_file(dir_path, lambda _: True)

            error_msg = str(exc_info.value)
            assert "is not a file" in error_msg

    def test_file_read_permission_error(self) -> None:
        """Test handling of file read permission errors."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "test.txt"
            test_file.write_text("content")
            test_file.chmod(0o000)  # Remove all permissions

            try:
                with pytest.raises(ValueError) as exc_info:
                    read_items_from_file(test_file, lambda _: True)

                error_msg = str(exc_info.value)
                assert "Cannot read file" in error_msg
                assert str(test_file) in error_msg
            finally:
                # Restore permissions for cleanup
                test_file.chmod(0o644)

    def test_expanduser_functionality(self) -> None:
        """Test that ~ in paths is expanded."""
        home_path = Path("~/test_file.txt")
        expanded_path = home_path.expanduser()

        # We can't actually test file reading with ~ without creating files in home dir,
        # but we can test that the function attempts to expand it by checking the error message
        with pytest.raises(ValueError) as exc_info:
            read_items_from_file(home_path, lambda _: True)

        error_msg = str(exc_info.value)
        # The error should contain the expanded path, not the ~ path
        assert str(expanded_path) in error_msg
        assert "~" not in error_msg

    def test_empty_file(self) -> None:
        """Test reading empty file returns empty list."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "empty.txt"
            test_file.write_text("")

            result = read_items_from_file(test_file, lambda _: True)
            assert result == []

    def test_file_with_only_whitespace(self) -> None:
        """Test file containing only whitespace returns empty list."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "whitespace.txt"
            test_file.write_text("  \n\t\n  \n")

            result = read_items_from_file(test_file, lambda _: True)
            assert result == []

    def test_complex_validation_scenario(self) -> None:
        """Test complex validation with lowercase and specific rules."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "test.txt"
            test_file.write_text("ADDR123\nADDR456\nADDR789")

            # Validator: lowercase items must start with 'addr' and be at least 7 chars
            def validator(item: str) -> bool:
                return item.startswith("addr") and len(item) >= 7

            result = read_items_from_file(test_file, validator, lowercase=True)
            assert result == ["addr123", "addr456", "addr789"]

            # Test validation error with lowercase
            test_file.write_text("ADDR123\nINVALID123\nADDR456")
            with pytest.raises(ValueError) as exc_info:
                read_items_from_file(test_file, validator, lowercase=True)

            error_msg = str(exc_info.value)
            assert "line 2" in error_msg
            assert "invalid123" in error_msg  # Should show lowercase version
