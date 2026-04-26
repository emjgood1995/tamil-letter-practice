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
    .block-container {
        max-width: 1120px;
        padding-top: 2rem;
    }
    .letter-card {
        align-items: center;
        border: 1px solid #d8dee4;
        border-radius: 8px;
        display: flex;
        justify-content: center;
        min-height: 260px;
        margin: 0.75rem 0 1rem;
        background: #fffdf7;
    }
    .letter-card span {
        color: #111827;
        font-size: clamp(6rem, 18vw, 12rem);
        line-height: 1;
    }
    .answer-line {
        border-left: 4px solid #2563eb;
        padding: 0.25rem 0 0.25rem 0.75rem;
        margin: 0.5rem 0 1rem;
        font-size: 1.05rem;
    }
    .missed-letter {
        font-size: 2rem;
        line-height: 1.2;
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
        st.session_state.feedback = {
            "is_correct": is_correct,
            "answer": f"{current.consonant.mei} + {current.vowel.tamil}",
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
