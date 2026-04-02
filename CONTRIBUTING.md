# Contributing to ACEest Fitness API

Thank you for your interest in contributing to the ACEest Fitness API project! This document provides guidelines and instructions for contributing.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

---

## Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inspiring community for all. Please read and adhere to our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get oriented
- Focus on constructive feedback
- Report unacceptable behavior to project maintainers

---

## Getting Started

### Prerequisites
- Python 3.8+
- Git
- Docker (recommended)
- GitHub account

### Fork and Clone
```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/your-username/aceest-fitness.git
cd aceest-fitness

# Add upstream remote
git remote add upstream https://github.com/original-org/aceest-fitness.git

# Verify remotes
git remote -v
```

### Set Up Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install black flake8 pylint pytest pytest-cov

# Verify setup
python app.py
```

---

## Development Workflow

### Create Feature Branch
```bash
# Update main
git checkout main
git pull upstream main

# Create feature branch from develop
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b bugfix/issue-number

# Or for documentation
git checkout -b docs/description
```

### Branch Naming Convention
- `feature/lowercase-with-dashes` - New features
- `bugfix/issue-number-description` - Bug fixes
- `hotfix/priority-issue` - Critical fixes
- `docs/description` - Documentation updates
- `refactor/area-of-change` - Code refactoring
- `test/description` - Test additions

### Keep Branch Updated
```bash
# Fetch latest from upstream
git fetch upstream

# Rebase on upstream/develop
git rebase upstream/develop

# If conflicts, resolve them
# Then continue rebase
git rebase --continue
```

---

## Coding Standards

### Python Style Guide
We follow PEP 8 with these conventions:

```python
# Imports
import os
import sys
from datetime import datetime

# Constants
DATABASE_NAME = "aceest.db"
MAX_CONNECTIONS = 100

# Functions
def process_client_data(client_id):
    """Process client data and return result.
    
    Args:
        client_id: Integer ID of client
        
    Returns:
        dict: Processed client data
        
    Raises:
        ValueError: If client_id is invalid
    """
    if not isinstance(client_id, int):
        raise ValueError("client_id must be an integer")
    
    return {}

# Classes
class ClientManager:
    """Manages client operations."""
    
    def __init__(self):
        self.clients = []
    
    def add_client(self, client):
        """Add client to manager."""
        self.clients.append(client)
```

### Code Quality Tools

#### Format Code with Black
```bash
black app.py tests/
```

#### Lint with Flake8
```bash
flake8 app.py --max-line-length=100
```

#### Check with Pylint
```bash
pylint app.py --disable=all --enable=E,F
```

#### Type Checking
```bash
# For type hints (if used)
mypy app.py
```

---

## Testing Requirements

### Write Tests for All Changes
```python
# tests/test_new_feature.py
import pytest

def test_new_feature_success(client, headers):
    """Test new feature works correctly."""
    response = client.post('/api/endpoint',
        json={'field': 'value'},
        headers=headers
    )
    assert response.status_code == 200

def test_new_feature_validation(client, headers):
    """Test input validation."""
    response = client.post('/api/endpoint',
        json={'field': ''},
        headers=headers
    )
    assert response.status_code == 400
```

### Run Tests Locally
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_app.py -v

# Run specific test
pytest tests/test_app.py::TestAuthenticationEndpoint::test_login_success -v

# Run with markers
pytest -m integration tests/
```

### Coverage Requirements
- Minimum 80% code coverage required
- All new code must have tests
- Critical paths must have tests

---

## Commit Guidelines

### Commit Message Format
```
type(scope): subject

body

footer
```

### Types
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect code meaning
- `refactor`: Code change that neither fixes a bug nor adds feature
- `perf`: Code change that improves performance
- `test`: Adding or updating tests
- `chore`: Changes to build process, dependencies, etc.

### Examples
```
feat(clients): add client status filtering

Allow clients to filter by membership status. Users can now
call GET /api/clients?status=Active to get active members only.

Closes #123
```

```
fix(auth): resolve token validation bug

The token validation was failing with tokens containing
special characters in the role field.

Fixes #456
```

```
docs: update API documentation

Add missing endpoint descriptions and examples for
the new metrics endpoint.
```

### Commit Best Practices
- One logical change per commit
- Write clear, descriptive messages
- Reference related issues
- Test before committing
- Use present tense ("add feature" not "added feature")

---

## Pull Request Process

### Before Creating PR
1. Update your branch: `git pull upstream develop`
2. Run all tests: `pytest tests/`
3. Run linting: `flake8 app.py`
4. Format code: `black app.py`
5. Create test coverage report

### Create Pull Request
```bash
# Push to your fork
git push origin feature/your-feature

# Go to GitHub and create PR
# - Title: concise description
# - Description: explain changes, file structure updates, breaking changes
# - Reference issues: "Closes #123"
```

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Changes Made
- Change 1
- Change 2

## Testing
- [ ] Added/updated unit tests
- [ ] All tests pass
- [ ] Coverage maintained at 80%+

## Checklist
- [ ] Code follows style guide
- [ ] Self-reviewed code
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings
```

### PR Review Process
1. Code review by maintainers
2. Tests must pass in CI/CD
3. Coverage must be maintained
4. No conflicts with base branch
5. Approval by 2+ maintainers

### Merge Requirements
- All checks passed (CI/CD, tests, linting)
- At least 2 approvals
- Discussion resolved
- Branch up to date

---

## Issue Reporting

### Bug Report Template
```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happened

## Environment
- Python version: 3.11
- OS: Windows/macOS/Linux
- Docker: Yes/No

## Screenshots
If applicable

## Logs
Error logs or stack traces
```

### Feature Request Template
```markdown
## Description
Clear description of the feature

## Use Case
Why is this needed?

## Proposed Solution
How should this be implemented?

## Alternatives Considered
Other approaches considered

## Additional Context
Any other information
```

---

## Development Commands

```bash
# Install development dependencies
pip install -r requirements.txt

# Format code
black app.py tests/

# Lint code
flake8 app.py tests/

# Run tests
pytest tests/ -v

# Generate coverage report
pytest --cov=app --cov-report=html tests/

# Build Docker image
docker build -t aceest:dev .

# Run Docker container
docker run -p 5000:5000 aceest:dev

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f aceest-api

# Run app locally
python app.py
```

---

## Questions or Need Help?

- Open an issue for questions
- Check existing issues and discussions
- Join our community chat
- Contact maintainers

---

## Recognition

Contributors will be recognized in:
- README.md contributors list
- Release notes
- GitHub contributors page

---

## License
By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing! 🎉
