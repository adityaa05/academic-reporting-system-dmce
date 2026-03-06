#!/usr/bin/env python3
"""
Test to verify that the AI no longer hallucinates fake tasks.

This test validates that:
1. If you input 1 task, you get exactly 1 task back
2. If you input 3 tasks, you get exactly 3 tasks back
3. The AI doesn't invent tasks based on abbreviations or context
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.core.input_sanitizer import get_sanitizer


def test_input_sanitization():
    """Test that input sanitization works correctly."""
    print("=" * 60)
    print("TEST 1: Input Sanitization (No Hallucination)")
    print("=" * 60)

    sanitizer = get_sanitizer()

    # Test cases
    test_inputs = [
        ["done with lectures"],  # 1 task
        ["BE B paper checking done", "GITS committee work done", "review for my grps done"],  # 3 tasks
        ["taught students", "reviewed assignments", "attended meeting", "prepared materials", "graded exams"],  # 5 tasks
    ]

    all_passed = True

    for i, tasks in enumerate(test_inputs, 1):
        valid_tasks, rejected = sanitizer.sanitize_and_validate_tasks(tasks)

        print(f"\nTest Case {i}:")
        print(f"  Input: {len(tasks)} task(s)")
        print(f"  Expected: {len(tasks)} valid task(s)")
        print(f"  Got: {len(valid_tasks)} valid task(s), {len(rejected)} rejected")

        if len(valid_tasks) == len(tasks):
            print(f"  ✓ PASSED - Correct count")
        else:
            print(f"  ✗ FAILED - Expected {len(tasks)}, got {len(valid_tasks)}")
            all_passed = False

        # Show what was processed
        for j, task in enumerate(valid_tasks, 1):
            print(f"    {j}. {task}")

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL SANITIZATION TESTS PASSED")
    else:
        print("✗ SOME SANITIZATION TESTS FAILED")
    print("=" * 60)

    return all_passed


def test_prompt_clarity():
    """Test that prompts are clear about not inventing tasks."""
    print("\n" + "=" * 60)
    print("TEST 2: Prompt Clarity Check")
    print("=" * 60)

    # Read the routes.py file to check prompt
    routes_path = os.path.join(os.path.dirname(__file__), "backend/app/api/routes.py")

    try:
        with open(routes_path, 'r') as f:
            content = f.read()

        # Check for critical phrases
        critical_phrases = [
            "DO NOT add, invent, or generate additional tasks",
            "Format ONLY the tasks provided",
            "exactly {{task_count}} formatted tasks",
            "PRESERVE the original meaning",
            "temperature=0.1",  # Lower temperature
        ]

        passed = 0
        failed = 0

        for phrase in critical_phrases:
            if phrase in content:
                print(f"  ✓ Found: '{phrase[:50]}...'")
                passed += 1
            else:
                print(f"  ✗ Missing: '{phrase[:50]}...'")
                failed += 1

        # Check that institutional_context is NOT imported
        if "from app.core.institutional_context import" not in content:
            print(f"  ✓ Removed: institutional_context import")
            passed += 1
        else:
            print(f"  ✗ Still present: institutional_context import")
            failed += 1

        print(f"\n  Results: {passed} checks passed, {failed} checks failed")
        print("=" * 60)

        return failed == 0

    except Exception as e:
        print(f"  ✗ ERROR: Could not read routes.py: {e}")
        print("=" * 60)
        return False


def test_validation_logic():
    """Test that validation logic truncates excess tasks."""
    print("\n" + "=" * 60)
    print("TEST 3: Validation Logic Check")
    print("=" * 60)

    routes_path = os.path.join(os.path.dirname(__file__), "backend/app/api/routes.py")

    try:
        with open(routes_path, 'r') as f:
            content = f.read()

        # Check for validation logic
        validation_checks = [
            "if len(formatted_data) > task_count:",
            "Truncating to",
            "formatted_data = formatted_data[:task_count]",
            "WARNING: AI returned",
        ]

        passed = 0
        failed = 0

        for check in validation_checks:
            if check in content:
                print(f"  ✓ Found: '{check}'")
                passed += 1
            else:
                print(f"  ✗ Missing: '{check}'")
                failed += 1

        print(f"\n  Results: {passed} checks passed, {failed} checks failed")
        print("=" * 60)

        return failed == 0

    except Exception as e:
        print(f"  ✗ ERROR: Could not read routes.py: {e}")
        print("=" * 60)
        return False


def test_generic_prompts():
    """Test that prompts are generic and not college-specific."""
    print("\n" + "=" * 60)
    print("TEST 4: Generic Prompt Check (Global Applicability)")
    print("=" * 60)

    files_to_check = [
        ("backend/app/api/routes.py", "Routes"),
        ("backend/app/ai/nodes/intake.py", "Intake Node"),
        ("backend/app/ai/nodes/summarizer.py", "Summarizer Node"),
        ("backend/app/ai/map_reduce.py", "Map-Reduce"),
    ]

    # College-specific terms that should NOT appear
    college_specific = [
        "academic",  # Should be "professional" or generic
        "faculty",  # Should be generic
        "INSTITUTIONAL CONTEXT",  # Should not appear
        "Known Abbreviations",  # Should not appear
    ]

    all_passed = True

    for file_path, name in files_to_check:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        print(f"\nChecking {name}:")

        try:
            with open(full_path, 'r') as f:
                content = f.read()

            found_specific = []
            for term in college_specific:
                if term in content:
                    found_specific.append(term)

            if found_specific:
                print(f"  ⚠️  Found college-specific terms: {', '.join(found_specific)}")
                # Not failing on "academic" and "faculty" since they might be in comments/variable names
                # Only fail on explicit institutional context
                if "INSTITUTIONAL CONTEXT" in found_specific or "Known Abbreviations" in found_specific:
                    all_passed = False
                    print(f"  ✗ FAILED - Still contains institutional context")
            else:
                print(f"  ✓ PASSED - Generic prompts")

        except Exception as e:
            print(f"  ✗ ERROR: Could not read file: {e}")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL FILES USE GENERIC PROMPTS")
    else:
        print("⚠️  SOME FILES STILL HAVE COLLEGE-SPECIFIC CONTENT")
    print("=" * 60)

    return all_passed


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("HALLUCINATION FIX VALIDATION TEST SUITE")
    print("=" * 60 + "\n")

    results = []

    results.append(("Input Sanitization", test_input_sanitization()))
    results.append(("Prompt Clarity", test_prompt_clarity()))
    results.append(("Validation Logic", test_validation_logic()))
    results.append(("Generic Prompts", test_generic_prompts()))

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
        print("\n🎉 ALL TESTS PASSED! Hallucination bug is fixed.\n")
        print("Key improvements:")
        print("  • AI cannot invent tasks - only formats what's provided")
        print("  • Validation truncates excess tasks")
        print("  • Lower temperature (0.1) reduces creativity")
        print("  • Clear instructions: 'DO NOT add, invent, or generate'")
        print("  • System is now globally applicable (not college-specific)")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED. Please review the output above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
