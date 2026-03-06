"""
Input validation and sanitization for report generation.

Handles trash/malformed input gracefully to ensure high-quality report generation.
"""

import re
from typing import List, Tuple


class InputSanitizer:
    """Validates and sanitizes user input for report generation."""

    # Patterns to detect low-quality input
    SPAM_PATTERNS = [
        r"^[.,!?;:\s]*$",  # Only punctuation/whitespace
        r"^(.)\1{10,}$",  # Repeated characters (aaaaaaaaaa...)
        r"^[0-9\s]+$",  # Only numbers
        r"^[\W_]+$",  # Only special characters
    ]

    # Minimum meaningful content length
    MIN_CONTENT_LENGTH = 3
    MAX_CONTENT_LENGTH = 500

    def __init__(self):
        """Initialize sanitizer."""
        pass

    def is_valid_task(self, task: str) -> bool:
        """
        Check if a task description is valid and meaningful.

        Args:
            task: Task description to validate

        Returns:
            True if valid, False otherwise
        """
        if not task or not isinstance(task, str):
            return False

        # Strip whitespace
        cleaned = task.strip()

        # Check minimum length
        if len(cleaned) < self.MIN_CONTENT_LENGTH:
            return False

        # Check maximum length
        if len(cleaned) > self.MAX_CONTENT_LENGTH:
            return False

        # Check against spam patterns
        for pattern in self.SPAM_PATTERNS:
            if re.match(pattern, cleaned):
                return False

        # Must contain at least one letter
        if not re.search(r"[a-zA-Z]", cleaned):
            return False

        return True

    def sanitize_task(self, task: str) -> str:
        """
        Clean and normalize task description.

        Args:
            task: Raw task description

        Returns:
            Sanitized task description
        """
        if not task or not isinstance(task, str):
            return ""

        # Strip leading/trailing whitespace
        cleaned = task.strip()

        # Normalize multiple spaces to single space
        cleaned = re.sub(r"\s+", " ", cleaned)

        # Remove control characters except newlines
        cleaned = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", cleaned)

        # Limit consecutive special characters
        cleaned = re.sub(r"([!?.,;:])\1{2,}", r"\1\1", cleaned)

        return cleaned

    def sanitize_and_validate_tasks(
        self, tasks: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Sanitize and validate a list of tasks.

        Args:
            tasks: List of raw task descriptions

        Returns:
            Tuple of (valid_tasks, rejected_tasks)
        """
        valid_tasks = []
        rejected_tasks = []

        for task in tasks:
            # Sanitize first
            sanitized = self.sanitize_task(task)

            # Then validate
            if self.is_valid_task(sanitized):
                valid_tasks.append(sanitized)
            else:
                rejected_tasks.append(task)

        return valid_tasks, rejected_tasks

    def get_quality_score(self, task: str) -> float:
        """
        Calculate quality score for a task (0.0 to 1.0).

        Args:
            task: Task description

        Returns:
            Quality score from 0.0 (worst) to 1.0 (best)
        """
        if not self.is_valid_task(task):
            return 0.0

        score = 1.0
        cleaned = self.sanitize_task(task)

        # Penalize very short tasks
        if len(cleaned) < 10:
            score -= 0.3

        # Penalize excessive capitalization
        if cleaned.isupper() and len(cleaned) > 10:
            score -= 0.2

        # Reward proper sentence structure (starts with capital, ends with punctuation)
        if cleaned and cleaned[0].isupper():
            score += 0.1
        if cleaned and cleaned[-1] in ".!?":
            score += 0.1

        # Reward presence of verbs (simple heuristic - past tense indicators)
        verb_indicators = ["ed ", "done", "completed", "finished", "reviewed", "taught"]
        if any(indicator in cleaned.lower() for indicator in verb_indicators):
            score += 0.1

        return max(0.0, min(1.0, score))

    def suggest_improvement(self, task: str) -> str:
        """
        Suggest improvement for low-quality task descriptions.

        Args:
            task: Task description

        Returns:
            Suggestion for improvement
        """
        if not task or not isinstance(task, str):
            return "Please provide a valid task description."

        cleaned = self.sanitize_task(task)

        if len(cleaned) < self.MIN_CONTENT_LENGTH:
            return "Task description is too short. Please provide more details."

        if len(cleaned) > self.MAX_CONTENT_LENGTH:
            return "Task description is too long. Please be more concise."

        if not re.search(r"[a-zA-Z]", cleaned):
            return "Task description must contain letters."

        # Check for common issues
        if cleaned.islower():
            return "Consider using proper capitalization."

        if not any(
            word in cleaned.lower()
            for word in [
                "completed",
                "finished",
                "done",
                "reviewed",
                "taught",
                "prepared",
                "conducted",
            ]
        ):
            return "Consider using action words (completed, reviewed, taught, etc.)."

        return "Task looks good!"


# Singleton instance
_sanitizer = InputSanitizer()


def get_sanitizer() -> InputSanitizer:
    """Get the input sanitizer instance."""
    return _sanitizer
