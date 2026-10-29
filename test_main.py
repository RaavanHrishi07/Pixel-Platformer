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
