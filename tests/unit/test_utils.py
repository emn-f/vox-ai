from unittest.mock import patch, mock_open
import subprocess
import pytest

from src.utils import git_version, get_version_from_changelog, limpeza_texto


def test_get_version_from_changelog_bracket_format():
    content = "# Changelog\n\n## [3.3.18] - 2026-06-01\n- Initial release"
    with patch("builtins.open", mock_open(read_data=content)):
        assert get_version_from_changelog() == "v3.3.18"


def test_get_version_from_changelog_v_format():
    content = "# Changelog\n\n## v4.0.2 - 21/06/2026\n- Bug fixes"
    with patch("builtins.open", mock_open(read_data=content)):
        assert get_version_from_changelog() == "v4.0.2"


def test_get_version_from_changelog_handles_ioerror():
    with patch("builtins.open", side_effect=IOError("Arquivo inexistente")):
        assert get_version_from_changelog() == ""


def test_git_version_fallback_when_no_tag():
    with patch("src.utils.get_current_branch", return_value="main"), \
         patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "git")), \
         patch("src.utils.get_version_from_changelog", return_value=""):
        if hasattr(git_version, "cache_clear"):
            git_version.cache_clear()
        assert git_version() == "v5.0.0"
        if hasattr(git_version, "cache_clear"):
            git_version.cache_clear()


@pytest.mark.unit
@pytest.mark.parametrize("branch", ["main", "HEAD", "unknown"])
def test_git_version_prefers_newer_changelog_over_stale_tag_in_prod(branch):
    with patch("src.utils.get_current_branch", return_value=branch), \
         patch("subprocess.check_output", return_value=b"v5.4.0\n"), \
         patch("src.utils.get_version_from_changelog", return_value="v5.9.0"), \
         patch("src.utils._get_changelog_mtime", return_value=100.0):
        git_version.cache_clear()
        assert git_version() == "v5.9.0"


@pytest.mark.unit
def test_git_version_uses_newer_git_tag_on_main():
    with patch("src.utils.get_current_branch", return_value="main"), \
         patch("subprocess.check_output", return_value=b"v5.10.0\n"), \
         patch("src.utils.get_version_from_changelog", return_value="v5.9.0"), \
         patch("src.utils._get_changelog_mtime", return_value=101.0):
        git_version.cache_clear()
        assert git_version() == "v5.10.0"


@pytest.mark.unit
def test_git_version_keeps_dev_tag_on_develop_branch():
    with patch("src.utils.get_current_branch", return_value="develop"), \
         patch("subprocess.check_output", return_value=b"dev-v4.9.1\n") as mock_co, \
         patch("src.utils.get_version_from_changelog", return_value="v5.9.0"), \
         patch("src.utils._get_changelog_mtime", return_value=102.0):
        git_version.cache_clear()
        assert git_version() == "dev-v4.9.1"
        assert "dev-v*" in mock_co.call_args.args[0]


@pytest.mark.unit
def test_git_version_cache_invalidates_when_changelog_mtime_changes():
    with patch("src.utils.get_current_branch", return_value="main"), \
         patch("subprocess.check_output", return_value=b"v5.4.0\n"), \
         patch("src.utils.get_version_from_changelog", side_effect=["v5.9.0", "v5.9.1"]), \
         patch("src.utils._get_changelog_mtime", side_effect=[200.0, 201.0]):
        git_version.cache_clear()
        assert git_version() == "v5.9.0"
        assert git_version() == "v5.9.1"


def test_limpeza_texto():
    assert limpeza_texto("Olá, Mundo! 123 LGBTQIA+") == "Olá, Mundo! 123 LGBTQIA+"
    assert limpeza_texto("") == ""
