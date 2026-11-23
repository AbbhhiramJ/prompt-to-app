"""Opt-in GitHub -> Vercel preview deployment adapter.

This module performs remote API operations only. It NEVER runs generated code,
uses provider credentials only in the trusted host, and publishes privately
to GitHub before requesting a Vercel preview build.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from base64 import b64encode
import json
import os
import re
import time
from typing import Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen

from .factory import FactoryCapabilities
from .workflow import validate_generated_files

GH = "https://api.github.com"
VERCEL = "https://api.vercel.com"
REPO_URL = re.compile(r"^https://github\.com/([A-Za-z0-9-]+)/([A-Za-z0-9_.-]+)$")
SHA = re.compile(r"^[a-f0-9]{40}$", re.I)


class ProviderError(RuntimeError):
    """An external provider failed, without exposing remote response contents."""


class JsonTransport:
    """Bounded HTTPS JSON requests, preserving token confidentiality."""

    def request(self, method: str, url: str, token: str, payload: object | None = None) -> dict:
        if not url.startswith((GH + "/", VERCEL + "/")):
            raise ProviderError("Unapproved provider endpoint")
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {
            "Authorization": "Bearer " + token,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "prompt-to-app-host",
        }
        req = Request(url, data=data, method=method, headers=headers)
        try:
            with urlopen(req, timeout=20) as response:
                raw = response.read(5_000_001)
            if len(raw) > 5_000_000:
                raise ProviderError("Provider response exceeded size limit")
            result = json.loads(raw)
            if not isinstance(result, dict):
                raise ProviderError("Unexpected provider response")
            return result
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            raise ProviderError("Provider API request failed") from None

    def probe(self, url: str) -> bool:
        host = urlparse(url).hostname or ""
        if host != "vercel.app" and not host.endswith(".vercel.app"):
            return False
        if not url.startswith("https://"):
            return False
        try:
            with urlopen(Request(url, method="GET"), timeout=10) as response:
                destination = urlparse(response.geturl())
                final_host = destination.hostname or ""
                return (
                    response.status == 200
                    and destination.scheme == "https"
                    and (final_host == "vercel.app" or final_host.endswith(".vercel.app"))
                )
        except (HTTPError, URLError, TimeoutError):
            return False


def slugify(name: str) -> str:
    candidate = re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")
    candidate = re.sub(r"-+", "-", candidate)
    if not candidate or len(candidate) > 60:
        raise ValueError("Invalid or overly long project name")
    return candidate


@dataclass
class GitHubVercelAdapter:
    github_token: str
    vercel_token: str
    team_id: str | None = None
    transport: JsonTransport = field(default_factory=JsonTransport)
    verify_attempts: int = 40
    verify_interval_seconds: float = 3.0
    _deployments: dict[str, str] = field(default_factory=dict, init=False)

    @classmethod
    def from_environment(cls) -> "GitHubVercelAdapter":
        # External writes are explicitly disabled by default.
        if os.getenv("PROMPT_TO_APP_ENABLE_PUBLISH", "") != "yes":
            raise ProviderError("Remote publishing is disabled")
        github_token = os.environ.get("GITHUB_TOKEN", "")
        vercel_token = os.environ.get("VERCEL_TOKEN", "")
        if not github_token or not vercel_token:
            raise ProviderError("Provider credentials are missing")
        return cls(github_token, vercel_token, team_id=os.getenv("VERCEL_TEAM_ID"))

    def _vercel(self, method: str, path: str, payload: object | None = None) -> dict:
        query = "?" + urlencode({"teamId": self.team_id}) if self.team_id else ""
        return self.transport.request(method, VERCEL + path + query, self.vercel_token, payload)

    def _github(self, method: str, path: str, payload: object | None = None) -> dict:
        return self.transport.request(method, GH + path, self.github_token, payload)

    @staticmethod
    def _repo_parts(repo_url: str) -> tuple[str, str]:
        matched = REPO_URL.fullmatch(repo_url)
        if not matched:
            raise ProviderError("Unexpected GitHub repository URL")
        return matched.group(1), matched.group(2)

    def create_repository(self, name: str, description: str) -> str:
        response = self._github("POST", "/user/repos", {
            "name": slugify(name), "description": description[:200],
            "private": True, "auto_init": True, "has_wiki": False,
        })
        url = response.get("html_url")
        if not isinstance(url, str):
            raise ProviderError("GitHub repository URL missing")
        self._repo_parts(url)
        if response.get("private") is not True:
            raise ProviderError("Repository was not created as private")
        return url

    def write_repository(self, repo_url: str, files: Mapping[str, str], message: str) -> str:
        errors = validate_generated_files(files)
        if errors or not files:
            raise ProviderError("Generated files failed publishing safety checks")
        owner, repo = self._repo_parts(repo_url)
        prefix = "/repos/" + quote(owner) + "/" + quote(repo)
        metadata = self._github("GET", prefix)
        if metadata.get("private") is not True:
            raise ProviderError("Refusing to write a public repository")
        branch = metadata.get("default_branch")
        if not isinstance(branch, str) or not branch or "/" in branch:
            raise ProviderError("Unexpected default branch")
        branch_path = quote(branch, safe="")
        base_ref = self._github("GET", prefix + "/git/ref/heads/" + branch_path)
        old_sha = base_ref.get("object", {}).get("sha")
        if not isinstance(old_sha, str) or not SHA.fullmatch(old_sha):
            raise ProviderError("GitHub branch commit missing")
        old_commit = self._github("GET", prefix + "/git/commits/" + old_sha)
        old_tree = old_commit.get("tree", {}).get("sha")
        if not isinstance(old_tree, str) or not SHA.fullmatch(old_tree):
            raise ProviderError("GitHub base tree missing")

        tree_entries = []
        for path, contents in sorted(files.items()):
            blob = self._github("POST", prefix + "/git/blobs", {
                "content": b64encode(contents.encode("utf-8")).decode("ascii"),
                "encoding": "base64",
            })
            blob_sha = blob.get("sha")
            if not isinstance(blob_sha, str) or not SHA.fullmatch(blob_sha):
                raise ProviderError("GitHub blob creation failed")
            tree_entries.append({"path": path, "mode": "100644", "type": "blob", "sha": blob_sha})

        tree = self._github("POST", prefix + "/git/trees", {
            "base_tree": old_tree, "tree": tree_entries,
        })
        tree_sha = tree.get("sha")
        if not isinstance(tree_sha, str) or not SHA.fullmatch(tree_sha):
            raise ProviderError("GitHub tree creation failed")
        commit = self._github("POST", prefix + "/git/commits", {
            "message": message, "tree": tree_sha, "parents": [old_sha],
        })
        commit_sha = commit.get("sha")
        if not isinstance(commit_sha, str) or not SHA.fullmatch(commit_sha):
            raise ProviderError("GitHub commit failed")
        self._github("PATCH", prefix + "/git/refs/heads/" + branch_path, {
            "sha": commit_sha, "force": False,
        })
        return commit_sha

    def deploy(self, repo_url: str, commit_sha: str) -> str:
        if not SHA.fullmatch(commit_sha):
            raise ProviderError("Invalid commit")
        owner, repo = self._repo_parts(repo_url)
        metadata = self._github("GET", f"/repos/{quote(owner)}/{quote(repo)}")
        if metadata.get("private") is not True:
            raise ProviderError("Refusing unreviewed public source")
        repo_id = metadata.get("id")
        branch = metadata.get("default_branch")
        if not isinstance(repo_id, int) or not isinstance(branch, str):
            raise ProviderError("Missing GitHub deployment metadata")
        project_name = slugify(repo)
        self._vercel("POST", "/v11/projects", {
            "name": project_name,
            "gitRepository": {"type": "github", "repo": owner + "/" + repo},
        })
        deployment = self._vercel("POST", "/v13/deployments", {
            "name": project_name,
            "gitSource": {
                "type": "github", "repoId": str(repo_id),
                "ref": branch, "sha": commit_sha,
            },
        })
        deployment_id = deployment.get("id")
        hostname = deployment.get("url")
        if not isinstance(deployment_id, str) or not isinstance(hostname, str):
            raise ProviderError("Vercel deployment details missing")
        url = "https://" + hostname
        if not urlparse(url).hostname or not urlparse(url).hostname.endswith(".vercel.app"):
            raise ProviderError("Unexpected Vercel deployment hostname")
        self._deployments[url] = deployment_id
        return url

    def verify_live(self, url: str) -> bool:
        deployment_id = self._deployments.get(url)
        if not deployment_id:
            return False
        for attempt in range(self.verify_attempts):
            result = self._vercel("GET", "/v13/deployments/" + quote(deployment_id, safe=""))
            state = result.get("readyState")
            if state == "READY":
                return self.transport.probe(url)
            if state in {"ERROR", "CANCELED"}:
                return False
            if attempt + 1 < self.verify_attempts:
                time.sleep(self.verify_interval_seconds)
        return False

    def capabilities(self) -> FactoryCapabilities:
        return FactoryCapabilities(
            create_repository=self.create_repository,
            write_repository=self.write_repository,
            deploy=self.deploy,
            verify_live=self.verify_live,
        )
