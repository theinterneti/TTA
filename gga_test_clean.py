"""Calculate totals with proper error handling."""
Logseq: [[TTA.dev/Gga_test_clean]]

import logging
from collections.abc import Iterable

logger = logging.getLogger(__name__)


def calculate_total(items: Iterable[float]) -> float:
    """Calculate and return the sum of items.

    Args:
        items: Iterable of numeric values to sum

    Returns:
        Sum of all items

    Raises:
        TypeError: If items contains non-numeric values
    """
    try:
        total = sum(items)
        logger.info("Calculated total: %f", total)
        return total
    except TypeError as e:
        logger.error("Invalid item type in collection: %s", e)
        raise