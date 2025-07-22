# Subscription System Test Suite

Comprehensive test suite for the subscription system covering all aspects from unit tests to end-to-end scenarios.

## Overview

This test suite provides complete coverage of the subscription system including:

- **Unit Tests**: Individual service and component testing
- **Integration Tests**: Service interaction and workflow testing  
- **End-to-End Tests**: Complete user journey testing
- **Performance Tests**: Load and scalability testing
- **Security Tests**: Data protection and access control testing
- **Validation Tests**: System validation and health checks

## Test Structure

```
tests/
├── unit/                           # Unit tests
│   ├── test_subscription_service.py   # SubscriptionService tests
│   └── test_payment_service.py        # PaymentService tests
├── integration/                    # Integration tests
│   ├── test_subscription_integration.py
│   ├── test_subscription_payment_integration.py
│   ├── test_webhook_integration.py
│   └── test_subscription_e2e.py
├── performance/                    # Performance tests
│   └── test_subscription_performance.py
├── security/                       # Security tests
│   └── test_subscription_security.py
├── validation/                     # Validation scripts
│   ├── validate_subscription_service.py
│   └── validate_payment_service.py
├── fixtures/                       # Test fixtures and data
│   └── subscription_fixtures.py
├── run_subscription_tests.py       # Test runner script
├── pytest.ini                     # Pytest configuration
└── README.md                      # This file
```

## Quick Start

### Run All Tests

```bash
# Run complete test suite
python tests/run_subscription_tests.py

# Run with detailed report
python tests/run_subscription_tests.py --report
```

### Run Specific Test Types

```bash
# Run only unit tests
python tests/run_subscription_tests.py --types unit unit_payment

# Run essential tests (quick validation)
python tests/run_subscription_tests.py --quick

# Run performance tests
python tests/run_subscription_tests.py --types performance

# Run security tests
python tests/run_subscription_tests.py --types security
```

### Run Individual Test Files

```bash
# Run specific test file
pytest tests/unit/test_subscription_service.py -v

# Run with coverage
pytest tests/unit/test_subscription_service.py --cov=services

# Run specific test class
pytest tests/unit/test_subscription_service.py::TestSubscriptionCRUD -v

# Run specific test method
pytest tests/unit/test_subscription_service.py::TestSubscriptionCRUD::test_create_subscription -v
```

## Test Categories

### Unit Tests

Test individual components in isolation:

- **SubscriptionService**: CRUD operations, usage limits, tracking
- **PaymentService**: Stripe integration, customer management, webhooks
- **Models**: Data validation and relationships
- **Utilities**: Helper functions and calculations

**Coverage**: 
- All public methods
- Error handling
- Edge cases
- Input validation

### Integration Tests

Test component interactions:

- **Service Integration**: SubscriptionService + PaymentService workflows
- **Database Integration**: Data persistence and consistency
- **Webhook Processing**: End-to-end webhook handling
- **API Integration**: Complete request/response cycles

**Coverage**:
- Complete user workflows
- Cross-service communication
- Data consistency
- Error propagation

### End-to-End Tests

Test complete user journeys:

- **Free to Pro Upgrade**: Complete subscription workflow
- **Payment Failures**: Error handling and recovery
- **Cancellation Flow**: Subscription termination
- **Feature Access**: Tier-based feature gating

**Coverage**:
- Real user scenarios
- API endpoint integration
- Frontend/backend communication
- Business logic validation

### Performance Tests

Test system performance and scalability:

- **Load Testing**: High concurrent usage
- **Throughput Testing**: Operations per second
- **Memory Usage**: Resource consumption
- **Database Performance**: Query optimization

**Coverage**:
- Concurrent operations
- Large datasets
- Memory efficiency
- Response times

### Security Tests

Test security measures and data protection:

- **Access Control**: User isolation and authorization
- **Input Validation**: SQL injection and XSS prevention
- **Data Protection**: Sensitive data handling
- **Payment Security**: PCI compliance measures

**Coverage**:
- Authentication/authorization
- Data privacy
- Input sanitization
- Audit trails

## Test Fixtures

The test suite includes comprehensive fixtures for different scenarios:

### User Fixtures
- `free_user`: Basic free tier user
- `pro_user`: Active Pro subscriber
- `expired_pro_user`: Expired Pro subscription
- `free_user_at_limit`: Free user at usage limit

### Scenario Fixtures
- `mixed_user_cohort`: Diverse user base for analytics
- `pro_user_heavy_usage`: High-usage Pro user
- `pro_user_with_payment_history`: User with payment records

### Usage Examples

```python
def test_subscription_upgrade(free_user, subscription_service):
    """Test upgrading free user to Pro"""
    # free_user fixture provides a ready-to-use free tier user
    result = await subscription_service.create_subscription(
        user_id=str(free_user.id),
        tier=SubscriptionTier.PRO
    )
    assert result.tier == SubscriptionTier.PRO
```

## Configuration

### Environment Variables

```bash
# Test database (optional, defaults to SQLite in-memory)
TEST_DATABASE_URL=sqlite:///./test.db

# Stripe test keys (for integration tests)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_test_...

# Test timeouts
TEST_TIMEOUT=300
PERFORMANCE_TEST_TIMEOUT=600
```

### Pytest Configuration

The `pytest.ini` file configures:
- Test discovery patterns
- Output formatting
- Timeout settings
- Async test support
- Warning filters

## Running Tests in CI/CD

### GitHub Actions Example

```yaml
name: Subscription Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run quick tests
        run: python tests/run_subscription_tests.py --quick
      
      - name: Run full test suite
        run: python tests/run_subscription_tests.py --report
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

### Docker Testing

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "tests/run_subscription_tests.py", "--report"]
```

## Test Data Management

### Database Setup
- Each test uses isolated database sessions
- Automatic cleanup after each test
- Transaction rollback for failed tests
- In-memory SQLite for speed

### Mock Data
- Stripe API calls are mocked by default
- Realistic test data via fixtures
- Configurable test scenarios
- Deterministic test outcomes

## Performance Benchmarks

### Expected Performance Metrics

| Operation | Target Time | Concurrent Users |
|-----------|-------------|------------------|
| Usage Limit Check | < 50ms | 100 |
| Usage Tracking | < 100ms | 50 |
| Subscription CRUD | < 200ms | 20 |
| Webhook Processing | < 500ms | 10 |
| Metrics Calculation | < 2s | 5 |

### Performance Test Thresholds

```python
# Example performance assertions
assert duration < 2.0, f"Operation took too long: {duration}s"
assert throughput > 50, f"Throughput too low: {throughput} ops/sec"
assert memory_increase < 100, f"Memory usage too high: {memory_increase}MB"
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database permissions
   ls -la *.db
   # Reset test database
   rm test_*.db
   ```

2. **Async Test Failures**
   ```bash
   # Install required packages
   pip install pytest-asyncio
   # Check asyncio mode in pytest.ini
   ```

3. **Import Errors**
   ```bash
   # Add backend to Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
   ```

4. **Stripe Mock Failures**
   ```bash
   # Verify mock patches in test files
   # Check stripe package version compatibility
   ```

### Debug Mode

```bash
# Run tests with debug output
pytest tests/unit/test_subscription_service.py -v -s --tb=long

# Run single test with debugging
pytest tests/unit/test_subscription_service.py::test_create_subscription -v -s --pdb
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=services --cov=models --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Contributing

### Adding New Tests

1. **Choose appropriate test category** (unit/integration/e2e/performance/security)
2. **Follow naming conventions** (`test_*.py`, `Test*` classes, `test_*` methods)
3. **Use existing fixtures** when possible
4. **Add performance assertions** for new operations
5. **Include security considerations** for sensitive operations

### Test Guidelines

- **Isolation**: Each test should be independent
- **Clarity**: Test names should describe the scenario
- **Coverage**: Test both success and failure cases
- **Performance**: Include timing assertions
- **Security**: Validate access control and data protection

### Code Review Checklist

- [ ] Tests cover new functionality
- [ ] Performance benchmarks included
- [ ] Security implications considered
- [ ] Error cases handled
- [ ] Documentation updated
- [ ] CI/CD pipeline passes

## Support

For questions or issues with the test suite:

1. Check this README for common solutions
2. Review test output and error messages
3. Check existing test implementations for examples
4. Consult the main application documentation

## Test Results Interpretation

### Success Criteria
- All test suites pass (100% success rate)
- Performance benchmarks met
- Security tests pass
- No memory leaks detected

### Failure Analysis
- Review failed test output
- Check performance metrics
- Validate security measures
- Examine error logs

### Reporting
- Automated reports generated with `--report` flag
- Detailed failure analysis included
- Performance metrics tracked
- Recommendations provided

The test suite is designed to provide confidence in the subscription system's reliability, performance, and security before production deployment.