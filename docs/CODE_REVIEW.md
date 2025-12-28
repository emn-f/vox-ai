# 🤖 AI-Powered Code Review System

Documentation for the integrated AI-powered code review system using Microsoft's CodeReviewer model.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Components](#core-components)
- [Usage Examples](#usage-examples)
- [GitHub Integration](#github-integration)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

The Code Review system integrates Microsoft's pre-trained **CodeReviewer** model from Hugging Face to provide automated, intelligent code analysis and review capabilities. It can:

- Analyze code diffs and changes
- Identify potential bugs and code quality issues
- Detect security vulnerabilities
- Provide improvement suggestions
- Generate structured review comments
- Integrate with GitHub pull requests

### Why CodeReviewer?

The Microsoft CodeReviewer model is specifically pre-trained on:
- Real code changes and commits
- Actual code review comments from developers
- Multiple programming languages
- Various code review scenarios

This makes it highly effective at understanding code patterns and providing relevant, contextual feedback.

## ✨ Features

### Core Features

✅ **Code Diff Analysis**
- Analyze any code diff/patch
- Automatic issue detection
- Severity level classification

✅ **Multi-Language Support**
- Python, JavaScript, Java, C++, Go, Rust
- Generic diff format support

✅ **Issue Categorization**
- Security vulnerabilities
- Performance problems
- Code style issues
- Bug detection
- Maintainability concerns

✅ **Severity Levels**
- 🔴 Critical: Security issues, crashes, bugs
- 🟠 Major: Significant improvements needed
- 🟡 Minor: Style and convention suggestions
- 🔵 Info: Informational suggestions

✅ **GitHub Integration**
- Review pull requests automatically
- Post comments directly to PRs
- Batch PR reviews
- Webhook support ready

✅ **Batch Processing**
- Review multiple files at once
- Efficient GPU utilization
- Progress tracking

## 📦 Installation

### Prerequisites

- Python 3.8+
- pip package manager
- (Optional) CUDA for GPU acceleration

### Setup

1. **Install Required Packages**

```bash
pip install transformers torch PyGithub
```

2. **Optional: GPU Support**

For NVIDIA GPUs:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

3. **Verify Installation**

```python
from src.core.code_reviewer import CodeReviewer
reviewer = CodeReviewer()
print(f"Device: {reviewer.device}")
```

## 🚀 Quick Start

### Basic Code Review

```python
from src.core.code_reviewer import CodeReviewer

# Initialize reviewer
reviewer = CodeReviewer()

# Prepare code diff
code_diff = """
diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -1,3 +1,5 @@
-password = 'hardcoded123'
+password = os.getenv('PASSWORD')
"""

# Run review
result = reviewer.review_code(code_diff)

# Check results
print(f"Score: {result.overall_score}/100")
print(f"Issues Found: {len(result.comments)}")
print(f"Summary: {result.summary}")

# Iterate through comments
for comment in result.comments:
    print(f"{comment.severity}: {comment.message}")
```

### GitHub PR Review

```python
from src.core.github_integration import GitHubCodeReviewBot
import os

# Initialize bot
bot = GitHubCodeReviewBot(
    github_token=os.getenv('GITHUB_TOKEN')
)

# Review a PR
result = bot.review_pull_request(
    repo_path="owner/repo",
    pr_number=42,
    post_comments=True  # Post to GitHub
)

print(result)
```

## 🏗️ Core Components

### CodeReviewer

Main class for code analysis.

**Key Methods:**

- `review_code(diff)` - Review a single code diff
- `batch_review(diffs)` - Review multiple diffs
- `prepare_input(diff)` - Format diff for model

**Key Attributes:**

- `device` - Processing device (cuda/cpu)
- `model` - The underlying transformer model
- `tokenizer` - Text tokenizer

### ReviewComment

Structure representing a single review comment.

```python
@dataclass
class ReviewComment:
    line: int                          # Line number
    severity: ReviewSeverity           # Critical/Major/Minor/Info
    message: str                       # Comment text
    suggestion: Optional[str] = None   # Code suggestion
    category: str = "general"          # Category (bug, security, etc.)
```

### CodeReviewResult

Complete review results.

```python
@dataclass
class CodeReviewResult:
    code_diff: str                     # Original diff
    comments: List[ReviewComment]      # Issues found
    summary: str                       # Summary text
    overall_score: float               # 0-100 score
    files_analyzed: int                # Number of files
    has_critical_issues: bool          # Critical issues present
```

### GitHubCodeReviewBot

GitHub integration for automated PR reviews.

**Key Methods:**

- `review_pull_request()` - Review single PR
- `review_multiple_prs()` - Review multiple PRs
- `watch_repository()` - Set up webhook watching

## 📚 Usage Examples

See `examples/code_review_example.py` for comprehensive examples:

1. **Basic Review** - Simple code review
2. **Batch Review** - Multiple file analysis
3. **GitHub Integration** - PR review and posting
4. **Custom Configuration** - Device and parameter tuning
5. **Severity Filtering** - Filter by issue severity

### Run Examples

```bash
# Run all examples
python examples/code_review_example.py

# Or with GitHub integration
export GITHUB_TOKEN="your_token_here"
python examples/code_review_example.py
```

## 🔗 GitHub Integration

### Setup GitHub Token

1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:user`
4. Set environment variable:

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
```

### Review a Pull Request

```python
bot = GitHubCodeReviewBot(os.getenv('GITHUB_TOKEN'))

result = bot.review_pull_request(
    repo_path="emn-f/vox-ai",
    pr_number=123,
    post_comments=True
)
```

### Automated Workflow (GitHub Actions)

Create `.github/workflows/code-review.yml`:

```yaml
name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install transformers torch PyGithub
      
      - name: Run AI Code Review
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python src/scripts/review_pr.py
```

## ⚙️ Configuration

### Device Selection

```python
# Auto-detect (CUDA if available, CPU otherwise)
reviewer = CodeReviewer()

# Force CPU
reviewer = CodeReviewer(device="cpu")

# Force CUDA
reviewer = CodeReviewer(device="cuda")
```

### Model Configuration

```python
reviewer = CodeReviewer(
    model_name="microsoft/codereviewer",
    device="cuda",
    cache_dir="./models"  # Local model cache
)
```

### Review Parameters

```python
result = reviewer.review_code(
    code_diff,
    max_length=512,      # Max output length
    num_beams=5,         # Beam search width
    temperature=0.7,     # Generation temperature
)
```

## 📖 API Reference

### CodeReviewer.review_code()

```python
def review_code(
    code_diff: str,
    max_length: int = 512,
    num_beams: int = 5,
    temperature: float = 0.7,
) -> CodeReviewResult
```

**Parameters:**
- `code_diff` - Code diff/patch to review
- `max_length` - Maximum tokens for review output
- `num_beams` - Beam search breadth (higher = better quality, slower)
- `temperature` - Randomness (0 = deterministic, 1 = random)

**Returns:** `CodeReviewResult` object

### CodeReviewer.batch_review()

```python
def batch_review(
    code_diffs: List[str],
    **kwargs,
) -> List[CodeReviewResult]
```

**Parameters:**
- `code_diffs` - List of diffs to review
- `**kwargs` - Additional parameters passed to `review_code()`

**Returns:** List of `CodeReviewResult` objects

### GitHubCodeReviewBot.review_pull_request()

```python
def review_pull_request(
    repo_path: str,
    pr_number: int,
    post_comments: bool = True,
) -> Dict[str, Any]
```

**Parameters:**
- `repo_path` - Repository path ("owner/repo")
- `pr_number` - Pull request number
- `post_comments` - Whether to post to GitHub

**Returns:** Dict with review results

## 💡 Best Practices

### 1. **Start with CPU for Testing**

```python
# CPU is faster for small diffs
reviewer = CodeReviewer(device="cpu")
```

### 2. **Batch Process Large Diffs**

```python
# Split large diffs into smaller ones
results = reviewer.batch_review(split_diffs)
```

### 3. **Filter by Severity**

```python
from src.core.code_reviewer import ReviewSeverity

critical = [c for c in result.comments 
            if c.severity == ReviewSeverity.CRITICAL]
```

### 4. **Cache Models**

```python
reviewer = CodeReviewer(cache_dir="./models")
# Models are cached locally, faster subsequent loads
```

### 5. **Monitor Performance**

```python
import logging
logging.basicConfig(level=logging.INFO)
# Shows device, model loading, review progress
```

## 🔧 Troubleshooting

### CUDA Out of Memory

```python
# Use CPU instead
reviewer = CodeReviewer(device="cpu")

# Or reduce max_length
result = reviewer.review_code(diff, max_length=256)
```

### Model Download Fails

```bash
# Set HF_HOME to custom directory
export HF_HOME="/path/to/cache"

# Or pass cache_dir parameter
reviewer = CodeReviewer(cache_dir="./models")
```

### GitHub API Rate Limit

```python
import time

# Add delays between API calls
for pr in prs:
    bot.review_pull_request(...)
    time.sleep(5)  # 5 second delay
```

### Model Not Found

```bash
# Ensure transformers is updated
pip install --upgrade transformers

# Check internet connection
# Model downloads from huggingface.co on first use
```

## 📈 Performance Metrics

### Model Characteristics

- **Model Size:** ~500MB
- **First Load:** ~2-3 minutes (downloads model)
- **Inference Time:** 5-15 seconds per diff (CPU)
- **Inference Time:** 1-3 seconds per diff (GPU)
- **Memory Usage:** ~2GB (CPU), ~4-8GB (GPU)

### Optimization Tips

1. Use GPU for repeated reviews
2. Batch process multiple diffs
3. Cache models locally
4. Reduce max_length for faster inference
5. Use lower beam width for speed

## 📝 License

Microsoft CodeReviewer: [MIT License](https://huggingface.co/microsoft/codereviewer)

## 🔗 Resources

- [Microsoft CodeReviewer Paper](https://arxiv.org/abs/2203.09095)
- [Hugging Face Model Card](https://huggingface.co/microsoft/codereviewer)
- [Transformers Documentation](https://huggingface.co/docs/transformers/)
- [GitHub API Documentation](https://docs.github.com/en/rest)

## 💬 Support

For issues or questions:
1. Check troubleshooting section
2. Review example code
3. Check model documentation
4. Open an issue on GitHub
