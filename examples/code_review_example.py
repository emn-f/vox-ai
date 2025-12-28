"""
Code Review Examples

This script demonstrates how to use the AI-powered code review system.
It includes examples for:
- Basic code review
- Batch reviewing multiple files
- GitHub PR integration
- Custom configuration
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.code_reviewer import CodeReviewer, ReviewSeverity
from src.core.github_integration import GitHubCodeReviewBot


def example_basic_review():
    """
    Example 1: Basic code review of a diff.
    """
    print("\n=== Example 1: Basic Code Review ===")
    
    # Sample code diff
    sample_diff = """
diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -1,5 +1,10 @@
 def calculate_total(items):
-    total = 0
-    for item in items:
-        total = total + item
-    return total
+    total = 0
+    for item in items:
+        if item is None:
+            total = total + 0
+        else:
+            total = total + item
+    return total
"""
    
    # Initialize reviewer
    reviewer = CodeReviewer()
    
    # Review the code
    result = reviewer.review_code(sample_diff)
    
    # Print results
    print(f"\nReview Summary: {result.summary}")
    print(f"Overall Score: {result.overall_score}/100")
    print(f"Files Analyzed: {result.files_analyzed}")
    print(f"Critical Issues: {result.has_critical_issues}")
    
    print("\nComments Found:")
    for comment in result.comments:
        print(
            f"  - [{comment.severity.value.upper()}] Line {comment.line}: "
            f"{comment.message}"
        )


def example_batch_review():
    """
    Example 2: Review multiple code diffs.
    """
    print("\n=== Example 2: Batch Code Review ===")
    
    diffs = [
        """diff --git a/file1.py b/file1.py
@@ -1,3 +1,5 @@
 import os
-password = 'hardcoded123'
+password = os.getenv('PASSWORD')
""",
        """diff --git a/file2.py b/file2.py
@@ -1,3 +1,3 @@
 def slow_function():
-    result = []
+    result = [x for x in range(1000000) if x % 2 == 0]
""",
    ]
    
    reviewer = CodeReviewer()
    results = reviewer.batch_review(diffs)
    
    print(f"\nReviewed {len(results)} files:")
    for i, result in enumerate(results, 1):
        print(f"\nFile {i}:")
        print(f"  Score: {result.overall_score}/100")
        print(f"  Issues: {len(result.comments)}")
        if result.comments:
            print(f"  Severity: {result.comments[0].severity.value}")


def example_github_integration():
    """
    Example 3: Review GitHub pull requests.
    """
    print("\n=== Example 3: GitHub PR Review ===")
    
    # This requires a GitHub token
    # Set via environment variable: GITHUB_TOKEN
    import os
    
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable not set")
        print("   Set it with: export GITHUB_TOKEN='your_token_here'")
        return
    
    try:
        # Initialize bot
        bot = GitHubCodeReviewBot(github_token)
        
        # Example: Review a specific PR
        # Replace with your repo and PR number
        repo_path = "emn-f/vox-ai"
        pr_number = 1
        
        result = bot.review_pull_request(
            repo_path,
            pr_number,
            post_comments=False,  # Set to True to post to GitHub
        )
        
        print(f"\nPR #{pr_number} Review Result:")
        print(f"  Status: {result.get('status')}")
        print(f"  Comments: {result.get('comments_count', 0)}")
        print(f"  Summary: {result.get('summary', 'N/A')}")
        print(f"  Score: {result.get('overall_score', 'N/A')}/100")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_custom_configuration():
    """
    Example 4: Using custom configuration.
    """
    print("\n=== Example 4: Custom Configuration ===")
    
    # Initialize with custom device (GPU or CPU)
    reviewer = CodeReviewer(
        model_name="microsoft/codereviewer",
        device="cpu",  # or 'cuda' for GPU
    )
    
    sample_diff = """
diff --git a/test.py b/test.py
@@ -1,3 +1,3 @@
 def test():
-    x = 1
-    y = 2
+    x, y = 1, 2
"""
    
    # Review with custom parameters
    result = reviewer.review_code(
        sample_diff,
        max_length=256,
        num_beams=3,
        temperature=0.5,
    )
    
    print(f"\nReview Complete")
    print(f"Device Used: {reviewer.device}")
    print(f"Score: {result.overall_score}/100")
    print(f"Summary: {result.summary}")


def example_severity_filtering():
    """
    Example 5: Filter comments by severity.
    """
    print("\n=== Example 5: Severity Filtering ===")
    
    reviewer = CodeReviewer()
    
    sample_diff = """
diff --git a/app.py b/app.py
@@ -1,10 +1,15 @@
 import json
+import pickle
 
 def process_data(data):
-    result = eval(data)  # SECURITY RISK!
+    result = json.loads(data)
 
 def cleanup():
-    os.system('rm -rf /')  # DANGEROUS!
+    os.remove('temp_file.txt')
"""
    
    result = reviewer.review_code(sample_diff)
    
    # Filter by severity
    print("\n🔴 Critical Issues:")
    critical = [c for c in result.comments if c.severity == ReviewSeverity.CRITICAL]
    for comment in critical:
        print(f"  - {comment.message}")
    
    print("\n🟠 Major Issues:")
    major = [c for c in result.comments if c.severity == ReviewSeverity.MAJOR]
    for comment in major:
        print(f"  - {comment.message}")
    
    print("\n🟡 Minor Issues:")
    minor = [c for c in result.comments if c.severity == ReviewSeverity.MINOR]
    for comment in minor:
        print(f"  - {comment.message}")
    
    # Summary statistics
    print(f"\n📊 Statistics:")
    print(f"  Critical: {len(critical)}")
    print(f"  Major: {len(major)}")
    print(f"  Minor: {len(minor)}")
    print(f"  Total: {len(result.comments)}")


def main():
    """
    Run all examples.
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║   AI-Powered Code Review System - Usage Examples             ║
║   Using: microsoft/codereviewer from Hugging Face            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Run examples
        example_basic_review()
        example_batch_review()
        example_severity_filtering()
        example_custom_configuration()
        example_github_integration()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
