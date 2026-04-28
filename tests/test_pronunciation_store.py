import json
import tempfile
import unittest
from pathlib import Path

from pronunciation_store import load_pronunciations, normalize_pronunciations


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


if __name__ == "__main__":
    unittest.main()
