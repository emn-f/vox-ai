"""
Testes unitários para o calculador dinâmico de versões SemVer (scripts/calc_next_version.py).
"""

import pytest
from scripts.calc_next_version import (
    determine_bump_type,
    parse_semver,
    calculate_next_version,
)

pytestmark = pytest.mark.unit


def test_parse_semver_production():
    assert parse_semver("v5.0.0", prefix="v") == (5, 0, 0)
    assert parse_semver("v1.12.3", prefix="v") == (1, 12, 3)
    assert parse_semver("v0.0.0", prefix="v") == (0, 0, 0)


def test_parse_semver_develop():
    assert parse_semver("dev-v3.0.17", prefix="dev-v") == (3, 0, 17)
    assert parse_semver("dev-v0.1.0", prefix="dev-v") == (0, 1, 0)


def test_determine_bump_type_patch():
    commits = [
        "fix(ui): corrige quebra de layout no sidebar",
        "docs: atualiza README com novos comandos",
        "chore(deps): atualiza dependencias",
        "perf(rag): otimiza busca vetorial",
    ]
    assert determine_bump_type(commits) == "patch"


def test_determine_bump_type_minor():
    commits = [
        "fix(ui): corrige quebra de layout no sidebar",
        "feat(audio): adiciona síntese de voz nativa",
        "docs: atualiza documentação",
    ]
    assert determine_bump_type(commits) == "minor"


def test_determine_bump_type_major_bang_header():
    commits = [
        "refactor(core)!: desacopla Streamlit da API de servico",
        "feat(api): adiciona rotas fastapi",
    ]
    assert determine_bump_type(commits) == "major"


def test_determine_bump_type_major_breaking_change_footer():
    commits = [
        "feat(api): altera payload de resposta\n\nBREAKING CHANGE: o campo 'reply' agora se chama 'response'",
        "fix: corrige bug de digitacao",
    ]
    assert determine_bump_type(commits) == "major"


def test_determine_bump_type_major_breaking_change_hyphen():
    commits = [
        "refactor: reestrutura modulos internos\n\nBREAKING-CHANGE: caminhos de import alterados",
    ]
    assert determine_bump_type(commits) == "major"


def test_calculate_next_version_patch():
    assert calculate_next_version("v5.0.0", "patch", prefix="v") == "v5.0.1"
    assert calculate_next_version("dev-v3.0.17", "patch", prefix="dev-v") == "dev-v3.0.18"


def test_calculate_next_version_minor():
    # Minor reseta o patch para 0
    assert calculate_next_version("v5.0.4", "minor", prefix="v") == "v5.1.0"
    assert calculate_next_version("v5.0.0", "minor", prefix="v") == "v5.1.0"


def test_calculate_next_version_major():
    # Major incrementa o major e reseta minor e patch para 0
    assert calculate_next_version("v5.2.3", "major", prefix="v") == "v6.0.0"
    assert calculate_next_version("v5.0.0", "major", prefix="v") == "v6.0.0"


def test_empty_commits_defaults_to_patch():
    assert determine_bump_type([]) == "patch"
