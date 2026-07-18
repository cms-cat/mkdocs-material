from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from resolve_release_version import (
    VersionResolutionError,
    main,
    read_core_version,
    resolve_release_version,
)


class ResolveReleaseVersionTests(unittest.TestCase):
    def test_uses_core_version_when_no_release_exists(self) -> None:
        self.assertEqual(resolve_release_version((9, 7, 7), []), "9.7.7")

    def test_uses_newer_core_version_without_subpatch(self) -> None:
        self.assertEqual(
            resolve_release_version((9, 7, 7), ["9.7.6.3"]), "9.7.7"
        )

    def test_starts_subpatch_series_for_unchanged_core(self) -> None:
        self.assertEqual(
            resolve_release_version((9, 7, 7), ["9.7.7"]), "9.7.7.1"
        )

    def test_increments_existing_subpatch(self) -> None:
        self.assertEqual(
            resolve_release_version((9, 7, 7), ["9.7.7", "9.7.7.1"]),
            "9.7.7.2",
        )

    def test_repeated_runs_coalesce_while_draft_is_unpublished(self) -> None:
        published_tags = ["9.7.7"]
        first_run = resolve_release_version((9, 7, 7), published_tags)
        second_run = resolve_release_version((9, 7, 7), published_tags)
        self.assertEqual(first_run, "9.7.7.1")
        self.assertEqual(second_run, first_run)

    def test_selects_highest_release_and_ignores_unrelated_tags(self) -> None:
        tags = ["not-a-package-release", "9.7.7.2", "9.7.6.20", "9.7.7.1"]
        self.assertEqual(resolve_release_version((9, 7, 7), tags), "9.7.7.3")

    def test_rejects_core_version_regression(self) -> None:
        with self.assertRaisesRegex(VersionResolutionError, "older than"):
            resolve_release_version((9, 7, 7), ["9.7.8"])


class ReadCoreVersionTests(unittest.TestCase):
    def read(self, contents: str) -> tuple[int, int, int]:
        with tempfile.TemporaryDirectory() as directory:
            requirements = Path(directory) / "requirements.txt"
            requirements.write_text(contents, encoding="utf-8")
            return read_core_version(requirements)

    def test_reads_exact_pin(self) -> None:
        self.assertEqual(self.read("mkdocs-material==9.7.7\n"), (9, 7, 7))

    def test_rejects_missing_pin(self) -> None:
        with self.assertRaisesRegex(VersionResolutionError, "does not contain"):
            self.read("mkdocs==1.6.1\n")

    def test_rejects_unsupported_version(self) -> None:
        with self.assertRaisesRegex(VersionResolutionError, "X.Y.Z"):
            self.read("mkdocs-material==9.7.7rc1\n")

    def test_rejects_multiple_requirements(self) -> None:
        with self.assertRaisesRegex(VersionResolutionError, "multiple"):
            self.read("mkdocs-material==9.7.6\nmkdocs_material==9.7.7\n")


class CommandLineTests(unittest.TestCase):
    def test_emits_github_actions_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            requirements = Path(directory) / "requirements.txt"
            requirements.write_text("mkdocs-material==9.7.7\n", encoding="utf-8")
            output = io.StringIO()
            with patch("sys.stdin", io.StringIO("9.7.7\n")), redirect_stdout(output):
                result = main(["--requirements", str(requirements)])

        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue(), "version=9.7.7.1\n")


if __name__ == "__main__":
    unittest.main()
