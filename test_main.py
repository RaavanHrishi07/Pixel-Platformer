import main


def test_level_count_and_names():
    assert len(main.LEVELS) == 3
    assert [level["name"] for level in main.LEVELS] == [
        "Green Hills", "Sky Ruins", "Lava Citadel"
    ]


def test_all_levels_have_required_fields():
    for level in main.LEVELS:
        assert level["world_width"] >= main.WIDTH
        assert level["platforms"]
        assert level["coins"]
        assert level["hazards"]
        assert level["goal"]


def test_spawns_are_inside_world():
    for level in main.LEVELS:
        x, y = level["spawn"]
        assert 0 <= x < level["world_width"]
        assert 0 <= y < main.HEIGHT


def test_intersection_detects_overlap():
    assert main.PlatformerGame.intersects((0, 0, 10, 10), (5, 5, 15, 15))


def test_intersection_rejects_separate_rectangles():
    assert not main.PlatformerGame.intersects((0, 0, 10, 10), (12, 12, 20, 20))


def test_coins_are_coordinate_pairs():
    for level in main.LEVELS:
        for coin in level["coins"]:
            assert len(coin) == 2
            assert all(isinstance(value, (int, float)) for value in coin)
