"""Tests for mush --version command."""

import re


class TestMushCommandVersion:
    """Tests Mush version command output format."""

    # Pattern: "Mush v0.2.0 (2026-01-27 develop)"
    VERSION_PATTERN = re.compile(
        r"^Mush v\d+\.\d+\.\d+ \(\d{4}-\d{2}-\d{2} \S+\)$"
    )

    def test_version_format(self, runner):
        """Test that mush --version outputs the expected format."""
        result = runner.run(["mush", "--version"])
        result.assert_success()
        result.assert_stderr_empty()

        output = result.stdout.strip()
        assert self.VERSION_PATTERN.match(output), (
            f"Version output does not match expected format.\n"
            f"Expected: 'Mush vX.Y.Z (YYYY-MM-DD branch)'\n"
            f"Got: '{output}'"
        )

    def test_version_components(self, runner):
        """Test that version string contains valid components."""
        result = runner.run(["mush", "--version"])
        result.assert_success()

        output = result.stdout.strip()

        # Verify starts with "Mush v"
        assert output.startswith("Mush v"), f"Should start with 'Mush v', got: '{output}'"

        # Extract and validate version number (semver)
        version_match = re.search(r"v(\d+)\.(\d+)\.(\d+)", output)
        assert version_match, f"Could not find semver in output: '{output}'"
        major, minor, patch = map(int, version_match.groups())
        assert major >= 0 and minor >= 0 and patch >= 0

        # Extract and validate date (YYYY-MM-DD)
        date_match = re.search(r"\((\d{4})-(\d{2})-(\d{2})", output)
        assert date_match, f"Could not find date in output: '{output}'"
        year, month, day = map(int, date_match.groups())
        assert 2020 <= year <= 2100, f"Year out of range: {year}"
        assert 1 <= month <= 12, f"Month out of range: {month}"
        assert 1 <= day <= 31, f"Day out of range: {day}"

        # Verify branch name exists (non-empty, no spaces)
        branch_match = re.search(r"\d{4}-\d{2}-\d{2} (\S+)\)$", output)
        assert branch_match, f"Could not find branch name in output: '{output}'"
        branch = branch_match.group(1)
        assert len(branch) > 0, "Branch name should not be empty"
