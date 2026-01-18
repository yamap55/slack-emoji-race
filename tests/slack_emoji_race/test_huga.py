from slack_emoji_race.huga import Huga


class TestHuga:
    def test_huga(self):
        assert Huga().piyo() == "piyo"
