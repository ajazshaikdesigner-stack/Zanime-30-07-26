# ZANIME Testing Guide

## Overview
ZANIME uses `pytest` for its test suite. The suite is divided into `smoke` tests (verifying UI bootup) and `unit` tests (verifying core managers).

## Running Tests
To run the full test suite locally:
```bash
python -m pytest tests/
```

To run a specific module:
```bash
python -m pytest tests/unit/test_core.py
```

## Writing Tests
- All test files must be prefixed with `test_`.
- Use the `qapp` fixture in `conftest.py` for any tests requiring a PySide6 QApplication instance.
- Do not couple tests directly to hardware constraints; mock services where appropriate.
