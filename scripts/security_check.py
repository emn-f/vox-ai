import re
import sys
import os
import subprocess


# Padrões de Regex para chaves (Supabase, Streamlit, HF, GitHub, Google)
PATTERNS = {
    "Supabase Key": r"(sbp_[a-zA-Z0-9]+|eyJ[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+)", 
    "Streamlit Secret": r"(st-[a-zA-Z0-9]+)",
    "Hugging Face Token": r"(hf_[a-zA-Z0-9]{34,})",
    "GitHub Token": r"(ghp_[a-zA-Z0-9]+|github_pat_[a-zA-Z0-9_]+)",
    "Google API Key": r"AIza[0-9A-Za-z-_]{35}"
}

IGNORED_FILES = ["scripts/security_check.py", ".env", ".gitignore", "requirements.txt"]

def check_file_content(file_path):
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                for key_name, pattern in PATTERNS.items():
                    if re.search(pattern, line):
                        issues.append({"type": key_name, "line": i + 1, "content": line.strip()})
    except Exception:
        pass
    return issues

def main():
    print(f"🔍 Iniciando verificação de segurança (Pre-Commit)...")
    # Pega arquivos stagiados
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], stdout=subprocess.PIPE, text=True)
        files = result.stdout.splitlines()
    except Exception as e:
        print(f"❌ Erro no Git: {e}")
        sys.exit(1)

    if not files:
        sys.exit(0)

    found_errors = False
    for file_path in files:
        if file_path in IGNORED_FILES or not os.path.exists(file_path):
            continue
            
        issues = check_file_content(file_path)
        if issues:
            found_errors = True
            print(f"\n🚫 SEGURANÇA: Credencial encontrada em {file_path}")
            for issue in issues:
                print(f"   - {issue['type']} na linha {issue['line']}")
    
    if found_errors:
        print(f"\n🛑 COMMIT BLOQUEADO: Remova as credenciais antes de prosseguir.")
        sys.exit(1)
    else:
        print(f"✅ Segurança OK.")
        sys.exit(0)

if __name__ == "__main__":
    main()