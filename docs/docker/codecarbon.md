# CodeCarbon Integration Guide

This guide explains how to use CodeCarbon for tracking energy usage and CO2 emissions in the TTA project.

## Table of Contents

- [Overview](#overview)
- [Configuration](#configuration)
- [Usage](#usage)
- [Viewing Reports](#viewing-reports)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

[CodeCarbon](https://codecarbon.io/) is a Python package that estimates the carbon emissions associated with computing. The TTA project integrates CodeCarbon to track energy usage and CO2 emissions during development and production.

Benefits of using CodeCarbon:
- Monitor energy consumption of AI models
- Identify optimization opportunities
- Track carbon footprint of development and production environments
- Generate reports for sustainability initiatives

## Configuration

CodeCarbon is configured in the `.codecarbon/config.json` file:

```json
{
  "project_name": "TTA",
  "measure_power_secs": 15,
  "save_to_file": true,
  "output_dir": "/app/logs/codecarbon",
  "emissions_endpoint": null,
  "experiment_id": null,
  "tracking_mode": "process",
  "log_level": "info"
}
```

Key configuration options:
- `project_name`: Name of the project (used in reports)
- `measure_power_secs`: Interval between power measurements (in seconds)
- `save_to_file`: Whether to save emissions data to a file
- `output_dir`: Directory where emissions data is saved
- `log_level`: Logging level (debug, info, warning, error)

Environment variables can also be used to configure CodeCarbon:
- `CODECARBON_LOG_LEVEL`: Logging level
- `CODECARBON_OUTPUT_DIR`: Output directory for emissions data

These environment variables are set in the Docker Compose files:
- Development: `docker-compose.dev.yml`
- Production: `docker-compose.prod.yml`

## Usage

### Basic Usage

To track emissions for a specific function:

```python
from codecarbon import EmissionsTracker

# Track emissions for a specific function
tracker = EmissionsTracker(project_name="TTA")
tracker.start()
# Your code here
emissions = tracker.stop()
print(f"Emissions: {emissions} kg CO2eq")
```

### Using as a Decorator

You can also use CodeCarbon as a decorator:

```python
from codecarbon import track_emissions

@track_emissions(project_name="TTA")
def my_function():
    # Your code here
    pass
```

### Tracking a Block of Code

To track emissions for a block of code:

```python
from codecarbon import EmissionsTracker

tracker = EmissionsTracker(project_name="TTA")
tracker.start()
try:
    # Your code here
finally:
    emissions = tracker.stop()
    print(f"Emissions: {emissions} kg CO2eq")
```

### Tracking a Script

To track emissions for an entire script:

```python
from codecarbon import EmissionsTracker

tracker = EmissionsTracker(project_name="TTA")
tracker.start()
# Your script code here
emissions = tracker.stop()
print(f"Emissions: {emissions} kg CO2eq")
```

## Viewing Reports

CodeCarbon generates emissions data in CSV format. The data is saved in the `/app/logs/codecarbon` directory.

To view the emissions data:

1. Navigate to the `/app/logs/codecarbon` directory
2. Open the CSV file in a spreadsheet application or use pandas:

```python
import pandas as pd

# Load the emissions data
emissions_data = pd.read_csv("/app/logs/codecarbon/emissions.csv")

# Display the data
print(emissions_data)

# Calculate total emissions
total_emissions = emissions_data["emissions"].sum()
print(f"Total emissions: {total_emissions} kg CO2eq")
```

## Best Practices

### When to Use CodeCarbon

- During model training to measure the carbon footprint
- When comparing different algorithms or approaches
- For long-running processes
- In CI/CD pipelines to track emissions over time

### Optimizing for Lower Emissions

- Use efficient algorithms
- Optimize batch sizes
- Use model pruning and quantization
- Consider using smaller models
- Run computations in regions with cleaner energy

### Reporting

- Include emissions data in model documentation
- Track emissions over time to identify trends
- Compare emissions across different models and approaches

## Troubleshooting

### Common Issues

#### Missing Emissions Data

If emissions data is not being generated:

1. Check if the output directory exists:
   ```bash
   ./scripts/orchestrate.sh exec app ls -la /app/logs/codecarbon
   ```

2. Verify that CodeCarbon is installed:
   ```bash
   ./scripts/orchestrate.sh exec app pip list | grep codecarbon
   ```

3. Check the CodeCarbon log level:
   ```bash
   ./scripts/orchestrate.sh exec app env | grep CODECARBON
   ```

#### Inaccurate Measurements

If measurements seem inaccurate:

1. Increase the measurement interval:
   ```json
   {
     "measure_power_secs": 30
   }
   ```

2. Use a different tracking mode:
   ```json
   {
     "tracking_mode": "machine"
   }
   ```

3. Check if hardware power monitoring is available:
   ```bash
   ./scripts/orchestrate.sh exec app python -c "from codecarbon.core.cpu import IntelPowerGadget; print(IntelPowerGadget.is_available())"
   ```

For more information about CodeCarbon, see the [official documentation](https://codecarbon.io/docs).


---
**Logseq:** [[TTA.dev/Docs/Docker/Codecarbon]]
