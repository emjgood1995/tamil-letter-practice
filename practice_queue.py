import random
from typing import Optional, Protocol


class Shuffler(Protocol):
    def shuffle(self, values: list[str]) -> None:
        ...


def build_card_queue(
    eligible_keys: list[str],
    *,
    exclude_key: Optional[str] = None,
    avoid_next_key: Optional[str] = None,
    shuffler: Optional[Shuffler] = None,
) -> list[str]:
    queue = [key for key in eligible_keys if key != exclude_key]

    if not queue and eligible_keys:
        queue = list(eligible_keys)

    active_shuffler = shuffler if shuffler else random
    active_shuffler.shuffle(queue)

    if avoid_next_key and len(queue) > 1 and queue[-1] == avoid_next_key:
        queue[0], queue[-1] = queue[-1], queue[0]

    return queue
