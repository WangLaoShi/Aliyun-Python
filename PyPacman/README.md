# PyPacman · 小白可读版说明

用 **Python + pygame** 写的吃豆人（Pac-Man）克隆。本 README 面向初学者：讲清怎么跑、目录怎么分、整体怎么设计，以及项目里用到了哪些 Python 基础知识。

> 原作者实现；本仓库补充了 `requirements.txt`、教学向中文注释与本说明。

---

## 1. 怎么运行（推荐虚拟环境）

在项目根目录 `PyPacman/` 下执行：

```bash
# 若还没有虚拟环境
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 安装依赖（目前只有 pygame）
pip install -r requirements.txt

# 启动游戏（请在 PyPacman 目录下运行，保证相对路径能找到 assets/、levels/）
python main.py
```

- **操作**：方向键移动；关闭窗口退出。
- **规则简述**：吃光豆子过关后关卡会重置；吃能量点后幽灵变蓝可被吃；撞到正常幽灵会死亡并重置角色位置。按 README 原文：没有严格 Game Over，可一直玩。

---

## 2. 项目结构（先建立地图）

```
PyPacman/
├── main.py                 # 入口：创建 GameRun 并进入主循环
├── requirements.txt        # 依赖清单（pygame）
├── README.md               # 本说明
├── LICENSE
├── assets/                 # 图片、音效等资源（运行时按相对路径加载）
├── levels/                 # 关卡 JSON + 最高分 stats.json
└── src/                    # 全部游戏逻辑（包）
    ├── configs.py          # 常量：颜色、速度、得分、幽灵参数
    ├── runner.py           # 游戏主循环、初始化音效/最高分
    ├── sounds.py           # 音效单例管理
    ├── log_handle.py       # logging 封装
    ├── game/               # 「状态 + 输入」层
    │   ├── state_management.py   # GameState：分数、方向、模式等
    │   └── event_management.py   # 键盘/退出/定时切换幽灵模式
    ├── gui/                # 「画面」层
    │   ├── screen_management.py  # 协调迷宫、分数、死亡/过关重置
    │   ├── pacman_grid.py        # 读关卡矩阵并画墙/豆/能量点
    │   ├── score_screen.py       # 分数文字
    │   └── loading_screen.py     # 加载图（当前主流程未强制使用）
    ├── sprites/            # 「角色」层
    │   ├── pacman.py       # 吃豆人移动、吃豆、动画帧
    │   ├── ghosts.py       # 幽灵基类 + Blinky/Pinky/Inky/Clyde + 管理器
    │   └── sprite_configs.py     # 图片路径字典
    └── utils/              # 工具函数
        ├── coord_utils.py  # 网格下标 ↔ 屏幕像素、细网格矩阵
        ├── draw_utils.py   # 画矩形/圆
        ├── ghost_movement_utils.py  # 幽灵选路、路口判定
        └── graph_utils.py  # A* 寻路（当前幽灵逻辑主要用距离启发式）
```

**一句话**：`main` 启动 → `runner` 每帧处理事件、清屏、画 GUI、更新精灵 → 状态都存在 `GameState` 里 → 迷宫来自 JSON 矩阵。

---

## 3. 设计思路（为什么这样拆）

### 3.1 分层

| 层 | 职责 | 典型文件 |
|----|------|----------|
| 入口 / 循环 | 初始化 pygame、固定帧率、事件泵、翻页显示 | `main.py`, `runner.py` |
| 状态 | 全局可变数据（方向、分数、幽灵模式…）集中一处 | `state_management.py` |
| 输入 | 把按键变成状态变化 | `event_management.py` |
| 视图 | 根据矩阵与状态画关卡和 HUD | `pacman_grid.py`, `score_screen.py` |
| 实体 | 吃豆人 / 幽灵每帧自己 `update` | `pacman.py`, `ghosts.py` |
| 工具 | 与业务弱相关的坐标、绘图、距离 | `utils/*` |

好处：改「得分」主要找 `GameState`；改「键盘」找 `EventHandler`；改「迷宫绘制」找 `PacmanGrid`。

### 3.2 主循环（游戏通用模式）

伪代码：

```text
初始化窗口、状态、精灵、音效
while 还在运行:
    处理事件（键盘、退出、定时器）
    清空屏幕
    画迷宫和分数
    更新所有精灵（移动、碰撞、吃豆）
    显示到屏幕
    控制 FPS
保存最高分并退出
```

对应代码在 `GameRun.main()`。

### 3.3 关卡数据驱动

`levels/level1.json` 里用二维字符串矩阵描述格子，例如：

- `wall` 墙
- `dot` 普通豆
- `power` 能量豆
- `void` / `null` 空地
- `elec` 幽灵巢门口的电栅栏线

程序读 JSON → 得到 `matrix` → 用「字符串 → 画法」的字典（`function_mapper`）绘制。**改关卡优先改 JSON，而不是改 Python 画墙代码。**

### 3.4 坐标两套体系

1. **矩阵下标** `(row, col)`：逻辑格子。
2. **屏幕像素** `(x, y)`：pygame 绘图位置。

`coord_utils` 负责互相转换。吃豆人还使用更细的 `tiny_matrix`（把一格再切成 `CELL_SIZE // PACMAN_SPEED` 份），方便按像素步进做撞墙检测。

### 3.5 幽灵 AI（简化版经典思路）

- **scatter（散开）**：去固定角落。
- **chase（追逐）**：各幽灵目标不同（Blinky 追当前位置；Pinky 看前方；Inky 结合 Blinky；Clyde 远近切换）。
- **scared（受惊）**：吃能量点后变蓝，目标随机；碰撞则幽灵重置并加分。

模式由定时器事件在 scatter ↔ chase 间切换（见 `EventHandler`）。

### 3.6 音效单例

`SoundManager` 用 `__new__` 保证全局只有一个实例，避免重复加载/多通道混乱。

---

## 4. 用到的 Python 基础知识对照表

| 基础知识 | 在本项目中的例子 |
|----------|------------------|
| 变量与类型 | `int`/`float`/`str`/`bool`/`tuple`；RGB 用三元组 |
| 列表 / 字典 | 关卡 `matrix`；`PACMAN_PATHS`、`GHOST_DELAYS` |
| `for` / `while` | 画格子双重循环；主循环 `while running` |
| `if / elif / else` | 按键方向、吃豆类型、幽灵模式分支 |
| 函数 | `get_coords_from_idx`、`draw_rect` 等工具函数 |
| 默认参数 / 关键字参数 | `load_sound(..., volumne=0.5)`；`**kwargs` 传给画法 |
| 模块与包 | `from src.runner import GameRun`；包内相对分层 |
| 类与对象 | `Pacman`、`Ghost`、`GameState`… |
| 继承 | `Pacman(Sprite)`；`Blinky(Ghost)` |
| 抽象基类 `ABC` | `Ghost.determine_target` 强制子类实现 |
| `@property` | `GameState` 用 getter/setter 保护字段 |
| 私有约定 | `__level`、`_ghost_mode`（名称改写 / 约定） |
| 异常 | `direction` / `ghost_mode` 非法值 `raise ValueError` |
| 文件与 JSON | `open` + `json.load` / `json.dump` |
| 列表推导式 | 加载动画帧 `for path in PACMAN_PATHS[...]` |
| 类型注解 | `screen: Surface`、`matrix: list[list[str]]` |
| 日志 | `logging` 封装为 `get_logger` |
| 标准库 | `sys`、`math`、`random`、`heapq`、`abc`、`typing` |
| 第三方库 | **pygame**：窗口、事件、精灵、音效、绘图 |

学完本项目，建议回头对照上表：每个概念都能在某个文件里找到「活例子」。

---

## 5. 关键文件阅读顺序（建议）

1. `main.py` — 入口有多短  
2. `src/runner.py` — 主循环全貌  
3. `src/configs.py` — 魔数从哪来  
4. `src/game/state_management.py` — 状态有哪些字段  
5. `src/game/event_management.py` — 输入如何改状态  
6. `src/gui/pacman_grid.py` — JSON 如何变成画面  
7. `src/sprites/pacman.py` — 移动与吃豆  
8. `src/sprites/ghosts.py` — 继承与 AI 差异  
9. `src/utils/*` — 坐标与寻路工具  

源码已按「小白教学」密度补充中文注释（模块 / 类 / 方法 docstring + 关键步骤说明），整体注释行数约达到代码行数的 **1.5 倍**。若某段仍看不懂，优先对照本 README 的「分层」和「两套坐标」。

---

## 6. 依赖说明

见 `requirements.txt`：

```text
pygame>=2.5.0
```

其余均为 Python 标准库。

---

## 7. 已知边界（读代码时别惊讶）

- 加载页 `LoadingScreen` 已写好，但当前主循环未强制展示。  
- `graph_utils.a_star` 已实现，幽灵日常移动主要依赖 `ghost_movement_utils` 的距离选向。  
- `SoundManager.load_sound` 参数名拼写为 `volumne`（历史笔误），调用处已按该名字传参。  
- 请在 **`PyPacman` 目录** 启动，否则 `assets/`、`levels/` 相对路径会失败。

祝学习愉快！改一处配置或 JSON 后立刻运行，观察画面变化，是最快的理解方式。
