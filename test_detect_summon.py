import re
from unittest.mock import MagicMock

class MockOracle:
    def __init__(self, valid_agents=None, registry=None):
        self.valid_agents = valid_agents or set()
        self.registry = registry or MagicMock()

    def _detect_summon(self, query: str):
        query_stripped = query.strip()
        if not query_stripped:
            return None

        start_match = re.match(r'^@(\w+)\s+(.*)', query_stripped)
        if start_match:
            entity_name = start_match.group(1).lower()
            if self.registry.get(entity_name) or entity_name in self.valid_agents:
                return (entity_name, start_match.group(2))

        mentions = re.findall(r'@(\w+)', query_stripped)
        for m in mentions:
            entity_name = m.lower()
            if self.registry.get(entity_name) or entity_name in self.valid_agents:
                return (entity_name, query_stripped)

        hey_match = re.match(r'^(?:hey|hi|summon)\s+(\w+),?\s+(.*)', query_stripped, re.IGNORECASE)
        if hey_match:
            entity_name = hey_match.group(1).lower()
            if self.registry.get(entity_name) or entity_name in self.valid_agents:
                return (entity_name, hey_match.group(2))

        return None

def test():
    # Setup
    registry = MagicMock()
    registry.get.side_effect = lambda name: name if name in ["sysadmin", "maat"] else None
    valid_agents = {"lilith", "roc_racoon"}
    oracle = MockOracle(valid_agents=valid_agents, registry=registry)

    test_cases = [
        ("@sysAdmin how do I deploy a container?", ("sysadmin", "how do I deploy a container?")),
        ("Hello @sysAdmin, can you help me with the server?", ("sysadmin", "Hello @sysAdmin, can you help me with the server?")),
        ("@lilith hello", ("lilith", "hello")),
        ("Hello @lilith, how are you?", ("lilith", "Hello @lilith, how are you?")),
        ("@roc_racoon mine the logs", ("roc_racoon", "mine the logs")),
        ("Hello @roc_racoon, mine the logs", ("roc_racoon", "Hello @roc_racoon, mine the logs")),
        ("@unknown_agent hello", None),
        ("just a normal query", None),
        ("hey Maat, help me", ("maat", "help me")),
    ]

    for query, expected in test_cases:
        result = oracle._detect_summon(query)
        print(f"Query: {query} -> Result: {result} (Expected: {expected})")
        assert result == expected

    print("All tests passed!")

if __name__ == "__main__":
    test()
