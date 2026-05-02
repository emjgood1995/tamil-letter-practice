import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pronunciation_store import (
    load_pronunciations,
    normalize_pronunciations,
    save_pronunciations_to_github,
)


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = json.dumps(payload)

    def json(self):
        return self._payload


class PronunciationStoreTest(unittest.TestCase):
    def test_normalize_pronunciations_uses_defaults_for_missing_values(self):
        data = normalize_pronunciations(
            {"vowels": {"அ": "ah"}, "consonants": {"க்": ""}},
            {"அ": "a", "ஆ": "aa"},
            {"க்": "ka"},
        )

        self.assertEqual(data["vowels"], {"அ": "ah", "ஆ": "aa"})
        self.assertEqual(data["consonants"], {"க்": "ka"})

    def test_load_pronunciations_reads_json_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "pronunciations.json"
            path.write_text(
                json.dumps(
                    {
                        "vowels": {"அ": "ah"},
                        "consonants": {"க்": "k"},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            data = load_pronunciations(
                {"அ": "a"},
                {"க்": "ka"},
                path=path,
            )

        self.assertEqual(data["vowels"], {"அ": "ah"})
        self.assertEqual(data["consonants"], {"க்": "k"})

    def test_load_pronunciations_handles_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "pronunciations.json"
            path.write_text("{", encoding="utf-8")

            data = load_pronunciations(
                {"அ": "a"},
                {"க்": "ka"},
                path=path,
            )

        self.assertEqual(data["vowels"], {"அ": "a"})
        self.assertEqual(data["consonants"], {"க்": "ka"})

    def test_save_pronunciations_retries_github_sha_conflict(self):
        data = {"vowels": {"அ": "a"}, "consonants": {"க்": "ka"}}
        get_responses = [
            FakeResponse(200, {"sha": "old-sha"}),
            FakeResponse(200, {"sha": "new-sha"}),
        ]
        put_responses = [
            FakeResponse(409, {"message": "is at new-sha but expected old-sha"}),
            FakeResponse(200, {"commit": {"html_url": "https://github.com/commit"}}),
        ]

        with patch("pronunciation_store.requests.get", side_effect=get_responses) as get:
            with patch("pronunciation_store.requests.put", side_effect=put_responses) as put:
                commit_url = save_pronunciations_to_github(
                    data,
                    token="token",
                    repo="owner/repo",
                )

        self.assertEqual(commit_url, "https://github.com/commit")
        self.assertEqual(get.call_count, 2)
        self.assertEqual(put.call_count, 2)
        self.assertEqual(put.call_args_list[0].kwargs["json"]["sha"], "old-sha")
        self.assertEqual(put.call_args_list[1].kwargs["json"]["sha"], "new-sha")


if __name__ == "__main__":
    unittest.main()
