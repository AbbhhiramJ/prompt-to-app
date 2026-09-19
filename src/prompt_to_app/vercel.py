import json
import os
from typing import Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class VercelError(RuntimeError):
    pass


def deploy(
    files: Dict[str, str],
    name: str = "prompt-to-app",
    token: Optional[str] = None,
    target: str = "production",
    project: Optional[str] = None,
    team_id: Optional[str] = None,
    api_base_url: str = "https://api.vercel.com",
) -> str:
    """Deploy generated web-app files to Vercel and return the deployment URL."""
    token = token or os.getenv("VERCEL_TOKEN")
    if not token:
        raise VercelError("VERCEL_TOKEN is required for cloud deployment")
    if not files:
        raise VercelError("no files to deploy")
    if target not in {"production", "staging"}:
        raise VercelError("target must be production or staging")

    payload = {
        "name": name,
        "files": [{"file": path, "data": content} for path, content in files.items()],
        "target": target,
        "skipAutoDetectionConfirmation": "1",
    }
    if project:
        payload["project"] = project
    if team_id:
        payload["teamId"] = team_id

    request = Request(
        f"{api_base_url.rstrip('/')}/v13/deployments",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise VercelError(f"Vercel deployment failed ({exc.code}): {detail}") from exc
    except URLError as exc:
        raise VercelError(f"Vercel connection failed: {exc.reason}") from exc

    url = body.get("url")
    if not url:
        raise VercelError(f"Vercel returned no deployment URL: {body}")
    return url if url.startswith("http") else f"https://{url}"
