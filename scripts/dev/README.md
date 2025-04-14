# TTA Development Scripts

This directory contains scripts for development tasks in the TTA project.

## Model Testing Scripts

The TTA project includes scripts for testing AI models:

- **enhanced_model_test.py**: Tests models with different configurations
- **async_model_test.py**: Tests multiple models in parallel
- **run_async_model_tests.sh**: Shell script to run async model tests
- **visualize_model_results.py**: Visualizes model test results
- **dynamic_model_selector.py**: Selects models for specific tasks

## Usage

### Enhanced Model Testing

```bash
python3 /app/scripts/enhanced_model_test.py --models Qwen/Qwen2.5-0.5B-Instruct Qwen/Qwen2.5-1.5B-Instruct --quantizations 4bit 8bit --flash-attention true false --temperatures 0.1 0.7 1.0 --output /app/model_test_results/test_results.json
```

### Asynchronous Model Testing

```bash
./scripts/run_async_model_tests.sh --models "google/gemma-2b" "Qwen/Qwen2.5-0.5B-Instruct" --max-concurrent 1 --quantization none
```

### Visualizing Results

```bash
python3 /app/scripts/visualize_model_results.py --results /app/model_test_results/test_results.json
```

### Dynamic Model Selection

```bash
python3 /app/scripts/dynamic_model_selector.py --task structured_output --max-memory 4000 --min-speed 20
```

## Related Documentation

For more information on model testing in the TTA project, see:

- [Model Testing Guide](../../Documentation/ai-framework/models/model-testing.md)
- [Models Guide](../../Documentation/ai-framework/models/models-guide.md)
- [AI Framework](../../Documentation/ai-framework/README.md)
