import tkinter as tk
from tkinter import messagebox
import math

WIDTH, HEIGHT = 960, 600
GRAVITY = 0.65
MOVE_SPEED = 5
JUMP_SPEED = -13.5
INVULNERABLE_FRAMES = 90
DIFFICULTIES = {"Easy": {"lives": 5, "enemy_speed": 1.1}, "Normal": {"lives": 3, "enemy_speed": 1.5}, "Hard": {"lives": 2, "enemy_speed": 2.0}}

LEVELS = [
    {
        "name": "Green Hills",
        "world_width": 1800,
        "spawn": (70, 440),
        "platforms": [
            (0, 520, 520, 80), (610, 480, 250, 30),
            (940, 430, 220, 30), (1240, 480, 250, 30),
            (1570, 520, 230, 80), (300, 410, 120, 22),
            (720, 360, 120, 22), (1060, 320, 120, 22),
            (1370, 390, 120, 22),
        ],
        "coins": [
            (180, 475), (350, 365), (665, 435), (770, 315),
            (1010, 385), (1110, 275), (1320, 435), (1410, 345),
            (1660, 475),
        ],
        "hazards": [
            (520, 500, 90, 20), (860, 460, 80, 20),
            (1160, 410, 80, 20), (1490, 500, 80, 20),
        ],
        "enemies": [(400, 484, 500), (1030, 394, 1150), (1620, 484, 1740)],
        "checkpoints": [(980, 390)],
        "goal": (1710, 430, 42, 90),
    },
    {
        "name": "Sky Ruins",
        "world_width": 2100,
        "spawn": (60, 400),
        "platforms": [
            (0, 520, 300, 80), (380, 470, 180, 25),
            (650, 410, 170, 25), (930, 350, 180, 25),
            (1220, 410, 180, 25), (1510, 460, 190, 25),
            (1810, 520, 290, 80), (250, 380, 100, 20),
            (520, 320, 100, 20), (790, 260, 100, 20),
            (1080, 250, 100, 20), (1370, 320, 100, 20),
            (1660, 360, 100, 20),
        ],
        "coins": [
            (130, 475), (290, 345), (445, 425), (560, 285),
            (710, 365), (830, 225), (990, 305), (1120, 215),
            (1280, 365), (1410, 285), (1570, 415), (1700, 325),
            (1900, 475), (2010, 475),
        ],
        "hazards": [
            (300, 500, 80, 20), (560, 450, 90, 20),
            (820, 390, 110, 20), (1110, 500, 110, 20),
            (1400, 440, 110, 20), (1700, 500, 110, 20),
        ],
        "enemies": [(420, 434, 520), (970, 314, 1060), (1540, 424, 1650)],
        "checkpoints": [(1260, 370)],
        "goal": (2025, 430, 42, 90),
    },
    {
        "name": "Lava Citadel",
        "world_width": 2300,
        "spawn": (60, 420),
        "platforms": [
            (0, 520, 240, 80), (330, 465, 150, 25),
            (570, 405, 150, 25), (820, 345, 150, 25),
            (1080, 400, 150, 25), (1340, 340, 150, 25),
            (1600, 400, 150, 25), (1870, 460, 150, 25),
            (2150, 520, 150, 80), (210, 365, 90, 20),
            (460, 300, 90, 20), (710, 245, 90, 20),
            (960, 235, 90, 20), (1210, 250, 90, 20),
            (1470, 275, 90, 20), (1730, 320, 90, 20),
            (1980, 365, 90, 20),
        ],
        "coins": [
            (100, 475), (245, 330), (380, 430), (500, 265),
            (620, 370), (750, 210), (875, 310), (1000, 200),
            (1130, 365), (1250, 215), (1390, 305), (1510, 240),
            (1660, 365), (1770, 285), (1930, 425), (2030, 330),
            (2200, 475),
        ],
        "hazards": [
            (240, 500, 90, 20), (480, 445, 90, 20),
            (720, 385, 100, 20), (970, 500, 110, 20),
            (1230, 380, 110, 20), (1490, 440, 110, 20),
            (1750, 500, 120, 20), (2020, 500, 120, 20),
        ],
        "enemies": [
            (360, 429, 450), (850, 309, 940),
            (1380, 304, 1470), (1900, 424, 1990),
        ],
        "checkpoints": [(1380, 300)],
        "goal": (2220, 430, 42, 90),
    },
]


def rectangles_intersect(a, b):
    """Return True when two axis-aligned rectangles overlap."""
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def player_rect(player):
    """Return the player's collision rectangle."""
    return (
        player["x"],
        player["y"],
        player["x"] + player["w"],
        player["y"] + player["h"],
    )


class PlatformerGame:
    """Side-scrolling platformer with per-level checkpoints."""

    def __init__(self, root):
        self.root = root
        root.title("Pixel Quest - 2D Platformer")
        root.geometry(f"{WIDTH}x{HEIGHT}")
        root.resizable(False, False)
        root.configure(bg="#101827")

        self.canvas = tk.Canvas(
            root, width=WIDTH, height=HEIGHT,
            bg="#87CEEB", highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)

        self.screen = "menu"
        self.difficulty = "Normal"
        self.menu_buttons = {}
        self.keys = set()
        root.bind("<KeyPress>", self.key_down)
        root.bind("<KeyRelease>", self.key_up)
        root.bind("<FocusOut>", lambda _event: self.keys.clear())

        self.level_index = 0
        self.total_coins = 0
        self.lives = DIFFICULTIES[self.difficulty]["lives"]
        self.paused = False
        self.load_level()
        self.tick()

    def key_down(self, event):
        key = event.keysym.lower()
        self.keys.add(key)
        if key == "escape":
            if self.screen in ("instructions", "settings"):
                self.screen = "menu"
            elif self.screen == "playing":
                self.screen = "menu"
                self.keys.clear()
            else:
                self.root.destroy()
            return
        if self.screen != "playing":
            if key in ("return", "space") and self.screen in ("menu", "game_over", "victory"):
                self.start_game()
            return
        if key == "p":
            self.paused = not self.paused
        elif key == "r":
            self.load_level()

    def key_up(self, event):
        self.keys.discard(event.keysym.lower())

    def load_level(self):
        """Load the selected level and reset its checkpoint progress."""
        data = LEVELS[self.level_index]
        self.level_name = data["name"]
        self.world_width = data["world_width"]
        self.spawn = tuple(data["spawn"])
        self.platforms = data["platforms"]
        self.hazards = data["hazards"]
        self.goal = data["goal"]
        self.checkpoint_positions = list(data["checkpoints"])
        self.active_checkpoint = None
        self.respawn_position = self.spawn

        self.coins = [
            {"x": x, "y": y, "taken": False}
            for x, y in data["coins"]
        ]
        self.enemies = [
            {
                "x": x, "y": y, "left": x, "right": right,
                "direction": 1, "alive": True,
            }
            for x, y, right in data["enemies"]
        ]
        self.player = {
            "x": float(self.spawn[0]), "y": float(self.spawn[1]),
            "vx": 0.0, "vy": 0.0, "w": 30, "h": 40,
            "on_ground": False, "invulnerable": 0,
        }
        self.camera_x = 0
        self.level_coins = 0
        self.checkpoint_message = 0
        self.animation_frame = 0
        self.coin_effects = []
        # Player animation state is reset whenever a level is loaded.
        self.player_anim_frame = 0
        self.player_anim_state = "idle"
        self.player_facing = 1
        self.landing_timer = 0

    def start_game(self):
        """Start a fresh run while preserving the selected settings."""
        self.screen = "playing"
        self.level_index = 0
        self.total_coins = 0
        self.lives = DIFFICULTIES[self.difficulty]["lives"]
        self.paused = False
        self.load_level()

    def handle_click(self, event):
        """Dispatch clicks to the currently visible menu buttons."""
        for name, bounds in self.menu_buttons.items():
            x1, y1, x2, y2 = bounds
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                if name == "start":
                    self.start_game()
                elif name == "instructions":
                    self.screen = "instructions"
                elif name == "settings":
                    self.screen = "settings"
                elif name == "back":
                    self.screen = "menu"
                elif name == "difficulty":
                    names = list(DIFFICULTIES)
                    self.difficulty = names[(names.index(self.difficulty) + 1) % len(names)]
                elif name == "retry":
                    self.start_game()
                elif name == "menu":
                    self.screen = "menu"
                elif name == "quit":
                    self.root.destroy()
                break

    def draw_button(self, name, label, x, y, width=260, height=48, fill="#2563EB"):
        x1, y1 = x - width // 2, y - height // 2
        x2, y2 = x + width // 2, y + height // 2
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#93C5FD", width=2)
        self.canvas.create_text(x, y, text=label, fill="#FFFFFF", font=("Segoe UI", 13, "bold"))
        self.menu_buttons[name] = (x1, y1, x2, y2)

    def draw_menu_background(self):
        c = self.canvas
        c.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#0F172A", outline="")
        # Pixel-art hills and floating platforms create a game-like title screen.
        c.create_oval(-100, 370, 420, 760, fill="#14532D", outline="")
        c.create_oval(300, 410, 800, 750, fill="#166534", outline="")
        c.create_oval(650, 360, 1150, 760, fill="#14532D", outline="")
        for x, y in ((90, 100), (830, 115), (760, 230), (180, 260), (690, 80)):
            c.create_rectangle(x, y, x + 90, y + 12, fill="#7C4A2D", outline="")
            c.create_rectangle(x, y, x + 90, y + 5, fill="#22C55E", outline="")
        c.create_oval(740, 145, 760, 165, fill="#FACC15", outline="#CA8A04", width=2)
        c.create_oval(790, 285, 810, 305, fill="#FACC15", outline="#CA8A04", width=2)

    def draw_menu_screen(self):
        self.menu_buttons = {}
        self.draw_menu_background()
        c = self.canvas
        c.create_text(WIDTH // 2, 82, text="PIXEL QUEST", fill="#F8FAFC", font=("Segoe UI", 36, "bold"))
        c.create_text(WIDTH // 2, 124, text="A tiny hero. A huge adventure.", fill="#93C5FD", font=("Segoe UI", 13))
        self.draw_button("start", "▶   START GAME", WIDTH // 2, 220, fill="#15803D")
        self.draw_button("instructions", "HOW TO PLAY  /  INSTRUCTIONS", WIDTH // 2, 282, width=300, fill="#334155")
        self.draw_button("settings", "⚙   SETTINGS", WIDTH // 2, 344, fill="#334155")
        c.create_text(WIDTH // 2, 425, text=f"Difficulty: {self.difficulty}   •   3 worlds   •   Checkpoints enabled", fill="#E2E8F0", font=("Segoe UI", 10))
        c.create_text(WIDTH // 2, 555, text="Move: ← → / A D     Jump: SPACE / ↑ / W     Pause: P", fill="#CBD5E1", font=("Segoe UI", 10))

    def draw_instructions_screen(self):
        self.menu_buttons = {}
        self.draw_menu_background()
        c = self.canvas
        c.create_text(WIDTH // 2, 90, text="HOW TO PLAY", fill="#F8FAFC", font=("Segoe UI", 28, "bold"))
        lines = ["MOVE      Left / Right arrows or A / D", "JUMP      Space, Up arrow or W", "PAUSE     Press P during a run", "CHECKPOINTS   Touch a flag to save your respawn point", "HAZARDS   Avoid spikes and enemies; stomp enemies from above", "GOAL      Reach the red flag to advance to the next world", "COINS     Collect coins and try to finish every level"]
        for i, line in enumerate(lines):
            c.create_text(WIDTH // 2, 175 + i * 42, text=line, fill="#E2E8F0", font=("Segoe UI", 12, "bold" if i == 0 else "normal"))
        self.draw_button("back", "←   BACK TO MENU", WIDTH // 2, 510, fill="#334155")

    def draw_settings_screen(self):
        self.menu_buttons = {}
        self.draw_menu_background()
        c = self.canvas
        c.create_text(WIDTH // 2, 110, text="SETTINGS", fill="#F8FAFC", font=("Segoe UI", 28, "bold"))
        c.create_text(WIDTH // 2, 195, text="DIFFICULTY", fill="#93C5FD", font=("Segoe UI", 12, "bold"))
        c.create_text(WIDTH // 2, 230, text=f"{self.difficulty}  •  {DIFFICULTIES[self.difficulty]['lives']} lives", fill="#F8FAFC", font=("Segoe UI", 18, "bold"))
        self.draw_button("difficulty", "CHANGE DIFFICULTY", WIDTH // 2, 300, width=280, fill="#334155")
        c.create_text(WIDTH // 2, 370, text="Easy: 5 lives     Normal: 3 lives     Hard: 2 lives", fill="#CBD5E1", font=("Segoe UI", 10))
        c.create_text(WIDTH // 2, 400, text="Settings apply to your next new run.", fill="#CBD5E1", font=("Segoe UI", 10))
        self.draw_button("back", "←   BACK TO MENU", WIDTH // 2, 500, fill="#334155")

    def draw_end_screen(self, victory=False):
        self.menu_buttons = {}
        self.draw_menu_background()
        c = self.canvas
        title = "QUEST COMPLETE!" if victory else "GAME OVER"
        color = "#86EFAC" if victory else "#FDA4AF"
        c.create_text(WIDTH // 2, 130, text=title, fill=color, font=("Segoe UI", 32, "bold"))
        c.create_text(WIDTH // 2, 200, text=f"Coins collected: {self.total_coins}", fill="#FACC15", font=("Segoe UI", 16, "bold"))
        c.create_text(WIDTH // 2, 238, text=f"World reached: {LEVELS[min(self.level_index, len(LEVELS)-1)]['name']}", fill="#E2E8F0", font=("Segoe UI", 12))
        self.draw_button("retry", "↻   PLAY AGAIN", WIDTH // 2, 320, fill="#15803D")
        self.draw_button("menu", "MAIN MENU", WIDTH // 2, 382, fill="#334155")
        self.draw_button("quit", "QUIT GAME", WIDTH // 2, 444, fill="#7F1D1D")

    def respawn_player(self):
        """Respawn at the last activated checkpoint without resetting the level."""
        x, y = self.respawn_position
        self.player.update({
            "x": float(x),
            "y": float(y),
            "vx": 0.0,
            "vy": 0.0,
            "on_ground": False,
            "invulnerable": INVULNERABLE_FRAMES,
        })
        self.camera_x = max(0, min(x - WIDTH * 0.38, self.world_width - WIDTH))

    def activate_checkpoints(self):
        """Activate a checkpoint when the player touches its marker."""
        rect = player_rect(self.player)
        for index, (x, y) in enumerate(self.checkpoint_positions):
            checkpoint_rect = (x, y, x + 28, y + 42)
            if rectangles_intersect(rect, checkpoint_rect):
                if self.active_checkpoint != index:
                    self.active_checkpoint = index
                    self.respawn_position = (x, y)
                    self.checkpoint_message = 90

    def lose_life(self):
        """Remove a life and respawn at the last checkpoint."""
        if self.player["invulnerable"] > 0:
            return

        self.lives -= 1
        if self.lives <= 0:
            self.screen = "game_over"
            self.keys.clear()
            return

        # Keep collected coins, defeated enemies and activated checkpoint
        # when the player has lives remaining.
        self.respawn_player()

    def move_player(self):
        p = self.player
        was_on_ground = p["on_ground"]
        if p["invulnerable"] > 0:
            p["invulnerable"] -= 1

        left = "left" in self.keys or "a" in self.keys
        right = "right" in self.keys or "d" in self.keys
        jump = "space" in self.keys or "up" in self.keys or "w" in self.keys

        p["vx"] = (MOVE_SPEED if right else 0) - (MOVE_SPEED if left else 0)
        if jump and p["on_ground"]:
            p["vy"] = JUMP_SPEED
            p["on_ground"] = False

        p["vy"] = min(p["vy"] + GRAVITY, 14)
        old_bottom = p["y"] + p["h"]
        p["x"] = max(0, min(self.world_width - p["w"], p["x"] + p["vx"]))

        x1, y1, x2, y2 = player_rect(p)
        for x, y, w, h in self.platforms:
            if rectangles_intersect((x1, y1, x2, y2), (x, y, x + w, y + h)):
                if p["vx"] > 0:
                    p["x"] = x - p["w"]
                elif p["vx"] < 0:
                    p["x"] = x + w
                x1, x2 = p["x"], p["x"] + p["w"]

        p["y"] += p["vy"]
        p["on_ground"] = False
        x1, y1, x2, y2 = player_rect(p)
        for x, y, w, h in self.platforms:
            if rectangles_intersect((x1, y1, x2, y2), (x, y, x + w, y + h)):
                if p["vy"] >= 0 and old_bottom <= y + 12:
                    p["y"] = y - p["h"]
                    p["vy"] = 0
                    p["on_ground"] = True
                elif p["vy"] < 0:
                    p["y"] = y + h
                    p["vy"] = 0
                x1, y1, x2, y2 = player_rect(p)

        if p["y"] > HEIGHT + 150:
            self.lose_life()

        self.update_player_animation(was_on_ground)

    def update_player_animation(self, was_on_ground=None):
        """Choose the player's animation state from movement and physics."""
        p = self.player
        if was_on_ground is None:
            was_on_ground = p["on_ground"]

        if p["vx"] < 0:
            self.player_facing = -1
        elif p["vx"] > 0:
            self.player_facing = 1

        if not p["on_ground"]:
            self.landing_timer = 0
            self.player_anim_state = "jump" if p["vy"] < 0 else "fall"
        elif not was_on_ground:
            self.landing_timer = 7
            self.player_anim_state = "land"
        elif self.landing_timer > 0:
            self.landing_timer -= 1
            self.player_anim_state = "land"
        elif abs(p["vx"]) > 0:
            self.player_anim_state = "run"
            self.player_anim_frame = (self.player_anim_frame + 1) % 12
        else:
            self.player_anim_state = "idle"

    def update_enemies(self):
        for enemy in self.enemies:
            if not enemy["alive"]:
                continue
            enemy["x"] += enemy["direction"] * DIFFICULTIES[self.difficulty]["enemy_speed"]
            if enemy["x"] <= enemy["left"]:
                enemy["x"], enemy["direction"] = enemy["left"], 1
            elif enemy["x"] >= enemy["right"]:
                enemy["x"], enemy["direction"] = enemy["right"], -1

            enemy_rect = (
                enemy["x"], enemy["y"],
                enemy["x"] + 30, enemy["y"] + 30,
            )
            if rectangles_intersect(player_rect(self.player), enemy_rect):
                p = self.player
                if p["vy"] > 1 and p["y"] + p["h"] - enemy["y"] < 22:
                    enemy["alive"] = False
                    p["vy"] = JUMP_SPEED * 0.65
                else:
                    self.lose_life()
                    return

    def collect_coins(self):
        rect = player_rect(self.player)
        for coin in self.coins:
            if coin["taken"]:
                continue
            coin_rect = (
                coin["x"] - 10, coin["y"] - 10,
                coin["x"] + 10, coin["y"] + 10,
            )
            if rectangles_intersect(rect, coin_rect):
                coin["taken"] = True
                self.level_coins += 1
                self.total_coins += 1
                self.spawn_coin_effect(coin["x"], coin["y"])

    def spawn_coin_effect(self, x, y):
        """Create a short sparkle burst and floating score for a collected coin."""
        colors = ("#FACC15", "#FEF08A", "#FFFFFF", "#FB923C")
        particles = []
        for index in range(8):
            angle = index * 3.141592653589793 / 4
            particles.append({
                "x": float(x), "y": float(y),
                "vx": (1.8 if index % 2 == 0 else 1.2) * __import__("math").cos(angle),
                "vy": (1.8 if index % 2 == 0 else 1.2) * __import__("math").sin(angle),
                "color": colors[index % len(colors)],
            })
        self.coin_effects.append({"x": x, "y": y, "age": 0, "particles": particles})

    def update_coin_effects(self):
        """Advance coin sparkles and remove effects after their short lifetime."""
        self.animation_frame += 1
        for effect in self.coin_effects:
            effect["age"] += 1
            for particle in effect["particles"]:
                particle["x"] += particle["vx"]
                particle["y"] += particle["vy"]
                particle["vy"] += 0.035
        self.coin_effects = [effect for effect in self.coin_effects if effect["age"] < 28]

    def check_hazards_and_goal(self):
        rect = player_rect(self.player)
        for x, y, w, h in self.hazards:
            if rectangles_intersect(rect, (x, y, x + w, y + h)):
                self.lose_life()
                return

        gx, gy, gw, gh = self.goal
        if rectangles_intersect(rect, (gx, gy, gx + gw, gy + gh)):
            if self.level_index < len(LEVELS) - 1:
                self.level_index += 1
                self.load_level()
            else:
                self.screen = "victory"
                self.keys.clear()

    def tick(self):
        if self.screen != "playing":
            if self.screen == "menu":
                self.draw_menu_screen()
            elif self.screen == "instructions":
                self.draw_instructions_screen()
            elif self.screen == "settings":
                self.draw_settings_screen()
            elif self.screen == "game_over":
                self.draw_end_screen(victory=False)
            elif self.screen == "victory":
                self.draw_end_screen(victory=True)
            self.root.after(16, self.tick)
            return
        if not self.paused:
            self.update_coin_effects()
            self.move_player()
            if self.screen != "playing":
                self.tick_draw_after_state_change()
                return
            self.update_enemies()
            self.collect_coins()
            self.activate_checkpoints()
            if not self.paused:
                self.check_hazards_and_goal()
            if self.screen != "playing":
                self.tick_draw_after_state_change()
                return

            if hasattr(self, "checkpoint_message") and self.checkpoint_message > 0:
                self.checkpoint_message -= 1

            self.camera_x = max(
                0, min(
                    self.player["x"] - WIDTH * 0.38,
                    self.world_width - WIDTH
                )
            )
        self.draw()
        self.root.after(16, self.tick)

    def tick_draw_after_state_change(self):
        """Render the end screen on the same frame that the run ends."""
        if self.screen == "game_over":
            self.draw_end_screen(victory=False)
        elif self.screen == "victory":
            self.draw_end_screen(victory=True)
        self.root.after(16, self.tick)

    def draw_background(self):
        c = self.canvas
        c.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#87CEEB", outline="")
        offset = (self.camera_x * 0.25) % 420
        for i in range(-1, 4):
            x = i * 420 - offset
            c.create_oval(x, 300, x + 500, 650, fill="#76C893", outline="")
        cloud_offset = (self.camera_x * 0.12) % 300
        for i in range(-1, 5):
            x = i * 300 - cloud_offset + 70
            c.create_oval(x, 70, x + 70, 105, fill="#F8FAFC", outline="")
            c.create_oval(x + 25, 52, x + 95, 105, fill="#F8FAFC", outline="")
            c.create_oval(x + 55, 72, x + 120, 105, fill="#F8FAFC", outline="")

    def draw(self):
        c = self.canvas
        c.delete("all")
        self.menu_buttons = {}
        self.draw_background()
        cam = self.camera_x

        for x, y, w, h in self.platforms:
            sx = x - cam
            if sx + w < -10 or sx > WIDTH + 10:
                continue
            c.create_rectangle(
                sx, y, sx + w, y + h,
                fill="#7C4A2D", outline="#5B3524", width=2
            )
            c.create_rectangle(sx, y, sx + w, y + 8, fill="#35A853", outline="")
            for tx in range(int(sx + 12), int(sx + w - 5), 26):
                c.create_rectangle(
                    tx, y + 17, tx + 10, y + 23,
                    fill="#99613D", outline=""
                )

        for x, y, w, h in self.hazards:
            sx = x - cam
            if -w <= sx <= WIDTH:
                count = max(1, int(w // 18))
                for i in range(count):
                    left = sx + i * w / count
                    right = sx + (i + 1) * w / count
                    c.create_polygon(
                        left, y + h, (left + right) / 2, y, right, y + h,
                        fill="#EF4444", outline="#991B1B"
                    )

        for coin in self.coins:
            if coin["taken"]:
                continue
            x, y = coin["x"] - cam, coin["y"]
            # A subtle pulse makes uncollected coins shimmer as the player moves.
            pulse = (self.animation_frame % 18) / 18
            half_width = 7 + abs(pulse - 0.5) * 6
            c.create_oval(
                x - half_width, y - 10, x + half_width, y + 10,
                fill="#FACC15", outline="#CA8A04", width=2
            )
            c.create_oval(x - 3, y - 7, x + 3, y + 7, fill="#FEF08A", outline="")

        # Draw collection sparkles and a floating +1 score popup.
        for effect in self.coin_effects:
            age = effect["age"]
            x, y = effect["x"] - cam, effect["y"] - age * 1.35
            if age < 20:
                c.create_text(
                    x, y - 12, text="+1 COIN", fill="#FFF7AE",
                    font=("Segoe UI", 10, "bold")
                )
            for particle in effect["particles"]:
                px, py = particle["x"] - cam, particle["y"]
                size = max(1.5, 4 - age * 0.1)
                c.create_line(px - size, py, px + size, py,
                              fill=particle["color"], width=2)
                c.create_line(px, py - size, px, py + size,
                              fill=particle["color"], width=2)

        for enemy in self.enemies:
            if not enemy["alive"]:
                continue
            x, y = enemy["x"] - cam, enemy["y"]
            if -40 <= x <= WIDTH + 40:
                c.create_oval(
                    x, y, x + 30, y + 30,
                    fill="#9333EA", outline="#581C87", width=2
                )
                c.create_oval(x + 6, y + 8, x + 12, y + 15, fill="white", outline="")
                c.create_oval(x + 18, y + 8, x + 24, y + 15, fill="white", outline="")
                c.create_oval(x + 9, y + 10, x + 12, y + 14, fill="#111827", outline="")
                c.create_oval(x + 21, y + 10, x + 24, y + 14, fill="#111827", outline="")

        # Checkpoint flags are grey until activated, then turn green.
        for index, (x, y) in enumerate(self.checkpoint_positions):
            sx = x - cam
            active = index == self.active_checkpoint
            pole = "#F8FAFC"
            flag = "#22C55E" if active else "#64748B"
            c.create_rectangle(sx, y, sx + 4, y + 42, fill=pole, outline="")
            c.create_polygon(
                sx + 4, y + 2, sx + 31, y + 11, sx + 4, y + 21,
                fill=flag, outline="#166534" if active else "#334155"
            )
            if active:
                c.create_text(
                    sx + 17, y - 8, text="CHECKPOINT!",
                    fill="#166534", font=("Segoe UI", 8, "bold")
                )

        gx, gy, gw, gh = self.goal
        sx = gx - cam
        c.create_rectangle(sx + 5, gy, sx + 10, gy + gh, fill="#E5E7EB", outline="")
        c.create_polygon(
            sx + 10, gy + 3, sx + 48, gy + 17, sx + 10, gy + 32,
            fill="#F43F5E", outline="#BE123C"
        )

        p = self.player
        if p["invulnerable"] == 0 or (p["invulnerable"] // 5) % 2 == 0:
            x, y = p["x"] - cam, p["y"]
            state = getattr(self, "player_anim_state", "idle")
            frame = getattr(self, "player_anim_frame", 0)
            facing = getattr(self, "player_facing", 1)

            # Small, restrained offsets keep the original 30x40 pixel hero design.
            bob = 0
            leg_left, leg_right = 34, 34
            arm_offset = 0
            body_y = 12
            body_bottom = 38
            if state == "run":
                phase = frame % 12
                stride = 4 if phase < 3 or 6 <= phase < 9 else -4
                bob = -2 if phase in (2, 3, 8, 9) else 0
                leg_left, leg_right = 34 + stride, 34 - stride
                arm_offset = -stride
            elif state == "jump":
                leg_left, leg_right = 29, 32
                arm_offset = -4
                body_y = 10
                body_bottom = 36
            elif state == "fall":
                leg_left, leg_right = 32, 32
                arm_offset = 3
            elif state == "land":
                squash = 2 if self.landing_timer > 3 else 1
                body_y = 12 + squash
                body_bottom = 38 - squash
                leg_left = leg_right = 35
            else:  # idle breathing
                bob = -1 if self.animation_frame % 30 < 15 else 0

            y += bob
            # Back arm, torso and front arm.
            c.create_rectangle(
                x + (1 if facing > 0 else 23), y + 16 + arm_offset,
                x + (7 if facing > 0 else 29), y + 29 + arm_offset,
                fill="#F4B183", outline="#B45309", width=1
            )
            c.create_rectangle(
                x + 4, y + body_y, x + 26, y + body_bottom,
                fill="#2563EB", outline="#1D4ED8", width=2
            )
            c.create_rectangle(
                x + (23 if facing > 0 else 1), y + 15 - arm_offset,
                x + (29 if facing > 0 else 7), y + 29 - arm_offset,
                fill="#F4B183", outline="#B45309", width=1
            )
            c.create_rectangle(
                x + 2, y + 2, x + 28, y + 18,
                fill="#F4B183", outline="#B45309", width=2
            )
            c.create_rectangle(
                x, y, x + 30, y + 8,
                fill="#DC2626", outline="#991B1B", width=2
            )
            eye_x = x + (18 if facing > 0 else 7)
            c.create_rectangle(eye_x, y + 8, eye_x + 5, y + 13, fill="#111827", outline="")

            # Alternating legs create a readable run cycle; airborne poses tuck them.
            left_foot_y = leg_left if state in ("run", "jump", "fall", "land") else 34
            right_foot_y = leg_right if state in ("run", "jump", "fall", "land") else 34
            c.create_rectangle(x + 3, y + left_foot_y, x + 13, y + left_foot_y + 6,
                               fill="#1F2937", outline="")
            c.create_rectangle(x + 18, y + right_foot_y, x + 28, y + right_foot_y + 6,
                               fill="#1F2937", outline="")

        c.create_rectangle(16, 14, 400, 94, fill="#101827", outline="#334155", width=2)
        c.create_text(
            30, 29, anchor="w", text=f"PIXEL QUEST  |  {self.level_name}",
            fill="#F8FAFC", font=("Segoe UI", 12, "bold")
        )
        c.create_text(
            30, 53, anchor="w",
            text=f"Coins: {self.total_coins}   This level: {self.level_coins}",
            fill="#FACC15", font=("Segoe UI", 11, "bold")
        )
        c.create_text(
            30, 76, anchor="w",
            text=f"Lives: {'♥ ' * self.lives}    Level {self.level_index + 1}/{len(LEVELS)}",
            fill="#FCA5A5", font=("Segoe UI", 10, "bold")
        )
        c.create_text(
            WIDTH - 18, 24, anchor="ne",
            text="MOVE: ← → / A D     JUMP: SPACE / ↑ / W",
            fill="#0F172A", font=("Segoe UI", 9, "bold")
        )
        c.create_text(
            WIDTH - 18, 43, anchor="ne",
            text="P: PAUSE     R: RESTART     ESC: QUIT",
            fill="#0F172A", font=("Segoe UI", 9, "bold")
        )

    def mainloop(self):
        self.root.mainloop()


def main():
    root = tk.Tk()
    PlatformerGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
