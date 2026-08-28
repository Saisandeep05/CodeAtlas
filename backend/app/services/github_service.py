import os
import shutil
import tempfile
import urllib.request
import urllib.error
import zipfile
import json
import logging
import socket
import re
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from config import (
    ALLOWED_HOSTS,
    MAX_PYTHON_FILES,
    MAX_FILE_SIZE_BYTES,
    MAX_TOTAL_SIZE_BYTES,
    CLONE_TIMEOUT_SECONDS,
    SKIP_DIRECTORIES,
)

logger = logging.getLogger("codeatlas")

class RepositoryValidationError(Exception):
    """Raised when a repository fails validation checks."""
    pass

def validate_github_url(repo_url: str) -> bool:
    service = GithubService()
    service.validate_url(repo_url)
    return True

class GithubService:
    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or tempfile.gettempdir()

    def validate_url(self, repo_url: str) -> Tuple[str, str]:
        if not repo_url or not isinstance(repo_url, str):
            raise RepositoryValidationError("Repository URL must be a non-empty string.")

        # Check for command injection characters
        forbidden_chars = [";", "&", "|", "`", "$", "\n", "\r", "<", ">"]
        for char in forbidden_chars:
            if char in repo_url:
                raise RepositoryValidationError(f"Invalid characters in repository URL.")

        try:
            parsed = urlparse(repo_url.rstrip("/"))
        except Exception:
            raise RepositoryValidationError(f"Invalid URL format: {repo_url}")

        if parsed.scheme not in ["http", "https"]:
            raise RepositoryValidationError("Only GitHub repositories are supported.")

        if parsed.username or parsed.password:
            raise RepositoryValidationError("URLs with embedded user credentials are not allowed.")

        if parsed.hostname not in ALLOWED_HOSTS:
            raise RepositoryValidationError(
                f"Only GitHub repositories are supported. "
                f"Got hostname: {parsed.hostname}"
            )

        path_parts = [p for p in parsed.path.strip("/").split("/") if p]
        if len(path_parts) < 2:
            raise RepositoryValidationError(
                f"URL must be in format https://github.com/user/repo. "
                f"Got: {repo_url}"
            )

        user = path_parts[0]
        repo = path_parts[1]
        if repo.endswith(".git"):
            repo = repo[:-4]

        # Valid github username and repo name characters
        valid_name_pattern = re.compile(r'^[a-zA-Z0-9_\-\.]+$')
        if not valid_name_pattern.match(user) or not valid_name_pattern.match(repo):
            raise RepositoryValidationError("Repository user or name contains invalid characters.")

        return user, repo

    def get_latest_commit_hash(self, repo_url: str) -> str:
        user, repo = self.validate_url(repo_url)
        api_url = f"https://api.github.com/repos/{user}/{repo}/commits?per_page=1"
        try:
            req = urllib.request.Request(api_url, headers={'User-Agent': 'CodeAtlas'})
            with urllib.request.urlopen(req, timeout=CLONE_TIMEOUT_SECONDS) as response:
                data = json.loads(response.read().decode())
                if data and isinstance(data, list):
                    return data[0]['sha']
        except Exception as e:
            logger.warning(f"Failed to fetch commit hash: {e}")
        return "unknown_hash"

    def clone_repo(self, repo_url: str) -> Tuple[str, str]:
        user, repo_name = self.validate_url(repo_url)
        commit_hash = self.get_latest_commit_hash(repo_url)

        target_dir = os.path.join(self.temp_dir, f"codeatlas_{repo_name}_{commit_hash}")

        if os.path.exists(target_dir):
            shutil.rmtree(target_dir, ignore_errors=True)

        os.makedirs(target_dir, exist_ok=True)

        zip_url = f"https://github.com/{user}/{repo_name}/archive/refs/heads/main.zip"
        zip_path = os.path.join(self.temp_dir, f"{repo_name}_{commit_hash}.zip")

        logger.info(f"Downloading {zip_url} into {target_dir}...")
        try:
            req = urllib.request.Request(zip_url, headers={'User-Agent': 'CodeAtlas'})
            with urllib.request.urlopen(req, timeout=CLONE_TIMEOUT_SECONDS) as response, open(zip_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        except urllib.error.HTTPError:
            zip_url = f"https://github.com/{user}/{repo_name}/archive/refs/heads/master.zip"
            try:
                req = urllib.request.Request(zip_url, headers={'User-Agent': 'CodeAtlas'})
                with urllib.request.urlopen(req, timeout=CLONE_TIMEOUT_SECONDS) as response, open(zip_path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            except Exception as e:
                raise RepositoryValidationError(f"Failed to download repository: {e}")
        except (TimeoutError, socket.timeout):
            raise RepositoryValidationError(f"Repository download timed out after {CLONE_TIMEOUT_SECONDS} seconds.")
        except Exception as e:
            raise RepositoryValidationError(f"Failed to download repository: {e}")

        # Check zip size
        if os.path.exists(zip_path):
            zip_size = os.path.getsize(zip_path)
            if zip_size > MAX_TOTAL_SIZE_BYTES:
                os.remove(zip_path)
                raise RepositoryValidationError(
                    f"Repository exceeds maximum total size of {MAX_TOTAL_SIZE_BYTES // 1_000_000} MB."
                )

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                total_uncompressed = sum(file.file_size for file in zip_ref.infolist())
                if total_uncompressed > MAX_TOTAL_SIZE_BYTES:
                    raise RepositoryValidationError(
                        f"Repository exceeds maximum uncompressed size of {MAX_TOTAL_SIZE_BYTES // 1_000_000} MB."
                    )
                zip_ref.extractall(target_dir)
        finally:
            if os.path.exists(zip_path):
                os.remove(zip_path)

        extracted_folders = os.listdir(target_dir)
        if len(extracted_folders) == 1:
            return os.path.join(target_dir, extracted_folders[0]), commit_hash

        return target_dir, commit_hash

    def get_python_files(self, repo_path: str) -> List[str]:
        py_files = []
        total_size = 0

        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [
                d for d in dirs
                if not d.startswith('.') and d not in SKIP_DIRECTORIES
            ]

            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(root, file)

                try:
                    file_size = os.path.getsize(file_path)
                except OSError:
                    continue

                if file_size > MAX_FILE_SIZE_BYTES:
                    logger.warning(f"Skipping oversized file ({file_size} bytes): {file_path}")
                    continue

                total_size += file_size
                if total_size > MAX_TOTAL_SIZE_BYTES:
                    raise RepositoryValidationError(
                        f"Repository exceeds maximum total Python code size of {MAX_TOTAL_SIZE_BYTES // 1_000_000} MB."
                    )

                py_files.append(file_path)

                if len(py_files) > MAX_PYTHON_FILES:
                    raise RepositoryValidationError(
                        f"Repository exceeds maximum of {MAX_PYTHON_FILES} Python files."
                    )

        return py_files

    def cleanup(self, repo_path: str):
        if os.path.exists(repo_path):
            try:
                parent = os.path.dirname(repo_path)
                if os.path.basename(parent).startswith("codeatlas_"):
                    shutil.rmtree(parent, ignore_errors=True)
                else:
                    shutil.rmtree(repo_path, ignore_errors=True)
            except Exception:
                pass
