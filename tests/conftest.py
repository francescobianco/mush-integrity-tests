"""Pytest configuration and fixtures for bash/system tool testing."""

import subprocess
import pytest
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class CommandResult:
    """Result of a command execution."""
    returncode: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.returncode == 0

    def assert_success(self):
        """Assert the command succeeded."""
        assert self.returncode == 0, f"Command failed with code {self.returncode}: {self.stderr}"

    def assert_failed(self, expected_code: Optional[int] = None):
        """Assert the command failed, optionally with a specific exit code."""
        assert self.returncode != 0, "Command should have failed but succeeded"
        if expected_code is not None:
            assert self.returncode == expected_code, f"Expected exit code {expected_code}, got {self.returncode}"

    def assert_stdout_contains(self, text: str):
        """Assert stdout contains the given text."""
        assert text in self.stdout, f"Expected '{text}' in stdout, got: {self.stdout}"

    def assert_stdout_equals(self, text: str):
        """Assert stdout equals the given text (stripped)."""
        assert self.stdout.strip() == text.strip(), f"Expected '{text}', got: '{self.stdout.strip()}'"

    def assert_stderr_contains(self, text: str):
        """Assert stderr contains the given text."""
        assert text in self.stderr, f"Expected '{text}' in stderr, got: {self.stderr}"

    def assert_stderr_empty(self):
        """Assert stderr is empty."""
        assert self.stderr.strip() == "", f"Expected empty stderr, got: {self.stderr}"


class CommandRunner:
    """Runner for executing commands and scripts."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def run(
        self,
        command: str | list[str],
        cwd: Optional[Path] = None,
        env: Optional[dict] = None,
        timeout: int = 30,
        shell: bool = False,
        input_text: Optional[str] = None
    ) -> CommandResult:
        """
        Run a command and return the result.

        Args:
            command: Command as string (if shell=True) or list of args
            cwd: Working directory (defaults to base_dir)
            env: Environment variables to set
            timeout: Timeout in seconds
            shell: Whether to run through shell
            input_text: Text to send to stdin
        """
        if cwd is None:
            cwd = self.base_dir

        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                timeout=timeout,
                shell=shell,
                capture_output=True,
                text=True,
                input=input_text
            )
            return CommandResult(
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr
            )
        except subprocess.TimeoutExpired as e:
            return CommandResult(
                returncode=-1,
                stdout=e.stdout or "",
                stderr=f"Command timed out after {timeout}s"
            )
        except FileNotFoundError as e:
            return CommandResult(
                returncode=127,  # Standard "command not found" exit code
                stdout="",
                stderr=f"Command not found: {e.filename}"
            )

    def run_script(
        self,
        script_path: str | Path,
        args: Optional[list[str]] = None,
        **kwargs
    ) -> CommandResult:
        """Run a bash script with optional arguments."""
        script = self.base_dir / script_path
        cmd = ["bash", str(script)]
        if args:
            cmd.extend(args)
        return self.run(cmd, **kwargs)

    def run_bash(self, script: str, **kwargs) -> CommandResult:
        """Run inline bash code."""
        return self.run(["bash", "-c", script], **kwargs)


@pytest.fixture
def project_dir() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def fixtures_dir(project_dir: Path) -> Path:
    """Return the fixtures directory."""
    return project_dir / "fixtures"


@pytest.fixture
def empty_fixture(fixtures_dir: Path) -> Path:
    """Return the empty fixture directory (for tests that create new content)."""
    return fixtures_dir / "empty"


@pytest.fixture
def runner(project_dir: Path) -> CommandRunner:
    """Return a CommandRunner instance."""
    return CommandRunner(project_dir)


@pytest.fixture
def tmp_script(tmp_path: Path):
    """Factory fixture to create temporary scripts for testing."""
    def _create_script(content: str, name: str = "test_script.sh") -> Path:
        script_path = tmp_path / name
        script_path.write_text(content)
        script_path.chmod(0o755)
        return script_path
    return _create_script