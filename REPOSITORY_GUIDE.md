# Repository Structure Guide

## Files to Commit ✅

### Core Package
- `cyberark_ccp/` - Main package source code
  - `__init__.py`
  - `client.py`
  - `exceptions.py` 
  - `py.typed`

### Configuration
- `pyproject.toml` - Modern Python packaging configuration
- `setup.py` - Setuptools configuration
- `tox.ini` - Multi-environment testing
- `MANIFEST.in` - Package inclusion rules

### Documentation
- `README.md` - Main documentation and usage guide
- `CHANGELOG.md` - Version history and changes
- `LICENSE` - MIT license
- `docs/` - Comprehensive documentation
  - `index.md`
  - `quick-start.md`
  - `configuration.md`
  - `testing.md`
  - `release-process.md`
  - `examples/` - Code examples

### Tests
- `test/` - Complete test suite
  - `test_client.py`
  - `test_exceptions.py`
  - `test_integration.py`
  - `test_api_compliance.py`
  - `requirements.txt`

### CI/CD
- `.github/workflows/` - GitHub Actions
  - `ci.yml` - Continuous integration
  - `release.yml` - Automated releases
  - `publish-test.yml` - TestPyPI publishing

### Project Files
- `.gitignore` - Git ignore rules
- `CLAUDE.md` - Claude Code configuration
- `CyberarkCCPRESTAPI.md` - API specification reference

## Files to NOT Commit ❌

### Build Artifacts
- `build/` - Build output directory
- `dist/` - Distribution packages
- `*.egg-info/` - Package metadata
- `wheels/` - Built wheel files
- `*.whl` - Wheel distribution files
- `*.tar.gz` - Source distribution files

### Python Cache
- `__pycache__/` - Python bytecode cache
- `*.pyc` - Compiled Python files
- `*.pyo` - Optimized Python files
- `*.pyd` - Python extension modules

### Testing Artifacts
- `.tox/` - Tox virtual environments
- `.pytest_cache/` - Pytest cache
- `.coverage` - Coverage data files
- `htmlcov/` - Coverage HTML reports
- `coverage.xml` - Coverage XML reports
- `.hypothesis/` - Hypothesis test data

### Development Environment
- `.conda/` - Conda environment
- `.venv/` - Virtual environment
- `venv/` - Virtual environment
- `env/` - Virtual environment
- `.env` - Environment variables
- `.python-version` - Python version file

### IDE Files
- `.vscode/` - VS Code settings
- `.idea/` - PyCharm/IntelliJ settings
- `*.sublime-project` - Sublime Text projects
- `*.sublime-workspace` - Sublime Text workspaces

### Operating System Files
- `.DS_Store` - macOS folder attributes
- `Thumbs.db` - Windows thumbnail cache
- `*.swp` - Vim swap files
- `*~` - Backup files

### Security Sensitive
- `*.pem` - Certificate files
- `*.key` - Private key files
- `*.p12` - PKCS#12 certificate files
- `secrets.json` - Secret configuration
- `.credentials` - Credential files

### Temporary Files
- `*.tmp` - Temporary files
- `*.temp` - Temporary files
- `*.log` - Log files
- `*.bak` - Backup files

## Pre-Commit Checklist

Before pushing to GitHub, ensure:

1. ✅ All tests pass: `pytest test/`
2. ✅ Code is formatted: `black cyberark_ccp test/`
3. ✅ Imports are sorted: `isort cyberark_ccp test/`
4. ✅ Linting passes: `flake8 cyberark_ccp test/`
5. ✅ Type checking passes: `mypy cyberark_ccp`
6. ✅ No sensitive files staged: `git status`
7. ✅ Build artifacts cleaned: `rm -rf build/ dist/ *.egg-info/`

## Git Commands for Clean Repository

```bash
# Check what will be committed
git status

# See ignored files (should include build artifacts)
git status --ignored

# Add only source files (not build artifacts)
git add cyberark_ccp/ test/ docs/ *.md *.toml *.py *.ini *.in LICENSE .github/ .gitignore

# Clean up any accidentally tracked files
git rm --cached -r build/ dist/ *.egg-info/ __pycache__/ .tox/ .pytest_cache/ || true

# Commit with descriptive message
git commit -m "Initial release: CyberArk CCP Python client v1.0.0"

# Push to GitHub
git push origin main
```

## Repository Size Optimization

The .gitignore configuration ensures:
- No binary build artifacts
- No cached Python bytecode
- No development environment files
- No IDE-specific configurations
- No temporary or log files
- No security-sensitive files

This keeps the repository clean, secure, and minimal while preserving all necessary source code and documentation.