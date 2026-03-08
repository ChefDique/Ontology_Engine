"""Tests for the CLI entry point __main__.py (TASK_F4)."""

from unittest.mock import patch

import pytest

from ontology_engine.__main__ import main


class TestCLIParsing:
    """Tests for CLI argument parsing."""

    def test_no_args_shows_help(self, capsys):
        """No arguments shows help and returns 1."""
        result = main([])
        assert result == 1

    def test_run_requires_crm(self):
        """Run command requires --crm flag."""
        with pytest.raises(SystemExit):
            main(["run", "test.pdf"])

    def test_run_invalid_crm(self):
        """Run command rejects invalid CRM values."""
        with pytest.raises(SystemExit):
            main(["run", "test.pdf", "--crm", "salesforce"])


class TestCLIHITL:
    """Tests for CLI HITL subcommands."""

    def test_hitl_list_empty(self, capsys, tmp_path, monkeypatch):
        """HITL list with empty queue prints 'No pending'."""
        from ontology_engine.hitl.review_queue import ReviewQueue
        _orig_init = ReviewQueue.__init__

        def _patched_init(self, queue_dir=None):
            _orig_init(self, queue_dir=tmp_path / "empty_q")

        monkeypatch.setattr(ReviewQueue, "__init__", _patched_init)

        result = main(["hitl", "list"])
        assert result == 0
        captured = capsys.readouterr()
        assert "No pending" in captured.out

    def test_hitl_show_nonexistent(self, capsys):
        """HITL show nonexistent ID returns error."""
        result = main(["hitl", "show", "nonexistent-id"])
        assert result == 1

    def test_hitl_approve_nonexistent(self, capsys):
        """HITL approve nonexistent ID returns error."""
        result = main(["hitl", "approve", "nonexistent-id"])
        assert result == 1

    def test_hitl_no_subcommand(self, capsys):
        """HITL without subcommand shows help."""
        result = main(["hitl"])
        assert result == 1


class TestCLIRun:
    """Tests for CLI run command."""

    def test_run_nonexistent_file(self, capsys):
        """Run with nonexistent file returns error."""
        result = main(["run", "/nonexistent/file.pdf", "--crm", "buildertrend"])
        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err

    @patch("ontology_engine.pipeline.run_pipeline")
    def test_run_success(self, mock_pipeline, capsys, tmp_path):
        """Run command prints summary on success."""
        input_pdf = tmp_path / "test.pdf"
        input_pdf.write_text("fake pdf")

        mock_pipeline.return_value = {
            "success": True,
            "output_path": str(tmp_path / "output.csv"),
            "hitl_items": [],
            "metadata": {
                "input_file": str(input_pdf),
                "target_crm": "buildertrend",
                "duration_seconds": 1.5,
                "page_count": 3,
                "line_item_count": 10,
            },
        }

        result = main(["run", str(input_pdf), "--crm", "buildertrend"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Pipeline Complete" in captured.out
        assert "buildertrend" in captured.out
