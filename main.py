import tkinter as tk
from tkinter import messagebox
import random

WIDTH, HEIGHT = 960, 600
GRAVITY = 0.65
MOVE_SPEED = 5
JUMP_SPEED = -13.5

LEVELS = [
    {
        "name": "Green Hills", "world_width": 1800, "spawn": (70, 440),
        "platforms": [(0,520,520,80),(610,480,250,30),(940,430,220,30),
                      (1240,480,250,30),(1570,520,230,80),(300,410,120,22),
                      (720,360,120,22),(1060,320,120,22),(1370,390,120,22)],
        "coins": [(180,475),(350,365),(665,435),(770,315),(1010,385),
                  (1110,275),(1320,435),(1410,345),(1660,475)],
        "hazards": [(520,500,90,20),(860,460,80,20),(1160,410,80,20),(1490,500,80,20)],
        "enemies": [(400,484,500),(1030,394,1150),(1620,484,1740)],
        "goal": (1710,430,42,90),
    },
    {
        "name": "Sky Ruins", "world_width": 2100, "spawn": (60,400),
        "platforms": [(0,520,300,80),(380,470,180,25),(650,410,170,25),
                      (930,350,180,25),(1220,410,180,25),(1510,460,190,25),
                      (1810,520,290,80),(250,380,100,20),(520,320,100,20),
                      (790,260,100,20),(1080,250,100,20),(1370,320,100,20),
                      (1660,360,100,20)],
        "coins": [(130,475),(290,345),(445,425),(560,285),(710,365),(830,225),
                  (990,305),(1120,215),(1280,365),(1410,285),(1570,415),
                  (1700,325),(1900,475),(2010,475)],
        "hazards": [(300,500,80,20),(560,450,90,20),(820,390,110,20),
                    (1110,500,110,20),(1400,440,110,20),(1700,500,110,20)],
        "enemies": [(420,434,520),(970,314,1060),(1540,424,1650)],
        "goal": (2025,430,42,90),
    },
    {
        "name": "Lava Citadel", "world_width": 2300, "spawn": (60,420),
        "platforms": [(0,520,240,80),(330,465,150,25),(570,405,150,25),
                      (820,345,150,25),(1080,400,150,25),(1340,340,150,25),
                      (1600,400,150,25),(1870,460,150,25),(2150,520,150,80),
                      (210,365,90,20),(460,300,90,20),(710,245,90,20),
                      (960,235,90,20),(1210,250,90,20),(1470,275,90,20),
                      (1730,320,90,20),(1980,365,90,20)],
        "coins": [(100,475),(245,330),(380,430),(500,265),(620,370),(750,210),
                  (875,310),(1000,200),(1130,365),(1250,215),(1390,305),
                  (1510,240),(1660,365),(1770,285),(1930,425),(2030,330),(2200,475)],
        "hazards": [(240,500,90,20),(480,445,90,20),(720,385,100,20),
                    (970,500,110,20),(1230,380,110,20),(1490,440,110,20),
                    (1750,500,120,20),(2020,500,120,20)],
        "enemies": [(360,429,450),(850,309,940),(1380,304,1470),(1900,424,1990)],
        "goal": (2220,430,42,90),
    },
]


class PlatformerGame:
    """Side-scrolling platformer built with Tkinter Canvas."""

    def __init__(self, root):
        self.root = root
        root.title("Pixel Quest - 2D Platformer")
        root.geometry(f"{WIDTH}x{HEIGHT}")
        root.resizable(False, False)
        root.configure(bg="#101827")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                bg="#87CEEB", highlightthickness=0)
        self.canvas.pack()
        self.keys = set()
        root.bind("<KeyPress>", self.key_down)
        root.bind("<KeyRelease>", self.key_up)
        root.bind("<FocusOut>", lambda _e: self.keys.clear())
        self.level_index = 0
        self.total_coins = 0
        self.lives = 3
        self.paused = False
        self.load_level()
        self.tick()

    def key_down(self, event):
        key = event.keysym.lower()
        self.keys.add(key)
        if key == "p":
            self.paused = not self.paused
        elif key == "r":
            self.load_level()
        elif key == "escape":
            self.root.destroy()

    def key_up(self, event):
        self.keys.discard(event.keysym.lower())

    def load_level(self):
        data = LEVELS[self.level_index]
        self.level_name = data["name"]
        self.world_width = data["world_width"]
        self.spawn = data["spawn"]
        self.platforms = data["platforms"]
        self.hazards = data["hazards"]
        self.goal = data["goal"]
        self.coins = [{"x": x, "y": y, "taken": False} for x, y in data["coins"]]
        self.enemies = [
            {"x": x, "y": y, "left": x, "right": right, "direction": 1, "alive": True}
            for x, y, right in data["enemies"]
        ]
        self.player = {"x": float(self.spawn[0]), "y": float(self.spawn[1]),
                       "vx": 0.0, "vy": 0.0, "w": 30, "h": 40,
                       "on_ground": False, "invulnerable": 0}
        self.camera_x = 0
        self.level_coins = 0

    @staticmethod
    def intersects(a, b):
        return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]

    def player_rect(self):
        p = self.player
        return p["x"], p["y"], p["x"] + p["w"], p["y"] + p["h"]

    def move_player(self):
        p = self.player
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

        # Horizontal collision resolution.
        x1, y1, x2, y2 = self.player_rect()
        for x, y, w, h in self.platforms:
            if self.intersects((x1,y1,x2,y2), (x,y,x+w,y+h)):
                if p["vx"] > 0:
                    p["x"] = x - p["w"]
                elif p["vx"] < 0:
                    p["x"] = x + w
                x1, x2 = p["x"], p["x"] + p["w"]

        p["y"] += p["vy"]
        p["on_ground"] = False
        x1, y1, x2, y2 = self.player_rect()
        for x, y, w, h in self.platforms:
            if self.intersects((x1,y1,x2,y2), (x,y,x+w,y+h)):
                if p["vy"] >= 0 and old_bottom <= y + 12:
                    p["y"] = y - p["h"]
                    p["vy"] = 0
                    p["on_ground"] = True
                elif p["vy"] < 0:
                    p["y"] = y + h
                    p["vy"] = 0
                x1, y1, x2, y2 = self.player_rect()
        if p["y"] > HEIGHT + 150:
            self.lose_life()

    def lose_life(self):
        if self.player["invulnerable"] > 0:
            return
        self.lives -= 1
        if self.lives <= 0:
            messagebox.showinfo("Game Over", f"Game over! Coins collected: {self.total_coins}")
            self.level_index, self.total_coins, self.lives = 0, 0, 3
        self.load_level()
        self.player["invulnerable"] = 90

    def update_enemies(self):
        for enemy in self.enemies:
            if not enemy["alive"]:
                continue
            enemy["x"] += enemy["direction"] * 1.5
            if enemy["x"] <= enemy["left"]:
                enemy["x"], enemy["direction"] = enemy["left"], 1
            elif enemy["x"] >= enemy["right"]:
                enemy["x"], enemy["direction"] = enemy["right"], -1
            rect = (enemy["x"], enemy["y"], enemy["x"] + 30, enemy["y"] + 30)
            if self.intersects(self.player_rect(), rect):
                p = self.player
                if p["vy"] > 1 and p["y"] + p["h"] - enemy["y"] < 22:
                    enemy["alive"] = False
                    p["vy"] = JUMP_SPEED * 0.65
                else:
                    self.lose_life()
                    return

    def collect_coins(self):
        rect = self.player_rect()
        for coin in self.coins:
            if coin["taken"]:
                continue
            c = (coin["x"]-10, coin["y"]-10, coin["x"]+10, coin["y"]+10)
            if self.intersects(rect, c):
                coin["taken"] = True
                self.level_coins += 1
                self.total_coins += 1

    def check_hazards_goal(self):
        rect = self.player_rect()
        for x, y, w, h in self.hazards:
            if self.intersects(rect, (x,y,x+w,y+h)):
                self.lose_life()
                return
        gx, gy, gw, gh = self.goal
        if self.intersects(rect, (gx,gy,gx+gw,gy+gh)):
            if self.level_index < len(LEVELS) - 1:
                self.level_index += 1
                self.load_level()
            else:
                messagebox.showinfo(
                    "Quest Complete!",
                    f"You completed all {len(LEVELS)} levels!\nCoins: {self.total_coins}"
                )
                self.level_index, self.total_coins, self.lives = 0, 0, 3
                self.load_level()

    def tick(self):
        if not self.paused:
            self.move_player()
            self.update_enemies()
            self.collect_coins()
            self.check_hazards_goal()
            self.camera_x = max(0, min(
                self.player["x"] - WIDTH * 0.38, self.world_width - WIDTH
            ))
        self.draw()
        self.root.after(16, self.tick)

    def draw_background(self):
        self.canvas.create_rectangle(0,0,WIDTH,HEIGHT, fill="#87CEEB", outline="")
        offset = (self.camera_x * 0.25) % 420
        for i in range(-1, 4):
            x = i * 420 - offset
            self.canvas.create_oval(x,300,x+500,650,fill="#76C893",outline="")
        cloud_offset = (self.camera_x * 0.12) % 300
        for i in range(-1,5):
            x = i * 300 - cloud_offset + 70
            self.canvas.create_oval(x,70,x+70,105,fill="#F8FAFC",outline="")
            self.canvas.create_oval(x+25,52,x+95,105,fill="#F8FAFC",outline="")
            self.canvas.create_oval(x+55,72,x+120,105,fill="#F8FAFC",outline="")

    def draw(self):
        c = self.canvas
        c.delete("all")
        self.draw_background()
        cam = self.camera_x

        for x,y,w,h in self.platforms:
            sx = x - cam
            if sx+w < -10 or sx > WIDTH+10:
                continue
            c.create_rectangle(sx,y,sx+w,y+h,fill="#7C4A2D",outline="#5B3524",width=2)
            c.create_rectangle(sx,y,sx+w,y+8,fill="#35A853",outline="")
            for tx in range(int(sx+12), int(sx+w-5), 26):
                c.create_rectangle(tx,y+17,tx+10,y+23,fill="#99613D",outline="")

        for x,y,w,h in self.hazards:
            sx = x-cam
            if -w <= sx <= WIDTH:
                count = max(1, int(w//18))
                for i in range(count):
                    left, right = sx+i*w/count, sx+(i+1)*w/count
                    c.create_polygon(left,y+h,(left+right)/2,y,right,y+h,
                                     fill="#EF4444",outline="#991B1B")

        for coin in self.coins:
            if coin["taken"]:
                continue
            x,y = coin["x"]-cam,coin["y"]
            c.create_oval(x-10,y-10,x+10,y+10,fill="#FACC15",outline="#CA8A04",width=2)
            c.create_oval(x-4,y-7,x+4,y+7,fill="#FEF08A",outline="")

        for e in self.enemies:
            if not e["alive"]:
                continue
            x,y = e["x"]-cam,e["y"]
            if -40 <= x <= WIDTH+40:
                c.create_oval(x,y,x+30,y+30,fill="#9333EA",outline="#581C87",width=2)
                c.create_oval(x+6,y+8,x+12,y+15,fill="white",outline="")
                c.create_oval(x+18,y+8,x+24,y+15,fill="white",outline="")
                c.create_oval(x+9,y+10,x+12,y+14,fill="#111827",outline="")
                c.create_oval(x+21,y+10,x+24,y+14,fill="#111827",outline="")

        gx,gy,gw,gh = self.goal
        sx = gx-cam
        c.create_rectangle(sx+5,gy,sx+10,gy+gh,fill="#E5E7EB",outline="")
        c.create_polygon(sx+10,gy+3,sx+48,gy+17,sx+10,gy+32,
                         fill="#F43F5E",outline="#BE123C")

        p = self.player
        if p["invulnerable"] == 0 or (p["invulnerable"]//5)%2 == 0:
            x,y = p["x"]-cam,p["y"]
            c.create_rectangle(x+4,y+12,x+26,y+38,fill="#2563EB",outline="#1D4ED8",width=2)
            c.create_rectangle(x+2,y+2,x+28,y+18,fill="#F4B183",outline="#B45309",width=2)
            c.create_rectangle(x,y,x+30,y+8,fill="#DC2626",outline="#991B1B",width=2)
            c.create_rectangle(x+18,y+8,x+23,y+13,fill="#111827",outline="")
            c.create_rectangle(x+3,y+34,x+13,y+40,fill="#1F2937",outline="")
            c.create_rectangle(x+18,y+34,x+28,y+40,fill="#1F2937",outline="")

        c.create_rectangle(16,14,390,94,fill="#101827",outline="#334155",width=2)
        c.create_text(30,29,anchor="w",text=f"PIXEL QUEST  |  {self.level_name}",
                      fill="#F8FAFC",font=("Segoe UI",12,"bold"))
        c.create_text(30,53,anchor="w",text=f"Coins: {self.total_coins}   This level: {self.level_coins}",
                      fill="#FACC15",font=("Segoe UI",11,"bold"))
        c.create_text(30,76,anchor="w",text=f"Lives: {'♥ ' * self.lives}    Level {self.level_index+1}/{len(LEVELS)}",
                      fill="#FCA5A5",font=("Segoe UI",10,"bold"))
        c.create_text(WIDTH-18,24,anchor="ne",text="MOVE: ← → / A D     JUMP: SPACE / ↑ / W",
                      fill="#0F172A",font=("Segoe UI",9,"bold"))
        c.create_text(WIDTH-18,43,anchor="ne",text="P: PAUSE     R: RESTART     ESC: QUIT",
                      fill="#0F172A",font=("Segoe UI",9,"bold"))
        if self.paused:
            c.create_rectangle(0,0,WIDTH,HEIGHT,fill="#0F172A",stipple="gray50",outline="")
            c.create_text(WIDTH/2,HEIGHT/2-15,text="PAUSED",fill="white",
                          font=("Segoe UI",32,"bold"))
            c.create_text(WIDTH/2,HEIGHT/2+28,text="Press P to continue",
                          fill="#CBD5E1",font=("Segoe UI",14))


def main():
    root = tk.Tk()
    PlatformerGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
