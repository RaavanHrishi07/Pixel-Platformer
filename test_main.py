"""Unit tests for Pixel Quest's level data and menu/game-state helpers."""
import main


def test_level_count_and_names():
    assert len(main.LEVELS) == 3
    assert [level["name"] for level in main.LEVELS] == [
        "Green Hills", "Sky Ruins", "Lava Citadel"
    ]


def test_all_levels_have_checkpoint_and_required_fields():
    for level in main.LEVELS:
        assert level["world_width"] >= main.WIDTH
        assert level["platforms"]
        assert level["coins"]
        assert level["hazards"]
        assert level["goal"]
        assert level["checkpoints"]
        assert level["enemies"]


def test_checkpoint_positions_are_inside_world():
    for level in main.LEVELS:
        for x, y in level["checkpoints"]:
            assert 0 <= x < level["world_width"]
            assert 0 <= y < main.HEIGHT


def test_spawns_are_inside_world():
    for level in main.LEVELS:
        x, y = level["spawn"]
        assert 0 <= x < level["world_width"]
        assert 0 <= y < main.HEIGHT


def test_intersection_detects_overlap():
    assert main.rectangles_intersect((0, 0, 10, 10), (5, 5, 15, 15))


def test_intersection_rejects_separate_rectangles():
    assert not main.rectangles_intersect((0, 0, 10, 10), (12, 12, 20, 20))


def test_player_rect_helper():
    player = {"x": 10, "y": 20, "w": 30, "h": 40}
    assert main.player_rect(player) == (10, 20, 40, 60)


def test_coins_are_coordinate_pairs():
    for level in main.LEVELS:
        for coin in level["coins"]:
            assert len(coin) == 2
            assert all(isinstance(value, (int, float)) for value in coin)


def test_menu_screens_are_declared_in_game_flow():
    source = open(main.__file__, encoding="utf-8").read()
    for screen in ("menu", "instructions", "settings", "playing", "game_over", "victory"):
        assert f'"{screen}"' in source


def test_difficulty_settings_have_valid_lives_and_enemy_speeds():
    assert set(main.DIFFICULTIES) == {"Easy", "Normal", "Hard"}
    assert main.DIFFICULTIES["Easy"]["lives"] > main.DIFFICULTIES["Normal"]["lives"]
    assert main.DIFFICULTIES["Normal"]["lives"] > main.DIFFICULTIES["Hard"]["lives"]
    assert main.DIFFICULTIES["Easy"]["enemy_speed"] < main.DIFFICULTIES["Hard"]["enemy_speed"]


def test_checkpoint_respawn_grants_invulnerability():
    assert main.INVULNERABLE_FRAMES > 0


def test_game_controls_are_documented():
    source = open(main.__file__, encoding="utf-8").read()
    for control in ("left", "right", "space", "escape", "checkpoint"):
        assert control in source.lower()


def test_coin_collection_creates_visual_effect_and_updates_score():
    game = main.PlatformerGame.__new__(main.PlatformerGame)
    game.player = {"x": 90, "y": 90, "w": 30, "h": 40}
    game.coins = [{"x": 100, "y": 100, "taken": False}]
    game.level_coins = 0
    game.total_coins = 0
    game.coin_effects = []
    game.collect_coins()
    assert game.coins[0]["taken"] is True
    assert game.level_coins == 1
    assert game.total_coins == 1
    assert len(game.coin_effects) == 1
    assert len(game.coin_effects[0]["particles"]) == 8


def test_coin_effects_animate_and_expire():
    game = main.PlatformerGame.__new__(main.PlatformerGame)
    game.animation_frame = 0
    game.coin_effects = [{
        "x": 10, "y": 20, "age": 0,
        "particles": [{"x": 10.0, "y": 20.0, "vx": 1.0, "vy": -1.0, "color": "#fff"}],
    }]
    game.update_coin_effects()
    assert game.animation_frame == 1
    assert game.coin_effects[0]["age"] == 1
    assert game.coin_effects[0]["particles"][0]["x"] == 11.0
    game.coin_effects[0]["age"] = 27
    game.update_coin_effects()
    assert game.coin_effects == []



def test_player_animation_state_starts_idle():
    game = main.PlatformerGame.__new__(main.PlatformerGame)
    game.player = {"vx": 0, "vy": 0, "on_ground": True}
    game.player_facing = 1
    game.player_anim_frame = 0
    game.player_anim_state = "idle"
    game.landing_timer = 0
    game.update_player_animation(was_on_ground=True)
    assert game.player_anim_state == "idle"


def test_player_running_animation_advances_and_faces_direction():
    game = main.PlatformerGame.__new__(main.PlatformerGame)
    game.player = {"vx": 5, "vy": 0, "on_ground": True}
    game.player_facing = 1
    game.player_anim_frame = 0
    game.player_anim_state = "idle"
    game.landing_timer = 0
    game.update_player_animation(was_on_ground=True)
    assert game.player_anim_state == "run"
    assert game.player_anim_frame == 1
    assert game.player_facing == 1


def test_player_jump_and_fall_animation_states():
    game = main.PlatformerGame.__new__(main.PlatformerGame)
    game.player_facing = 1
    game.player_anim_frame = 0
    game.landing_timer = 0
    game.player = {"vx": -5, "vy": -6, "on_ground": False}
    game.update_player_animation(was_on_ground=True)
    assert game.player_anim_state == "jump"
    assert game.player_facing == -1
    game.player["vy"] = 4
    game.update_player_animation(was_on_ground=False)
    assert game.player_anim_state == "fall"


def test_player_landing_animation_is_triggered():
    game = main.PlatformerGame.__new__(main.PlatformerGame)
    game.player = {"vx": 0, "vy": 0, "on_ground": True}
    game.player_facing = 1
    game.player_anim_frame = 0
    game.landing_timer = 0
    game.update_player_animation(was_on_ground=False)
    assert game.player_anim_state == "land"
    assert game.landing_timer == 7


def make_combat_game():
    game = main.PlatformerGame.__new__(main.PlatformerGame)
    game.player = {"x": 100.0, "y": 100.0, "vx": 0.0, "vy": 0.0, "w": 30, "h": 40, "on_ground": True, "invulnerable": 0}
    game.player_facing = 1
    game.attack_timer = 0
    game.attack_cooldown = 0
    game.attack_has_hit = False
    game.enemies = [{"x": 140.0, "y": 108.0, "left": 140.0, "right": 180.0, "direction": 1, "alive": True}]
    game.difficulty = "Normal"
    game.lives = 3
    game.screen = "playing"
    game.keys = set()
    game.respawn_position = (100, 100)
    game.camera_x = 0
    game.world_width = main.WIDTH
    return game


def test_attack_starts_and_respects_cooldown():
    game = make_combat_game()
    assert game.start_attack() is True
    assert game.attack_timer == main.ATTACK_DURATION
    assert game.attack_cooldown == main.ATTACK_COOLDOWN
    assert game.start_attack() is False


def test_attack_hitbox_faces_player_direction():
    game = make_combat_game()
    right_box = game.get_attack_rect()
    assert right_box[0] >= game.player["x"] + game.player["w"] - 2
    game.player_facing = -1
    left_box = game.get_attack_rect()
    assert left_box[2] <= game.player["x"] + 2


def test_sword_attack_defeats_enemy_once():
    game = make_combat_game()
    assert game.start_attack()
    game.update_enemies()
    assert game.enemies[0]["alive"] is False
    assert game.enemies[0]["defeated_timer"] == 12
    assert game.attack_has_hit is True


def test_attack_cooldown_counts_down():
    game = make_combat_game()
    game.attack_cooldown = 3
    game.update_enemies()
    assert game.attack_cooldown == 2
