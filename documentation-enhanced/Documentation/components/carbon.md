# Carbon Tracking Component

The Carbon Tracking Component provides methods for tracking carbon emissions of functions and components using the [CodeCarbon](https://codecarbon.io/) library.

## Overview

CodeCarbon is a Python package that estimates the amount of carbon dioxide (CO2) produced by the computing resources used to execute code. The Carbon Tracking Component integrates CodeCarbon into the TTA project, making it easy to track and report on the carbon emissions of your code.

## Installation

CodeCarbon is included as a dependency in the TTA project. It should be installed automatically when you set up the project. If you need to install it manually, you can use pip:

```bash
pip install codecarbon>=2.8.0
```

## Configuration

The Carbon Tracking Component is configured in the `config/tta_config.yaml` file:

```yaml
# Carbon Tracking Configuration
carbon:
  enabled: true
  project_name: TTA
  output_dir: logs/codecarbon
  log_level: info
  measurement_interval: 15
  track_components: true
```

### Configuration Options

- `enabled`: Whether carbon tracking is enabled
- `project_name`: Name of the project for emissions tracking
- `output_dir`: Directory to save emissions data
- `log_level`: Log level for codecarbon (debug, info, warning, error, critical)
- `measurement_interval`: Measurement interval in seconds
- `track_components`: Whether to track emissions for all components

## Usage

### Using the Carbon Component

```python
from src.orchestration import TTAConfig
from src.components import CarbonComponent

# Create a configuration object
config = TTAConfig()

# Create a Carbon component
carbon = CarbonComponent(config)

# Start the Carbon component
carbon.start()

# Track emissions for a specific function
def my_function():
    # Your code here
    return "result"

result = carbon.track_function(my_function)

# Get emissions report
report = carbon.get_emissions_report()
print(f"Total emissions: {report['total_emissions']} kg CO2eq")

# Stop the Carbon component
carbon.stop()
```

### Using the Carbon Decorator

The Carbon Component provides a decorator that you can use to track emissions for specific functions:

```python
from src.orchestration import TTAConfig
from src.components import CarbonComponent

# Create a configuration object
config = TTAConfig()

# Create a Carbon component
carbon = CarbonComponent(config)

# Get the carbon decorator
carbon_decorator = carbon.get_carbon_decorator()

# Use the decorator to track emissions
@carbon_decorator
def my_function():
    # Your code here
    return "result"

# Call the function
result = my_function()
```

### Using the Built-in Decorator

You can also use the built-in decorator from the `tta.dev` repository:

```python
from tta.dev.src.utils.decorators import track_carbon

@track_carbon(project_name="TTA", output_dir="logs/codecarbon")
def my_function():
    # Your code here
    return "result"

# Call the function
result = my_function()
```

## Emissions Report

The Carbon Component provides a method to get a report of carbon emissions:

```python
report = carbon.get_emissions_report()
```

The report is a dictionary with the following structure:

```python
{
    "project_name": "TTA",
    "timestamp": "2023-06-01T12:00:00.000000",
    "total_emissions": 0.000123,
    "unit": "kg CO2eq",
    "functions": {
        "my_function_2023-06-01T12:00:00.000000": {
            "function": "my_function",
            "timestamp": "2023-06-01T12:00:00.000000",
            "emissions": 0.000123,
            "unit": "kg CO2eq"
        }
    }
}
```

## Emissions Data

The Carbon Component saves emissions data to a JSON file in the `logs/codecarbon` directory. The file is named `emissions_YYYYMMDD_HHMMSS.json`.

You can view the emissions data using any JSON viewer or by loading it in Python:

```python
import json

with open("logs/codecarbon/emissions_20230601_120000.json", "r") as f:
    data = json.load(f)

print(f"Total emissions: {data['total_emissions']} kg CO2eq")
```

## Best Practices

- Use the Carbon Component to track emissions for long-running or resource-intensive functions
- Use the `track_components` option to automatically track emissions for all components
- Review the emissions report regularly to identify areas for improvement
- Consider using the emissions data to offset your carbon footprint

## Troubleshooting

If you encounter issues with the Carbon Component, check the following:

- Make sure CodeCarbon is installed (`pip install codecarbon>=2.8.0`)
- Check the logs for any error messages
- Verify that the `output_dir` exists and is writable
- Try increasing the `measurement_interval` if you're getting too many measurements

## References

- [CodeCarbon Documentation](https://codecarbon.io/)
- [CodeCarbon GitHub Repository](https://github.com/mlco2/codecarbon)
- [Carbon Tracking Component Source Code](../../src/components/carbon_component.py)
