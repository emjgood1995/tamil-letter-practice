import base64
import json
from pathlib import Path
from typing import Any, Optional

import requests


PRONUNCIATIONS_PATH = Path(__file__).with_name("pronunciations.json")
DEFAULT_GITHUB_REPO = "emjgood1995/tamil-letter-practice"
DEFAULT_GITHUB_BRANCH = "main"
DEFAULT_GITHUB_PATH = "pronunciations.json"


class PronunciationStoreError(Exception):
    pass


def normalize_pronunciations(
    raw: dict[str, Any],
    default_vowels: dict[str, str],
    default_consonants: dict[str, str],
) -> dict[str, dict[str, str]]:
    if not isinstance(raw, dict):
        raw = {}

    vowels = normalize_pronunciation_map(raw.get("vowels", {}), default_vowels)
    consonants = normalize_pronunciation_map(
        raw.get("consonants", {}),
        default_consonants,
    )

    return {
        "vowels": vowels,
        "consonants": consonants,
        "compound_vowels": normalize_pronunciation_map(
            raw.get("compound_vowels", {}),
            vowels,
        ),
        "compound_consonants": normalize_pronunciation_map(
            raw.get("compound_consonants", {}),
            consonants,
        ),
    }


def normalize_pronunciation_map(
    raw: object,
    defaults: dict[str, str],
) -> dict[str, str]:
    if not isinstance(raw, dict):
        raw = {}

    normalized = {}
    for letter, default in defaults.items():
        value = raw.get(letter, default)
        value = str(value).strip()
        normalized[letter] = value if value else default

    return normalized


def load_pronunciations(
    default_vowels: dict[str, str],
    default_consonants: dict[str, str],
    path: Path = PRONUNCIATIONS_PATH,
) -> dict[str, dict[str, str]]:
    if not path.exists():
        return normalize_pronunciations({}, default_vowels, default_consonants)

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raw = {}

    return normalize_pronunciations(raw, default_vowels, default_consonants)


def pronunciations_json(data: dict[str, dict[str, str]]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def save_pronunciations_file(
    data: dict[str, dict[str, str]],
    path: Path = PRONUNCIATIONS_PATH,
) -> None:
    path.write_text(pronunciations_json(data), encoding="utf-8")


def save_pronunciations_to_github(
    data: dict[str, dict[str, str]],
    *,
    token: str,
    repo: str = DEFAULT_GITHUB_REPO,
    branch: str = DEFAULT_GITHUB_BRANCH,
    path: str = DEFAULT_GITHUB_PATH,
) -> str:
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    content = base64.b64encode(pronunciations_json(data).encode("utf-8")).decode("ascii")

    put_response = None
    for _ in range(2):
        sha = github_file_sha(url, headers, branch)
        put_response = put_github_file(url, headers, branch, content, sha)

        if put_response.status_code in (200, 201):
            response_data = put_response.json()
            return response_data.get("commit", {}).get("html_url", "")

        if put_response.status_code != 409:
            break

    raise PronunciationStoreError(github_error_message(put_response))


def github_file_sha(url: str, headers: dict[str, str], branch: str) -> Optional[str]:
    try:
        get_response = requests.get(url, headers=headers, params={"ref": branch}, timeout=15)
    except requests.RequestException as exc:
        raise PronunciationStoreError(f"GitHub update failed: {exc}") from exc

    if get_response.status_code == 200:
        return get_response.json()["sha"]

    if get_response.status_code == 404:
        return None

    raise PronunciationStoreError(github_error_message(get_response))


def put_github_file(
    url: str,
    headers: dict[str, str],
    branch: str,
    content: str,
    sha: Optional[str],
) -> requests.Response:
    payload = {
        "message": "Update pronunciations",
        "content": content,
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha

    try:
        return requests.put(url, headers=headers, json=payload, timeout=15)
    except requests.RequestException as exc:
        raise PronunciationStoreError(f"GitHub update failed: {exc}") from exc


def github_error_message(response: requests.Response) -> str:
    try:
        detail = response.json().get("message", response.text)
    except ValueError:
        detail = response.text

    return f"GitHub update failed with HTTP {response.status_code}: {detail}"
