# Tessera Test Suite

## Required Packages
Install the following packages before running tests:
```bash
pip install pytest pytest-cov
```

## Running Tests

### Run all tests with coverage report
```bash
pytest Tessera/tests/ --cov=. --cov-report=term-missing
```

### Run all tests without coverage
```bash
pytest Tessera/tests/
```

### Run a specific test file
```bash
pytest Tessera/tests/test_converters.py --cov=. --cov-report=term-missing
```

### Generate an HTML coverage report
```bash
pytest Tessera/tests/ --cov=. --cov-report=html
```
Opens `htmlcov/index.html` in your browser for a full visual breakdown per file.

---

## Understanding the Output

### Test Results
```
Tessera\tests\test_converters.py .....   [ 43%]
```
- Each `.` is a passing test
- Each `F` is a failing test
- Each `E` is a test that errored out (unexpected exception)
- The percentage is overall progress through the test suite

### Coverage Table
```
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
Tessera\converters.py      28      1    96%   19
```
- **Stmts** — total number of executable lines in the file
- **Miss** — number of lines not executed during tests
- **Cover** — percentage of lines covered
- **Missing** — the specific line numbers not covered

---

## What to Ignore

### `transpiler_pass.py` line 24
This is the `pass` statement inside the abstract `run` method. It will never
be executed by design — subclasses always override it. This miss is expected
and can be ignored. Target coverage for this file is 89%.

### Test files themselves
Coverage on test files will always show 100% and can be ignored — they are
not application code.

---

## Coverage Targets

| File                                      | Target | Notes                            |
|-------------------------------------------|--------|----------------------------------|
| circuit.py                                | 100%   |                                  |
| instruction.py                            | 100%   |                                  |
| gate_library.py                           | 100%   |                                  |
| converters.py                             | 100%   |                                  |
| pass_manager.py                           | 100%   |                                  |
| passes/identity_pass.py                   | 100%   |                                  |
| transpiler_pass.py                        | 89%    | Abstract method miss is expected |
| backends/basis_gate_sets.py               | 100%   |                                  |
| backends/decomposition_maps.py            | 100%   |                                  |
| passes/basis_translation_pass.py          | 100%   |                                  |
| transpiler.py                             | 100%   |                                  |

---

## Adding New Tests
When you add a new pass or module:
1. Create a corresponding `test_<module_name>.py` in this folder
2. Cover at minimum: happy path, edge cases, and any raised exceptions
3. Run the full suite to make sure nothing else broke