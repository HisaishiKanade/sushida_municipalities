import pygame
import json
import os
import time
import random
from .config import *
from .elements import Button, TextLabel, OptionBox
from .game_state import GameSettings
from .resources import Resources
from .models import SushiPlate

class Scene:
    """场景基类"""
    def __init__(self):
        self.next_scene = self # 默认指向自己，表示不切换
    
    def handle_event(self, event): pass
    def update(self): pass
    def draw(self, screen): pass
    
    def switch_to(self, new_scene):
        self.next_scene = new_scene

# ================= 1. 标题画面 =================
class TitleScene(Scene):
    def __init__(self):
        super().__init__()
        # 标题
        self.background = Resources.get_img("open_bg")
        self.title = TextLabel(WIDTH//2, 150, "寿司打", font_size=80, color=GOLD)
        self.subtitle = TextLabel(WIDTH//2, 230, "全国自治体Ver.", font_size=30, color=WHITE)
        
        # 开始按钮
        self.btn_start = Button(WIDTH//2 - 100, 400, 200, 60, "スタート", 
                                callback=self.go_to_options)

    def go_to_options(self):
        self.switch_to(OptionScene(GameSettings()))

    def update(self):
        self.btn_start.update()

    def draw(self, screen):
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(WOOD_DARK) 
        
        self.title.draw(screen)
        self.subtitle.draw(screen)
        self.btn_start.draw(screen)

    def handle_event(self, event):
        self.btn_start.handle_event(event)


# ================= 2. 设置画面 =================
class OptionScene(Scene):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        
        self.lbl_title = TextLabel(WIDTH//2, 80, "設定", font_size=50, color=WHITE)

        # 难度选择
        self.opt_diff = OptionBox(WIDTH//2 - 100, 180, 200, 50, 
                                  options=["EASY", "MEDIUM", "HARD"], 
                                  label="難易度:")

                                  
        # 罗马音显示开关（根据当前 settings 初始化）
        roma_default = 0 if getattr(self.settings, "show_roma", True) else 1
        self.opt_roma = OptionBox(WIDTH//2 - 100, 240, 200, 50,
                                  options=[True, False],
                                  default_index=roma_default,
                                  label="ローマ字:")
        
        # ふりがな 开关（新加）
        furi_default = 0 if getattr(self.settings, "furigana", True) else 1
        self.opt_furi = OptionBox(WIDTH//2 - 100, 300, 200, 50,
                                  options=[True, False],
                                  default_index=furi_default,
                                  label="ふりがな:")

        # 开始按钮（下移）
        self.btn_go = Button(WIDTH//2 - 100, 480, 200, 60, "GO！",
                             callback=self.start_game)

    def start_game(self):
        diff = self.opt_diff.get_value()
        self.settings.apply_difficulty(diff)
    
        self.settings.show_roma = self.opt_roma.get_value()
        self.settings.furigana = self.opt_furi.get_value()
    
        try:
            self.switch_to(GameScene(self.settings))
        except Exception as e:
            print(f"DEBUG: 进入游戏失败: {e}")

    def update(self):
        self.opt_diff.update()
        self.opt_roma.update()
        self.btn_go.update()
        self.opt_furi.update()

    def draw(self, screen):
        screen.fill(WOOD_DARK)
        self.lbl_title.draw(screen)
        self.opt_diff.draw(screen)
        self.opt_roma.draw(screen)
        self.btn_go.draw(screen)
        self.opt_furi.draw(screen)


    def handle_event(self, event):
        self.opt_diff.handle_event(event)
        self.opt_roma.handle_event(event)
        self.btn_go.handle_event(event)
        self.opt_furi.handle_event(event)


            


# ================= 2. 暂停菜单 =================
class PauseScene(Scene):
    def __init__(self, game_scene):
        super().__init__()
        self.game_scene = game_scene
        
        self.lbl_pause = TextLabel(WIDTH//2, 180, "一時停止中", font_size=60, color=WHITE)

        self.btn_retry = Button(WIDTH//2 - 100, 280, 200, 60, "やり直す", 
                               callback=self.retry_game)
        
        self.btn_exit = Button(WIDTH//2 - 100, 370, 200, 60, "ホーム", 
                              callback=self.go_to_title)
        
        self.btn_resume = Button(WIDTH//2 - 100, 460, 200, 60, "再開", 
                               callback=self.resume_game)
        
        

    def retry_game(self):
        # 重新开始，直接创建一个全新的场景，不会有指针残留问题
        self.switch_to(GameScene(self.game_scene.settings))

    def go_to_title(self):
        self.switch_to(TitleScene())

    def resume_game(self):
        # --- 修复无限切换的核心 ---
        self.game_scene.next_scene = self.game_scene 
        self.switch_to(self.game_scene)

    def update(self):
        self.btn_retry.update()
        self.btn_exit.update()
        self.btn_resume.update()

    def handle_event(self, event):
        # ESC 键也同样调用带修复逻辑的 resume_game
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.resume_game()
        
        self.btn_retry.handle_event(event)
        self.btn_exit.handle_event(event)
        self.btn_resume.handle_event(event)

    def draw(self, screen):
        # 绘制背景
        self.game_scene.draw(screen)
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160)) # 稍微深一点，更有暂停感
        screen.blit(overlay, (0, 0))
        
        self.lbl_pause.draw(screen)
        self.btn_retry.draw(screen)
        self.btn_exit.draw(screen)
        self.btn_resume.draw(screen)
        

# src/scenes.py

# ================= 3. 游戏画面 =================
class GameScene(Scene):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.score = 0
        # ===== 连打/奖励系统 =====
        self.combo = 0
        self.time_bonus = 0  # 已获得的额外时间（秒），参与倒计时
        self.popups = []     # 浮动提示：[{text,x,y,t0,dur}]
        self.popup_base_y = 340

        
        # --- 新增统计数据 ---
        self.correct_keys = 0
        self.miss_keys = 0
        self.total_words_cleared = 0
        
        self.words_pool = self.load_words()
        self.start_time = time.time()
        self.time_left = self.settings.time_limit 
        self.current_plate = None
        self.game_over = False
        
        self.fonts = {
            'kanji': pygame.font.Font(FONT_PATH, 48),
            'furi': pygame.font.Font(FONT_PATH, 26),  # 新增：ふりがな
            'roma': pygame.font.Font(None, 40),
            'ui': pygame.font.Font(FONT_PATH, 28),
            'popup': pygame.font.Font(FONT_PATH, 26)
        }
        self.spawn_plate()
    # src/scenes.py 中的 GameScene 类

    def load_words(self):
        # 根据难度加载不同文件
        filename = f"words_{self.settings.difficulty.lower()}.json"
        path = os.path.join(DATA_DIR, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            print(f"Error loading {path}")
            return [{"kanji": "测试", "kana": "てすと", "roma": "test"}]

    def spawn_plate(self):
        """生成一个新的盘子"""
        if not self.words_pool:
            self.words_pool = self.load_words() # 重新加载或循环
            
        import random
        word_data = random.choice(self.words_pool)
        self.current_plate = SushiPlate(word_data)

    def handle_event(self, event):
        if self.game_over:
            return
    
        # 暂停
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.switch_to(PauseScene(self))
            return
    
        # 只处理文字输入（支持 IME/更稳定）
        if event.type != pygame.TEXTINPUT:
            return
        if not self.current_plate:
            return
    
        # 关键：先拿到 result
        ch = event.text.lower()
        result = self.current_plate.check_input(ch)
    
        if result == "HIT":
            self.correct_keys += 1
    
        elif result == "MISS":
            self.miss_keys += 1
            self.score = max(0, self.score - 5)
    
            # 连打惩罚：减半（想清零就改成 self.combo = 0）
            self.combo = self.combo // 2
    
            if self.combo == 0:
                self.add_popup("COMBO BREAK", WIDTH//2, 360, dur=0.8)
    
        elif result == "CLEARED":
            self.correct_keys += 1
    
            # 1) combo +1
            self.combo += 1
    
            # 2) base 由长度档位决定
            L = getattr(self.current_plate, "target_len", len(getattr(self.current_plate, "display_roma", "")))
            base = self.base_price_by_len(L)
    
            # 3) gain = base * (1 + 0.08*min(combo,25))
            mult = 1 + COMBO_STEP * min(self.combo, COMBO_CAP)
            gain = int(base * mult)
            self.score += gain
    
            # 提示：+分 & combo
            self.add_popup(f"+{gain}円", WIDTH//2, 360, dur=0.9)
            if self.combo >= 2:
                self.add_popup(f"COMBO {self.combo}", WIDTH//2, 330, dur=0.8)
    
            # 4) 小额加时（每10连 +1s，整局最多+10s）
            if (self.combo % TIME_BONUS_EVERY == 0) and (self.time_bonus < TIME_BONUS_CAP):
                self.time_bonus += TIME_BONUS_AMOUNT
                self.add_popup("+1s", WIDTH//2 + 140, 360, dur=0.9)
    
            # 5) 下一个词
            self.total_words_cleared += 1
            self.spawn_plate()

        
                        
                
    def update(self):
        if self.game_over: return
        elapsed = time.time() - self.start_time
        total_limit = self.settings.time_limit + self.time_bonus
        self.time_left = max(0, total_limit - elapsed)

        
        if self.time_left <= 0:
            self.game_over = True
            # --- 统计完成，进入结算 ---
            stats = {
                "score": self.score,
                "correct": self.correct_keys,
                "miss": self.miss_keys,
                "time_spent": max(0.001, elapsed),
                "difficulty": self.settings.difficulty
            }
            self.switch_to(ResultScene(self.settings, stats))
            return 

        if self.current_plate:
            if self.current_plate.update():  # 盘子流失（算未完成）
                self.miss_keys += 1
                self.score = max(0, self.score - 10)  # 可选：漏盘也扣一点分
        
                # 连打惩罚：减半（你也可以改成 0）
                self.combo = 0
        
                # 提示：MISS
                self.add_popup("MISS", WIDTH//2, self.popup_base_y, dur=0.8)
        
                # combo 断了再提示 COMBO BREAK
                if self.combo == 0:
                    self.add_popup("COMBO BREAK", WIDTH//2, self.popup_base_y - 30, dur=0.8)
        
                self.spawn_plate()



    def draw(self, screen):
        # 核心修改：白色背景
        screen.fill(BG_COLOR) 
        BELT_Y = 190   # 轨道整体y（越小越靠上）
        BELT_H = 180
        HUD_Y  = 380   # HUD整体y（越小越靠上）
        HUD_TEXT_DY = 20

        
        # 1. 轨道 (浅灰色的传送带)
        pygame.draw.rect(screen, (255, 255, 255), (0, BELT_Y, WIDTH, BELT_H))
        pygame.draw.line(screen, (210, 210, 210), (0, BELT_Y), (WIDTH, BELT_Y), 3)
        pygame.draw.line(screen, (210, 210, 210), (0, BELT_Y + BELT_H), (WIDTH, BELT_Y + BELT_H), 3)


        # 2. UI 文字 (改为深色以便在白底显示)
        score_surf = self.fonts['ui'].render(f"金額: {self.score} 円", True, BLACK)
        time_surf = self.fonts['ui'].render(f"残り: {int(self.time_left)}s", True, RED)
        screen.blit(score_surf, (30, 30))
        screen.blit(time_surf, (WIDTH - 150, 30))
        if self.combo >= 2:
            combo_surf = self.fonts['ui'].render(f"COMBO: {self.combo}", True, GOLD)
            screen.blit(combo_surf, (30, 65))

        # 3. 焦点输入框 (HUD)
        if self.current_plate and not self.game_over:
            hud_rect = pygame.Rect(WIDTH//2 - 300, HUD_Y, 600, 150)
            pygame.draw.rect(screen, (255, 255, 255), hud_rect, border_radius=15)
            pygame.draw.rect(screen, (200, 200, 200), hud_rect, 2, border_radius=15)
            
            # ====== HUD：都道府县（浅色）+ 市町村（深色） ======
            pref = getattr(self.current_plate, "prefix_kanji", "")
            name = self.current_plate.kanji
            
            pref_surf = self.fonts['kanji'].render(pref, True, (170, 170, 170))
            name_surf = self.fonts['kanji'].render(name, True, BLACK)
            
            total_w_name = pref_surf.get_width() + name_surf.get_width()
            name_start_x = WIDTH // 2 - total_w_name // 2
            
            y_name = HUD_Y + 15 + HUD_TEXT_DY
            pref_x = name_start_x
            name_x = name_start_x + pref_surf.get_width()
            
            screen.blit(pref_surf, (pref_x, y_name))
            screen.blit(name_surf, (name_x, y_name))
            
            # ====== ふりがな：只对准市町村部分（name） ======
            if getattr(self.settings, "furigana", True):
                furi_text = getattr(self.current_plate, "kana", "")
                f_surf = self.fonts['furi'].render(furi_text, True, (120, 120, 120))
            
                name_center_x = name_x + name_surf.get_width() // 2
                f_x = name_center_x - f_surf.get_width() // 2
                f_y = y_name - 28  # 控制ふりがな高度
            
                screen.blit(f_surf, (f_x, f_y))
            
            # ====== ローマ字：红色已输入 + 灰色未输入 ======
            if getattr(self.settings, "show_roma", True):
                typed, remaining = self.current_plate.get_display_text()
            
                t_surf = self.fonts['roma'].render(typed, True, RED)
                u_surf = self.fonts['roma'].render(remaining, True, (150, 150, 150))
            
                total_w_roma = t_surf.get_width() + u_surf.get_width()
                roma_start_x = WIDTH // 2 - total_w_roma // 2
                roma_y = HUD_Y + 75 + HUD_TEXT_DY  # 现在跟 HUD_Y 联动
            
                screen.blit(t_surf, (roma_start_x, roma_y))
                screen.blit(u_surf, (roma_start_x + t_surf.get_width(), roma_y))
                
        now = time.time()
        alive = []
        for p in self.popups:
            t = (now - p["t0"]) / p["dur"]
            if t >= 1:
                continue
        
            # 上浮一点
            y = p["y"] - int(25 * t)
        
            surf = self.fonts.get("popup", self.fonts["ui"]).render(p["text"], True, GOLD)
            rect = surf.get_rect(center=(p["x"], y))
            screen.blit(surf, rect)
        
            alive.append(p)
        
        self.popups = alive
            
        if self.current_plate:
            self.current_plate.draw(screen, self.fonts)

        

                
    def base_price_by_len(self, L: int) -> int:
        for upper, price in PRICE_TIERS:
            if L <= upper:
                return price
        return PRICE_TIERS[-1][1]

    def add_popup(self, text, x, y, dur=0.9):
        self.popups.append({"text": text, "x": x, "y": y, "t0": time.time(), "dur": dur})



# ================= 4. 结算画面 =================
class ResultScene(Scene):
    def __init__(self, settings, stats):
        super().__init__()
        self.settings = settings
        self.stats = stats
        
        # 计算盈亏
        self.earned = stats['score']
        self.cost = COURSE_COSTS.get(stats['difficulty'], 3000)
        self.profit = self.earned - self.cost
        self.kps = stats['correct'] / stats['time_spent'] if stats['time_spent'] > 0 else 0

        # 功能按钮
        self.btn_again = Button(WIDTH//2 - 320, 500, 200, 50, "やり直す", 
                               callback=lambda: self.switch_to(GameScene(self.settings)))
        self.btn_course = Button(WIDTH//2 - 100, 500, 200, 50, "コース選択", 
                                callback=lambda: self.switch_to(OptionScene(self.settings)))
        self.btn_title = Button(WIDTH//2 + 120, 500, 200, 50, "ホーム", 
                               callback=lambda: self.switch_to(TitleScene()))

    def update(self):
        self.btn_again.update()
        self.btn_course.update()
        self.btn_title.update()

    def handle_event(self, event):
        self.btn_again.handle_event(event)
        self.btn_course.handle_event(event)
        self.btn_title.handle_event(event)

    def draw(self, screen):
        screen.fill((240, 220, 200)) # 浅木色背景
        
        # 1. 绘制类似 image_10dc1b.png 的白色纸张
        paper_rect = pygame.Rect(50, 40, WIDTH - 100, 440)
        pygame.draw.rect(screen, WHITE, paper_rect, border_radius=10)
        
        # 2. 标题和课程
        font_main = pygame.font.Font(FONT_PATH, 40)
        font_sub = pygame.font.Font(FONT_PATH, 24) 
        
        header_text = f"{self.settings.difficulty} {self.cost}円コース"
        h_surf = font_sub.render(header_text, True, BLACK)
        screen.blit(h_surf, (WIDTH//2 - h_surf.get_width()//2, 70))

        # 3. 盈亏显示
        res_text = f"{self.earned} 円分ゲット！ - {self.cost} 円払って..."
        r_surf = font_sub.render(res_text, True, (100, 100, 100))
        screen.blit(r_surf, (WIDTH//2 - r_surf.get_width()//2, 130))

        # 盈亏核心大字
        profit_color = RED if self.profit >= 0 else (50, 50, 50)
        profit_msg = f"{abs(self.profit)} 円{'分お得でした！' if self.profit >= 0 else '分損でした...'}"
        p_surf = font_main.render(profit_msg, True, profit_color)
        screen.blit(p_surf, (WIDTH//2 - p_surf.get_width()//2, 200))

        # 4. 底部统计详细项 (KPS等)
        col_y = 320
        stats_labels = ["正確キー", "KPS", "ミス数"]
        stats_vals = [f"{self.stats['correct']}回", f"{self.kps:.1f}回/秒", f"{self.stats['miss']}回"]
        
        for i in range(3):
            col_centers = [WIDTH * 1/6, WIDTH * 3/6, WIDTH * 5/6]  # 三等分的中心
            lx = int(col_centers[i])
            l_surf = font_sub.render(stats_labels[i], True, RED)
            v_surf = font_main.render(stats_vals[i], True, BLACK)
            screen.blit(l_surf, (lx - l_surf.get_width()//2, col_y))
            screen.blit(v_surf, (lx - v_surf.get_width()//2, col_y + 45))

        self.btn_again.draw(screen)
        self.btn_course.draw(screen)
        self.btn_title.draw(screen)