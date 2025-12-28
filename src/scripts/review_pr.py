#!/usr/bin/env python
"""
GitHub Actions Script for Automated Code Review

Run this script in a GitHub Actions workflow to automatically
review pull requests using the AI-powered code review system.

Environment Variables:
    GITHUB_TOKEN: GitHub personal access token
    GITHUB_REPOSITORY: Repository name (owner/repo)
    GITHUB_EVENT_PULL_REQUEST_NUMBER: PR number
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.code_reviewer import CodeReviewer
from src.core.github_integration import GitHubCodeReviewBot


def get_github_context():
    """
    Extract GitHub context from environment variables.
    
    Returns:
        Dict with repo, pr_number, and token
    """
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        logger.error("GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    repo = os.getenv('GITHUB_REPOSITORY')
    if not repo:
        logger.error("GITHUB_REPOSITORY environment variable not set")
        sys.exit(1)
    
    # PR number from GitHub Actions
    pr_number = os.getenv('GITHUB_EVENT_PULL_REQUEST_NUMBER')
    if not pr_number:
        logger.error("GITHUB_EVENT_PULL_REQUEST_NUMBER environment variable not set")
        logger.info("This script should be run from a pull_request event")
        sys.exit(1)
    
    return {
        'token': token,
        'repo': repo,
        'pr_number': int(pr_number),
    }


def main():
    """
    Main entry point for the GitHub Actions workflow.
    """
    logger.info("Starting AI Code Review...")
    logger.info(f"Python {sys.version}")
    
    try:
        # Get GitHub context
        context = get_github_context()
        logger.info(f"Repository: {context['repo']}")
        logger.info(f"PR Number: {context['pr_number']}")
        
        # Initialize code reviewer
        logger.info("Loading CodeReviewer model...")
        reviewer = CodeReviewer()
        logger.info(f"Using device: {reviewer.device}")
        
        # Initialize GitHub bot
        logger.info("Authenticating with GitHub...")
        bot = GitHubCodeReviewBot(
            github_token=context['token'],
            code_reviewer=reviewer,
        )
        
        # Review the PR
        logger.info(f"Reviewing PR #{context['pr_number']}...")
        result = bot.review_pull_request(
            repo_path=context['repo'],
            pr_number=context['pr_number'],
            post_comments=True,
        )
        
        # Log results
        logger.info("\n" + "="*60)
        logger.info("Code Review Complete")
        logger.info("="*60)
        logger.info(f"Status: {result.get('status')}")
        logger.info(f"Comments Found: {result.get('comments_count', 0)}")
        logger.info(f"Overall Score: {result.get('overall_score', 'N/A')}/100")
        logger.info(f"Has Critical Issues: {result.get('has_critical', False)}")
        logger.info(f"Summary: {result.get('summary', 'N/A')}")
        logger.info("="*60)
        
        # Set exit code based on critical issues
        if result.get('has_critical', False):
            logger.warning("\n⚠️ Critical issues found!")
            # You can set this to fail the workflow if desired
            # sys.exit(1)
        
        logger.info("\n✅ Code review completed successfully!")
        
    except Exception as e:
        logger.error(f"\n❌ Error during code review: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()
