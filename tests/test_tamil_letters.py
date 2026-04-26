import unittest

from tamil_letters import (
    CONSONANT_GROUPS,
    CONSONANTS,
    VOWEL_PAIRS,
    VOWELS,
    all_compounds,
    build_compound,
    table_rows,
)


class TamilLettersTest(unittest.TestCase):
    def test_generates_core_compound_set(self):
        self.assertEqual(len(CONSONANTS), 18)
        self.assertEqual(len(VOWELS), 12)
        self.assertEqual(len(all_compounds()), 216)

    def test_compound_examples(self):
        ka = CONSONANTS[0]
        nna = CONSONANTS[-1]

        self.assertEqual(build_compound(ka, VOWELS[0]).glyph, "க")
        self.assertEqual(build_compound(ka, VOWELS[1]).glyph, "கா")
        self.assertEqual(build_compound(ka, VOWELS[2]).glyph, "கி")
        self.assertEqual(build_compound(ka, VOWELS[-1]).glyph, "கௌ")
        self.assertEqual(build_compound(nna, VOWELS[10]).glyph, "னோ")

    def test_answer_grid_groupings(self):
        grouped_consonants = [
            consonant for _, consonants in CONSONANT_GROUPS for consonant in consonants
        ]
        paired_vowels = [vowel for pair in VOWEL_PAIRS for vowel in pair]

        self.assertEqual([len(group[1]) for group in CONSONANT_GROUPS], [6, 6, 6])
        self.assertEqual(len(VOWEL_PAIRS), 6)
        self.assertTrue(all(len(pair) == 2 for pair in VOWEL_PAIRS))
        self.assertEqual(set(grouped_consonants), {consonant.mei for consonant in CONSONANTS})
        self.assertEqual(set(paired_vowels), {vowel.tamil for vowel in VOWELS})

    def test_table_rows_use_tamil_only_headers(self):
        rows = table_rows()

        self.assertEqual(rows[0]["Consonant"], "க்")
        self.assertIn("அ", rows[0])
        self.assertNotIn("அ  a", rows[0])


if __name__ == "__main__":
    unittest.main()
