from __future__ import annotations

import random
import time


class Throttle:
    def __init__(self, min_seconds: float = 1.5, max_seconds: float = 3.0) -> None:
        self.min_seconds = min_seconds
        self.max_seconds = max_seconds

    def wait(self) -> None:
        sleep_for = random.uniform(self.min_seconds, self.max_seconds)
        time.sleep(sleep_for)
