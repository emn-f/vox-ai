"""
GitHub Integration for Automated Code Review

This module provides integration with GitHub API to automatically
review pull requests using the CodeReviewer model.
"""

import logging
from typing import Optional, Dict, Any, List
import re

try:
    from github import Github, GithubException
    from github.PullRequest import PullRequest
    from github.Repository import Repository
except ImportError:
    raise ImportError(
        "Please install PyGithub: pip install PyGithub"
    )

from .code_reviewer import CodeReviewer, ReviewComment


logger = logging.getLogger(__name__)


class GitHubCodeReviewBot:
    """
    Automated code review bot for GitHub pull requests.
    
    This class handles:
    - Fetching pull request diffs
    - Running code reviews
    - Posting comments back to GitHub
    
    Example:
        >>> bot = GitHubCodeReviewBot(github_token)
        >>> bot.review_pull_request("owner/repo", pr_number)
    """
    
    def __init__(
        self,
        github_token: str,
        code_reviewer: Optional[CodeReviewer] = None,
    ):
        """
        Initialize the GitHub review bot.
        
        Args:
            github_token: GitHub personal access token
            code_reviewer: CodeReviewer instance (creates new if None)
        """
        try:
            self.github = Github(github_token)
            self.user = self.github.get_user()
            logger.info(f"Authenticated as {self.user.login}")
        except GithubException as e:
            logger.error(f"GitHub authentication failed: {e}")
            raise
        
        self.code_reviewer = code_reviewer or CodeReviewer()
    
    def review_pull_request(
        self,
        repo_path: str,
        pr_number: int,
        post_comments: bool = True,
    ) -> Dict[str, Any]:
        """
        Review a pull request.
        
        Args:
            repo_path: Repository path ("owner/repo")
            pr_number: Pull request number
            post_comments: Whether to post comments to GitHub
            
        Returns:
            Review results dictionary
        """
        try:
            # Get repository and PR
            repo = self.github.get_repo(repo_path)
            pr = repo.get_pull(pr_number)
            
            logger.info(f"Reviewing PR #{pr_number} in {repo_path}")
            
            # Get the diff
            diff = self._get_pr_diff(repo, pr)
            
            if not diff:
                logger.warning("No diff found for PR")
                return {
                    "status": "no_diff",
                    "pr_number": pr_number,
                }
            
            # Run code review
            review_result = self.code_reviewer.review_code(diff)
            
            # Post comments if requested
            if post_comments and review_result.comments:
                self._post_review_comments(pr, review_result.comments)
            
            return {
                "status": "success",
                "pr_number": pr_number,
                "comments_count": len(review_result.comments),
                "summary": review_result.summary,
                "overall_score": review_result.overall_score,
                "has_critical": review_result.has_critical_issues,
            }
            
        except GithubException as e:
            logger.error(f"GitHub error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reviewing PR: {e}")
            raise
    
    def review_multiple_prs(
        self,
        repo_path: str,
        state: str = "open",
        post_comments: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Review multiple pull requests.
        
        Args:
            repo_path: Repository path ("owner/repo")
            state: PR state ('open', 'closed', or 'all')
            post_comments: Whether to post comments to GitHub
            
        Returns:
            List of review results
        """
        repo = self.github.get_repo(repo_path)
        prs = repo.get_pulls(state=state)
        
        results = []
        for pr in prs:
            try:
                result = self.review_pull_request(
                    repo_path,
                    pr.number,
                    post_comments=post_comments,
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to review PR #{pr.number}: {e}")
                results.append({
                    "status": "error",
                    "pr_number": pr.number,
                    "error": str(e),
                })
        
        return results
    
    def _get_pr_diff(self, repo: Repository, pr: PullRequest) -> str:
        """
        Get the diff for a pull request.
        
        Args:
            repo: GitHub repository
            pr: Pull request object
            
        Returns:
            Diff content as string
        """
        try:
            # Get all commits in the PR
            commits = pr.get_commits()
            diffs = []
            
            for commit in commits:
                # Get diff from the commit
                commit_obj = repo.get_commit(commit.sha)
                for file in commit_obj.files:
                    if file.patch:
                        diffs.append(file.patch)
            
            return "\n".join(diffs)
            
        except Exception as e:
            logger.error(f"Failed to get PR diff: {e}")
            return ""
    
    def _post_review_comments(
        self,
        pr: PullRequest,
        comments: List[ReviewComment],
    ) -> None:
        """
        Post review comments to a pull request.
        
        Args:
            pr: Pull request object
            comments: List of review comments
        """
        # Group comments by severity for better formatting
        by_severity = {}
        for comment in comments:
            if comment.severity not in by_severity:
                by_severity[comment.severity] = []
            by_severity[comment.severity].append(comment)
        
        # Create consolidated comment
        comment_text = self._format_review_comment(by_severity)
        
        try:
            pr.create_issue_comment(comment_text)
            logger.info(f"Posted review comment to PR #{pr.number}")
        except GithubException as e:
            logger.error(f"Failed to post comment: {e}")
    
    def _format_review_comment(self, comments_by_severity: Dict) -> str:
        """
        Format review comments for GitHub.
        
        Args:
            comments_by_severity: Comments grouped by severity
            
        Returns:
            Formatted markdown comment
        """
        parts = [
            "## 🤖 AI Code Review\n",
            "Automated code review analysis completed.\n",
        ]
        
        severity_order = ['CRITICAL', 'MAJOR', 'MINOR', 'INFO']
        severity_emojis = {
            'CRITICAL': '🔴',
            'MAJOR': '🟠',
            'MINOR': '🟌',
            'INFO': '👇',
        }
        
        for severity in severity_order:
            if severity in comments_by_severity:
                comments = comments_by_severity[severity]
                emoji = severity_emojis.get(severity, '•')
                parts.append(f"\n### {emoji} {severity} ({len(comments)})\n")
                
                for i, comment in enumerate(comments[:5], 1):  # Limit to 5 per severity
                    parts.append(
                        f"{i}. **[Line {comment.line}]** {comment.message}\n"
                    )
                    if comment.suggestion:
                        parts.append(f"   > {comment.suggestion}\n")
                
                if len(comments) > 5:
                    parts.append(f"\n_... and {len(comments) - 5} more {severity} issue(s)_\n")
        
        parts.append(
            "\n---\n"
            "*This is an automated review. Please review comments manually.*\n"
        )
        
        return "".join(parts)
    
    def watch_repository(
        self,
        repo_path: str,
        auto_review: bool = True,
    ) -> None:
        """
        Set up webhook for automatic PR review.
        
        Args:
            repo_path: Repository path ("owner/repo")
            auto_review: Whether to enable auto-review
            
        Note:
            This requires additional setup with GitHub webhooks.
            In production, you'd typically use a GitHub App or
            webhook service to trigger reviews automatically.
        """
        logger.info(f"Setting up review watcher for {repo_path}")
        # Implementation depends on deployment strategy
        # (GitHub Actions, webhook server, etc.)
