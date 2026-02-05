
import pygame
import os
from .config import WIDTH, HEIGHT, BASE_DIR

class Resources:
    _images = {}
    _sushi_imgs = []  # 存放 20 种寿司图片

    @classmethod
    def load_all(cls):
        """统一加载所有素材"""
        assets_dir = os.path.join(BASE_DIR, "assets")
        
        # 1. 加载背景图
        open_bg_path = os.path.join(assets_dir, "open_bg.png")
        if os.path.exists(open_bg_path):
            cls._images["open_bg"] = pygame.image.load(open_bg_path).convert()
            cls._images["open_bg"] = pygame.transform.scale(cls._images["open_bg"], (WIDTH, HEIGHT))

        # 2. 批量加载寿司图片 (移除 sara.png 逻辑，解决报错)
        sushi_dir = os.path.join(assets_dir, "sushi")
        cls._sushi_imgs = []
        for i in range(1, 20):
            # 匹配文件名 "sushi (1).png" 到 "sushi (20).png"
            path = os.path.join(sushi_dir, f"sushi ({i}).png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                # 统一缩放到合适大小
                img = pygame.transform.scale(img, (220, 150))
                cls._sushi_imgs.append(img)
            else:
                print(f"提示: 找不到寿司图片 {path}")

    @classmethod
    def get_img(cls, name):
        return cls._images.get(name)

    @classmethod
    def get_random_sushi(cls):
        """随机获取一个寿司形象"""
        import random
        return random.choice(cls._sushi_imgs) if cls._sushi_imgs else None

