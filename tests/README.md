# GTA Analytics V2 - Test Suite

Comprehensive test suite for GTA Analytics V2 hybrid architecture.

## 📁 Structure

```
tests/
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_kill_parser.py
│   ├── test_team_tracker.py
│   ├── test_multi_api_client.py
│   └── test_config.py
├── integration/             # Integration tests (require services)
│   └── test_processing_pipeline.py
├── e2e/                     # End-to-end tests (full system)
├── conftest.py              # Shared fixtures
└── README.md                # This file
```

## 🚀 Quick Start

### Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
# Run entire test suite
pytest

# Run with coverage report
pytest --cov=backend --cov-report=html --cov-report=term
```

### Run Specific Test Categories

```bash
# Unit tests only (fast)
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v -m integration

# End-to-end tests only
pytest tests/e2e/ -v -m e2e
```

## 🏷️ Test Markers

Tests are organized with pytest markers:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Integration tests requiring services
- `@pytest.mark.e2e` - Full system end-to-end tests
- `@pytest.mark.slow` - Tests that take > 1 second
- `@pytest.mark.real_api` - Tests that use real API (consume credits)

### Run Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run all except slow tests
pytest -m "not slow"

# Run integration tests but skip real API calls
pytest -m "integration and not real_api"
```

## 📊 Coverage

Generate coverage report:

```bash
# HTML report (opens in browser)
pytest --cov=backend --cov-report=html
open htmlcov/index.html  # or start htmlcov/index.html on Windows

# Terminal report
pytest --cov=backend --cov-report=term

# Coverage for specific module
pytest tests/unit/test_kill_parser.py --cov=backend.src.brazilian_kill_parser
```

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)

Fast, isolated tests for individual components:

- **test_kill_parser.py**: BrazilianKillParser (15+ tests)
  - Standard format parsing
  - Different keywords (MATOU, KILLED, etc.)
  - Edge cases and error handling
  
- **test_team_tracker.py**: TeamTracker (25+ tests)
  - Kill registration
  - Statistics and leaderboards
  - Team management
  
- **test_multi_api_client.py**: MultiAPIClient (15+ tests)
  - Key rotation and load balancing
  - API fallback
  - Model normalization
  
- **test_config.py**: Configuration validation (20+ tests)
  - API key validation
  - Environment parsing
  - Security checks

### Integration Tests (`tests/integration/`)

Tests for component interactions:

- **test_processing_pipeline.py**: Complete pipeline
  - OCR → Vision AI → Parser → Tracker
  - Error handling
  - Statistics aggregation

### End-to-End Tests (`tests/e2e/`)

Full system tests (to be implemented):

- **test_full_system.py**: Complete workflow
- **test_load.py**: Performance under load
- **test_resilience.py**: Failure recovery

## 🔧 Configuration

### Environment Variables for Testing

Create a `.env.test` file:

```bash
# Test mode (uses mocks instead of real APIs)
TEST_MODE=true

# Mock API keys for testing
API_KEYS=sk-or-v1-test-key-1,sk-proj-test-key-2

# Test configuration
GATEWAY_URL=http://localhost:8000
OCR_ENABLED=true
GAME_TYPE=gta
```

### pytest.ini

Configuration is in `pytest.ini` at project root:

```ini
[pytest]
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow tests
    real_api: Tests using real API
```

## 📝 Writing Tests

### Example Unit Test

```python
import pytest
from src.brazilian_kill_parser import BrazilianKillParser

class TestKillParser:
    @pytest.fixture
    def parser(self):
        return BrazilianKillParser()
    
    def test_parse_standard_format(self, parser):
        text = "PPP player1 MATOU LLL player2 100m"
        result = parser.parse_kill_line(text)
        
        assert result is not None
        assert result['killer'] == 'player1'
        assert result['victim'] == 'player2'
```

### Using Fixtures

Common fixtures are in `conftest.py`:

```python
def test_with_mock_frame(mock_frame_base64):
    # mock_frame_base64 is automatically provided
    assert len(mock_frame_base64) > 0

def test_with_mock_kills(mock_multiple_kills):
    # mock_multiple_kills provides test kill data
    assert len(mock_multiple_kills) == 3
```

## 🎯 Test Coverage Goals

| Module | Target Coverage | Current |
|--------|----------------|---------|
| brazilian_kill_parser.py | > 90% | ✅ |
| team_tracker.py | > 90% | ✅ |
| multi_api_client.py | > 85% | ✅ |
| processor.py | > 80% | 🔄 |
| config.py | > 85% | ✅ |

## 🐛 Debugging Tests

### Run Single Test

```bash
# Run specific test file
pytest tests/unit/test_kill_parser.py -v

# Run specific test class
pytest tests/unit/test_kill_parser.py::TestBrazilianKillParser -v

# Run specific test method
pytest tests/unit/test_kill_parser.py::TestBrazilianKillParser::test_parse_standard_format -v
```

### Verbose Output

```bash
# Show print statements
pytest -s

# Very verbose
pytest -vv

# Show local variables on failure
pytest -l
```

### Debug with pdb

```python
def test_something():
    import pdb; pdb.set_trace()  # Breakpoint
    # ... test code
```

Or use pytest's built-in debugger:

```bash
pytest --pdb  # Drop into debugger on failure
```

## ⚡ Performance

### Parallel Execution

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run with 4 workers
pytest -n 4
```

### Skip Slow Tests

```bash
# Skip tests marked as slow
pytest -m "not slow"
```

## 🔄 Continuous Integration

### GitHub Actions (example)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest --cov=backend --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## 📚 Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## 🤝 Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure > 80% coverage for new code
3. Run full test suite before committing
4. Add appropriate markers (@pytest.mark.unit, etc.)

## 📞 Support

For issues or questions about tests:
- Check existing test examples in `tests/unit/`
- Review fixtures in `conftest.py`
- See implementation plan in `brain/implementation_plan.md`
