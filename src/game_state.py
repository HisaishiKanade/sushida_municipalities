TIME_LIMITS = {
    "EASY": 60,
    "MEDIUM": 90,
    "HARD": 120
}


class GameSettings:
        

    def __init__(self):
        self.difficulty = "EASY"
        self.time_limit = TIME_LIMITS[self.difficulty]
        self.show_roma = True
        self.furigana = True

    def apply_difficulty(self, diff: str):
        self.difficulty = diff
        self.time_limit = TIME_LIMITS.get(diff, 60)

    def __repr__(self):
        return (
            f"配置(难度={self.difficulty}, 时间={self.time_limit}s, "
            f"ローマ字={'ON' if self.show_roma else 'OFF'}, "
            f"ふりがな={'ON' if self.furigana else 'OFF'})"
        )
