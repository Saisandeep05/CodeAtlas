import pytest
from app.services.github_service import validate_github_url, RepositoryValidationError, GithubService

def test_url_validation_safety():
    """Verify URL validation rejects file://, ftp://, ssh:// and non-github hostnames."""
    valid_urls = [
        "https://github.com/fastapi/fastapi",
        "https://github.com/psf/requests.git",
        "http://github.com/django/django"
    ]
    for url in valid_urls:
        assert validate_github_url(url) is True

    invalid_urls = [
        "file:///etc/passwd",
        "ftp://github.com/repo",
        "https://gitlab.com/owner/repo",
        "https://evil-site.com/github.com/repo",
        "javascript:alert(1)"
    ]
    for url in invalid_urls:
        with pytest.raises(RepositoryValidationError):
            validate_github_url(url)

def test_repository_file_count_limits():
    """Verify repository safety limit constants for Stage 2."""
    from config import MAX_PYTHON_FILES, MAX_FILE_SIZE_BYTES, MAX_TOTAL_SIZE_BYTES
    assert MAX_PYTHON_FILES == 800
    assert MAX_FILE_SIZE_BYTES == 3_000_000
    assert MAX_TOTAL_SIZE_BYTES == 150_000_000
