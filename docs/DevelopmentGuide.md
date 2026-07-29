# Development Guide

## Setup Environment

1. Install Python 3.11.
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`

## Running Tests

Run the test suite using pytest:
```bash
pytest tests/
```

## Adding New UI Components

1. Place new components in `src/ui/components/`.
2. Ensure components do not contain heavy business logic.
3. Emit events using the `EventBus` for actions.

## Adding Plugins

Place new plugins in the `plugins/` directory. They will be dynamically loaded by the `PluginManager`.
