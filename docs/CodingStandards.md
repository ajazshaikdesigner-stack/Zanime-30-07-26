# Coding Standards

1. **Language**: Python 3.11+
2. **Style**: PEP 8 compliant. Use `black` for formatting and `flake8` for linting.
3. **Type Hints**: All functions and methods MUST include Python type hints.
4. **Docstrings**: Use Google Style docstrings for all modules, classes, and public functions.
5. **SOLID Principles**: Adhere to SOLID design principles.
6. **No Global Variables**: Use singletons or dependency injection via the `ZanimeApp` context.
7. **Exception Handling**: Catch specific exceptions, never use bare `except:` blocks without re-raising or logging appropriately. All exceptions must be logged.
