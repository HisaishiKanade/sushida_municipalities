import pygame
import sys
from src.config import *
from src.scenes import TitleScene, OptionScene, GameScene, ResultScene
from src.resources import Resources

def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)  
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("寿司打-全国自治体Ver.")
    pygame.key.set_repeat(500, 50)

    Resources.load_all()
    Resources.play_bgm("welcome") 

    clock = pygame.time.Clock()
    current_scene = TitleScene()

    print("游戏启动成功！等待输入...")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                current_scene.handle_event(event)

        current_scene.update()

        if current_scene.next_scene != current_scene:
            print(f"切换场景: {type(current_scene).__name__} -> {type(current_scene.next_scene).__name__}")
            current_scene = current_scene.next_scene

            # ✅根据场景类型切换 BGM
            if isinstance(current_scene, (TitleScene, OptionScene)):
                Resources.play_bgm("welcome")
            elif isinstance(current_scene, GameScene):
                Resources.play_bgm("game")
            elif isinstance(current_scene, ResultScene):
                Resources.play_bgm("sum")

        current_scene.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()