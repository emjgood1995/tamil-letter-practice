# Tamil Letter Practice

A small Streamlit app for practising Tamil compound letters.

The app uses the 18 core Tamil consonants and 12 vowels to generate 216 uyirmei
letters. Each quiz card shows a compound letter, and you choose the consonant and
vowel that make it.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Test

```bash
python3 -m unittest discover -s tests
```

## Pronunciation Persistence

The app reads default romanisation values from `pronunciations.json`. Changes made
in the Pronunciations tab update that file.

To let the deployed Streamlit app commit pronunciation changes back to GitHub,
add these secrets in Streamlit Cloud:

```toml
[github]
token = "github_pat_..."
repo = "emjgood1995/tamil-letter-practice"
branch = "main"
path = "pronunciations.json"
```

The token needs contents read/write access for this repository.
