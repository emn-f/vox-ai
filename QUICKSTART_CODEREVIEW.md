# 🚀 Quick Start - AI Code Review

Guia rápido para começar a usar o sistema de code review alimentado por IA!

## 1️⃣ Instalação (30 segundos)

```bash
# Instalar dependências
pip install -r requirements.txt
```

## 2️⃣ Seu Primeiro Review (1 minuto)

```python
from src.core.code_reviewer import CodeReviewer

# Inicializar
reviewer = CodeReviewer()

# Seu código diff
diff = """
diff --git a/main.py b/main.py
@@ -1,3 +1,5 @@
-x = eval(input())  # PERIGO!
+x = json.loads(input())
"""

# Analisar
result = reviewer.review_code(diff)

# Ver resultados
print(f"🎯 Score: {result.overall_score}/100")
print(f"💬 Issues: {len(result.comments)}")
for c in result.comments:
    print(f"  [{c.severity.value}] {c.message}")
```

## 3️⃣ GitHub Integration (2 minutos)

### Setup

```bash
# 1. Criar token em https://github.com/settings/tokens
# - Permissões: repo, read:user

# 2. Set variável de ambiente
export GITHUB_TOKEN="ghp_seu_token_aqui"
```

### Usar

```python
from src.core.github_integration import GitHubCodeReviewBot
import os

bot = GitHubCodeReviewBot(os.getenv('GITHUB_TOKEN'))

# Revisar um PR
result = bot.review_pull_request(
    repo_path="emn-f/vox-ai",
    pr_number=42,
    post_comments=True
)

print(result)
```

## 4️⃣ Automação GitHub Actions (1 minuto)

Já está configurada! Apenas:

1. Crie/atualize um PR
2. O bot analisará automaticamente
3. Comentários aparecerão no PR

**Arquivo**: `.github/workflows/code-review.yml` ✅

## 5️⃣ Exemplos Práticos

```bash
# Rodar todos os 5 exemplos
python examples/code_review_example.py
```

**Exemplos incluídos:**
1. Review básico
2. Processamento em batch
3. Integração GitHub
4. Configuração customizada
5. Filtragem por severidade

## 📊 Níveis de Severidade

| Emoji | Nível | Exemplos |
|-------|-------|----------|
| 🔴 | Critical | Bugs, vulnerabilidades, crashes |
| 🟠 | Major | Performance, issues importantes |
| 🟡 | Minor | Estilo, convenções |
| 🔵 | Info | Sugestões informativas |

## ⚙️ Configuração Rápida

### Usar GPU (se disponível)
```python
reviewer = CodeReviewer(device="cuda")
```

### Cache Local
```python
reviewer = CodeReviewer(cache_dir="./models")
```

### Parâmetros
```python
result = reviewer.review_code(
    diff,
    max_length=512,
    num_beams=5,
    temperature=0.7
)
```

## 🧪 Testes

```bash
# Testes unitários
python -m pytest tests/test_code_reviewer.py -v
```

## 📚 Documentação

- **Completa**: `docs/CODE_REVIEW.md`
- **Exemplos**: `examples/code_review_example.py`
- **API**: Docstrings em `src/core/code_reviewer.py`

## 🆘 Problemas Comuns

### CUDA Out of Memory
```python
reviewer = CodeReviewer(device="cpu")
```

### Modelo não baixa
```bash
export HF_HOME="/caminho/para/cache"
```

### GitHub token inválido
```bash
# Gere novo em https://github.com/settings/tokens
export GITHUB_TOKEN="novo_token"
```

## 📈 Performance

| Operação | CPU | GPU |
|----------|-----|-----|
| Primeiro load | 2-3 min | 2-3 min |
| Review/diff | 5-15s | 1-3s |

## 🎯 Próximas Ações

1. ✅ Rodar `python examples/code_review_example.py`
2. ✅ Ler `docs/CODE_REVIEW.md`
3. ✅ Testar em um PR do seu repo
4. ✅ Customizar conforme necessário

---

## 💡 Dica Profissional

Combine com linters:
```python
# CodeReviewer para análise semântica
review = reviewer.review_code(diff)

# Combine com Black, Flake8, etc.
# para análise completa de qualidade
```

---

**Pronto para começar?** 🚀

```bash
python examples/code_review_example.py
```
