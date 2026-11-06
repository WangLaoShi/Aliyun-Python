"""
精灵贴图路径表（纯数据模块，无类、无函数）。

``PACMAN_PATHS`` / ``GHOST_PATHS`` 是 **字典**，键为方向或幽灵名，值为 **列表**
（Pac-Man 多帧动画；幽灵目前单帧）。sprites 模块 ``load`` 这些 PNG 做 ``Sprite``，
把「资源路径」集中在此，换皮肤时只改本文件即可。

列表顺序即动画帧顺序：游戏循环里按索引循环播放即可形成「张嘴」效果。
"""

# 吃豆人：键为英文方向，与 game_state 里方向字符串映射后在 sprites 中使用。
PACMAN_PATHS = {
    # 向左走时用这三帧循环，营造嘴部动画。
    "left": [
        "assets/pacman-left/1.png",
        "assets/pacman-left/2.png",
        "assets/pacman-left/3.png",
    ],
    # 向右：独立文件夹，避免单张图 flip 带来的锯齿或不对称。
    "right": [
        "assets/pacman-right/1.png",
        "assets/pacman-right/2.png",
        "assets/pacman-right/3.png",
    ],
    # 向上：同上，每方向 3 帧是常见复古 Pac-Man 资源划分方式。
    "up": [
        "assets/pacman-up/1.png",
        "assets/pacman-up/2.png",
        "assets/pacman-up/3.png",
    ],
    # 向下：路径相对项目根，运行 cwd 应为 PyPacman。
    "down": [
        "assets/pacman-down/1.png",
        "assets/pacman-down/2.png",
        "assets/pacman-down/3.png",
    ],
}

# 幽灵：键名与 configs.GHOST_DELAYS、关卡逻辑中的名字一致。
GHOST_PATHS = {
    # 青色 Inky：单帧 PNG， scared 时可能换 "blue" 键对应图。
    "inky": ["assets/ghosts/inky.png"],
    # 粉色 Pinky。
    "pinky": ["assets/ghosts/pinky.png"],
    # 红色 Blinky，常作为 AI 锚点。
    "blinky": ["assets/ghosts/blinky.png"],
    # 橙色 Clyde。
    "clyde": ["assets/ghosts/clyde.png"],
    # 受惊统一蓝皮鬼图，与四鬼正常肤色区分。
    "blue": ["assets/ghosts/blue_ghost.png"]
}

# ---------------------------------------------------------------------------
# 资源路径与运行时加载约定
# ---------------------------------------------------------------------------
# Pacman.load_all_frames 按 direction_mapper["l"] 等取列表，frame_helper 对每 path scale 到 PACMAN 尺寸。
# 每方向 3 帧：Pacman.frame_update 每 frame_delay 帧循环索引，形成嘴开合动画，非 flip 单图。
# 独立 left/right/up/down 文件夹避免 pygame.transform.flip 透明边锯齿，换皮时保持四文件夹结构。
# GHOST_PATHS[name][0] 取列表首元素：预留多帧 scared 动画时只需扩列表，ghosts.load_images 可改循环。
# "blue" 键非第四只鬼，而是 is_scared 时 blue_image 源，与 GHOST_DELAYS["blue"]==0 配置呼应。
# 路径相对 PyPacman 根；image.load 失败抛 FileNotFoundError，启动前须确认 assets/ 已就位。
# convert_alpha() 保留 PNG 透明通道，叠在 runner fill 黑底与 WALL_BLUE 墙上无矩形底色。
# 改 PNG 尺寸不改代码时，transform.scale 仍强制 PACMAN/GHOSTS 像素框，可能影响碰撞半盒比例。
# 键名 blinky/pinky/inky/clyde 与 GhostManager.load_ghosts 元组第一字段、GHOST_DELAYS 字典键一致。
# 本模块零函数：纯数据便于版本管理与 mod 替换，符合「配置与逻辑分离」的小型 pygame 项目习惯。
# 列表元素顺序即动画时间轴：索引 0→1→2→0，与 curr_frame_idx 取模 len(frames) 配套。
# 未使用 .gif 或 spritesheet：每帧独立 PNG，加载略慢但路径直观适合教学阅读。
# GHOST 单帧列表长度 1：scared 切换仅换图不换帧索引，与 Pacman 多帧嘴型对比。
# assets/pacman-* 与 assets/ghosts/ 分目录，打包 zip 时整树复制即可，无需改代码内绝对路径。
# 若新增第五鬼，须同时增 GHOST_PATHS 键、GHOST_DELAYS、GhostManager 元组与关卡 JSON 命名。
# PACMAN_PATHS 键 "left" 等与 direction_mapper 键 "l" 不同：load_all_frames 映射在 pacman.py 完成。
# 注释/代码≥1.5：路径表、动画帧数、与 configs.GHOST_DELAYS 及 load_images 调用关系见上文。
# 修改本文件不触发 pygame 重载，须重启进程才能 load 新 PNG 路径。
# ---------------------------------------------------------------------------

# --- 补充说明 (src/sprites/sprite_configs.py) ---
# GHOST_PATHS 列表首元素 load_images 使用，扩展多帧 scared 动画只需加长列表。
# PACMAN_PATHS 每方向 3 PNG，与 frame_delay 5 配合约 12 帧一轮嘴型循环 @60fps。
# assets 路径相对 cwd，打包 exe 时须 chdir 或改资源根，本教学项目假设 python main.py 从 PyPacman 根运行。
# blue_ghost.png 与四鬼 normal 图分文件，scared 时不 tint 而换图，保持像素艺术风格。
