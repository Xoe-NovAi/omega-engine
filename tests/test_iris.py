"""Tests for Iris Intent Matcher."""

from omega.iris.matcher import IntentMatcher


def test_classify_summon():
    matcher = IntentMatcher()
    intent, entity = matcher.classify("@Sekhmet give me strength")
    assert intent == "summon"
    assert entity == "Sekhmet"


def test_classify_summon_hey():
    matcher = IntentMatcher()
    intent, entity = matcher.classify("hey lilith, what do you see?")
    assert intent == "summon"
    assert entity == "lilith"


def test_classify_greeting():
    matcher = IntentMatcher()
    intent, entity = matcher.classify("hello")
    assert intent == "direct"
    assert entity is None


def test_classify_farewell():
    matcher = IntentMatcher()
    intent, entity = matcher.classify("thank you")
    assert intent == "direct"
    assert entity is None


def test_classify_domain():
    matcher = IntentMatcher()
    intent, entity = matcher.classify("what is the meaning of justice?")
    assert intent == "domain"
    assert entity is None


def test_is_iris_capable():
    matcher = IntentMatcher()
    assert matcher.is_iris_capable("hello") is True
    assert matcher.is_iris_capable("bye") is True
    assert matcher.is_iris_capable("what can you do?") is True
    assert matcher.is_iris_capable("what is justice?") is False


def test_iris_response():
    matcher = IntentMatcher()
    response = matcher.iris_response("hello")
    assert response is not None
    assert "Iris" in response

    response = matcher.iris_response("help")
    assert response is not None
    assert "Pillar Keepers" in response

    response = matcher.iris_response("what is quantum physics?")
    assert response is None  # Iris cannot answer this directly
