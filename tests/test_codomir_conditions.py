"""Box state and TMX validation, isolated from codomir import side effects."""
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from tests.test_codomir import _run


BOX_MAP = Path(__file__).parent / "fixtures" / "codomir_boxes.tmx"


def _check(snippet):
    result = _run(f"BOX_MAP = {str(BOX_MAP.resolve())!r}\n" + snippet)
    assert result.returncode == 0, result.stdout + result.stderr


def test_maps_without_boxes_remain_compatible():
    _check("""
import codomir.quest as quest
assert quest.quest_scene.box_positions == frozenset()
assert not quest.quest_scene.get_sprite_list('boxes')
pygamejr = __import__('pygamejr')
pygamejr.every_frame = lambda count: iter([0] * count)
player.move_forward()
player.move_forward()
assert player.is_win
""")


def test_multiple_boxes_have_one_dynamic_sprite_each():
    _check("""
import codomir.quest as quest
set_map(BOX_MAP)
scene = quest.quest_scene
assert scene.initial_box_positions == ((2, 3), (5, 5))
assert scene.box_positions == {(2, 3), (5, 5)}
assert set(scene.box_sprites) == scene.box_positions
group = scene.get_sprite_list('boxes')
assert set(group) == set(scene.box_sprites.values())
assert len(group) == 2
for (x, y), sprite in scene.box_sprites.items():
    assert sprite.rect.topleft == (x * 64, y * 64)
    assert sprite.visible
    assert sprite.groups() == [group]
""")


def test_repeated_reset_restores_boxes_player_and_template():
    _check("""
import copy
from pathlib import Path
import codomir.quest as quest
set_map(BOX_MAP)
scene = quest.quest_scene
template = copy.deepcopy(quest.tilemap.tmxdata.layernames['boxes'].data)
source = Path(BOX_MAP).read_bytes()
for _ in range(3):
    scene._move_box((2, 3), (3, 3))
    assert scene.box_positions == {(3, 3), (5, 5)}
    assert scene.box_sprites[(3, 3)].rect.topleft == (192, 192)
    player.turn_left()
    player.set_position_by_tile(3, 3)
    player._is_end = player._is_win_state = player._is_game_over_state = True
    player.reset()
    assert scene.box_positions == {(2, 3), (5, 5)}
    assert len(scene.get_sprite_list('boxes')) == 2
    assert (player._tile_x, player._tile_y) == (1, 3)
    assert player.rect.center == (96, 224)
    assert player._direction == quest.Direction.RIGHT
    assert not any((player.is_finished, player.is_win, player.is_game_over))
    for (x, y), sprite in scene.box_sprites.items():
        assert sprite.rect.topleft == (64*x, 64*y)
assert quest.tilemap.tmxdata.layernames['boxes'].data == template
assert Path(BOX_MAP).read_bytes() == source
""")


def test_map_replacement_discards_old_boxes_and_restores_right():
    _check("""
import codomir.quest as quest
set_map(BOX_MAP)
old_scene = quest.quest_scene
old_sprites = list(old_scene.box_sprites.values())
old_scene._move_box((2, 3), (3, 3))
player.turn_left()
set_map(BOX_MAP)
assert quest.quest_scene.box_positions == {(2, 3), (5, 5)}
assert not old_scene.box_positions
assert not old_scene.get_sprite_list('boxes')
assert all(not sprite.groups() for sprite in old_sprites)
assert player._direction == quest.Direction.RIGHT
player.turn_left()
set_map(maps.linear.map1)
assert not quest.quest_scene.box_positions
assert not quest.quest_scene.get_sprite_list('boxes')
assert player._direction == quest.Direction.RIGHT
assert player not in old_scene.get_sprite_list('default')
""")


def _variant(tmp_path, change):
    root = ET.parse(BOX_MAP).getroot()
    root.find('tileset').set('source', str(
        (BOX_MAP.parents[2] / 'src/codomir/resources/kenney_sokoban/sokoban_tilesheet.tsx').resolve()
    ))
    change(root)
    path = tmp_path / 'variant.tmx'
    ET.ElementTree(root).write(path, encoding='UTF-8', xml_declaration=True)
    return path


def _box_at(root, index, gid=15):
    values = [0] * 64
    values[index] = gid
    root.find("layer[@name='boxes']/data").text = ','.join(map(str, values))


@pytest.mark.parametrize(('change', 'message'), [
    (lambda root: _box_at(root, 26, 89), 'Box'),
    (lambda root: _box_at(root, 0), 'wall'),
    (lambda root: _box_at(root, 25), 'Spawn'),
    (lambda root: root.find("layer[@name='boxes']").set('name', 'decorations'), 'boxes'),
    (lambda root: root.find("layer[@name='boxes']").set('width', '9'), 'dimensions'),
    (lambda root: root.find("layer[@name='boxes']").set('offsetx', '32'), 'offset'),
    (lambda root: root.find("layer[@name='boxes']").set('x', '-1'), 'offset'),
    (lambda root: _replace_boxes_with_objects(root), 'tile layer'),
    (lambda root: _extend_boxes_beyond_map(root), 'outside'),
    (lambda root: root.append(ET.fromstring(ET.tostring(root.find("layer[@name='boxes']")))), 'one boxes'),
    (lambda root: _add_spawn_on_box(root), 'Spawn'),
    (lambda root: _add_box_object(root), 'boxes'),
])
def test_invalid_box_layout_is_rejected_without_replacing_scene(tmp_path, change, message):
    path = _variant(tmp_path, change)
    _check(f"""
import codomir.quest as quest
set_map(BOX_MAP)
previous = quest.quest_scene
previous_map = quest.tilemap
try:
    set_map({str(path)!r})
except ValueError as error:
    assert {message!r} in str(error), str(error)
else:
    raise AssertionError('Expected invalid box layout to be rejected')
assert quest.quest_scene is previous
assert quest.tilemap is previous_map
assert previous.box_positions == {{(2, 3), (5, 5)}}
""")


def _replace_boxes_with_objects(root):
    root.remove(root.find("layer[@name='boxes']"))
    ET.SubElement(root, 'objectgroup', id='5', name='boxes')


def _extend_boxes_beyond_map(root):
    data = root.find("layer[@name='boxes']/data")
    data.text += ',' + ','.join(['15'] + ['0'] * 7)


def _add_spawn_on_box(root):
    data = root.find("layer[@name='objects']/data")
    values = data.text.split(',')
    values[5 * 8 + 5] = '40'
    data.text = ','.join(values)


def _add_box_object(root):
    group = ET.SubElement(root, 'objectgroup', id='6', name='decorations')
    ET.SubElement(group, 'object', id='1', gid='15', x='192', y='256', width='64', height='64')


@pytest.mark.parametrize('empty', [False, True])
def test_boxes_at_map_edge_or_empty_layer(tmp_path, empty):
    def change(root):
        data = root.find("layer[@name='boxes']/data")
        values = [0] * 64
        values[63] = 0 if empty else 15
        data.text = ','.join(map(str, values))
        walls = root.find("layer[@name='walls']/data")
        values = walls.text.split(',')
        values[63] = '0'
        walls.text = ','.join(values)
    path = _variant(tmp_path, change)
    _check(f"""
import codomir.quest as quest
set_map({str(path)!r})
expected = set() if {empty!r} else {{(7, 7)}}
assert quest.quest_scene.box_positions == expected
assert len(quest.quest_scene.get_sprite_list('boxes')) == len(expected)
player.reset()
assert quest.quest_scene.box_positions == expected
""")


def test_box_semantics_do_not_depend_on_tileset_firstgid(tmp_path):
    def remap(root):
        root.find('tileset').set('firstgid', '101')
        for data in root.findall('layer/data'):
            data.text = ','.join(str(int(gid) + 100 if int(gid) else 0)
                                 for gid in data.text.split(','))
    path = _variant(tmp_path, remap)
    _check(f"""
import codomir.quest as quest
set_map({str(path)!r})
assert quest.quest_scene.box_positions == {{(2, 3), (5, 5)}}
""")
