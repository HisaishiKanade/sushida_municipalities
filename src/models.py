import pygame
import random
from .config import WIDTH

# ============================================================
# 1) かな → ローマ字 对应表（支持多种合法输入）
# ============================================================

ROMA_MAP = {
    # 五十音
    'あ':['a'], 'い':['i'], 'う':['u'], 'え':['e'], 'お':['o'],
    'か':['ka','ca'], 'き':['ki'], 'く':['ku','cu','qu'], 'け':['ke'], 'こ':['ko','co'],
    'さ':['sa'], 'し': ['shi', 'si', 'ci'], 'す':['su'], 'せ':['se','ce'], 'そ':['so'],
    'た':['ta'], 'ち': ['chi', 'ti'], 'つ': ['tsu', 'tu'], 'て':['te'], 'と':['to'],
    'な':['na'], 'に':['ni'], 'ぬ':['nu'], 'ね':['ne'], 'の':['no'],
    'は':['ha'], 'ひ':['hi'], 'ふ':['fu', 'hu'], 'へ':['he'], 'ほ':['ho'],
    'ま':['ma'], 'み':['mi'], 'む':['mu'], 'め':['me'], 'も':['mo'],
    'や':['ya'], 'ゆ':['yu'], 'よ':['yo'],
    'ら':['ra'], 'り':['ri'], 'る':['ru'], 'れ':['re'], 'ろ':['ro'],
    'わ':['wa'], 'を':['wo'],

    # 拨音（n 的特殊规则在逻辑里处理）
    'ん':['nn','xn','n'],

    # 濁音・半濁音
    'が':['ga'], 'ぎ':['gi'], 'ぐ':['gu'], 'げ':['ge'], 'ご':['go'],
    'ざ':['za'], 'じ':['ji', 'zi'], 'ず':['zu'], 'ぜ':['ze'], 'ぞ':['zo'],
    'だ':['da'], 'ぢ':['di','ji'], 'づ':['du','zu'], 'で':['de'], 'ど':['do'],
    'ば':['ba'], 'び':['bi'], 'ぶ':['bu'], 'べ':['be'], 'ぼ':['bo'],
    'ぱ':['pa'], 'ぴ':['pi'], 'ぷ':['pu'], 'ぺ':['pe'], 'ぽ':['po'],

    # 拗音
    'きゃ':['kya'], 'きゅ':['kyu'], 'きょ':['kyo'],
    'しゃ': ['sha', 'sya'],
    'しゅ': ['shu', 'syu'],
    'しょ': ['sho', 'syo'],
    'ちゃ': ['cha', 'tya'],
    'ちゅ': ['chu', 'tyu'],
    'ちょ': ['cho', 'tyo'],
    'にゃ':['nya'], 'にゅ':['nyu'], 'にょ':['nyo'],
    'ひゃ':['hya'], 'ひゅ':['hyu'], 'ひょ':['hyo'],
    'みゃ':['mya'], 'みゅ':['myu'], 'みょ':['myo'],
    'りゃ':['rya'], 'りゅ':['ryu'], 'りょ':['ryo'],
    'ぎゃ':['gya'], 'ぎゅ':['gyu'], 'ぎょ':['gyo'],
    'じゃ': ['ja', 'jya', 'zya'],
    'じゅ': ['ju', 'jyu', 'zyu'],
    'じょ': ['jo', 'jyo', 'zyo'],
    'びゃ':['bya'], 'びゅ':['byu'], 'びょ':['byo'],
    'ぴゃ':['pya'], 'ぴゅ':['pyu'], 'ぴょ':['pyo'],

    # 小写假名（LA / XA 系列）
    'ぁ':['la','xa'], 'ぃ':['li','xi'], 'ぅ':['lu','xu'], 'ぇ':['le','xe'], 'ぉ':['lo','xo'],
    'ゃ':['lya','xya'], 'ゅ':['lyu','xyu'], 'ょ':['lyo','xyo'],

    # 促音（ltu/xtu）+ 双写规则由逻辑处理
    'っ':['ltu','xtu'],
}


# ============================================================
# 2) 工具：拆分假名（优先识别 2 字符拗音）
# ============================================================

def split_kana(text):
    res = []
    i = 0
    while i < len(text):
        if i + 1 < len(text) and text[i:i+2] in ROMA_MAP:
            res.append(text[i:i+2])
            i += 2
        else:
            res.append(text[i])
            i += 1
    return res


# ============================================================
# 3) 多路径输入状态（状态机路径）
# ============================================================

class InputPath:
    def __init__(self, kana_index=0, buffer="", typed=""):
        self.kana_index = kana_index
        self.buffer = buffer
        self.typed = typed

    def clone(self):
        return InputPath(self.kana_index, self.buffer, self.typed)


# ============================================================
# 4) SushiPlate：寿司盘子 + 输入判定系统（多路径）
# ============================================================

class SushiPlate:
    def __init__(self, word_data):
        from .resources import Resources
        


        self.prefix_kanji = word_data.get("prefix_kanji", "")
        self.kanji = word_data['kanji']           # 市町村汉字
        self.kana = word_data['kana']             # 市町村假名（输入用）

        # 这个 display_roma 不再作为“判定依据”，只用于 fallback/UI参考
        self.display_roma = word_data.get('roma', '').lower()

        self.kana_list = split_kana(self.kana)

        self.image = Resources.get_random_sushi()
        self.x = 900
        self.y = 200
        self.speed = 3 + (len(self.display_roma) * 0.05)

        self.is_active = True
        self.is_cleared = False
        self.shake_amount = 0

        # 多路径输入状态集合
        self.paths = [InputPath(0, "", "")]
        
        typed0, remaining0 = self.get_display_text()  # 初始 typed0 应为空
        self.target_len = len(typed0 + remaining0)

        # UI 显示的“玩家真实输入内容”
        self.typed_roma = ""


    def _build_remaining_from_path(self, path):
        """
        根据当前路径，生成“剩余应该显示的 romaji 字符串”
        """
        remaining = ""
    
        # 1) 当前 kana：补齐当前 buffer 对应的剩余部分
        if path.kana_index < len(self.kana_list):
            valid = self._get_valid_romas(path.kana_index)
    
            # 能匹配当前 buffer 的候选
            candidates = [r for r in valid if r.startswith(path.buffer)]
            if candidates:
                chosen = candidates[0]  # 按 ROMA_MAP 顺序优先（更像寿司打）
                remaining += chosen[len(path.buffer):]
            else:
                # 理论上不会发生；保险
                remaining += ""
    
        # 2) 后续 kana：直接用每个 kana 的“优先拼法”(valid[0])
        for i in range(path.kana_index + 1, len(self.kana_list)):
            valid = self._get_valid_romas(i)
            if valid:
                remaining += valid[0]
            else:
                remaining += "?"
    
        return remaining



    def get_display_text(self):
        """
        返回 (typed, remaining) 两段字符串
        typed：玩家已输入（红色）
        remaining：玩家未输入（灰色）
        """
        if not self.paths:
            return self.typed_roma, ""

        # 选当前最佳路径（进度最大，buffer 最短优先）
        best = max(self.paths, key=lambda p: (p.kana_index, len(p.typed), -len(p.buffer)))

        typed = best.typed
        remaining = self._build_remaining_from_path(best)

        return typed, remaining
    

    def _get_valid_romas(self, kana_index):
        """
        获取当前 kana 的合法 romaji 列表（含上下文规则）
        """
        kana = self.kana_list[kana_index]
        valid = list(ROMA_MAP.get(kana, []))


        # -------- 促音：っ 的双写规则（补齐 ch/sh/ts 等）--------
        if kana == 'っ' and kana_index + 1 < len(self.kana_list):
            next_kana = self.kana_list[kana_index + 1]
            next_romas = ROMA_MAP.get(next_kana, [])
        
            # 1) 常规：允许双写“下一个拼法的首字母”（但只限辅音）
            for r in next_romas:
                if not r:
                    continue
                fc = r[0]
                if fc.isalpha() and fc not in "aeiou":
                    valid.append(fc)
        
            # 2) 特殊：当下一假名以 ch/sh/ts 开头时，额外允许 t/s
            # 目的是支持：っち -> tchi，っちゃ -> tcha 等
            starts = set()
            for r in next_romas:
                if len(r) >= 2:
                    starts.add(r[:2])
        
            # ch: 允许 t（tchi/tcha/tchu/tcho）
            if "ch" in starts:
                valid.append("t")
        
            # sh: 有些规则表也允许 s（通常已包含，但保险）
            if "sh" in starts:
                valid.append("s")
        
            # ts: 通常首字母就是 t，但保险
            if "ts" in starts:
                valid.append("t")


        # -------- 拨音：ん 的 n 规则（图里那套）--------
        if kana == 'ん':
            if kana_index + 1 < len(self.kana_list):
                next_kana = self.kana_list[kana_index + 1]
                next_romas = ROMA_MAP.get(next_kana, [])
                next_firsts = [r[0] for r in next_romas if r]

                # 后面不是元音/y 开头，则允许单独 n
                if next_firsts and all(c not in "aeiouy" for c in next_firsts):
                    if "n" not in valid:
                        valid.append("n")

        return valid


    def check_input(self, char):
        """
        玩家输入一个字符：更新 paths 状态集合
        """
        if self.is_cleared or not self.is_active:
            return "IGNORE"

        new_paths = []

        for path in self.paths:
            if path.kana_index >= len(self.kana_list):
                continue

            kana = self.kana_list[path.kana_index]
            valid_romas = self._get_valid_romas(path.kana_index)

            new_buffer = path.buffer + char

            # 前缀匹配
            matched = [r for r in valid_romas if r.startswith(new_buffer)]
            if not matched:
                continue

            p2 = path.clone()
            p2.buffer = new_buffer
            p2.typed += char

            # 如果 buffer 完整匹配某个拼法，则提交 kana
            if new_buffer in matched:

                # ---- 促音双写情况：buffer 只有一个字母，且不是 x/l ----
                if kana == 'っ' and len(new_buffer) == 1 and new_buffer not in ('x', 'l'):
                    # 提交促音本身
                    p2.kana_index += 1
                    p2.buffer = ""
                
                    # 决定是否“复用”这个字母作为下一个假名的首字母
                    # - 常规（pp/kk/ss/tt...）：复用
                    # - 特殊（tchi/tcha...）：不复用，只消耗促音
                    reused = False
                    if p2.kana_index < len(self.kana_list):
                        next_valid = self._get_valid_romas(p2.kana_index)
                
                        # 如果下一个假名确实有拼法以该字母开头，则走复用路径（pp, cchi 等）
                        if any(r.startswith(char) for r in next_valid):
                            p3 = p2.clone()
                            p3.buffer = char
                            new_paths.append(p3)
                            reused = True
                
                    # 不可复用时（例如 char='t' 但下个是 'chi/cha'），就只完成促音，下一假名从空开始
                    if not reused:
                        new_paths.append(p2)
                
                    continue


                # 普通提交
                p2.kana_index += 1
                p2.buffer = ""

            new_paths.append(p2)

        # 没有任何路径匹配 → MISS
        if not new_paths:
            self.shake_amount = 10
            return "MISS"

        # 去重：防止路径爆炸
        dedup = {}
        for p in new_paths:
            key = (p.kana_index, p.buffer, p.typed)
            dedup[key] = p

        self.paths = list(dedup.values())

        # 限制最大路径数量（避免复杂词汇导致爆炸）
        self.paths = sorted(self.paths, key=lambda p: (p.kana_index, len(p.typed)), reverse=True)[:40]

        # UI 选最佳路径（typed 最长）
        best = max(self.paths, key=lambda p: len(p.typed))
        self.typed_roma = best.typed

        # 如果任何路径已经完成所有 kana
        if any(p.kana_index >= len(self.kana_list) for p in self.paths):
            self.is_cleared = True
            self.is_active = False
            return "CLEARED"

        return "HIT"


    def update(self):
        self.x -= self.speed

        if self.shake_amount > 0:
            self.shake_amount -= 1

        if self.x < -450:
            self.is_active = False
            return True

        return False


    def draw(self, screen, fonts):
        if not self.is_active and not self.is_cleared:
            return

        curr_x = self.x + (random.randint(-self.shake_amount, self.shake_amount) if self.shake_amount > 0 else 0)
        curr_y = self.y + (random.randint(-self.shake_amount, self.shake_amount) if self.shake_amount > 0 else 0)

        # 1. 寿司图
        if self.image:
            screen.blit(self.image, (curr_x, curr_y))

        # 2. 汉字
        k_surf = fonts['kanji'].render(self.kanji, True, (40, 40, 40))
        screen.blit(k_surf, (curr_x + 110 - k_surf.get_width() // 2, curr_y + 40))
