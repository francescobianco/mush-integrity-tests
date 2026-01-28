"""Tests for mush new command."""

import shutil
from pathlib import Path


class TestMushCommandNew:
    """Tests Mush new command functionality."""

    PROJECT_NAME = "test-new-project"

    # Expected file contents
    EXPECTED_MUSH_MD = """\
# Mush - Shell Package Manager

## Project Structure
- `Manifest.toml` - package manifest (name, version, edition, dependencies)
- `src/main.sh` - entry point with `main()` function
- `src/<module>.sh` - single-file modules
- `src/<module>/module.sh` - folder modules with submodules

## Keywords
- `module <name>` - load a module from src/
- `public <name>` - expose a submodule outside its parent module
- `extern package <name>` - declare external dependency
- `embed <name>` - embed module source in the final binary
- `inject file <name>` / `inject env <VAR>` - inject files or env vars at build time
- `legacy` - backward compatibility with traditional shell scripting

## Naming Convention
Functions follow the pattern: `<projectname>_<modulename>_<functionname>`
- Variables: lowercase snake_case (e.g. `my_variable`)
- Constants: UPPERCASE (e.g. `PI=3.14`)
- Functions: snake_case (e.g. `my_function`)

## Commands
- `mush new <name>` - create new project
- `mush init` - init project in existing directory
- `mush build` - build debug binary to target/debug/
- `mush build --release` - build release binary
- `mush run` - build and run

## Manifest.toml
[package] section: name, version (semver), edition ("2022")
[dependencies] section: `package_name = "version_constraint"`
"""

    EXPECTED_MAIN_SH = """\

main() {
  echo "Hello World!"
}
"""

    def _get_expected_manifest(self, project_name: str) -> str:
        """Return expected Manifest.toml content for given project name."""
        return f"""\
[package]
name = "{project_name}"
version = "0.1.0"
edition = "2022"

# See more keys and their definitions at https://mush.javanile.org/manifest.html

[dependencies]
"""

    def _cleanup_project(self, fixture_dir: Path):
        """Remove only the project directory created by this test."""
        project_path = fixture_dir / self.PROJECT_NAME
        if project_path.exists():
            shutil.rmtree(project_path)

    def test_new_creates_project_directory(self, runner, empty_fixture):
        """Test that 'mush new' creates the project directory with correct structure and content."""
        # Cleanup only our specific project from previous runs
        self._cleanup_project(empty_fixture)

        project_path = empty_fixture / self.PROJECT_NAME

        # Verify directory doesn't exist before
        assert not project_path.exists(), f"Project directory should not exist before test: {project_path}"

        # Run mush new command in the empty fixture directory
        result = runner.run(["mush", "new", self.PROJECT_NAME], cwd=empty_fixture)
        result.assert_success()

        # Verify the project directory was created
        assert project_path.exists(), f"Project directory was not created: {project_path}"
        assert project_path.is_dir(), f"Project path should be a directory: {project_path}"

        # Verify expected files exist
        expected_files = [
            "MUSH.md",
            "Manifest.toml",
            "src/main.sh",
        ]
        for file_path in expected_files:
            full_path = project_path / file_path
            assert full_path.exists(), f"Expected file not found: {file_path}"
            assert full_path.is_file(), f"Expected path should be a file: {file_path}"

        # Verify src directory exists
        src_dir = project_path / "src"
        assert src_dir.exists(), "src directory was not created"
        assert src_dir.is_dir(), "src should be a directory"

        # Verify file contents
        mush_md = (project_path / "MUSH.md").read_text()
        assert mush_md == self.EXPECTED_MUSH_MD, (
            f"MUSH.md content mismatch.\nExpected:\n{self.EXPECTED_MUSH_MD}\nGot:\n{mush_md}"
        )

        manifest = (project_path / "Manifest.toml").read_text()
        expected_manifest = self._get_expected_manifest(self.PROJECT_NAME)
        assert manifest == expected_manifest, (
            f"Manifest.toml content mismatch.\nExpected:\n{expected_manifest}\nGot:\n{manifest}"
        )

        main_sh = (project_path / "src/main.sh").read_text()
        assert main_sh == self.EXPECTED_MAIN_SH, (
            f"src/main.sh content mismatch.\nExpected:\n{self.EXPECTED_MAIN_SH}\nGot:\n{main_sh}"
        )

    def test_new_fails_if_directory_exists(self, runner, empty_fixture):
        """Test that 'mush new' fails if the project directory already exists."""
        project_path = empty_fixture / self.PROJECT_NAME

        # Ensure directory exists (create it if needed)
        project_path.mkdir(exist_ok=True)

        # Run mush new command - should fail
        result = runner.run(["mush", "new", self.PROJECT_NAME], cwd=empty_fixture)
        result.assert_failed()
