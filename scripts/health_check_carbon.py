#!/usr/bin/env python3
"""Health check script for Carbon component."""

# Logseq: [[TTA.dev/Scripts/Health_check_carbon]]

import sys
from pathlib import Path


def health_check():
    """Perform health check on Carbon component."""
    try:
        # Import component
        from src.components.carbon_component import CarbonComponent
        from src.orchestration import TTAConfig

        # Load configuration
        config = TTAConfig()

        # Initialize component
        carbon = CarbonComponent(config)

        # Check output directory
        output_dir = Path(carbon.output_dir)
        if not output_dir.exists():
            return False

        if not output_dir.is_dir():
            return False

        # Check write permissions
        test_file = output_dir / ".health_check"
        try:
            test_file.touch()
            test_file.unlink()
        except Exception:
            return False

        # Check codecarbon availability
        try:
            from codecarbon import EmissionsTracker

            codecarbon_available = True
        except ImportError:
            codecarbon_available = False

        # Test component start/stop
        if codecarbon_available:
            if not carbon.start():
                return False

            if not carbon.stop():
                return False

        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    sys.exit(0 if health_check() else 1)
