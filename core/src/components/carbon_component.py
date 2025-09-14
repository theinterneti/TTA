"""
Carbon Tracking Component

This module provides a component for tracking carbon emissions across the TTA project.

Classes:
    CarbonComponent: Component for tracking carbon emissions

Example:
    ```python
    from src.orchestration import TTAConfig
    from src.components.carbon_component import CarbonComponent

    # Create a configuration object
    config = TTAConfig()

    # Create a Carbon component
    carbon = CarbonComponent(config)

    # Start the Carbon component
    carbon.start()

    # Track emissions for a specific function
    emissions = carbon.track_function(my_function, *args, **kwargs)

    # Get emissions report
    report = carbon.get_emissions_report()
    ```
"""

import datetime
import json
import logging
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

# Try to import codecarbon for carbon tracking
try:
    from codecarbon import EmissionsTracker, track_emissions

    CODECARBON_AVAILABLE = True
except ImportError:
    CODECARBON_AVAILABLE = False

from src.orchestration.component import Component
from src.orchestration.decorators import log_entry_exit, timing_decorator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type variables for better type hinting
F = TypeVar("F", bound=Callable[..., Any])
T = TypeVar("T")


class CarbonComponent(Component):
    """
    Component for tracking carbon emissions across the TTA project.

    This component provides methods for tracking carbon emissions of
    functions and components using the codecarbon library.

    Attributes:
        root_dir: Root directory of the project
        output_dir: Directory to save emissions data
        project_name: Name of the project for emissions tracking
        log_level: Log level for codecarbon
        measurement_interval: Measurement interval in seconds
        emissions_data: Dictionary of emissions data
    """

    def __init__(self, config: Any):
        """
        Initialize the Carbon component.

        Args:
            config: Configuration object
        """
        super().__init__(config, name="carbon", dependencies=[])

        self.root_dir = Path(__file__).parent.parent.parent
        self.output_dir = self.config.get(
            "carbon.output_dir", str(self.root_dir / "logs" / "codecarbon")
        )
        self.project_name = self.config.get("carbon.project_name", "TTA")
        self.log_level = self.config.get("carbon.log_level", "info")
        self.measurement_interval = self.config.get("carbon.measurement_interval", 15)

        self.emissions_data: dict[str, dict[str, Any]] = {}

        logger.info(
            f"Initialized Carbon component with output directory: {self.output_dir}"
        )

    @log_entry_exit
    @timing_decorator
    def _start_impl(self) -> bool:
        """
        Start the Carbon component.

        This method initializes the codecarbon library and creates the output directory.

        Returns:
            bool: True if the component was started successfully, False otherwise
        """
        try:
            if not CODECARBON_AVAILABLE:
                logger.warning(
                    "codecarbon not available, carbon tracking will be disabled"
                )
                return False

            # Create the output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)

            # Initialize emissions data
            self.emissions_data = {}

            logger.info(
                f"Carbon component started with output directory: {self.output_dir}"
            )
            return True
        except Exception as e:
            logger.error(f"Error starting Carbon component: {e}")
            return False

    @log_entry_exit
    @timing_decorator
    def _stop_impl(self) -> bool:
        """
        Stop the Carbon component.

        This method saves the emissions data to a file.

        Returns:
            bool: True if the component was stopped successfully, False otherwise
        """
        try:
            if not CODECARBON_AVAILABLE:
                logger.warning("codecarbon not available, carbon tracking was disabled")
                return True

            # Save emissions data to a file
            self._save_emissions_data()

            logger.info("Carbon component stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping Carbon component: {e}")
            return False

    def track_function(self, func: F, *args: Any, **kwargs: Any) -> Any:
        """
        Track carbon emissions of a function.

        Args:
            func: Function to track
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Any: Result of the function

        Raises:
            Exception: If an error occurs during function execution
        """
        if not CODECARBON_AVAILABLE:
            logger.warning(
                f"codecarbon not available, skipping emissions tracking for {func.__name__}"
            )
            return func(*args, **kwargs)

        # Create the output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Track emissions
        tracker = EmissionsTracker(
            project_name=self.project_name,
            output_dir=self.output_dir,
            log_level=self.log_level,
            measure_power_secs=self.measurement_interval,
        )

        tracker.start()
        try:
            result = func(*args, **kwargs)
            emissions = tracker.stop()

            # Store emissions data
            timestamp = datetime.datetime.now().isoformat()
            self.emissions_data[f"{func.__name__}_{timestamp}"] = {
                "function": func.__name__,
                "timestamp": timestamp,
                "emissions": emissions,
                "unit": "kg CO2eq",
            }

            logger.info(f"{func.__name__} emitted {emissions:.6f} kg CO2eq")
            return result
        except Exception as e:
            tracker.stop()
            logger.error(f"Exception in {func.__name__}: {e}")
            raise

    def get_emissions_report(self) -> dict[str, Any]:
        """
        Get a report of carbon emissions.

        Returns:
            Dict[str, Any]: Dictionary containing emissions data
        """
        if not CODECARBON_AVAILABLE:
            logger.warning("codecarbon not available, emissions report is empty")
            return {"error": "codecarbon not available"}

        # Calculate total emissions
        total_emissions = sum(
            data["emissions"] for data in self.emissions_data.values()
        )

        # Create the report
        report = {
            "project_name": self.project_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "total_emissions": total_emissions,
            "unit": "kg CO2eq",
            "functions": self.emissions_data,
        }

        return report

    def _save_emissions_data(self) -> None:
        """
        Save emissions data to a file.
        """
        if not self.emissions_data:
            logger.info("No emissions data to save")
            return

        # Create the output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Save the data to a JSON file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/emissions_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.get_emissions_report(), f, indent=2)

        logger.info(f"Emissions data saved to {filename}")

    def get_carbon_decorator(self, project_name: str | None = None) -> Callable[[F], F]:
        """
        Get a decorator for tracking carbon emissions of a function.

        Args:
            project_name: Name of the project for emissions tracking

        Returns:
            Callable[[F], F]: Decorator function
        """
        if not CODECARBON_AVAILABLE:
            logger.warning("codecarbon not available, carbon decorator will be a no-op")

            # Return a no-op decorator
            def no_op_decorator(func: F) -> F:
                return func

            return no_op_decorator

        project = project_name or self.project_name

        # Create the output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Return the track_emissions decorator
        return track_emissions(
            project_name=project, output_dir=self.output_dir, log_level=self.log_level
        )
