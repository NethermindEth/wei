# Wei LangGraph Tests

This directory contains tests for the Wei LangGraph implementation.

## Setup

1. Make sure the parent directory has a `.env` file with your API keys. The tests use the parent directory's `.env` file, so you don't need a separate one in the tests directory.

```bash
# Make sure this file exists and has your API keys
../langgraph/.env
```

2. Make sure you have all the required dependencies installed:

```bash
cd ..  # Go to the parent directory
pip install -r requirements.txt
```

## Running Tests

Run tests from the `tests` directory:

```bash
cd /path/to/wei/langgraph/tests
python test_simple_analyzer.py
python test_deep_analyzer.py
python test_argument_generation.py
```

Or run tests from the parent directory:

```bash
cd /path/to/wei/langgraph
python tests/test_simple_analyzer.py
python tests/test_deep_analyzer.py
python tests/test_argument_generation.py
```

## Troubleshooting

If you encounter import errors, make sure:

1. You're running the tests from either the `tests` directory or the parent directory
2. The parent directory is in your Python path
3. All required dependencies are installed

The `import_helper.py` module is used to add the parent directory to the Python path, so imports should work regardless of where you run the tests from.
