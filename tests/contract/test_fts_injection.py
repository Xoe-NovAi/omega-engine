"""Contract Tests — P2-6 FTS5 MATCH Syntax Injection Prevention.

[P2-6 / §4 audit] FTS5 has its own query grammar (AND/OR/NOT/NEAR, "phrase",
-exclude, *). An unescaped user search string containing these tokens
triggers `sqlite3.OperationalError: fts5: syntax error` — a
denial-of-service-by-error. The `escape_fts_query()` helper neutralizes
FTS5 metacharacters by wrapping each token in double quotes.

[T10: Integrity] Malformed FTS queries degrade gracefully (return []),
never propagate a raw DB error to the caller.
"""

import sqlite3
from pathlib import Path

import pytest

from omega.memory.fts_index import ConversationFTSIndex, escape_fts_query


class TestEscapeFtsQuery:
    """Unit tests for the canonical FTS5 escaper."""

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("hello world", '"hello" "world"'),
            ("simple", '"simple"'),
            ("", ""),
            ("   ", ""),
            ('quote"test', '"quote\\"test"'),
            ("AND OR NOT", '"AND" "OR" "NOT"'),
            ("NEAR -exclude *", '"NEAR" "-exclude" "*"'),
            ("(group) by", '"(group)" "by"'),
        ],
    )
    def test_escapes_special_tokens(self, raw, expected):
        assert escape_fts_query(raw) == expected

    def test_no_unescaped_metacharacters(self):
        """Escaped output must not contain bare FTS5 operators."""
        for evil in ["AND", "OR", "NOT", "NEAR", "*", "-", "(", ")"]:
            out = escape_fts_query(f"test {evil} foo")
            # Each token is wrapped in quotes — operators are inert.
            assert f'"{evil}"' in out


class TestFtsSearchDegradesGracefully:
    """ConversationFTSIndex.search must not raise on malformed FTS queries."""

    @pytest.fixture
    def fts(self, tmp_path: Path):
        idx = ConversationFTSIndex(tmp_path / "test_fts.db")
        idx.initialize()
        yield idx
        idx.close()

    @pytest.mark.anyio
    async def test_malformed_query_returns_empty_not_raise(self, fts):
        """A query with FTS5 special syntax must not raise OperationalError."""
        # Seed an exchange so the table is non-empty.
        await fts.index_exchange("sess-1", "entity-1", "user", "hello world")

        # These would trigger `fts5: syntax error` without escaping.
        for evil in ["\"", "(", ")", "*", "AND", "NEAR", "a\"b"]:
            result = await fts.search(evil, "entity-1", limit=10)
            assert isinstance(result, list), f"search({evil!r}) raised instead of degrading"

    @pytest.mark.anyio
    async def test_normal_query_still_works(self, fts):
        await fts.index_exchange("sess-1", "entity-1", "user", "hello world foo")
        result = await fts.search("hello", "entity-1", limit=10)
        assert len(result) == 1
        assert "hello" in result[0]["content"]
