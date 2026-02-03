"""
Shared utilities for stock advisor skills.

This package provides centralized functionality to eliminate code duplication
across all skills and enable efficient data access patterns.

Modules:
    project: Single source of truth for project root detection
    data_access: Unified data I/O layer for all file operations
    quality_scoring: 0-100 quality scoring for analytics and data
    parallel_fetch: Concurrent execution of data fetching workflows
    validators: Shared validation functions

Example:
    from .claude.shared import get_project_root, DataAccess

    root = get_project_root()
    da = DataAccess()
    analytics = da.read_analytics("NVDA")
"""
from .project import get_project_root
from .data_access import DataAccess, AnalyticsFiles
from .quality_scoring import QualityScore, score_analytics_files, score_price_data
from .validators import validate_ticker, validate_analytics_structure

__all__ = [
    "get_project_root",
    "DataAccess",
    "AnalyticsFiles",
    "QualityScore",
    "score_analytics_files",
    "score_price_data",
    "validate_ticker",
    "validate_analytics_structure",
]

__version__ = "1.0.0"
