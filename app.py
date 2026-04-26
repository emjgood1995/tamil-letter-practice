import random
from typing import Optional

import streamlit as st

from tamil_letters import (
    CONSONANT_BY_MEI,
    CONSONANT_GROUPS,
    CONSONANTS,
    VOWEL_BY_TAMIL,
    VOWEL_PAIRS,
    VOWELS,
    all_compounds,
    compound_by_key,
    table_rows,
)


st.set_page_config(
    page_title="Tamil Letter Practice",
    page_icon="அ",
    layout="wide",
)


st.markdown(
    """
    <style>
    :root {
        --paper: #fffaf2;
        --surface: #ffffff;
        --surface-warm: #fff3d6;
        --surface-cool: #e7f8f4;
        --ink: #22313f;
        --muted: #6b7280;
        --coral: #e85d3f;
        --saffron: #f4b942;
        --teal: #087f7a;
        --mint: #9be7c5;
        --sky: #c9ecff;
        --border: #efd8b2;
    }
    .stApp {
        background:
            linear-gradient(180deg, #fffaf2 0%, #fff7e8 52%, #eefbf7 100%);
        color: var(--ink);
    }
    [data-testid="stHeader"] {
        background: rgba(255, 250, 242, 0.88);
    }
    .block-container {
        max-width: 1120px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    h1 {
        color: #173f3b;
        font-weight: 800;
    }
    h3, [data-testid="stMarkdownContainer"] strong {
        color: #27445c;
    }
    section[data-testid="stSidebar"] {
        background: #fff1d6;
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #3f3428;
    }
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid #f1dfbf;
        border-radius: 8px;
        box-shadow: 0 10px 24px rgba(122, 88, 34, 0.08);
        padding: 0.85rem 1rem;
    }
    .letter-card {
        align-items: center;
        border: 2px solid #f2c56b;
        border-radius: 8px;
        box-shadow: 0 18px 40px rgba(92, 64, 25, 0.13);
        display: flex;
        justify-content: center;
        min-height: 260px;
        margin: 0.75rem 0 1.25rem;
        background:
            linear-gradient(135deg, #fff7cf 0%, #ffe7df 46%, #daf6ee 100%);
    }
    .letter-card span {
        color: #18363d;
        font-size: clamp(6rem, 18vw, 12rem);
        font-weight: 800;
        line-height: 1;
        text-shadow: 0 5px 0 rgba(255, 255, 255, 0.75);
    }
    .answer-line {
        background: rgba(255, 255, 255, 0.86);
        border: 1px solid #cdeee4;
        border-left: 5px solid var(--teal);
        border-radius: 8px;
        box-shadow: 0 8px 20px rgba(8, 127, 122, 0.08);
        color: var(--ink);
        padding: 0.55rem 0.85rem;
        margin: 0.75rem 0 1rem;
        font-size: 1.05rem;
    }
    .pronunciation-line {
        background: #ffffff;
        border: 1px solid #f0d08b;
        border-radius: 8px;
        box-shadow: 0 8px 20px rgba(244, 185, 66, 0.12);
        color: var(--ink);
        display: flex;
        flex-wrap: wrap;
        gap: 0.7rem;
        margin: 0.5rem 0 1rem;
        padding: 0.75rem 0.9rem;
    }
    .pronunciation-chip {
        align-items: baseline;
        background: #fff5d6;
        border: 1px solid #f4d58f;
        border-radius: 8px;
        display: inline-flex;
        gap: 0.45rem;
        padding: 0.35rem 0.6rem;
    }
    .pronunciation-letter {
        color: #173f3b;
        font-size: 1.55rem;
        font-weight: 800;
        line-height: 1;
    }
    .pronunciation-text {
        color: #a33d2b;
        font-size: 1.05rem;
        font-weight: 800;
    }
    .missed-letter {
        font-size: 2rem;
        line-height: 1.2;
    }
    [data-testid="stCaptionContainer"] {
        color: #a16207;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    div[data-testid="stButton"] > button {
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid #edc56e;
        border-radius: 8px;
        box-shadow: 0 6px 14px rgba(92, 64, 25, 0.08);
        color: #243044;
        font-size: 1.2rem;
        font-weight: 800;
        min-height: 3rem;
        transition: background 120ms ease, border-color 120ms ease, box-shadow 120ms ease,
            transform 120ms ease;
    }
    div[data-testid="stButton"] > button:hover:enabled {
        background: #fff0bc;
        border-color: var(--coral);
        box-shadow: 0 9px 20px rgba(232, 93, 63, 0.18);
        color: #173f3b;
        transform: translateY(-1px);
    }
    div[data-testid="stButton"] > button[kind="primary"],
    div[data-testid="stButton"] button[data-testid="stBaseButton-primary"] {
        background: var(--teal);
        border-color: var(--teal);
        box-shadow: 0 8px 20px rgba(8, 127, 122, 0.22);
        color: #ffffff;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover:enabled,
    div[data-testid="stButton"] button[data-testid="stBaseButton-primary"]:hover:enabled {
        background: #0a6c68;
        border-color: #0a6c68;
        color: #ffffff;
    }
    div[data-testid="stButton"] > button:disabled {
        background: #f2f4f7;
        border-color: #e4e7ec;
        box-shadow: none;
        color: #9aa4b2;
        opacity: 0.78;
    }
    div[data-testid="stAlert"] {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def reset_stats() -> None:
    st.session_state.stats = {
        "attempts": 0,
        "correct": 0,
        "streak": 0,
        "best_streak": 0,
        "missed": {},
    }


def choose_new_card(eligible_keys: list[str]) -> None:
    st.session_state.current_key = random.choice(eligible_keys)
    st.session_state.answer_locked = False
    st.session_state.feedback = None
    st.session_state.show_pronunciation = False
    st.session_state.selected_consonant = None
    st.session_state.selected_vowel = None


def available_cards(selected_consonants: list[str], selected_vowels: list[str]) -> list[str]:
    consonants = [CONSONANT_BY_MEI[mei] for mei in selected_consonants]
    vowels = [VOWEL_BY_TAMIL[tamil] for tamil in selected_vowels]
    return [compound.key for compound in all_compounds(consonants, vowels)]


def select_answer(letter: str, state_key: str) -> None:
    st.session_state[state_key] = letter
    st.rerun()


def render_letter_grid(
    rows: tuple[tuple[str, ...], ...],
    available_letters: list[str],
    selected_letter: Optional[str],
    state_key: str,
    key_prefix: str,
    row_labels: Optional[tuple[str, ...]] = None,
) -> None:
    available = set(available_letters)

    for row_index, row in enumerate(rows):
        if row_labels:
            st.caption(row_labels[row_index])

        columns = st.columns(6, gap="small")
        for column_index, letter in enumerate(row):
            is_selected = selected_letter == letter
            columns[column_index].button(
                letter,
                key=f"{key_prefix}_{row_index}_{column_index}",
                type="primary" if is_selected else "secondary",
                disabled=letter not in available or st.session_state.answer_locked,
                width="stretch",
                on_click=select_answer,
                args=(letter, state_key),
            )


if "stats" not in st.session_state:
    reset_stats()

if "answer_locked" not in st.session_state:
    st.session_state.answer_locked = False

if "feedback" not in st.session_state:
    st.session_state.feedback = None

if "selected_consonant" not in st.session_state:
    st.session_state.selected_consonant = None

if "selected_vowel" not in st.session_state:
    st.session_state.selected_vowel = None

if "show_pronunciation" not in st.session_state:
    st.session_state.show_pronunciation = False


st.title("Tamil Letter Practice")

with st.sidebar:
    st.header("Practice Set")
    selected_consonants = st.multiselect(
        "Consonants",
        options=[consonant.mei for consonant in CONSONANTS],
        default=[consonant.mei for consonant in CONSONANTS],
    )
    selected_vowels = st.multiselect(
        "Vowels",
        options=[vowel.tamil for vowel in VOWELS],
        default=[vowel.tamil for vowel in VOWELS],
    )
    review_missed = st.toggle(
        "Review missed only",
        value=False,
        disabled=not st.session_state.stats["missed"],
    )

    if st.button("Reset score", width="stretch"):
        reset_stats()
        st.session_state.current_key = None
        st.session_state.answer_locked = False
        st.session_state.feedback = None
        st.session_state.show_pronunciation = False
        st.session_state.selected_consonant = None
        st.session_state.selected_vowel = None
        st.rerun()


eligible_keys = available_cards(selected_consonants, selected_vowels)

if review_missed:
    missed_keys = set(st.session_state.stats["missed"])
    eligible_keys = [key for key in eligible_keys if key in missed_keys]

if not eligible_keys:
    st.warning("The current filters have no letters to practise.")
    st.stop()

if st.session_state.get("current_key") not in eligible_keys:
    choose_new_card(eligible_keys)

if st.session_state.get("selected_consonant") not in selected_consonants:
    st.session_state.selected_consonant = None

if st.session_state.get("selected_vowel") not in selected_vowels:
    st.session_state.selected_vowel = None

current = compound_by_key(st.session_state.current_key)
stats = st.session_state.stats
accuracy = round((stats["correct"] / stats["attempts"]) * 100) if stats["attempts"] else 0

practice_tab, table_tab, missed_tab = st.tabs(["Practice", "Letter table", "Missed"])

with practice_tab:
    metric_cols = st.columns(4)
    metric_cols[0].metric("Correct", stats["correct"])
    metric_cols[1].metric("Attempts", stats["attempts"])
    metric_cols[2].metric("Accuracy", f"{accuracy}%")
    metric_cols[3].metric("Streak", stats["streak"])

    st.markdown(
        f'<div class="letter-card"><span>{current.glyph}</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown("**Consonants**")
    render_letter_grid(
        rows=tuple(group[1] for group in CONSONANT_GROUPS),
        row_labels=tuple(group[0] for group in CONSONANT_GROUPS),
        available_letters=selected_consonants,
        selected_letter=st.session_state.selected_consonant,
        state_key="selected_consonant",
        key_prefix="consonant_answer",
    )

    st.markdown("**Vowels**")
    render_letter_grid(
        rows=(
            tuple(pair[0] for pair in VOWEL_PAIRS),
            tuple(pair[1] for pair in VOWEL_PAIRS),
        ),
        available_letters=selected_vowels,
        selected_letter=st.session_state.selected_vowel,
        state_key="selected_vowel",
        key_prefix="vowel_answer",
    )

    selected_consonant = st.session_state.selected_consonant
    selected_vowel = st.session_state.selected_vowel
    selected_consonant_text = selected_consonant if selected_consonant else "None"
    selected_vowel_text = selected_vowel if selected_vowel else "None"
    st.markdown(
        f'<div class="answer-line">{selected_consonant_text} + {selected_vowel_text}</div>',
        unsafe_allow_html=True,
    )

    action_cols = st.columns([1, 1, 4])
    submitted = action_cols[0].button(
        "Check answer",
        type="primary",
        disabled=st.session_state.answer_locked
        or not selected_consonant
        or not selected_vowel,
        width="stretch",
    )
    next_clicked = action_cols[1].button("Next", width="stretch")

    if submitted:
        is_correct = (
            selected_consonant == current.consonant.mei
            and selected_vowel == current.vowel.tamil
        )
        stats["attempts"] += 1

        if is_correct:
            stats["correct"] += 1
            stats["streak"] += 1
            stats["best_streak"] = max(stats["best_streak"], stats["streak"])
            stats["missed"].pop(current.key, None)
        else:
            stats["streak"] = 0
            stats["missed"][current.key] = stats["missed"].get(current.key, 0) + 1

        st.session_state.answer_locked = True
        st.session_state.show_pronunciation = False
        st.session_state.feedback = {
            "is_correct": is_correct,
            "answer": f"{current.consonant.mei} + {current.vowel.tamil}",
            "consonant": current.consonant.mei,
            "consonant_latin": current.consonant.latin,
            "vowel": current.vowel.tamil,
            "vowel_latin": current.vowel.latin,
        }
        st.rerun()

    if next_clicked:
        choose_new_card(eligible_keys)
        st.rerun()

    feedback = st.session_state.feedback
    if feedback:
        if feedback["is_correct"]:
            st.success("Correct")
        else:
            st.error("Not quite")
        st.markdown(
            f'<div class="answer-line">{feedback["answer"]}</div>',
            unsafe_allow_html=True,
        )
        if not st.session_state.show_pronunciation:
            if st.button("Reveal pronunciation", width="content"):
                st.session_state.show_pronunciation = True

        if st.session_state.show_pronunciation:
            st.markdown(
                f"""
                <div class="pronunciation-line">
                    <span class="pronunciation-chip">
                        <span class="pronunciation-letter">{feedback["consonant"]}</span>
                        <span class="pronunciation-text">{feedback["consonant_latin"]}</span>
                    </span>
                    <span class="pronunciation-chip">
                        <span class="pronunciation-letter">{feedback["vowel"]}</span>
                        <span class="pronunciation-text">{feedback["vowel_latin"]}</span>
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

with table_tab:
    st.dataframe(table_rows(), hide_index=True, width="stretch")

with missed_tab:
    missed = stats["missed"]
    if not missed:
        st.info("No missed letters yet.")
    else:
        for key, count in sorted(missed.items(), key=lambda item: item[1], reverse=True):
            compound = compound_by_key(key)
            cols = st.columns([1, 3, 1])
            cols[0].markdown(
                f'<div class="missed-letter">{compound.glyph}</div>',
                unsafe_allow_html=True,
            )
            cols[1].write(f"{compound.consonant.mei} + {compound.vowel.tamil}")
            cols[2].write(f"Missed {count}")
