import pygame
import os

# --- 基础路径设置 ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FONT_PATH = "C:/Windows/Fonts/msgothic.ttc"  # Windows 默认日文字体

# --- 窗口参数 ---
WIDTH, HEIGHT = 900, 600
FPS = 60

# --- 颜色主题 (木纹风) ---
# 这里的颜色可以在 Google 搜 "Wood Color Palette" 找更好看的
BG_COLOR = (200, 200, 200)  # 修改为近白色
WOOD_DARK = (61, 43, 31)    # 深褐色 (背景)
WOOD_LIGHT = (133, 94, 66)  # 浅木色 (按钮背景)
GOLD = (212, 175, 55)       # 金色 (高亮/边框)
WHITE = (240, 240, 240)
BLACK = (20, 20, 20)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
SAKURA = (229, 82, 103)
SALMON = (248, 131, 147)

# --- 默认游戏设置 ---
DEFAULT_SETTINGS = {
    "difficulty": "EASY",   # EASY, MEDIUM, HARD
    "time_limit": 60,       # 秒
    "furigana": True,       # 是否显示假名
    "sound": True           # 是否开启音效
}

COURSE_COSTS = {
    "EASY": 3000,
    "MEDIUM": 5000,
    "HARD": 10000
}

# ===== 计分/连打参数 =====
COMBO_STEP = 0.08
COMBO_CAP = 25

TIME_BONUS_EVERY = 10   # 每多少连击奖励一次
TIME_BONUS_AMOUNT = 1   # 每次奖励多少秒
TIME_BONUS_CAP = 10     # 整局最多加多少秒

# 按“目标最短罗马字长度”分档（你可以后面再调数值）
# (上限, base分)
PRICE_TIERS = [
    (5,  80),
    (8,  120),
    (11, 180),
    (999, 250),
]
