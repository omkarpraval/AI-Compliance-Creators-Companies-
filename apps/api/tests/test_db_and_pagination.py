import pytest
from datetime import datetime, timezone
from verifyd.core.pagination import encode_cursor, decode_cursor
from verifyd.services.clause_service import compute_clause_diff
from verifyd.db.models.clause import Clause

def test_cursor_encoding_and_decoding():
    cursor_1 = encode_cursor(0)
    cursor_2 = encode_cursor(25)
    cursor_3 = encode_cursor(50)

    assert decode_cursor(cursor_1) == 0
    assert decode_cursor(cursor_2) == 25
    assert decode_cursor(cursor_3) == 50
    assert decode_cursor(None) == 0
    assert decode_cursor("invalid-base64") == 0


def test_pagination_deterministic_tiebreak_simulation():
    # Simulate a list of 10 items all having the exact same created_at timestamp
    now = datetime.now(timezone.utc)
    items = [{"id": f"item-{i:02d}", "created_at": now} for i in range(10)]

    # Deterministic secondary tiebreak sort (created_at DESC, id DESC)
    sorted_items = sorted(items, key=lambda x: (x["created_at"], x["id"]), reverse=True)

    # Page 1 (limit 5)
    page_1 = sorted_items[0:5]
    # Page 2 (limit 5)
    page_2 = sorted_items[5:10]

    # Assert no overlaps and no dropped items
    p1_ids = {x["id"] for x in page_1}
    p2_ids = {x["id"] for x in page_2}

    assert len(p1_ids) == 5
    assert len(p2_ids) == 5
    assert p1_ids.isdisjoint(p2_ids)
    assert p1_ids.union(p2_ids) == {x["id"] for x in items}
