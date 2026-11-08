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


def test_limpeza_texto():
    assert limpeza_texto("Olá, Mundo! 123 LGBTQIA+") == "Olá, Mundo! 123 LGBTQIA+"
    assert limpeza_texto("") == ""
