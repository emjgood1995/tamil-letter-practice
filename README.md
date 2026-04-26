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
