# 寿司打・全国自治体版（Sushida Municipalities）

一个基于 **pygame** 实现的日文打字游戏，灵感来自经典游戏「寿司打」，  
结合 **日本全国自治体名称** 作为打字素材，并加入了完整的 **音效 / BGM / UI 系统**。

> 当前版本：Test Ver. 0.2

---

## 🎮 游戏特色

- ⌨️ **日文打字玩法**
  - 支持罗马字输入
  - 可选择是否显示罗马字 / ふりがな

- 🍣 **寿司传送带系统**
  - 寿司随时间滑动，未完成会判定为 miss
  - 连续正确输入可触发 **Combo**

- 🔊 **完整音效系统**
  - SE：打字 / miss / clear / combo / 按钮音效
  - BGM：开始 & 设置 / 游戏中 / 结算界面三段音乐
  - **SE / BGM 音量可在设置与暂停界面实时调节**

- 🖼️ **UI & 视觉**
  - 不同场景对应不同背景图
  - 传送带与 HUD 支持透明度
  - 结算界面根据盈亏显示成功 / 失败背景

---

## 🛠️ 运行环境

- Python 3.10+
- pygame 2.6+

推荐使用 **conda 虚拟环境**。

---

## ▶️ 运行方式

1. 克隆仓库

```bash
git clone https://github.com/HisaishiKanade/sushida_municipalities.git
cd sushida_municipalities
安装依赖（确保已进入虚拟环境）

pip install pygame
启动游戏

python main.py
⚙️ 游戏设置说明
在「设置界面 / 暂停界面」中可以调整：

难度：EASY / MEDIUM / HARD

罗马字显示：ON / OFF

ふりがな显示：ON / OFF

SE 音量

BGM 音量

设置会在游戏过程中即时生效。

📁 项目结构（简要）
assets/
├─ bg/        # 各场景背景图
├─ bgm/       # 背景音乐
├─ se/        # 音效（含 combo）
├─ sushi/     # 寿司图片素材

src/
├─ scenes.py      # 各场景逻辑
├─ elements.py    # UI 组件（Button / OptionBox / Slider）
├─ models.py      # 游戏对象（寿司盘等）
├─ resources.py   # 资源与音频管理
├─ game_state.py  # 游戏状态与设置
📌 开发状态
 基础打字玩法

 多场景系统

 音效 & BGM

 音量控制滑条

 设置持久化（保存到文件）

 可执行文件打包（exe）

🤖 AI 使用声明（AI Disclosure）

本项目的代码由作者与 AI（ChatGPT）协作完成，用于学习、实验与创作目的。

项目中使用的图片素材由「豆包」AI 生成。

所有 AI 生成内容均经过人工选择与整合，仅用于非商业用途。

📜 License
本项目为个人学习 / 练习作品，
素材版权归原作者所有，仅用于非商业用途。
