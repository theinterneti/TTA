# TTA Model Testing Framework

This document provides a comprehensive guide to the model testing frameworks used in the TTA project, including both synchronous and asynchronous testing approaches.

## Overview

The TTA project includes two main model testing frameworks:

1. **Enhanced Model Testing Framework**: Tests models with different configurations in a synchronous manner
2. **Asynchronous Model Testing Framework**: Tests multiple models in parallel for faster evaluation

Both frameworks help in selecting the optimal model for specific tasks in dynamic agent generation.

## Enhanced Model Testing Framework

### Components

The Enhanced Model Testing Framework consists of three main components:

1. **Enhanced Model Testing** (`enhanced_model_test.py`): Tests models with different quantization levels, flash attention settings, and temperature values.
2. **Results Visualization** (`visualize_model_results.py`): Creates visualizations and reports from test results.
3. **Dynamic Model Selector** (`dynamic_model_selector.py`): Recommends the best model for specific tasks or agent types.

### Features

- **Comprehensive Testing**:
  - Multiple quantization levels (4-bit, 8-bit, none)
  - Flash attention toggle
  - Temperature variation (0.1, 0.7, 1.0)
  - Multiple evaluation metrics

- **Evaluation Metrics**:
  - Speed (tokens/second)
  - Memory usage
  - Structured output capability
  - Tool use capability
  - Creativity/diversity of responses
  - Reasoning ability

- **Result Analysis**:
  - Performance comparison across models
  - Best configurations for different tasks
  - Task-specific recommendations

- **Visualizations**:
  - Speed comparison charts
  - Memory usage charts
  - Temperature effect analysis
  - Task performance comparison
  - Flash attention impact
  - Model capabilities radar chart

- **Dynamic Model Selection**:
  - Task-based model selection
  - Agent-type-based model selection
  - Constraint-based filtering (memory, speed)

### Usage

#### Running Model Tests

```bash
python3 /app/scripts/enhanced_model_test.py --models Qwen/Qwen2.5-0.5B-Instruct Qwen/Qwen2.5-1.5B-Instruct --quantizations 4bit 8bit --flash-attention true false --temperatures 0.1 0.7 1.0 --output /app/model_test_results/test_results.json
```

Options:
- `--models`: Models to test (default: all available models)
- `--quantizations`: Quantization levels to test (4bit, 8bit, none)
- `--flash-attention`: Flash attention settings to test (true, false)
- `--temperatures`: Temperature settings to test
- `--output`: Output file for results

#### Visualizing Results

```bash
python3 /app/scripts/visualize_model_results.py --results /app/model_test_results/test_results.json
```

Options:
- `--results`: Path to results JSON file
- `--analysis`: Path to analysis JSON file (optional)
- `--output-dir`: Directory to save visualizations (optional)

#### Selecting Models for Tasks

```bash
python3 /app/scripts/dynamic_model_selector.py --task structured_output --max-memory 4000 --min-speed 20
```

Options:
- `--analysis`: Path to analysis JSON file (optional)
- `--task`: Task type (speed_critical, memory_constrained, structured_output, tool_use, creative_content, complex_reasoning)
- `--agent`: Agent type (creative, analytical, assistant, chat, coding, summarization, translation)
- `--max-memory`: Maximum memory in MB
- `--min-speed`: Minimum speed in tokens/second

## Asynchronous Model Testing Framework

### Components

The Asynchronous Model Testing Framework consists of three main components:

1. **Async Model Testing** (`async_model_test.py`): Main script for asynchronous model testing
2. **Run Async Model Tests** (`run_async_model_tests.sh`): Shell script to run the async model tests
3. **Visualize Async Results** (`visualize_async_results.py`): Script to visualize the test results

### Features

- **Parallel Testing**: Test multiple models concurrently
- **Configurable Concurrency**: Control the number of models tested in parallel
- **Comprehensive Metrics**: Collect performance metrics for each model
- **Visualization**: Generate charts and reports from test results

### Usage

#### Running Async Model Tests

To test all available models:

```bash
./scripts/run_async_model_tests.sh --max-concurrent 1 --quantization none
```

To test specific models:

```bash
./scripts/run_async_model_tests.sh --models "google/gemma-2b" "Qwen/Qwen2.5-0.5B-Instruct" --max-concurrent 1 --quantization none
```

Options:
- `--models`: Space-separated list of models to test (default: all available models)
- `--max-concurrent`: Maximum number of concurrent tests (default: 1)
- `--quantization`: Quantization level to use (default: 4bit, options: 4bit, 8bit, none)
- `--flash-attention`: Whether to use flash attention (default: true, options: true, false)
- `--temperature`: Temperature for generation (default: 0.7)
- `--output-dir`: Directory to save results (default: /app/model_test_results)

#### Visualizing Results

To visualize the test results:

```bash
./scripts/visualize_async_results.py --results /app/model_test_results/async_model_test_TIMESTAMP.json --output-dir /app/model_test_results/visualizations
```

This will generate:
- Charts comparing model performance
- An HTML report with detailed results

## Task and Agent Types

### Task Types

- **speed_critical**: Tasks that require fast response times
- **memory_constrained**: Tasks that need to run with limited memory resources
- **structured_output**: Tasks that require generating valid structured data (e.g., JSON)
- **tool_use**: Tasks that involve understanding and using tools or APIs
- **creative_content**: Tasks that require creative and diverse text generation
- **complex_reasoning**: Tasks that involve step-by-step reasoning or problem-solving

### Agent Types

- **creative**: Prioritizes creative content generation
- **analytical**: Prioritizes complex reasoning and structured output
- **assistant**: Prioritizes tool use and structured output with good speed
- **chat**: Prioritizes speed and creative content
- **coding**: Prioritizes structured output and complex reasoning
- **summarization**: Prioritizes speed and complex reasoning
- **translation**: Prioritizes speed and structured output

## Integration with Dynamic Agent Generation

The dynamic model selector can be integrated into agent generation workflows:

```python
import json
import subprocess

def get_model_for_agent(agent_type, memory_constraint=None, speed_constraint=None):
    cmd = ["python3", "/app/scripts/dynamic_model_selector.py", "--agent", agent_type]

    if memory_constraint:
        cmd.extend(["--max-memory", str(memory_constraint)])
    if speed_constraint:
        cmd.extend(["--min-speed", str(speed_constraint)])

    result = subprocess.check_output(cmd).decode('utf-8')
    return json.loads(result)

# Example usage
model_config = get_model_for_agent("assistant", memory_constraint=4000)
model_name = model_config["selected_model"]
quantization = model_config["recommended_config"]["quantization"]
temperature = model_config["recommended_config"]["temperature"]

# Use these settings to initialize the model for the agent
```

## Extending the Frameworks

### Adding New Models or Metrics to Enhanced Model Testing

1. Add new models to the `DEFAULT_MODELS` list in `enhanced_model_test.py`
2. Add new test prompts to the `TEST_PROMPTS` dictionary
3. Implement new evaluation functions for specific capabilities
4. Update the `TASK_TYPES` dictionary in `dynamic_model_selector.py` for new task types
5. Update the agent-task mapping in `get_model_config_for_agent()` for new agent types

### Adding New Prompt Types or Test Metrics to Async Model Testing

1. Add new prompt types to the `TEST_PROMPTS` dictionary in `async_model_test.py`
2. Add new evaluation metrics to the `test_model` function in `async_model_test.py`
3. Update the visualization code in `visualize_async_results.py` to include the new metrics

## Requirements

- Python 3.8+
- PyTorch 2.0+ (for flash attention support)
- Transformers library
- Matplotlib and Seaborn (for visualizations)
- Pandas (for data analysis)
- psutil (for memory monitoring)

## Future Improvements

- Add support for more model architectures
- Implement more sophisticated evaluation metrics
- Add support for multi-GPU testing
- Integrate with model serving frameworks
- Add A/B testing capabilities for model selection
- Implement continuous monitoring of model performance


---
**Logseq:** [[TTA.dev/Docs/Ai-framework/Models/Model-testing]]
