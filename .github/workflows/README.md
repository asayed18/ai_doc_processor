# GitHub Workflows

This directory contains GitHub Actions workflows for continuous integration, testing, and deployment of the AI Document Processor application.

## Available Workflows

### 🚀 Main CI Pipeline (`ci.yml`)

**Triggers:** Push to `main`/`develop`, Pull Requests

**Purpose:** Primary CI pipeline that runs on every push and PR.

**Jobs:**
- **backend-tests**: Runs integration tests with mocked Anthropic API
- **frontend-tests**: Builds and lints the Next.js frontend  
- **code-quality**: Checks code formatting and import sorting
- **security-scan**: Scans for vulnerabilities with Trivy

**Key Features:**
- ✅ Uses PostgreSQL service for database tests
- ✅ Mocks Anthropic API calls (no real API usage)
- ✅ Caches dependencies for faster builds
- ✅ Generates SARIF security reports

### 🧪 Full Test Suite (`full-test-suite.yml`)

**Triggers:** Weekly schedule (Sundays 2 AM UTC), Manual dispatch

**Purpose:** Comprehensive testing including slow/performance tests.

**Jobs:**
- **comprehensive-tests**: All tests including coverage reports
- **performance-tests**: Load and performance testing

**Key Features:**
- ✅ Code coverage reporting with Codecov
- ✅ Optional slow test inclusion
- ✅ Detailed test artifacts and reports

### 🌐 Cross-Platform Tests (`cross-platform.yml`)

**Triggers:** Push to `main`, Pull Requests

**Purpose:** Tests compatibility across different operating systems and Python versions.

**Matrix Testing:**
- **OS**: Ubuntu, Windows, macOS
- **Python**: 3.11, 3.12

**Key Features:**
- ✅ SQLite fallback for simpler database setup
- ✅ OS-specific environment file creation
- ✅ Core functionality verification across platforms

### 🏷️ Release Pipeline (`release.yml`)

**Triggers:** Version tags (`v*`), Manual dispatch

**Purpose:** Automated release process with full validation.

**Jobs:**
- **test-before-release**: Final test verification
- **build-and-test-docker**: Docker image building and testing
- **create-release**: GitHub release creation with changelog

**Key Features:**
- ✅ Automated changelog generation
- ✅ Docker health checks
- ✅ Release notes with test status

### 🔍 Code Quality (`code-quality.yml`)

**Triggers:** Push to `main`/`develop`, Pull Requests

**Purpose:** Code quality, formatting, and style checks.

**Jobs:**
- **linting-and-formatting**: Python code style checks (Black, isort, flake8)
- **frontend-linting**: TypeScript/React linting and compilation
- **test-quality**: Test coverage analysis
- **dependency-check**: Security and dependency audits

## Test Environment Configuration

All workflows use consistent test environment configuration:

```env
ENVIRONMENT=test
DEBUG=true
APP_NAME="AI Document Processor Test"
DATABASE_URL=postgresql://testuser:testpassword@localhost:5432/testdb
ANTHROPIC_API_KEY=test_key_not_used  # ← Mocked, never hits real API
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=application/pdf,text/plain
```

## Mock Service Integration

🎯 **Key Feature**: All workflows use the MockAIService instead of real Anthropic API calls:

- ✅ No API costs in CI/CD
- ✅ Predictable test results  
- ✅ No rate limiting issues
- ✅ Tests run in isolated environments
- ✅ Verifiable through `tests/test_debug.py`

## Security Features

- 🔒 **Trivy scanning** for vulnerabilities
- 🔒 **Dependency auditing** with pipenv check
- 🔒 **SARIF reports** uploaded to GitHub Security tab
- 🔒 **No sensitive data** in test environments

## Performance Optimizations

- ⚡ **Dependency caching** for faster builds
- ⚡ **Parallel job execution** where possible
- ⚡ **Fail-fast strategies** for quick feedback
- ⚡ **Selective test execution** based on triggers

## Monitoring and Reporting

- 📊 **Coverage reports** with Codecov integration
- 📊 **Test artifacts** preserved for investigation
- 📊 **Step summaries** with test results
- 📊 **Release notes** with automatic changelog

## Usage Examples

### Running Tests Locally (Same as CI)

```bash
# Backend tests (same as CI)
cd backend
pipenv install --dev
pipenv run pytest -m "not slow" --tb=short -v

# Verify mock service (same as CI debug check)
pipenv run pytest tests/test_debug.py -v
```

### Manual Release Trigger

1. Go to Actions → Release workflow
2. Click "Run workflow"
3. Enter version (e.g., `v1.2.3`)
4. All tests run before release creation

### Monitoring Workflow Status

- ✅ **Green checkmarks**: All tests passing with mocked API
- ❌ **Red X marks**: Check logs for specific failures
- 🟡 **Yellow circles**: Workflows in progress

## Troubleshooting

### Common Issues

1. **Database connection failures**: Check PostgreSQL service status
2. **Mock service not working**: Verify `tests/test_debug.py` passes
3. **Dependency cache issues**: Clear cache in workflow settings

### Debug Commands

```bash
# Verify mock service is being used
pipenv run pytest tests/test_debug.py -v -s

# Check test environment
pipenv run python -c "from app.core.config import settings; print(settings.environment)"

# Verify no real API calls
grep -r "claude-3" tests/ || echo "No real API references in tests"
```

This CI/CD setup ensures reliable, fast, and cost-effective testing of the AI Document Processor while maintaining high code quality standards.