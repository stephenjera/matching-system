import pytest
from class_matching_system import MatchingSystem


system = MatchingSystem()


class TestMatchingSystem:
    def test_get_matches(self):
        assert type(system.get_matches()) == list

    def test_get_past_matches(self):
        assert type(system.get_past_matches()) == list
