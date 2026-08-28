import pytest
import os
import shutil
import tempfile
from fastapi.testclient import TestClient
from app.main import app
from app.services.github_service import GithubService, RepositoryValidationError
from app.middleware.rate_limiter import global_rate_limiter

client = TestClient(app)

def test_url_validation_strict_safety():
    service = GithubService()

    valid_urls = [
        "https://github.com/fastapi/fastapi",
        "https://github.com/psf/requests.git",
        "https://github.com/pallets/flask"
    ]
    for url in valid_urls:
        user, repo = service.validate_url(url)
        assert user != ""
        assert repo != ""

    invalid_urls = [
        "file:///etc/passwd",
        "ftp://github.com/repo",
        "git@github.com:user/repo.git",
        "https://user:pass@github.com/user/repo",
        "https://evil-site.com/github.com/repo",
        "https://github.com/user/repo; rm -rf /",
        "https://github.com/user/repo | cat /etc/passwd"
    ]
    for url in invalid_urls:
        with pytest.raises(RepositoryValidationError):
            service.validate_url(url)

def test_cleanup_guarantee_on_failure():
    service = GithubService()
    temp_dir = tempfile.mkdtemp(prefix="test_codeatlas_cleanup_")

    try:
        dummy_repo_dir = os.path.join(temp_dir, "codeatlas_dummy_hash")
        os.makedirs(dummy_repo_dir, exist_ok=True)
        assert os.path.exists(dummy_repo_dir)

        # Trigger cleanup
        service.cleanup(dummy_repo_dir)
        assert not os.path.exists(dummy_repo_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_rate_limiting_middleware():
    global_rate_limiter.client_records.clear()
    test_ip = "192.168.1.100"

    # Make 10 allowed requests
    for i in range(10):
        allowed, _ = global_rate_limiter.is_allowed(test_ip)
        assert allowed is True

    # 11th request should be blocked
    allowed, retry_after = global_rate_limiter.is_allowed(test_ip)
    assert allowed is False
    assert retry_after > 0
