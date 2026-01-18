"""main"""

from logging_config import setup_logging
from slack_emoji_race.huga import Huga

setup_logging()

if __name__ == "__main__":
    Huga().piyo()
