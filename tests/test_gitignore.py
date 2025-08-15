import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
GITIGNORE = ROOT / ".gitignore"

@pytest.fixture(scope="module")
def gitignore_text():
    """
    Loads the .gitignore file content from the repository root.
    """
    if not GITIGNORE.exists():
        pytest.skip(".gitignore not found at repository root; skipping gitignore content tests.")
    return GITIGNORE.read_text(encoding="utf-8", errors="ignore")

@pytest.mark.describe("Gitignore presence and basic structure")
class TestGitignorePresence:
    def test_gitignore_exists(self):
        assert GITIGNORE.exists(), "Expected a .gitignore file at the repository root."

    def test_gitignore_is_text(self, gitignore_text):
        assert isinstance(gitignore_text, str)
        # Sanity: ensure it's not empty
        assert len(gitignore_text.strip()) > 0, ".gitignore should not be empty."

@pytest.mark.describe("Core Python ignores are present")
class TestPythonIgnores:
    @pytest.mark.parametrize("pattern", [
        r"^__pycache__/$",
        r"^\*\.py\[cod\]$",
        r"^\*\$py\.class$",
        r"^\.so$",
    ])
    def test_core_python_entries(self, gitignore_text, pattern):
        # Use re.M to match full lines
        assert re.search(pattern, gitignore_text, flags=re.M), f"Missing Python ignore pattern: {pattern}"

    @pytest.mark.parametrize("pattern", [
        r"^\.Python$",
        r"^build/$",
        r"^develop-eggs/$",
        r"^dist/$",
        r"^downloads/$",
        r"^eggs/$",
        r"^\.eggs/$",
        r"^lib/$",
        r"^lib64/$",
        r"^parts/$",
        r"^sdist/$",
        r"^var/$",
        r"^wheels/$",
        r"^share/python-wheels/$",
        r"^\*\.egg-info/$",
        r"^\.installed\.cfg$",
        r"^\*\.egg$",
        r"^MANIFEST$",
    ])
    def test_packaging_related_entries(self, gitignore_text, pattern):
        assert re.search(pattern, gitignore_text, flags=re.M), f"Missing packaging ignore pattern: {pattern}"

@pytest.mark.describe("Tooling and reports ignores are present")
class TestToolingIgnores:
    @pytest.mark.parametrize("pattern", [
        r"^htmlcov/$",
        r"^\.tox/$",
        r"^\.nox/$",
        r"^\.coverage$",
        r"^\.coverage\.\*$",
        r"^\.cache$",
        r"^nosetests\.xml$",
        r"^coverage\.xml$",
        r"^\*\.cover$",
        r"^\*\.py,cover$",
        r"^\.hypothesis/$",
        r"^\.pytest_cache/$",
        r"^cover/$",
    ])
    def test_test_and_coverage_related_entries(self, gitignore_text, pattern):
        assert re.search(pattern, gitignore_text, flags=re.M), f"Missing coverage/testing ignore pattern: {pattern}"

@pytest.mark.describe("Framework-specific ignores are present")
class TestFrameworkSpecificIgnores:
    @pytest.mark.parametrize("pattern", [
        r"^db\.sqlite3$",
        r"^db\.sqlite3-journal$",
        r"^instance/$",
        r"^\.webassets-cache$",
        r"^\.scrapy$",
        r"^docs/_build/$",
        r"^\.pybuilder/$",
        r"^target/$",
        r"^\.ipynb_checkpoints$",
        r"^profile_default/$",
        r"^ipython_config\.py$",
        r"^__pypackages__/$",
        r"^\.pdm\.toml$",
        r"^\.pdm-python$",
        r"^\.pdm-build/$",
        r"^celerybeat-schedule$",
        r"^celerybeat\.pid$",
        r"^\*\.sage\.py$",
    ])
    def test_various_framework_entries(self, gitignore_text, pattern):
        assert re.search(pattern, gitignore_text, flags=re.M), f"Missing framework/tool ignore pattern: {pattern}"

@pytest.mark.describe("Environment and virtualenv ignores are present")
class TestEnvironmentIgnores:
    @pytest.mark.parametrize("pattern", [
        r"^\.env$",
        r"^\.venv$",
        r"^env/$",
        r"^venv/$",
        r"^ENV/$",
        r"^env\.bak/$",
        r"^venv\.bak/$",
    ])
    def test_virtualenv_entries(self, gitignore_text, pattern):
        assert re.search(pattern, gitignore_text, flags=re.M), f"Missing virtual environment ignore pattern: {pattern}"

@pytest.mark.describe("IDE/editor and project tool ignores are present")
class TestEditorIgnores:
    @pytest.mark.parametrize("pattern", [
        r"^\.spyderproject$",
        r"^\.spyproject$",
        r"^\.ropeproject$",
        r"^/site$",
        r"^\.mypy_cache/$",
        r"^\.dmypy\.json$",
        r"^dmypy\.json$",
        r"^\.pyre/$",
        r"^\.pytype/$",
        r"^cython_debug/$",
        r"^\.ruff_cache/$",
        r"^\.pypircg$",  # As present in the diff
    ])
    def test_editor_and_analyzers(self, gitignore_text, pattern):
        assert re.search(pattern, gitignore_text, flags=re.M), f"Missing editor/tooling ignore pattern: {pattern}"

@pytest.mark.describe("PyCharm / JetBrains ignore block")
class TestJetBrainsIgnores:
    @pytest.mark.parametrize("pattern", [
        r"^\.idea/\*\*/workspace\.xml$",
        r"^\.idea/\*\*/tasks\.xml$",
        r"^\.idea/\*\*/usage\.statistics\.xml$",
        r"^\.idea/\*\*/dictionaries$",
        r"^\.idea/\*\*/shelf$",
        r"^\.idea/\*\*/aws\.xml$",
        r"^\.idea/\*\*/contentModel\.xml$",
        r"^\.idea/\*\*/dataSources/$",
        r"^\.idea/\*\*/dataSources\.ids$",
        r"^\.idea/\*\*/dataSources\.local\.xml$",
        r"^\.idea/\*\*/sqlDataSources\.xml$",
        r"^\.idea/\*\*/dynamic\.xml$",
        r"^\.idea/\*\*/uiDesigner\.xml$",
        r"^\.idea/\*\*/dbnavigator\.xml$",
        r"^\.idea/\*\*/gradle\.xml$",
        r"^\.idea/\*\*/libraries$",
        r"^cmake-build-\*/$",
        r"^\.idea/\*\*/mongoSettings\.xml$",
        r"^\*\.iws$",
        r"^out/$",
        r"^\.idea_modules/$",
        r"^atlassian-ide-plugin\.xml$",
        r"^\.idea/replstate\.xml$",
        r"^\.idea/sonarlint/$",
        r"^com_crashlytics_export_strings\.xml$",
        r"^crashlytics\.properties$",
        r"^crashlytics-build\.properties$",
        r"^fabric\.properties$",
        r"^\.idea/httpRequests$",
        r"^\.idea/caches/build_file_checksums\.ser$",
        r"^\.vscode/settings\.json$",
        r"^/\.idea/misc\.xml$",
        r"^/\.idea/inspectionProfiles/profiles_settings\.xml$",
        r"^/\.idea/vcs\.xml$",
    ])
    def test_jetbrains_related(self, gitignore_text, pattern):
        assert re.search(pattern, gitignore_text, flags=re.M), f"Missing JetBrains/IDE ignore pattern: {pattern}"

@pytest.mark.describe("Duplication sanity checks")
class TestDuplication:
    def test_duplicate_critical_entries_present_but_not_required_unique(self, gitignore_text):
        """
        Some sections are duplicated in the provided diff (e.g., packaging block).
        We do not enforce uniqueness; we only ensure that critical entries appear at least once.
        """
        required = [
            r"^__pycache__/$",
            r"^\*\.py\[cod\]$",
            r"^\.pytest_cache/$",
            r"^\.mypy_cache/$",
            r"^\.ruff_cache/$",
        ]
        for pattern in required:
            assert re.search(pattern, gitignore_text, flags=re.M), f"Critical pattern missing: {pattern}"

@pytest.mark.describe("Edge cases and robustness")
class TestEdgeCases:
    def test_no_windows_line_endings_in_critical_lines(self, gitignore_text):
        """
        Ensure the gitignore uses consistent line endings (LF). This test checks critical lines do not have CR characters.
        """
        critical_lines = [
            "__pycache__/",
            "*.py[cod]",
            ".pytest_cache/",
        ]
        for line in critical_lines:
            assert (line + "\r\n") not in gitignore_text, f"Found CRLF for critical entry: {line!r}"

    def test_no_trailing_whitespace_on_critical_lines(self, gitignore_text):
        """
        Trailing whitespace can cause confusion in some tools. Check critical entries do not have trailing spaces.
        """
        for ln in gitignore_text.splitlines():
            if ln.strip() in {"__pycache__/", "*.py[cod]", ".pytest_cache/"}:
                assert ln == ln.rstrip(), f"Trailing whitespace found on critical entry line: {ln!r}"