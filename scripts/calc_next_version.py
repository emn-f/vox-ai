#!/usr/bin/env python3
"""
Módulo e utilitário CLI para cálculo dinâmico de versão SemVer (Semantic Versioning)
baseado na convenção Conventional Commits.

Regras de Incremento:
- MAJOR: Qualquer commit com '!' após tipo/escopo (ex: 'feat!:', 'refactor(api)!:')
         ou com rodapé/corpo contendo 'BREAKING CHANGE:' ou 'BREAKING-CHANGE:'.
- MINOR: Qualquer commit de nova funcionalidade com tipo 'feat' ou 'feat(...)'.
- PATCH: Commits de correção, melhoria interna, performance ou documentação
         (ex: 'fix', 'perf', 'refactor', 'docs', 'style', 'chore', 'test', 'ci', 'build').
"""

import argparse
import os
import re
import subprocess
import sys
from typing import List, Optional, Tuple


def get_latest_tag(prefix: str = "v") -> str:
    """
    Retorna a última tag válida do Git para o prefixo especificado.
    Utiliza ordenação SemVer (--sort=-v:refname).
    """
    try:
        cmd = ["git", "tag", "--list", f"{prefix}[0-9]*", "--sort=-v:refname"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        tags = [t.strip() for t in res.stdout.splitlines() if t.strip()]
        if tags:
            return tags[0]
    except Exception:
        pass
    return f"{prefix}0.0.0"


def parse_semver(tag: str, prefix: str = "v") -> Tuple[int, int, int]:
    """
    Extrai a tupla (major, minor, patch) de uma tag SemVer.
    Ex: 'v5.0.0' -> (5, 0, 0)
    Ex: 'dev-v3.2.1' -> (3, 2, 1)
    """
    clean = tag
    if clean.startswith(prefix):
        clean = clean[len(prefix):]
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", clean)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    return 0, 0, 0


def determine_bump_type(commits: List[str]) -> str:
    """
    Analisa a lista de mensagens de commits e retorna:
    - 'major': se houver breaking change.
    - 'minor': se houver ao menos um commit 'feat'.
    - 'patch': caso padrão para fixes e outras tarefas.
    """
    has_breaking = False
    has_feat = False

    for commit in commits:
        if not commit or not commit.strip():
            continue

        raw = commit.strip()
        lines = raw.splitlines()
        header = lines[0].strip()
        body = "\n".join(lines[1:]) if len(lines) > 1 else ""

        # 1. Breaking Change no cabeçalho (ex: feat!: ou feat(core)!:)
        if re.search(r"^[a-zA-Z0-9_-]+(\([^)]+\))?!:", header):
            has_breaking = True
            break

        # 2. Breaking Change no corpo ou rodapé
        if (
            re.search(r"BREAKING[- ]CHANGE\s*:", body, re.IGNORECASE)
            or re.search(r"BREAKING[- ]CHANGE\s*:", header, re.IGNORECASE)
        ):
            has_breaking = True
            break

        # 3. Nova funcionalidade (feat)
        if re.match(r"^feat(\([^)]+\))?:", header, re.IGNORECASE):
            has_feat = True

    if has_breaking:
        return "major"
    if has_feat:
        return "minor"
    return "patch"


def calculate_next_version(
    current_tag: str,
    bump_type: str,
    prefix: str = "v",
) -> str:
    """
    Calcula a próxima versão semântica aplicando o tipo de incremento.
    """
    major, minor, patch = parse_semver(current_tag, prefix)

    if bump_type == "major":
        return f"{prefix}{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{prefix}{major}.{minor + 1}.0"
    else:
        return f"{prefix}{major}.{minor}.{patch + 1}"


def get_commits_range(from_ref: str, to_ref: str = "HEAD") -> List[str]:
    """
    Obtém as mensagens completas dos commits entre from_ref e to_ref.
    """
    try:
        # Se from_ref for uma tag 0.0.0 que não existe fisicamente, busca todo o histórico até to_ref
        check_cmd = ["git", "rev-parse", "--verify", from_ref]
        has_ref = subprocess.run(check_cmd, capture_output=True).returncode == 0

        if has_ref:
            git_range = f"{from_ref}..{to_ref}"
            cmd = ["git", "log", git_range, "--format=%B---COMMIT_DELIMITER---"]
        else:
            cmd = ["git", "log", to_ref, "--format=%B---COMMIT_DELIMITER---"]

        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        raw_chunks = res.stdout.split("---COMMIT_DELIMITER---")
        return [c.strip() for c in raw_chunks if c.strip()]
    except Exception as e:
        print(f"⚠️ Erro ao listar commits entre {from_ref} e {to_ref}: {e}", file=sys.stderr)
        return []


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calculador Dinâmico de Versão SemVer com Conventional Commits."
    )
    parser.add_argument(
        "--prefix",
        default="v",
        help="Prefixo da tag (ex: 'v' para produção, 'dev-v' para desenvolvimento).",
    )
    parser.add_argument(
        "--from-tag",
        default=None,
        help="Tag base inicial. Se omitido, busca automaticamente a mais recente com o prefixo.",
    )
    parser.add_argument(
        "--to-ref",
        default="HEAD",
        help="Referência final de commit/branch (padrão: HEAD).",
    )
    parser.add_argument(
        "--export-github",
        action="store_true",
        help="Exporta as saídas new_tag, bump_type e last_tag para $GITHUB_OUTPUT.",
    )

    args = parser.parse_args()

    last_tag = args.from_tag or get_latest_tag(prefix=args.prefix)
    commits = get_commits_range(from_ref=last_tag, to_ref=args.to_ref)
    bump_type = determine_bump_type(commits)
    new_tag = calculate_next_version(current_tag=last_tag, bump_type=bump_type, prefix=args.prefix)

    print(f"Última Tag: {last_tag}")
    print(f"Commits Analisados: {len(commits)}")
    print(f"Incremento Detectado: {bump_type}")
    print(f"Nova Tag Gerada: {new_tag}")

    if args.export_github:
        gh_output = os.environ.get("GITHUB_OUTPUT")
        if gh_output and os.path.exists(gh_output):
            with open(gh_output, "a", encoding="utf-8") as f:
                f.write(f"new_tag={new_tag}\n")
                f.write(f"bump_type={bump_type}\n")
                f.write(f"last_tag={last_tag}\n")
            print(f"✅ Exportado para $GITHUB_OUTPUT: new_tag={new_tag}, bump_type={bump_type}")
        else:
            # Em modo fallback/local se não houver arquivo físico
            print(f"::set-output name=new_tag::{new_tag}")
            print(f"::set-output name=bump_type::{bump_type}")
            print(f"::set-output name=last_tag::{last_tag}")


if __name__ == "__main__":
    main()
