"""
Unit Tests for Code Review System

Tests for the CodeReviewer and GitHubCodeReviewBot modules.
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.code_reviewer import (
    CodeReviewer,
    ReviewComment,
    ReviewSeverity,
    CodeReviewResult,
)


class TestCodeReviewer(unittest.TestCase):
    """
    Test cases for the CodeReviewer class.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        # Initialize reviewer once for all tests
        try:
            cls.reviewer = CodeReviewer()
        except Exception as e:
            print(f"Warning: Could not initialize CodeReviewer: {e}")
            cls.reviewer = None
    
    def setUp(self):
        """Set up test case."""
        if self.reviewer is None:
            self.skipTest("CodeReviewer not available")
    
    def test_initialization(self):
        """Test CodeReviewer initialization."""
        self.assertIsNotNone(self.reviewer.model)
        self.assertIsNotNone(self.reviewer.tokenizer)
        self.assertIn(self.reviewer.device, ['cuda', 'cpu'])
    
    def test_empty_diff(self):
        """Test review with empty diff."""
        result = self.reviewer.review_code("")
        
        self.assertEqual(len(result.comments), 0)
        self.assertEqual(result.overall_score, 100.0)
        self.assertFalse(result.has_critical_issues)
    
    def test_whitespace_diff(self):
        """Test review with whitespace-only diff."""
        result = self.reviewer.review_code("   \n\n  \t  ")
        
        self.assertEqual(len(result.comments), 0)
        self.assertEqual(result.overall_score, 100.0)
    
    def test_prepare_input(self):
        """Test input preparation."""
        code_diff = "test code"
        prepared = self.reviewer.prepare_input(code_diff)
        
        self.assertIn("<code_diff>", prepared)
        self.assertIn("</code_diff>", prepared)
        self.assertIn(code_diff, prepared)
    
    def test_severity_detection(self):
        """Test severity detection."""
        # Test critical keywords
        severity = self.reviewer._detect_severity("This is a security vulnerability")
        self.assertEqual(severity, ReviewSeverity.CRITICAL)
        
        # Test major keywords
        severity = self.reviewer._detect_severity("Performance issue found")
        self.assertEqual(severity, ReviewSeverity.MAJOR)
        
        # Test minor keywords
        severity = self.reviewer._detect_severity("Consider style changes")
        self.assertEqual(severity, ReviewSeverity.MINOR)
    
    def test_category_detection(self):
        """Test issue category detection."""
        # Test security
        category = self.reviewer._detect_category("SQL injection vulnerability")
        self.assertEqual(category, "security")
        
        # Test performance
        category = self.reviewer._detect_category("Optimize performance")
        self.assertEqual(category, "performance")
        
        # Test style
        category = self.reviewer._detect_category("Code style improvements")
        self.assertEqual(category, "style")
    
    def test_count_files(self):
        """Test file counting in diff."""
        diff_single = "diff --git a/file.py b/file.py\n..."
        count = self.reviewer._count_files(diff_single)
        self.assertEqual(count, 1)
        
        diff_multiple = "diff --git a/file1.py b/file1.py\n...\ndiff --git a/file2.py b/file2.py\n..."
        count = self.reviewer._count_files(diff_multiple)
        self.assertEqual(count, 2)
    
    def test_calculate_score(self):
        """Test score calculation."""
        # No comments = perfect score
        score = self.reviewer._calculate_score([])
        self.assertEqual(score, 100.0)
        
        # With critical issue
        comments = [
            ReviewComment(
                line=1,
                severity=ReviewSeverity.CRITICAL,
                message="Critical issue",
            )
        ]
        score = self.reviewer._calculate_score(comments)
        self.assertLess(score, 100.0)
        self.assertGreaterEqual(score, 0)
    
    def test_generate_summary(self):
        """Test summary generation."""
        # No issues
        comments = []
        summary = self.reviewer._generate_summary(comments)
        self.assertIn("No issues", summary)
        
        # With critical issues
        comments = [
            ReviewComment(
                line=1,
                severity=ReviewSeverity.CRITICAL,
                message="Issue 1",
            ),
            ReviewComment(
                line=2,
                severity=ReviewSeverity.CRITICAL,
                message="Issue 2",
            ),
        ]
        summary = self.reviewer._generate_summary(comments)
        self.assertIn("2", summary)
        self.assertIn("critical", summary.lower())
    
    def test_batch_review(self):
        """Test batch review."""
        diffs = [
            "diff --git a/file1.py b/file1.py\n...",
            "diff --git a/file2.py b/file2.py\n...",
        ]
        
        results = self.reviewer.batch_review(diffs)
        
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIsInstance(result, CodeReviewResult)


class TestReviewComment(unittest.TestCase):
    """
    Test cases for ReviewComment dataclass.
    """
    
    def test_review_comment_creation(self):
        """Test ReviewComment creation."""
        comment = ReviewComment(
            line=42,
            severity=ReviewSeverity.MAJOR,
            message="Test message",
            category="bug",
        )
        
        self.assertEqual(comment.line, 42)
        self.assertEqual(comment.severity, ReviewSeverity.MAJOR)
        self.assertEqual(comment.message, "Test message")
        self.assertEqual(comment.category, "bug")
    
    def test_severity_enum(self):
        """Test ReviewSeverity enum."""
        severities = list(ReviewSeverity)
        self.assertIn(ReviewSeverity.CRITICAL, severities)
        self.assertIn(ReviewSeverity.MAJOR, severities)
        self.assertIn(ReviewSeverity.MINOR, severities)
        self.assertIn(ReviewSeverity.INFO, severities)


class TestCodeReviewResult(unittest.TestCase):
    """
    Test cases for CodeReviewResult dataclass.
    """
    
    def test_result_creation(self):
        """Test CodeReviewResult creation."""
        comments = [
            ReviewComment(
                line=1,
                severity=ReviewSeverity.MAJOR,
                message="Issue",
            )
        ]
        
        result = CodeReviewResult(
            code_diff="test diff",
            comments=comments,
            summary="Test summary",
            overall_score=85.5,
            files_analyzed=1,
            has_critical_issues=False,
        )
        
        self.assertEqual(result.code_diff, "test diff")
        self.assertEqual(len(result.comments), 1)
        self.assertEqual(result.overall_score, 85.5)
        self.assertEqual(result.files_analyzed, 1)
        self.assertFalse(result.has_critical_issues)


if __name__ == "__main__":
    # Run tests
    unittest.main()
