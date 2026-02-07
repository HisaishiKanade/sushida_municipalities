import pygame
import os
from .config import WIDTH, HEIGHT, BASE_DIR

class Resources:
    _images = {}
    _sushi_imgs = []      # 寿司图片列表
    _combo_sounds = []    # 下标0..7 对应 combo(1)..combo(8)
    _se = {} 
    _bgm = {}            # ✅新增：bgm 名称->文件路径
    _current_bgm = None  # ✅新增：当前正在播放的 bgm key
    _se_volume = 0.8
    _bgm_volume = 0.6

    @classmethod
    def load_all(cls):
        """统一加载所有素材"""
        assets_dir = os.path.join(BASE_DIR, "assets")

        # 1. 加载背景图（统一放到 assets/bg）
        bg_dir = os.path.join(assets_dir, "bg")

        bg_files = {
            "open_bg": "open_bg.png",
            "game_bg": "game_bg.png",
            "success_bg": "success_bg.png",
            "fail_bg": "fail_bg.png",
        }

        for key, fname in bg_files.items():
            p = os.path.join(bg_dir, fname)
            if os.path.exists(p):
                img = pygame.image.load(p).convert()
                cls._images[key] = pygame.transform.scale(img, (WIDTH, HEIGHT))
            else:
                print(f"提示: 找不到背景图 {p}")


        sushi_dir = os.path.join(assets_dir, "sushi")
        cls._sushi_imgs = []
        for i in range(1, 20):
            path = os.path.join(sushi_dir, f"sushi ({i}).png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (220, 150))
                cls._sushi_imgs.append(img)
            else:
                print(f"提示: 找不到寿司图片 {path}")

        # ===== 音效：combo =====
        se_dir = os.path.join(assets_dir, "se")
        combo_dir = os.path.join(se_dir, "combo")

        cls._combo_sounds = []
        for i in range(1, 9):
            p = os.path.join(combo_dir, f"combo ({i}).mp3")
            if os.path.exists(p):
                cls._combo_sounds.append(pygame.mixer.Sound(p))
            else:
                print(f"提示: 找不到 combo 音效 {p}")

        
        # ====== ✅新增：加载单个 SE 音效 ======
        cls._se = {}
        se_files = [
            "start", "go", "clear", "miss", "success", "fail", "button"
        ]
        for name in se_files:
            p = os.path.join(se_dir, f"{name}.mp3")
            if os.path.exists(p):
                cls._se[name] = pygame.mixer.Sound(p)
            else:
                print(f"提示: 找不到 SE 音效 {p}")

        # ====== ✅新增：BGM 路径 ======
        bgm_dir = os.path.join(assets_dir, "bgm")
        cls._bgm = {
            "welcome": os.path.join(bgm_dir, "01_welcome.mp3"),
            "game":    os.path.join(bgm_dir, "02_game.mp3"),
            "sum":     os.path.join(bgm_dir, "03_sum.mp3"),
        }
        cls._current_bgm = None


    @classmethod
    def get_img(cls, name):
        return cls._images.get(name)

    @classmethod
    def get_random_sushi(cls):
        """随机获取一个寿司形象"""
        import random
        return random.choice(cls._sushi_imgs) if cls._sushi_imgs else None

    @classmethod
    def play_combo(cls, combo_level: int):
        """combo_level: 1,2,3...；超过8一直播放8"""
        if not cls._combo_sounds:
            return
        level = max(1, int(combo_level))
        level = min(level, 8)
        snd = cls._combo_sounds[level - 1]
        snd.set_volume(cls._se_volume)
        snd.play()

    @classmethod
    def play_se(cls, name: str):
        s = cls._se.get(name)
        if s:
            s.set_volume(cls._se_volume)
            s.play()

    @classmethod
    def play_bgm(cls, key: str, loop: bool = True, volume: float | None = None):
        """key: 'welcome'/'game'/'sum'。重复调用同一首不会重播。"""
        path = cls._bgm.get(key)
        if not path or not os.path.exists(path):
            print(f"提示: 找不到 BGM {key}: {path}")
            return

        if cls._current_bgm == key:
            return  # ✅同一首不用重复 load/play

        cls._current_bgm = key
        pygame.mixer.music.load(path)
        
        if volume is None:
            volume = cls._bgm_volume
        else:
            cls._bgm_volume = max(0.0, min(1.0, float(volume)))

        pygame.mixer.music.set_volume(cls._bgm_volume)
        pygame.mixer.music.play(-1 if loop else 0)

    @classmethod
    def stop_bgm(cls):
        cls._current_bgm = None
        pygame.mixer.music.stop()

    @classmethod
    def set_se_volume(cls, v: float):
        cls._se_volume = max(0.0, min(1.0, float(v)))

    @classmethod
    def set_bgm_volume(cls, v: float):
        cls._bgm_volume = max(0.0, min(1.0, float(v)))
        pygame.mixer.music.set_volume(cls._bgm_volume) 