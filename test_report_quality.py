#!/usr/bin/env python3
"""
Test script for validating report generation quality improvements.

Tests:
1. Unknown abbreviations should NOT be expanded with hallucinated expansions
2. Known abbreviations should be expanded correctly
3. Trash input should be handled gracefully
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.core.institutional_context import get_institutional_context
from app.core.input_sanitizer import get_sanitizer


def test_institutional_context():
    """Test institutional context handling."""
    print("=" * 60)
    print("TEST 1: Institutional Context")
    print("=" * 60)

    context = get_institutional_context()

    # Test cases: (abbreviation, should_expand)
    test_cases = [
        ("GITS", False, "GITS"),  # Unknown - should keep as-is
        ("BE", True, "Final Year Engineering"),  # Known - should expand
        ("FE", True, "First Year Engineering"),  # Known
        ("NBA", True, "National Board of Accreditation"),  # Known committee
        ("RANDOM", False, "RANDOM"),  # Unknown - should keep as-is
        ("grps", True, "group supervision"),  # Known academic term
    ]

    passed = 0
    failed = 0

    for abbrev, should_expand, expected in test_cases:
        result = context.expand_abbreviation(abbrev)

        if should_expand:
            if result == expected:
                print(f"✓ {abbrev} → {result} (CORRECT)")
                passed += 1
            else:
                print(f"✗ {abbrev} → {result} (EXPECTED: {expected})")
                failed += 1
        else:
            if result == expected:
                print(f"✓ {abbrev} → {result} (Kept as-is - CORRECT)")
                passed += 1
            else:
                print(f"✗ {abbrev} → {result} (EXPECTED: kept as '{expected}')")
                failed += 1

    print(f"\nContext Test Results: {passed} passed, {failed} failed\n")
    return failed == 0


def test_input_sanitization():
    """Test input sanitization and validation."""
    print("=" * 60)
    print("TEST 2: Input Sanitization")
    print("=" * 60)

    sanitizer = get_sanitizer()

    # Test cases: (input, should_be_valid, description)
    test_cases = [
        ("BE B paper checking done", True, "Valid task"),
        ("GITS committee work done", True, "Valid task with unknown abbrev"),
        ("review for my grps done", True, "Valid task with known abbrev"),
        ("", False, "Empty string"),
        ("   ", False, "Only whitespace"),
        ("!!!", False, "Only special chars"),
        ("ab", False, "Too short"),
        ("a" * 600, False, "Too long"),
        ("12345", False, "Only numbers"),
        ("aaaaaaaaaaaaaaaa", False, "Repeated chars"),
        ("Completed grading of 50 assignments", True, "Valid detailed task"),
    ]

    passed = 0
    failed = 0

    for task, should_be_valid, description in test_cases:
        is_valid = sanitizer.is_valid_task(task)
        display_task = task[:50] + "..." if len(task) > 50 else task

        if is_valid == should_be_valid:
            status = "VALID" if is_valid else "INVALID"
            print(f"✓ {status}: '{display_task}' - {description}")
            passed += 1
        else:
            expected = "VALID" if should_be_valid else "INVALID"
            actual = "VALID" if is_valid else "INVALID"
            print(f"✗ Expected {expected}, got {actual}: '{display_task}' - {description}")
            failed += 1

    print(f"\nSanitization Test Results: {passed} passed, {failed} failed\n")
    return failed == 0


def test_sanitize_and_validate():
    """Test batch sanitization and validation."""
    print("=" * 60)
    print("TEST 3: Batch Sanitization")
    print("=" * 60)

    sanitizer = get_sanitizer()

    input_tasks = [
        "BE B paper checking done",
        "GITS committee work done",
        "",  # Invalid - empty
        "review for my grps done",
        "!!!",  # Invalid - only special chars
        "Taught FE students about data structures",
        "ab",  # Invalid - too short
    ]

    valid_tasks, rejected_tasks = sanitizer.sanitize_and_validate_tasks(input_tasks)

    print(f"Input: {len(input_tasks)} tasks")
    print(f"Valid: {len(valid_tasks)} tasks")
    print(f"Rejected: {len(rejected_tasks)} tasks")
    print()

    print("Valid Tasks:")
    for i, task in enumerate(valid_tasks, 1):
        print(f"  {i}. {task}")

    print("\nRejected Tasks:")
    for i, task in enumerate(rejected_tasks, 1):
        print(f"  {i}. '{task}'")

    # We expect 4 valid tasks and 3 rejected
    expected_valid = 4
    expected_rejected = 3

    if len(valid_tasks) == expected_valid and len(rejected_tasks) == expected_rejected:
        print(f"\n✓ Batch sanitization PASSED")
        return True
    else:
        print(f"\n✗ Expected {expected_valid} valid and {expected_rejected} rejected")
        print(f"  Got {len(valid_tasks)} valid and {len(rejected_tasks)} rejected")
        return False


def test_context_prompt_generation():
    """Test context prompt generation for AI."""
    print("=" * 60)
    print("TEST 4: Context Prompt Generation")
    print("=" * 60)

    context = get_institutional_context()
    prompt = context.get_context_prompt()

    print("Generated Context Prompt:")
    print("-" * 60)
    print(prompt)
    print("-" * 60)

    # Check that critical rules are present
    required_strings = [
        "INSTITUTIONAL CONTEXT",
        "CRITICAL RULES",
        "ONLY expand abbreviations listed above",
        "DO NOT make up or guess expansions",
        "BE = Final Year Engineering",
        "GITS",  # Should be in the list
    ]

    passed = 0
    failed = 0

    print("\nChecking for required content:")
    for required in required_strings:
        if required in prompt:
            print(f"✓ Found: '{required}'")
            passed += 1
        else:
            print(f"✗ Missing: '{required}'")
            failed += 1

    print(f"\nPrompt Generation Test Results: {passed} passed, {failed} failed\n")
    return failed == 0


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("REPORT GENERATION QUALITY TEST SUITE")
    print("=" * 60 + "\n")

    results = []

    results.append(("Institutional Context", test_institutional_context()))
    results.append(("Input Sanitization", test_input_sanitization()))
    results.append(("Batch Sanitization", test_sanitize_and_validate()))
    results.append(("Context Prompt Generation", test_context_prompt_generation()))

    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Report generation quality is improved.\n")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED. Please review the output above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
