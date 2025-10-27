# ruff: noqa: ALL
#!/usr/bin/env python3
"""Health check script for Carbon component."""

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
            print(f"❌ Output directory does not exist: {output_dir}")
            return False

        if not output_dir.is_dir():
            print(f"❌ Output path is not a directory: {output_dir}")
            return False

        # Check write permissions
        test_file = output_dir / ".health_check"
        try:
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            print(f"❌ Cannot write to output directory: {e}")
            return False

        # Check codecarbon availability
        try:
            from codecarbon import EmissionsTracker

            print("✅ codecarbon library: Available")
            codecarbon_available = True
        except ImportError:
            print("⚠️  codecarbon library: Not available (graceful degradation)")
            codecarbon_available = False

        # Test component start/stop
        if codecarbon_available:
            if not carbon.start():
                print("❌ Component failed to start")
                return False
            print("✅ Component started successfully")

            if not carbon.stop():
                print("❌ Component failed to stop")
                return False
            print("✅ Component stopped successfully")

        print("✅ Carbon component: OK")
        print(f"✅ Output directory writable: {output_dir}")
        print("✅ Configuration: Valid")
        print(f"✅ Project name: {carbon.project_name}")
        print(f"✅ Log level: {carbon.log_level}")
        print(f"✅ Measurement interval: {carbon.measurement_interval}s")

        return True

    except Exception as e:
        print(f"❌ Health check failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    sys.exit(0 if health_check() else 1)
