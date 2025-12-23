# Tests

Unit and integration tests for the GPU-accelerated data science agents.

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Test Structure

- `test_agents.py` - Tests for individual agents
- `test_pipeline.py` - Integration tests for complete workflows
- `benchmarks/` - Performance benchmarking scripts

## Requirements

```bash
pip install pytest pytest-cov
```
