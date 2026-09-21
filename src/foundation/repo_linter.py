# src/foundation/repo_linter.py
"""
Repository Structure Validation Utilities.

This module provides tools to validate the foundational structure of the 
AERIS codebase. It checks for the presence of required architectural directories
and enforces a standard template for Architecture Decision Records (ADRs).

Exported Functions:
    get_missing_directories(base_path, required_dirs): Returns a list of missing paths.
    validate_adr_format(content): Validates string content against ADR rules.

Module Attributes:
    REQUIRED_ADR_SECTIONS (list[str]): Regex patterns required in an ADR.
"""

import re
from pathlib import Path
from typing import List

REQUIRED_ADR_SECTIONS: List[str] = [
    r"^#\s+ADR",        # Must start with a Level 1 Header containing "ADR"
    r"^##\s+Context",   # Must contain a Level 2 Header "Context"
    r"^##\s+Decision"   # Must contain a Level 2 Header "Decision"
]

def get_missing_directories(base_path: Path, required_dirs: List[str]) -> List[str]:
    """
    Checks the base_path for the existence of required directories.

    Args:
        base_path (Path): The root path of the repository.
        required_dirs (List[str]): A list of relative directory paths.

    Returns:
        List[str]: A list of directory paths that do not exist.
    """
    missing_dirs: List[str] = []
    for dir_path in required_dirs:
        target_path = base_path / dir_path
        if not target_path.is_dir():
            missing_dirs.append(dir_path)
    return missing_dirs

def validate_adr_format(content: str) -> bool:
    """
    Validates that a string containing Markdown has the required ADR sections.

    Args:
        content (str): The raw text content of the ADR file.

    Returns:
        bool: True if all required sections are present, False otherwise.
    """
    for section_pattern in REQUIRED_ADR_SECTIONS:
        if not re.search(section_pattern, content, re.MULTILINE | re.IGNORECASE):
            return False
    return True