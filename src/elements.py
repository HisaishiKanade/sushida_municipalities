import pygame
from .config import *

class UIElement:
    """所有 UI 组件的基类"""
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def update(self):
        pass

    def draw(self, screen):
        pass

    def handle_event(self, event):
        pass


class TextLabel(UIElement):
    """纯文本标签，用于显示标题或说明"""
    def __init__(self, x, y, text, font_size=30, color=WHITE, center=True):
        super().__init__(x, y, 0, 0)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(FONT_PATH, font_size)
        self.center = center
        self._render()

    def _render(self):
        self.surf = self.font.render(self.text, True, self.color)
        if self.center:
            # 如果是居中模式，x, y 视为中心点
            self.rect = self.surf.get_rect(center=(self.rect.x, self.rect.y))
        else:
            self.rect = self.surf.get_rect(topleft=(self.rect.x, self.rect.y))

    def draw(self, screen):
        screen.blit(self.surf, self.rect)


class Button(UIElement):
    """普通按钮"""
    def __init__(self, x, y, w, h, text, callback=None, font_size=28):
        super().__init__(x, y, w, h)
        self.text = text
        self.callback = callback  # 点击后执行的函数
        self.font = pygame.font.Font(FONT_PATH, font_size)
        self.is_hovered = False
        
    def update(self):
        # 检测鼠标悬停
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
            # 1. 创建一个支持透明度的表面 (Surface)
            s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            
            # 2. 设置颜色和透明度 (RGBA)
            # 悬停时金黄色半透明，平时深木色半透明
            if self.is_hovered:
                bg_color = (212, 175, 55, 220)  # GOLD + Alpha(220)
                text_color = BLACK
            else:
                bg_color = (61, 43, 31, 180)    # WOOD_DARK + Alpha(180)
                text_color = WHITE
    
            # 3. 在表面上画圆角矩形并贴到主屏幕
            pygame.draw.rect(s, bg_color, s.get_rect(), border_radius=12)
            pygame.draw.rect(s, (255, 255, 255, 255), s.get_rect(), 2, border_radius=12) # 亮白边框
            screen.blit(s, self.rect.topleft)
    
            # 4. 绘制文字
            text_surf = self.font.render(self.text, True, text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered: # 左键点击
                if self.callback:
                    self.callback() # 执行回调函数


class OptionBox(UIElement):
    """设置选项框：点击循环切换选项"""
    def __init__(self, x, y, w, h, options, default_index=0, label=""):
        super().__init__(x, y, w, h)
        self.options = options # 例如 ["EASY", "MEDIUM", "HARD"]
        self.index = default_index
        self.label = label # 选项左边的说明文字，例如 "难度:"
        self.font = pygame.font.Font(FONT_PATH, 28)
        self.is_hovered = False

    def get_value(self):
        """获取当前选中的值"""
        return self.options[self.index]

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        # 1. 绘制左侧说明文字
        if self.label:
            label_surf = self.font.render(self.label, True, WHITE)
            # 文字画在按钮左侧 10 像素处
            screen.blit(label_surf, (self.rect.x - label_surf.get_width() - 15, self.rect.y + 10))

        # 2. 绘制选项框背景
        bg_color = GOLD if self.is_hovered else WOOD_LIGHT
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=5)

        # 3. 绘制当前选项文字
        current_text = str(self.options[self.index])
        # 针对布尔值做一点显示优化
        if current_text == "True": current_text = "ON"
        if current_text == "False": current_text = "OFF"
        
        text_color = BLACK if self.is_hovered else WHITE
        text_surf = self.font.render(current_text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                # 循环切换下一个选项
                self.index = (self.index + 1) % len(self.options)