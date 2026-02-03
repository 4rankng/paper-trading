"""
Project root detection - single source of truth.

This module provides the canonical implementation of get_project_root()
used across all skills to eliminate 55+ duplicate implementations.
"""
from pathlib import Path


def get_project_root() -> Path:
    """
    Get the project root directory (my-stock-advisor).

    This is the single source of truth for project root detection.
    All skills should use this implementation instead of duplicating
    the logic in their own modules.

    Detection Strategy (in order of priority):
    1. Look for .git/ directory
    2. Look for watchlist.json file
    3. Look for prices/ directory
    4. Walk up from current location (max 6 levels)
    5. Fallback to current working directory

    Returns:
        Path: The project root directory

    Raises:
        RuntimeError: If project root cannot be determined
    """
    # Start from the current file's location and walk up
    current = Path(__file__).resolve().parent

    # Check if we're in .claude/shared/ - go up two levels
    if current.name == "shared" and current.parent.name == ".claude":
        candidate = current.parent.parent
        if _is_project_root(candidate):
            return candidate

    # Walk up the directory tree (max 6 levels)
    for _ in range(6):
        if _is_project_root(current):
            return current
        parent = current.parent
        if parent == current:  # reached filesystem root
            break
        current = parent

    # Fallback: try current working directory
    cwd = Path.cwd()
    if _is_project_root(cwd):
        return cwd

    raise RuntimeError(
        "Project root not found. Expected markers: .git/, watchlist.json, prices/"
    )


def _is_project_root(path: Path) -> bool:
    """
    Check if a path is the project root directory.

    Args:
        path: Path to check

    Returns:
        bool: True if path appears to be project root
    """
    markers = [
        ".git",
        "watchlist.json",
        "prices",
        "portfolios.json",
        "analytics",
        ".claude",
    ]
    return any((path / m).exists() for m in markers)


def get_data_dir(name: str) -> Path:
    """
    Get a data directory path by name.

    Args:
        name: Directory name (e.g., 'prices', 'analytics', 'news')

    Returns:
        Path: Full path to the data directory
    """
    root = get_project_root()
    return root / name


def ensure_dir(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure

    Returns:
        Path: The same path (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path
