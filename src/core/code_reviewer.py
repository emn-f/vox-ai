"""
Code Review Module using Microsoft CodeReviewer Model

This module provides AI-powered code review capabilities using the
microsoft/codereviewer model from Hugging Face. It analyzes code changes
and provides intelligent feedback.
"""

import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum

try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import torch
except ImportError:
    raise ImportError(
        "Please install transformers: pip install transformers torch"
    )


logger = logging.getLogger(__name__)


class ReviewSeverity(str, Enum):
    """Severity levels for code review comments."""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


@dataclass
class ReviewComment:
    """Represents a single code review comment."""
    line: int
    severity: ReviewSeverity
    message: str
    suggestion: Optional[str] = None
    category: str = "general"  # bug, performance, style, security, etc.


@dataclass
class CodeReviewResult:
    """Complete code review result."""
    code_diff: str
    comments: List[ReviewComment]
    summary: str
    overall_score: float  # 0-100
    files_analyzed: int
    has_critical_issues: bool


class CodeReviewer:
    """
    AI-powered code reviewer using Microsoft's CodeReviewer model.
    
    This class handles loading the model, tokenizing code diffs,
    and generating review comments.
    
    Example:
        >>> reviewer = CodeReviewer()
        >>> result = reviewer.review_code(code_diff)
        >>> for comment in result.comments:
        ...     print(f"Line {comment.line}: {comment.message}")
    """
    
    MODEL_NAME = "microsoft/codereviewer"
    
    def __init__(
        self,
        model_name: str = MODEL_NAME,
        device: Optional[str] = None,
        cache_dir: Optional[str] = None,
    ):
        """
        Initialize the CodeReviewer.
        
        Args:
            model_name: Hugging Face model identifier
            device: Device to use ('cuda', 'cpu', or None for auto-detection)
            cache_dir: Directory to cache downloaded models
        """
        self.model_name = model_name
        self.device = device or self._get_device()
        self.cache_dir = cache_dir
        
        logger.info(f"Loading {model_name} on device {self.device}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=cache_dir,
            )
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                cache_dir=cache_dir,
            ).to(self.device)
            
            # Evaluation mode for inference
            self.model.eval()
            logger.info("CodeReviewer model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _get_device(self) -> str:
        """Detect available device."""
        if torch.cuda.is_available():
            device = "cuda"
            logger.info(f"CUDA available, using GPU: {torch.cuda.get_device_name(0)}")
        else:
            device = "cpu"
            logger.info("Using CPU for inference")
        
        return device
    
    def prepare_input(self, code_diff: str) -> str:
        """
        Prepare code diff for the model.
        
        Args:
            code_diff: The code diff/patch content
            
        Returns:
            Formatted input string for the model
        """
        # Format: <code_diff> represents the diff content
        formatted = f"<code_diff> {code_diff} </code_diff>"
        return formatted.strip()
    
    def review_code(
        self,
        code_diff: str,
        max_length: int = 512,
        num_beams: int = 5,
        temperature: float = 0.7,
    ) -> CodeReviewResult:
        """
        Review code changes using the CodeReviewer model.
        
        Args:
            code_diff: The code diff to review
            max_length: Maximum length of generated review
            num_beams: Number of beams for beam search
            temperature: Temperature for generation
            
        Returns:
            CodeReviewResult containing review comments and analysis
        """
        if not code_diff or not code_diff.strip():
            logger.warning("Empty code diff provided")
            return CodeReviewResult(
                code_diff=code_diff,
                comments=[],
                summary="No code diff to review",
                overall_score=100.0,
                files_analyzed=0,
                has_critical_issues=False,
            )
        
        logger.info(f"Reviewing code diff (length: {len(code_diff)})")
        
        try:
            # Prepare input
            input_text = self.prepare_input(code_diff)
            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                max_length=1024,
                truncation=True,
            ).to(self.device)
            
            # Generate review
            with torch.no_grad():
                output_ids = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=num_beams,
                    temperature=temperature,
                    early_stopping=True,
                )
            
            # Decode output
            review_text = self.tokenizer.decode(
                output_ids[0],
                skip_special_tokens=True,
            )
            
            # Parse review into structured comments
            comments = self._parse_review(review_text, code_diff)
            
            # Calculate metrics
            summary = self._generate_summary(comments)
            overall_score = self._calculate_score(comments)
            has_critical = any(
                c.severity == ReviewSeverity.CRITICAL
                for c in comments
            )
            
            result = CodeReviewResult(
                code_diff=code_diff,
                comments=comments,
                summary=summary,
                overall_score=overall_score,
                files_analyzed=self._count_files(code_diff),
                has_critical_issues=has_critical,
            )
            
            logger.info(f"Review complete: {len(comments)} issues found")
            return result
            
        except Exception as e:
            logger.error(f"Error during code review: {e}")
            raise
    
    def batch_review(
        self,
        code_diffs: List[str],
        **kwargs,
    ) -> List[CodeReviewResult]:
        """
        Review multiple code diffs.
        
        Args:
            code_diffs: List of code diffs to review
            **kwargs: Additional arguments passed to review_code
            
        Returns:
            List of CodeReviewResult objects
        """
        results = []
        for i, diff in enumerate(code_diffs, 1):
            logger.info(f"Processing diff {i}/{len(code_diffs)}")
            result = self.review_code(diff, **kwargs)
            results.append(result)
        
        return results
    
    def _parse_review(self, review_text: str, code_diff: str) -> List[ReviewComment]:
        """
        Parse generated review text into structured comments.
        
        Args:
            review_text: Generated review from the model
            code_diff: Original code diff
            
        Returns:
            List of ReviewComment objects
        """
        comments = []
        
        # Split review into potential comments
        lines = review_text.split('\n')
        
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            
            # Simple heuristic-based parsing
            # In production, you might want more sophisticated NLP
            severity = self._detect_severity(line)
            category = self._detect_category(line)
            
            comment = ReviewComment(
                line=i + 1,
                severity=severity,
                message=line.strip(),
                category=category,
            )
            comments.append(comment)
        
        return comments[:10]  # Limit to top 10 comments
    
    def _detect_severity(self, text: str) -> ReviewSeverity:
        """Detect severity level from text."""
        text_lower = text.lower()
        
        critical_keywords = ['error', 'crash', 'bug', 'security', 'vulnerability']
        if any(kw in text_lower for kw in critical_keywords):
            return ReviewSeverity.CRITICAL
        
        major_keywords = ['important', 'issue', 'problem', 'performance']
        if any(kw in text_lower for kw in major_keywords):
            return ReviewSeverity.MAJOR
        
        minor_keywords = ['style', 'convention', 'readable', 'consider']
        if any(kw in text_lower for kw in minor_keywords):
            return ReviewSeverity.MINOR
        
        return ReviewSeverity.INFO
    
    def _detect_category(self, text: str) -> str:
        """Detect issue category from text."""
        text_lower = text.lower()
        
        categories = {
            'security': ['security', 'vulnerability', 'unsafe', 'injection'],
            'performance': ['performance', 'slow', 'efficient', 'optimize'],
            'bug': ['bug', 'error', 'crash', 'fail', 'exception'],
            'style': ['style', 'convention', 'format', 'readable'],
            'maintainability': ['maintain', 'refactor', 'simplify', 'complex'],
        }
        
        for category, keywords in categories.items():
            if any(kw in text_lower for kw in keywords):
                return category
        
        return 'general'
    
    def _generate_summary(self, comments: List[ReviewComment]) -> str:
        """Generate a summary of the review."""
        if not comments:
            return "✅ No issues found. Code looks good!"
        
        critical_count = sum(
            1 for c in comments if c.severity == ReviewSeverity.CRITICAL
        )
        major_count = sum(
            1 for c in comments if c.severity == ReviewSeverity.MAJOR
        )
        
        summary_parts = []
        if critical_count > 0:
            summary_parts.append(f"🔴 {critical_count} critical issue(s)")
        if major_count > 0:
            summary_parts.append(f"🟠 {major_count} major issue(s)")
        
        if summary_parts:
            return ", ".join(summary_parts) + " found in review."
        
        return "✅ Review complete with minor suggestions."
    
    def _calculate_score(self, comments: List[ReviewComment]) -> float:
        """Calculate overall code quality score (0-100)."""
        if not comments:
            return 100.0
        
        total_weight = 0
        weighted_deductions = 0
        
        severity_weights = {
            ReviewSeverity.CRITICAL: 20,
            ReviewSeverity.MAJOR: 10,
            ReviewSeverity.MINOR: 5,
            ReviewSeverity.INFO: 1,
        }
        
        for comment in comments:
            weight = severity_weights.get(comment.severity, 5)
            total_weight += weight
            weighted_deductions += weight
        
        # Scale deductions (max 100 deduction = score 0)
        score = max(0, 100 - min(100, weighted_deductions))
        return score
    
    def _count_files(self, code_diff: str) -> int:
        """Count number of files in diff."""
        # Simple heuristic: count 'diff --git' occurrences
        return code_diff.count('diff --git')
