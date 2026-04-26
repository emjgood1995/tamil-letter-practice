import unittest

from tamil_letters import CONSONANTS, VOWELS, all_compounds, build_compound


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


if __name__ == "__main__":
    unittest.main()
