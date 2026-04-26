from dataclasses import dataclass


PULLI = "\u0bcd"


@dataclass(frozen=True)
class Vowel:
    tamil: str
    latin: str
    sign: str


@dataclass(frozen=True)
class Consonant:
    base: str
    latin: str

    @property
    def mei(self) -> str:
        return f"{self.base}{PULLI}"


@dataclass(frozen=True)
class CompoundLetter:
    glyph: str
    consonant: Consonant
    vowel: Vowel

    @property
    def key(self) -> str:
        return make_key(self.consonant.mei, self.vowel.tamil)


VOWELS = (
    Vowel("அ", "a", ""),
    Vowel("ஆ", "aa", "\u0bbe"),
    Vowel("இ", "i", "\u0bbf"),
    Vowel("ஈ", "ii", "\u0bc0"),
    Vowel("உ", "u", "\u0bc1"),
    Vowel("ஊ", "uu", "\u0bc2"),
    Vowel("எ", "e", "\u0bc6"),
    Vowel("ஏ", "ee", "\u0bc7"),
    Vowel("ஐ", "ai", "\u0bc8"),
    Vowel("ஒ", "o", "\u0bca"),
    Vowel("ஓ", "oo", "\u0bcb"),
    Vowel("ஔ", "au", "\u0bcc"),
)


CONSONANTS = (
    Consonant("க", "ka"),
    Consonant("ங", "nga"),
    Consonant("ச", "ca"),
    Consonant("ஞ", "nya"),
    Consonant("ட", "tta"),
    Consonant("ண", "nna"),
    Consonant("த", "ta"),
    Consonant("ந", "na"),
    Consonant("ப", "pa"),
    Consonant("ம", "ma"),
    Consonant("ய", "ya"),
    Consonant("ர", "ra"),
    Consonant("ல", "la"),
    Consonant("வ", "va"),
    Consonant("ழ", "zha"),
    Consonant("ள", "lla"),
    Consonant("ற", "rra"),
    Consonant("ன", "na"),
)


CONSONANT_BY_MEI = {consonant.mei: consonant for consonant in CONSONANTS}
VOWEL_BY_TAMIL = {vowel.tamil: vowel for vowel in VOWELS}


def make_key(consonant_mei: str, vowel_tamil: str) -> str:
    return f"{consonant_mei}|{vowel_tamil}"


def build_compound(consonant: Consonant, vowel: Vowel) -> CompoundLetter:
    return CompoundLetter(
        glyph=f"{consonant.base}{vowel.sign}",
        consonant=consonant,
        vowel=vowel,
    )


def all_compounds(consonants=CONSONANTS, vowels=VOWELS) -> list[CompoundLetter]:
    return [
        build_compound(consonant, vowel)
        for consonant in consonants
        for vowel in vowels
    ]


def compound_by_key(key: str) -> CompoundLetter:
    consonant_mei, vowel_tamil = key.split("|", maxsplit=1)
    return build_compound(CONSONANT_BY_MEI[consonant_mei], VOWEL_BY_TAMIL[vowel_tamil])


def consonant_label(consonant: Consonant) -> str:
    return f"{consonant.mei}  {consonant.latin}"


def vowel_label(vowel: Vowel) -> str:
    return f"{vowel.tamil}  {vowel.latin}"


def table_rows() -> list[dict[str, str]]:
    rows = []
    for consonant in CONSONANTS:
        row = {"Consonant": consonant_label(consonant)}
        for vowel in VOWELS:
            row[vowel_label(vowel)] = build_compound(consonant, vowel).glyph
        rows.append(row)
    return rows
