# Release Process Guide

This guide explains how to create and publish releases of the CyberArk CCP Python client.

## Prerequisites

Before creating a release, ensure you have:

1. **PyPI Account**: Access to the PyPI project with publishing permissions
2. **GitHub Permissions**: Write access to the repository
3. **API Tokens**: 
   - PyPI API token stored in `PYPI_API_TOKEN` GitHub secret
   - TestPyPI API token stored in `TEST_PYPI_API_TOKEN` GitHub secret

## Setting Up API Tokens

### PyPI API Token

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Create a new API token with scope for the `cyberark-ccp` project
3. Add the token to GitHub repository secrets as `PYPI_API_TOKEN`

### TestPyPI API Token

1. Go to [TestPyPI Account Settings](https://test.pypi.org/manage/account/)
2. Create a new API token
3. Add the token to GitHub repository secrets as `TEST_PYPI_API_TOKEN`

## Release Workflow

### 1. Development and Testing

```bash
# Ensure all tests pass
pytest test/

# Run full test suite with tox
tox

# Check code quality
tox -e lint
tox -e typecheck

# Verify package builds correctly
tox -e build
```

### 2. Version Management

Update version numbers in:
- `pyproject.toml`
- `setup.py`
- `cyberark_ccp/__init__.py` (if version is exported)

### 3. Update Documentation

- Update `CHANGELOG.md` with new features, fixes, and breaking changes
- Review and update `README.md` if needed
- Update documentation in `docs/` directory

### 4. Create Release Commit

```bash
git add .
git commit -m "Release v1.0.0"
git push origin main
```

### 5. Create and Push Tag

```bash
# Create tag
git tag -a v1.0.0 -m "Release v1.0.0"

# Push tag to trigger release workflow
git push origin v1.0.0
```

### 6. Monitor Release Process

The release workflow will automatically:
1. Run full test suite across all supported Python versions
2. Build the package
3. Publish to PyPI
4. Create GitHub release with artifacts

## Automated Workflows

### CI Workflow (`.github/workflows/ci.yml`)

Runs on every push and pull request:
- Tests across Python 3.7-3.12
- Code quality checks (flake8, black, isort, mypy)
- Security scanning (safety, bandit)
- Coverage reporting
- Package building and validation

### Release Workflow (`.github/workflows/release.yml`)

Triggered by version tags (v*):
- Full test suite
- Package building
- PyPI publication
- GitHub release creation

### TestPyPI Workflow (`.github/workflows/publish-test.yml`)

Runs on main branch changes:
- Publishes to TestPyPI for testing
- Can be manually triggered

## Manual Release Process

If automated workflows fail, you can release manually:

### 1. Build Package

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*
```

### 2. Test Upload to TestPyPI

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ cyberark-ccp
```

### 3. Upload to PyPI

```bash
# Upload to production PyPI
twine upload dist/*
```

### 4. Create GitHub Release

1. Go to [GitHub Releases](https://github.com/Tech-Daddy-Digital/CyberarkCCP/releases)
2. Click "Create a new release"
3. Select the version tag
4. Add release notes from CHANGELOG.md
5. Attach build artifacts if needed

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (x.0.0): Breaking changes
- **MINOR** (x.y.0): New features, backward compatible
- **PATCH** (x.y.z): Bug fixes, backward compatible

Examples:
- `1.0.0`: Initial stable release
- `1.1.0`: New features added
- `1.1.1`: Bug fixes
- `2.0.0`: Breaking changes

## Pre-release Versions

For testing purposes, use pre-release identifiers:
- `1.0.0a1`: Alpha release
- `1.0.0b1`: Beta release
- `1.0.0rc1`: Release candidate

## Hotfix Process

For critical bugs in production:

1. Create hotfix branch from the release tag:
   ```bash
   git checkout -b hotfix/1.0.1 v1.0.0
   ```

2. Make necessary fixes
3. Update version to patch level (1.0.1)
4. Create and test the fix
5. Create new tag and release

## Rollback Process

If a release has critical issues:

### 1. Remove from PyPI
- Contact PyPI support if needed (releases cannot be deleted)
- Mark release as yanked to prevent new installations

### 2. Communicate Issue
- Update GitHub release with warning
- Post issue in repository
- Notify users through appropriate channels

### 3. Prepare Fix
- Create hotfix with fix
- Release new version as soon as possible

## Release Checklist

### Pre-Release
- [ ] All tests pass locally and in CI
- [ ] Code quality checks pass
- [ ] Documentation is updated
- [ ] Version numbers are updated
- [ ] CHANGELOG.md is updated
- [ ] Security scan passes

### Release
- [ ] Tag is created and pushed
- [ ] GitHub Actions workflow succeeds
- [ ] Package is available on PyPI
- [ ] GitHub release is created

### Post-Release
- [ ] Installation from PyPI works
- [ ] Documentation is accessible
- [ ] Release is announced (if applicable)
- [ ] Issues/questions are monitored

## Troubleshooting

### Common Issues

**Build Failures:**
- Check dependencies in pyproject.toml
- Verify Python version compatibility
- Review build logs in GitHub Actions

**Upload Failures:**
- Verify API tokens are correct
- Check package name conflicts
- Ensure version number is unique

**Test Failures:**
- Run tests locally with same Python version
- Check for environment-specific issues
- Review test coverage reports

### Getting Help

- [GitHub Issues](https://github.com/Tech-Daddy-Digital/CyberarkCCP/issues) for build problems
- PyPI support for publication issues
- Team members for process questions

## Security Considerations

- Never commit API tokens or credentials
- Use GitHub secrets for sensitive data
- Regularly rotate API tokens
- Monitor release workflow permissions
- Review security scan results before release