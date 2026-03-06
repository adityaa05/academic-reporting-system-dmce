"""
Institutional context and glossary for AI report generation.

This module provides domain-specific knowledge about the institution to prevent
AI hallucination when processing abbreviations and domain-specific terms.
"""

from typing import Dict, Optional

# Department-specific committees and their full forms
COMMITTEES = {
    "GITS": "GITS",  # Internal IT department committee - keep as-is
    "NBA": "National Board of Accreditation",
    "NAAC": "National Assessment and Accreditation Council",
    "IQAC": "Internal Quality Assurance Cell",
    "BOS": "Board of Studies",
    "BoS": "Board of Studies",
    "SAC": "Student Activity Committee",
    "CDC": "Career Development Cell",
    "EDC": "Entrepreneurship Development Cell",
}

# Year/Class abbreviations
# Note: BE can mean both "Final Year Engineering" (when referring to students/class)
# and "Bachelor of Engineering" (when referring to degree). Context matters.
# We prioritize the year meaning since it's more commonly used in daily reports.
YEAR_ALIASES = {
    "FE": "First Year Engineering",
    "SE": "Second Year Engineering",
    "TE": "Third Year Engineering",
    "BE": "Final Year Engineering",  # Fourth Year (also Bachelor of Engineering degree)
    "SY": "Second Year",
    "TY": "Third Year",
    "FY": "First Year",
}

# Degree programs
DEGREE_PROGRAMS = {
    "B.E.": "Bachelor of Engineering",
    "ME": "Master of Engineering",
    "M.E.": "Master of Engineering",
    "MTech": "Master of Technology",
    "M.Tech": "Master of Technology",
    "PhD": "Doctor of Philosophy",
    "Ph.D.": "Doctor of Philosophy",
}

# Branch/Department abbreviations
BRANCHES = {
    "CS": "Computer Science",
    "IT": "Information Technology",
    "EXTC": "Electronics and Telecommunication",
    "ETRX": "Electronics Engineering",
    "MECH": "Mechanical Engineering",
    "CIVIL": "Civil Engineering",
    "EE": "Electrical Engineering",
    "INSTRU": "Instrumentation Engineering",
}

# Academic activities
ACADEMIC_TERMS = {
    "GRPS": "group supervision",
    "grps": "group supervision",
    "SoE": "Statement of Eligibility",
    "CoE": "Controller of Examinations",
    "IA": "Internal Assessment",
    "ESE": "End Semester Examination",
    "TW": "Term Work",
    "OR": "Oral Examination",
    "PR": "Practical Examination",
}

# Common administrative tasks
ADMIN_TERMS = {
    "HOD": "Head of Department",
    "HoD": "Head of Department",
    "TPO": "Training and Placement Officer",
    "FA": "Faculty Advisor",
}


class InstitutionalContext:
    """Provides institutional context for AI processing."""

    def __init__(self, department: Optional[str] = None):
        """
        Initialize institutional context.

        Args:
            department: Department name for department-specific context
        """
        self.department = department
        self.glossary = {
            **COMMITTEES,
            **YEAR_ALIASES,
            **DEGREE_PROGRAMS,
            **BRANCHES,
            **ACADEMIC_TERMS,
            **ADMIN_TERMS,
        }

    def expand_abbreviation(self, abbrev: str) -> str:
        """
        Expand abbreviation if known, otherwise return as-is.

        Args:
            abbrev: Abbreviation to expand

        Returns:
            Expanded form if known, otherwise original abbreviation
        """
        # Case-insensitive lookup
        for key, value in self.glossary.items():
            if key.upper() == abbrev.upper():
                return value
        # Unknown abbreviation - return as-is without hallucination
        return abbrev

    def get_context_prompt(self) -> str:
        """
        Generate context prompt for AI with institutional knowledge.

        Returns:
            Formatted prompt text with institutional context
        """
        context_lines = [
            "INSTITUTIONAL CONTEXT:",
            "",
            "Known Abbreviations (expand only these):",
        ]

        # Group by category
        categories = [
            ("Year/Class", YEAR_ALIASES),
            ("Degree Programs", DEGREE_PROGRAMS),
            ("Committees", COMMITTEES),
            ("Departments/Branches", BRANCHES),
            ("Academic Terms", ACADEMIC_TERMS),
            ("Administrative", ADMIN_TERMS),
        ]

        for category_name, terms in categories:
            if terms:
                context_lines.append(f"\n{category_name}:")
                for abbrev, full_form in sorted(terms.items()):
                    if abbrev != full_form:  # Only show if different
                        context_lines.append(f"  - {abbrev} = {full_form}")

        context_lines.extend([
            "",
            "Terms to Keep As-Is (internal/domain-specific, no expansion needed):",
            "  - GITS (internal IT department committee)",
            "",
            "CRITICAL RULES:",
            "1. ONLY expand abbreviations listed above",
            "2. If an abbreviation is NOT in this list, keep it EXACTLY as written",
            "3. DO NOT make up or guess expansions for unknown abbreviations",
            "4. For terms like GITS, preserve them exactly without inventing expansions",
            "5. When uncertain, preserve the original text verbatim",
        ])

        return "\n".join(context_lines)

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text by providing hints for known abbreviations.

        This can be used to inject context inline, making it easier for
        the AI to understand without hallucinating.

        Args:
            text: Raw text to preprocess

        Returns:
            Text with inline hints for known abbreviations
        """
        # For now, return as-is. This can be enhanced to add inline hints
        # like "GITS (internal committee)" if needed
        return text

    def add_custom_term(self, abbreviation: str, full_form: str):
        """
        Add a custom institutional term at runtime.

        Args:
            abbreviation: The abbreviation
            full_form: The full form/expansion
        """
        self.glossary[abbreviation] = full_form


# Singleton instance for easy access
default_context = InstitutionalContext()


def get_institutional_context(department: Optional[str] = None) -> InstitutionalContext:
    """
    Get institutional context instance.

    Args:
        department: Department name for department-specific context

    Returns:
        InstitutionalContext instance
    """
    if department:
        return InstitutionalContext(department=department)
    return default_context
