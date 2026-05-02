import hmac
from collections.abc import Mapping
from typing import Optional

import streamlit as st

from practice_queue import build_card_queue
from pronunciation_store import (
    DEFAULT_GITHUB_BRANCH,
    DEFAULT_GITHUB_PATH,
    DEFAULT_GITHUB_REPO,
    PronunciationStoreError,
    load_pronunciations,
    save_pronunciations_file,
    save_pronunciations_to_github,
)
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


def new_quiz_stats() -> dict[str, int]:
    return {
        "attempts": 0,
        "correct": 0,
        "streak": 0,
        "best_streak": 0,
    }


def default_vowel_pronunciations() -> dict[str, str]:
    return {vowel.tamil: vowel.latin for vowel in VOWELS}


def default_consonant_pronunciations() -> dict[str, str]:
    return {consonant.mei: consonant.latin for consonant in CONSONANTS}


def default_compound_vowel_pronunciations() -> dict[str, str]:
    return default_vowel_pronunciations()


def default_compound_consonant_pronunciations() -> dict[str, str]:
    return default_consonant_pronunciations()


def initialize_pronunciations() -> None:
    keys = (
        "vowel_pronunciations",
        "consonant_pronunciations",
        "compound_vowel_pronunciations",
        "compound_consonant_pronunciations",
    )
    if all(key in st.session_state for key in keys):
        return

    stored = load_pronunciations(
        default_vowel_pronunciations(),
        default_consonant_pronunciations(),
    )

    if "vowel_pronunciations" not in st.session_state:
        st.session_state.vowel_pronunciations = stored["vowels"]

    if "consonant_pronunciations" not in st.session_state:
        st.session_state.consonant_pronunciations = stored["consonants"]

    if "compound_vowel_pronunciations" not in st.session_state:
        st.session_state.compound_vowel_pronunciations = stored["compound_vowels"]

    if "compound_consonant_pronunciations" not in st.session_state:
        st.session_state.compound_consonant_pronunciations = stored[
            "compound_consonants"
        ]


def pronunciation_for(letter: str, kind: str) -> str:
    pronunciation_map = st.session_state[f"{kind}_pronunciations"]
    return pronunciation_map[letter]


def pronunciation_rows(kind: str, letters: list[str]) -> list[dict[str, str]]:
    compound_kind = f"compound_{kind}"
    return [
        {
            "Letter": letter,
            "Pronunciation": pronunciation_for(letter, kind),
            "Compound pronunciation": pronunciation_for(letter, compound_kind),
        }
        for letter in letters
    ]


def row_text(row: dict[str, str], column: str, default: str = "") -> str:
    value = row.get(column, default)
    if value is None:
        return ""
    return str(value).strip()


def clean_pronunciation_rows(
    rows: list[dict[str, str]],
    valid_letters: list[str],
) -> tuple[dict[str, str], dict[str, str], list[str]]:
    valid = set(valid_letters)
    cleaned = {}
    compound_cleaned = {}
    invalid_letters = []

    for row in rows:
        letter = row_text(row, "Letter")
        pronunciation = row_text(row, "Pronunciation")
        compound_pronunciation = row_text(
            row,
            "Compound pronunciation",
            pronunciation,
        )

        if letter not in valid:
            continue

        if not pronunciation or not compound_pronunciation:
            invalid_letters.append(letter)
            continue

        cleaned[letter] = pronunciation
        compound_cleaned[letter] = compound_pronunciation

    missing = [
        letter
        for letter in valid_letters
        if (
            letter not in cleaned
            or letter not in compound_cleaned
        )
        and letter not in invalid_letters
    ]
    invalid_letters.extend(missing)
    return cleaned, compound_cleaned, invalid_letters


def reset_all_answer_states() -> None:
    reset_answer_state()
    reset_named_answer_state("vowel_test")
    reset_named_answer_state("consonant_test")


def pronunciation_payload(
    vowel_pronunciations: dict[str, str],
    consonant_pronunciations: dict[str, str],
    compound_vowel_pronunciations: dict[str, str],
    compound_consonant_pronunciations: dict[str, str],
) -> dict[str, dict[str, str]]:
    return {
        "vowels": vowel_pronunciations,
        "consonants": consonant_pronunciations,
        "compound_vowels": compound_vowel_pronunciations,
        "compound_consonants": compound_consonant_pronunciations,
    }


def get_secret_dict() -> dict:
    try:
        return dict(st.secrets)
    except Exception:
        return {}


def pronunciation_admin_password() -> Optional[str]:
    secrets = get_secret_dict()
    admin = secrets.get("admin", {})
    if not isinstance(admin, Mapping):
        admin = {}

    password = (
        admin.get("password")
        or secrets.get("PRONUNCIATION_ADMIN_PASSWORD")
        or secrets.get("ADMIN_PASSWORD")
    )
    if not password:
        return None

    return str(password)


def query_param_value(name: str) -> Optional[str]:
    try:
        value = st.query_params.get(name)
    except Exception:
        return None

    if isinstance(value, list):
        return str(value[0]) if value else None

    if value is None:
        return None

    return str(value)


def pronunciation_admin_requested() -> bool:
    value = query_param_value("admin")
    return bool(value and value.lower() in {"1", "true", "yes"})


def render_pronunciation_admin_gate() -> bool:
    if "pronunciation_admin_unlocked" not in st.session_state:
        st.session_state.pronunciation_admin_unlocked = False

    if st.session_state.pronunciation_admin_unlocked:
        st.divider()
        st.caption("Pronunciation admin")
        if st.button("Lock pronunciation editor", width="stretch"):
            st.session_state.pronunciation_admin_unlocked = False
            st.rerun()
        return True

    if not pronunciation_admin_requested():
        return False

    st.divider()
    st.caption("Pronunciation admin")
    password = pronunciation_admin_password()
    if not password:
        st.warning("Admin password is not configured.")
        return False

    entered_password = st.text_input(
        "Password",
        type="password",
        key="pronunciation_admin_password",
    )
    if st.button("Unlock pronunciation editor", width="stretch"):
        if hmac.compare_digest(
            entered_password.encode("utf-8"),
            password.encode("utf-8"),
        ):
            st.session_state.pronunciation_admin_unlocked = True
            st.rerun()
        else:
            st.error("Incorrect password.")

    return False


def github_persistence_config() -> Optional[dict[str, str]]:
    secrets = get_secret_dict()
    github = secrets.get("github", {})
    if not isinstance(github, Mapping):
        github = {}

    token = github.get("token") or secrets.get("GITHUB_TOKEN")
    if not token:
        return None

    return {
        "token": str(token),
        "repo": str(
            github.get("repo")
            or secrets.get("GITHUB_REPO")
            or DEFAULT_GITHUB_REPO
        ),
        "branch": str(
            github.get("branch")
            or secrets.get("GITHUB_BRANCH")
            or DEFAULT_GITHUB_BRANCH
        ),
        "path": str(
            github.get("path")
            or secrets.get("GITHUB_PATH")
            or DEFAULT_GITHUB_PATH
        ),
    }


def persist_pronunciations(
    vowel_pronunciations: dict[str, str],
    consonant_pronunciations: dict[str, str],
    compound_vowel_pronunciations: dict[str, str],
    compound_consonant_pronunciations: dict[str, str],
) -> tuple[str, str]:
    data = pronunciation_payload(
        vowel_pronunciations,
        consonant_pronunciations,
        compound_vowel_pronunciations,
        compound_consonant_pronunciations,
    )
    try:
        save_pronunciations_file(data)
    except OSError as exc:
        return ("error", f"Could not write pronunciations.json: {exc}")

    github_config = github_persistence_config()
    if not github_config:
        return (
            "warning",
            "Saved to pronunciations.json in this app session. Add GitHub secrets to commit changes back to the repo.",
        )

    try:
        commit_url = save_pronunciations_to_github(data, **github_config)
    except PronunciationStoreError as exc:
        return (
            "warning",
            f"Saved locally, but the GitHub update failed: {exc}",
        )

    if commit_url:
        return ("success", f"Pronunciations updated and committed to GitHub: {commit_url}")

    return ("success", "Pronunciations updated and committed to GitHub.")


def show_pronunciation_update_message() -> None:
    message = st.session_state.pop("pronunciation_update_message", "")
    level = st.session_state.pop("pronunciation_update_level", "success")
    if not message:
        return

    if level == "warning":
        st.warning(message)
    elif level == "error":
        st.error(message)
    else:
        st.success(message)


def reset_answer_state() -> None:
    st.session_state.answer_locked = False
    st.session_state.feedback = None
    st.session_state.show_pronunciation = False
    st.session_state.selected_consonant = None
    st.session_state.selected_vowel = None


def practice_set_signature(eligible_keys: list[str]) -> tuple[str, ...]:
    return tuple(eligible_keys)


def refill_card_queue(
    eligible_keys: list[str],
    *,
    exclude_key: Optional[str] = None,
    avoid_next_key: Optional[str] = None,
) -> None:
    st.session_state.card_queue = build_card_queue(
        eligible_keys,
        exclude_key=exclude_key,
        avoid_next_key=avoid_next_key,
    )
    st.session_state.card_queue_signature = practice_set_signature(eligible_keys)


def sync_card_queue(eligible_keys: list[str]) -> None:
    signature = practice_set_signature(eligible_keys)

    if st.session_state.get("card_queue_signature") == signature:
        return

    current_key = st.session_state.get("current_key")
    exclude_key = current_key if current_key in eligible_keys else None
    refill_card_queue(
        eligible_keys,
        exclude_key=exclude_key,
        avoid_next_key=current_key,
    )


def choose_new_card(eligible_keys: list[str]) -> None:
    if not st.session_state.get("card_queue"):
        refill_card_queue(
            eligible_keys,
            avoid_next_key=st.session_state.get("current_key"),
        )

    st.session_state.current_key = st.session_state.card_queue.pop()
    reset_answer_state()


def reset_named_answer_state(prefix: str) -> None:
    st.session_state[f"{prefix}_answer_locked"] = False
    st.session_state[f"{prefix}_feedback"] = None
    st.session_state[f"{prefix}_selected_answer"] = None


def initialize_named_quiz(prefix: str) -> None:
    defaults = {
        f"{prefix}_queue": [],
        f"{prefix}_queue_signature": None,
        f"{prefix}_current_key": None,
        f"{prefix}_selected_answer": None,
        f"{prefix}_answer_locked": False,
        f"{prefix}_feedback": None,
        f"{prefix}_stats": new_quiz_stats(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_named_quiz(prefix: str) -> None:
    st.session_state[f"{prefix}_queue"] = []
    st.session_state[f"{prefix}_queue_signature"] = None
    st.session_state[f"{prefix}_current_key"] = None
    st.session_state[f"{prefix}_stats"] = new_quiz_stats()
    reset_named_answer_state(prefix)


def available_cards(selected_consonants: list[str], selected_vowels: list[str]) -> list[str]:
    consonants = [CONSONANT_BY_MEI[mei] for mei in selected_consonants]
    vowels = [VOWEL_BY_TAMIL[tamil] for tamil in selected_vowels]
    return [compound.key for compound in all_compounds(consonants, vowels)]


def select_answer(letter: str, state_key: str) -> None:
    st.session_state[state_key] = letter


def filter_state_key(kind: str, letter: str) -> str:
    codepoints = "_".join(f"{ord(character):04x}" for character in letter)
    return f"filter_{kind}_{codepoints}"


def set_filter_letters(kind: str, letters: list[str], enabled: bool) -> None:
    for letter in letters:
        st.session_state[filter_state_key(kind, letter)] = enabled


def render_sidebar_letter_filter(
    *,
    kind: str,
    title: str,
    rows: tuple[tuple[str, ...], ...],
    all_letters: list[str],
    columns_per_row: int,
    row_labels: Optional[tuple[str, ...]] = None,
) -> list[str]:
    st.markdown(f"**{title}**")
    action_cols = st.columns(2)
    if action_cols[0].button("All", key=f"{kind}_filter_all", width="stretch"):
        set_filter_letters(kind, all_letters, True)
    if action_cols[1].button("None", key=f"{kind}_filter_none", width="stretch"):
        set_filter_letters(kind, all_letters, False)

    for row_index, row in enumerate(rows):
        if row_labels:
            st.caption(row_labels[row_index])

        columns = st.columns(columns_per_row, gap="small")
        for letter_index, letter in enumerate(row):
            columns[letter_index % columns_per_row].toggle(
                letter,
                value=True,
                key=filter_state_key(kind, letter),
                width="stretch",
            )

    return [
        letter
        for letter in all_letters
        if st.session_state.get(filter_state_key(kind, letter), True)
    ]


def refill_named_queue(
    prefix: str,
    eligible_keys: list[str],
    *,
    exclude_key: Optional[str] = None,
    avoid_next_key: Optional[str] = None,
) -> None:
    st.session_state[f"{prefix}_queue"] = build_card_queue(
        eligible_keys,
        exclude_key=exclude_key,
        avoid_next_key=avoid_next_key,
    )
    st.session_state[f"{prefix}_queue_signature"] = practice_set_signature(eligible_keys)


def sync_named_queue(prefix: str, eligible_keys: list[str]) -> None:
    signature = practice_set_signature(eligible_keys)

    if st.session_state.get(f"{prefix}_queue_signature") == signature:
        return

    current_key = st.session_state.get(f"{prefix}_current_key")
    exclude_key = current_key if current_key in eligible_keys else None
    refill_named_queue(
        prefix,
        eligible_keys,
        exclude_key=exclude_key,
        avoid_next_key=current_key,
    )


def choose_named_card(prefix: str, eligible_keys: list[str]) -> None:
    queue_key = f"{prefix}_queue"

    if not st.session_state.get(queue_key):
        refill_named_queue(
            prefix,
            eligible_keys,
            avoid_next_key=st.session_state.get(f"{prefix}_current_key"),
        )

    st.session_state[f"{prefix}_current_key"] = st.session_state[queue_key].pop()
    reset_named_answer_state(prefix)


def render_letter_grid(
    rows: tuple[tuple[str, ...], ...],
    available_letters: list[str],
    selected_letter: Optional[str],
    state_key: str,
    key_prefix: str,
    row_labels: Optional[tuple[str, ...]] = None,
    disabled: bool = False,
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
                disabled=letter not in available or disabled,
                width="stretch",
                on_click=select_answer,
                args=(letter, state_key),
            )


def render_option_grid(
    rows: tuple[tuple[tuple[str, str], ...], ...],
    available_keys: list[str],
    selected_key: Optional[str],
    state_key: str,
    key_prefix: str,
    disabled: bool = False,
) -> None:
    available = set(available_keys)

    for row_index, row in enumerate(rows):
        columns = st.columns(6, gap="small")
        for column_index, (option_key, label) in enumerate(row):
            is_selected = selected_key == option_key
            columns[column_index].button(
                label,
                key=f"{key_prefix}_{row_index}_{column_index}",
                type="primary" if is_selected else "secondary",
                disabled=option_key not in available or disabled,
                width="stretch",
                on_click=select_answer,
                args=(option_key, state_key),
            )


def vowel_pronunciation_rows() -> tuple[tuple[tuple[str, str], ...], ...]:
    return (
        tuple(
            (vowel_tamil, pronunciation_for(vowel_tamil, "vowel"))
            for vowel_tamil, _ in VOWEL_PAIRS
        ),
        tuple(
            (vowel_tamil, pronunciation_for(vowel_tamil, "vowel"))
            for _, vowel_tamil in VOWEL_PAIRS
        ),
    )


def consonant_pronunciation_rows() -> tuple[tuple[tuple[str, str], ...], ...]:
    return tuple(
        tuple((mei, pronunciation_for(mei, "consonant")) for mei in consonants)
        for _, consonants in CONSONANT_GROUPS
    )


def render_quiz_metrics(stats: dict[str, int]) -> None:
    accuracy = round((stats["correct"] / stats["attempts"]) * 100) if stats["attempts"] else 0
    metric_cols = st.columns(4)
    metric_cols[0].metric("Correct", stats["correct"])
    metric_cols[1].metric("Attempts", stats["attempts"])
    metric_cols[2].metric("Accuracy", f"{accuracy}%")
    metric_cols[3].metric("Streak", stats["streak"])


def render_pronunciation_quiz(
    *,
    prefix: str,
    eligible_keys: list[str],
    option_rows: tuple[tuple[tuple[str, str], ...], ...],
    pronunciation_kind: str,
    empty_message: str,
) -> None:
    if not eligible_keys:
        st.warning(empty_message)
        return

    sync_named_queue(prefix, eligible_keys)

    if (
        st.session_state.get(f"{prefix}_current_key") not in eligible_keys
        and not st.session_state[f"{prefix}_answer_locked"]
    ):
        choose_named_card(prefix, eligible_keys)

    current_key = st.session_state[f"{prefix}_current_key"]
    selected_key = st.session_state[f"{prefix}_selected_answer"]
    stats = st.session_state[f"{prefix}_stats"]
    current_pronunciation = pronunciation_for(current_key, pronunciation_kind)

    render_quiz_metrics(stats)
    st.markdown(
        f'<div class="letter-card"><span>{current_key}</span></div>',
        unsafe_allow_html=True,
    )
    render_option_grid(
        rows=option_rows,
        available_keys=eligible_keys,
        selected_key=selected_key,
        state_key=f"{prefix}_selected_answer",
        key_prefix=f"{prefix}_answer",
        disabled=st.session_state[f"{prefix}_answer_locked"],
    )

    selected_text = (
        pronunciation_for(selected_key, pronunciation_kind) if selected_key else "None"
    )
    st.markdown(
        f'<div class="answer-line">{selected_text}</div>',
        unsafe_allow_html=True,
    )

    action_cols = st.columns([1, 1, 4])
    submitted = action_cols[0].button(
        "Check answer",
        type="primary",
        disabled=st.session_state[f"{prefix}_answer_locked"] or not selected_key,
        width="stretch",
        key=f"{prefix}_check",
    )
    next_clicked = action_cols[1].button(
        "Next",
        width="stretch",
        key=f"{prefix}_next",
    )

    if submitted:
        selected_pronunciation = pronunciation_for(selected_key, pronunciation_kind)
        is_correct = selected_pronunciation == current_pronunciation
        stats["attempts"] += 1

        if is_correct:
            stats["correct"] += 1
            stats["streak"] += 1
            stats["best_streak"] = max(stats["best_streak"], stats["streak"])
        else:
            stats["streak"] = 0

        st.session_state[f"{prefix}_answer_locked"] = True
        st.session_state[f"{prefix}_feedback"] = {
            "is_correct": is_correct,
            "answer": f"{current_key}  {current_pronunciation}",
        }
        st.rerun()

    if next_clicked:
        choose_named_card(prefix, eligible_keys)
        st.rerun()

    feedback = st.session_state[f"{prefix}_feedback"]
    if feedback:
        if feedback["is_correct"]:
            st.success("Correct")
        else:
            st.error("Not quite")
        st.markdown(
            f'<div class="answer-line">{feedback["answer"]}</div>',
            unsafe_allow_html=True,
        )


def render_pronunciation_settings() -> None:
    show_pronunciation_update_message()

    if st.button("Reset defaults", key="reset_pronunciations", width="content"):
        vowel_defaults = default_vowel_pronunciations()
        consonant_defaults = default_consonant_pronunciations()
        compound_vowel_defaults = default_compound_vowel_pronunciations()
        compound_consonant_defaults = default_compound_consonant_pronunciations()
        level, message = persist_pronunciations(
            vowel_defaults,
            consonant_defaults,
            compound_vowel_defaults,
            compound_consonant_defaults,
        )
        st.session_state.vowel_pronunciations = vowel_defaults
        st.session_state.consonant_pronunciations = consonant_defaults
        st.session_state.compound_vowel_pronunciations = compound_vowel_defaults
        st.session_state.compound_consonant_pronunciations = compound_consonant_defaults
        st.session_state.pop("vowel_pronunciation_editor", None)
        st.session_state.pop("consonant_pronunciation_editor", None)
        st.session_state.pronunciation_update_level = level
        st.session_state.pronunciation_update_message = message
        reset_all_answer_states()
        st.rerun()

    st.markdown("**Vowels**")
    vowel_rows = st.data_editor(
        pronunciation_rows("vowel", [vowel.tamil for vowel in VOWELS]),
        hide_index=True,
        disabled=["Letter"],
        key="vowel_pronunciation_editor",
        width="stretch",
        column_config={
            "Letter": st.column_config.TextColumn("Letter", width="small"),
            "Pronunciation": st.column_config.TextColumn("Pronunciation", width="medium"),
            "Compound pronunciation": st.column_config.TextColumn(
                "Compound pronunciation",
                width="medium",
            ),
        },
    )

    st.markdown("**Consonants**")
    consonant_rows = st.data_editor(
        pronunciation_rows("consonant", [consonant.mei for consonant in CONSONANTS]),
        hide_index=True,
        disabled=["Letter"],
        key="consonant_pronunciation_editor",
        width="stretch",
        column_config={
            "Letter": st.column_config.TextColumn("Letter", width="small"),
            "Pronunciation": st.column_config.TextColumn("Pronunciation", width="medium"),
            "Compound pronunciation": st.column_config.TextColumn(
                "Compound pronunciation",
                width="medium",
            ),
        },
    )

    if st.button("Apply changes", type="primary", key="apply_pronunciations", width="content"):
        vowel_updates, compound_vowel_updates, invalid_vowels = clean_pronunciation_rows(
            vowel_rows,
            [vowel.tamil for vowel in VOWELS],
        )
        (
            consonant_updates,
            compound_consonant_updates,
            invalid_consonants,
        ) = clean_pronunciation_rows(
            consonant_rows,
            [consonant.mei for consonant in CONSONANTS],
        )

        if invalid_vowels or invalid_consonants:
            st.error("Every pronunciation must have a value.")
        else:
            level, message = persist_pronunciations(
                vowel_updates,
                consonant_updates,
                compound_vowel_updates,
                compound_consonant_updates,
            )
            st.session_state.vowel_pronunciations = vowel_updates
            st.session_state.consonant_pronunciations = consonant_updates
            st.session_state.compound_vowel_pronunciations = compound_vowel_updates
            st.session_state.compound_consonant_pronunciations = (
                compound_consonant_updates
            )
            reset_all_answer_states()
            st.session_state.pronunciation_update_level = level
            st.session_state.pronunciation_update_message = message
            st.rerun()


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

if "card_queue" not in st.session_state:
    st.session_state.card_queue = []

if "card_queue_signature" not in st.session_state:
    st.session_state.card_queue_signature = None

initialize_pronunciations()
initialize_named_quiz("vowel_test")
initialize_named_quiz("consonant_test")


st.title("Tamil Letter Practice")

with st.sidebar:
    st.header("Practice Set")
    selected_vowels = render_sidebar_letter_filter(
        kind="vowel",
        title="Vowels",
        rows=VOWEL_PAIRS,
        all_letters=[vowel.tamil for vowel in VOWELS],
        columns_per_row=2,
    )
    selected_consonants = render_sidebar_letter_filter(
        kind="consonant",
        title="Consonants",
        rows=tuple(group[1] for group in CONSONANT_GROUPS),
        all_letters=[consonant.mei for consonant in CONSONANTS],
        columns_per_row=3,
        row_labels=tuple(group[0] for group in CONSONANT_GROUPS),
    )
    review_missed = st.toggle(
        "Review missed only",
        value=False,
        disabled=not st.session_state.stats["missed"],
    )

    if st.button("Reset score", width="stretch"):
        reset_stats()
        st.session_state.current_key = None
        st.session_state.card_queue = []
        st.session_state.card_queue_signature = None
        reset_answer_state()
        reset_named_quiz("vowel_test")
        reset_named_quiz("consonant_test")
        st.rerun()

    can_edit_pronunciations = render_pronunciation_admin_gate()


eligible_keys = available_cards(selected_consonants, selected_vowels)

if review_missed:
    missed_keys = set(st.session_state.stats["missed"])
    eligible_keys = [key for key in eligible_keys if key in missed_keys]

if eligible_keys:
    sync_card_queue(eligible_keys)

if (
    st.session_state.get("current_key") not in eligible_keys
    and not st.session_state.answer_locked
    and eligible_keys
):
    choose_new_card(eligible_keys)

if st.session_state.get("selected_consonant") not in selected_consonants:
    st.session_state.selected_consonant = None

if st.session_state.get("selected_vowel") not in selected_vowels:
    st.session_state.selected_vowel = None

stats = st.session_state.stats
accuracy = round((stats["correct"] / stats["attempts"]) * 100) if stats["attempts"] else 0

tab_names = [
    "Practice",
    "Vowel test",
    "Consonant test",
]
if can_edit_pronunciations:
    tab_names.append("Pronunciations")
tab_names.extend(["Letter table", "Missed"])

tabs = dict(zip(tab_names, st.tabs(tab_names)))
practice_tab = tabs["Practice"]
vowel_tab = tabs["Vowel test"]
consonant_tab = tabs["Consonant test"]
settings_tab = tabs.get("Pronunciations")
table_tab = tabs["Letter table"]
missed_tab = tabs["Missed"]

with practice_tab:
    if not eligible_keys:
        st.warning("The current filters have no compound letters to practise.")
    else:
        current = compound_by_key(st.session_state.current_key)
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
            disabled=st.session_state.answer_locked,
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
            disabled=st.session_state.answer_locked,
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
                "consonant_latin": pronunciation_for(
                    current.consonant.mei,
                    "compound_consonant",
                ),
                "vowel": current.vowel.tamil,
                "vowel_latin": pronunciation_for(
                    current.vowel.tamil,
                    "compound_vowel",
                ),
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

with vowel_tab:
    render_pronunciation_quiz(
        prefix="vowel_test",
        eligible_keys=selected_vowels,
        option_rows=vowel_pronunciation_rows(),
        pronunciation_kind="vowel",
        empty_message="Select at least one vowel in the sidebar.",
    )

with consonant_tab:
    render_pronunciation_quiz(
        prefix="consonant_test",
        eligible_keys=selected_consonants,
        option_rows=consonant_pronunciation_rows(),
        pronunciation_kind="consonant",
        empty_message="Select at least one consonant in the sidebar.",
    )

if settings_tab is not None:
    with settings_tab:
        render_pronunciation_settings()

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
