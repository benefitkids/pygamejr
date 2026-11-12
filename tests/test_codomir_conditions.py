"""Box state, sensors and movement, isolated from codomir import side effects."""
from pathlib import Path
import ast
import json
import xml.etree.ElementTree as ET

import pytest

from tests.test_codomir import _run


BOX_MAP = Path(__file__).parent / "fixtures" / "codomir_boxes.tmx"
CONDITIONS_MAP = BOX_MAP.parents[2] / 'src/codomir/resources/kenney_sokoban/map_conditions1.tmx'
CONDITIONS_DEMO = BOX_MAP.parents[2] / 'demo/codomir/conditions/map1.py'
MANIFEST = json.loads((BOX_MAP.parent / 'codomir_conditions.json').read_text(encoding='utf-8'))['maps']


def test_conditions_manifest_matches_public_exports():
    exports = ast.parse((BOX_MAP.parents[2] / 'src/codomir/maps/conditions.py').read_text(encoding='utf-8'))
    numbers = [entry['number'] for entry in MANIFEST]
    assert len(numbers) == len(set(numbers)), 'Duplicate map number'
    public = {int(target.id[3:]) for node in exports.body if isinstance(node, ast.Assign)
              for target in node.targets if isinstance(target, ast.Name)
              and target.id.startswith('map') and target.id[3:].isdigit()}
    assert public == set(numbers), 'Every exported map needs a manifest entry'


@pytest.mark.parametrize('entry', MANIFEST, ids=lambda entry: f"map{entry['number']}")
def test_conditions_map_acceptance(entry, tmp_path):
    from tests.codomir_validator import validate_entry, validate_tmx, run_engine
    number = entry['number']
    map_path = CONDITIONS_MAP.with_name(f'map_conditions{number}.tmx')
    demo_path = CONDITIONS_DEMO.with_name(f'map{number}.py')
    source = demo_path.read_text(encoding='utf-8')
    validate_entry(entry, source)
    validate_tmx(entry, map_path)
    run_engine(entry, source, map_path, tmp_path)


@pytest.mark.parametrize('entry', MANIFEST, ids=lambda entry: f"map{entry['number']}")
def test_conditions_public_demo_replay_and_reference_solutions(entry):
    """Exercise the public script and both controls without replacing rendering."""
    demo = CONDITIONS_DEMO.with_name(f"map{entry['number']}.py")
    _check(f"""
import runpy
from pathlib import Path
from types import SimpleNamespace
import pygamejr
import pygamejr.base as base
import codomir
import codomir.quest as quest
from tests.codomir_validator import validate_source

entry = {entry!r}
base.clock = SimpleNamespace(tick=lambda fps: 16)
codomir.wait_quit = lambda: None
completions = []
player.on_complete = completions.append
source = Path({str(demo)!r}).read_text(encoding='utf-8')
tree, _ = validate_source(source, entry['learning_stage'], number=entry['number'], require_demo=True)
commands = {{name: getattr(player, name) for name in ('push', 'move_forward', 'turn_left', 'turn_right')}}

def guarded(command):
    def run():
        assert not player.is_finished, 'Demo or reference command after Win'
        return command()
    return run
for name, command in commands.items():
    setattr(player, name, guarded(command))

def check_boxes(expected):
    scene = quest.quest_scene
    assert scene.box_positions == set(map(tuple, expected))
    group = scene.get_sprite_list('boxes')
    assert len(group) == len(expected)
    assert set(group) == set(scene.box_sprites.values())
    for (x, y), sprite in scene.box_sprites.items():
        assert sprite.rect.topleft == (x * 64, y * 64)
        assert sprite.visible and sprite.groups() == [group]

def check_win(count):
    assert player.is_finished and player.is_win and not player.is_game_over
    assert (player._tile_x, player._tile_y) == tuple(entry['win'])
    assert completions == [True] * count
    check_boxes(entry['final_boxes'])
    # Finished movement must not fire the completion callback again.
    commands['push']()
    commands['move_forward']()
    assert completions == [True] * count
    check_boxes(entry['final_boxes'])

def reset():
    player.reset()
    assert not any((player.is_finished, player.is_win, player.is_game_over))
    assert (player._tile_x, player._tile_y) == tuple(entry['spawn'])
    assert player._direction == quest.Direction.RIGHT
    check_boxes(entry['boxes'])

runpy.run_path({str(demo)!r})
assert pygamejr.screen.get_size() == (512, 512)
check_win(1)
reset()
# Replay the teaching body on the same scene, without set_map masking reset bugs.
exec(compile(tree, '<conditions-replay>', 'exec'), {{'player': player}})
check_win(2)
reset()
exec('\\n'.join(entry['linear_solution']), {{'player': player}})
check_win(3)
if entry['number'] >= 4:
    reset()
    exec('\\n'.join(entry['loop_solution']), {{'player': player}})
    check_win(4)

reset()
previous = list(completions)
player.turn_left()
player.move_forward()
assert player.is_game_over and not player.is_win
assert completions == previous + [False]
commands['move_forward']()
commands['push']()
assert completions == previous + [False]
reset()
assert completions == previous + [False]
""")


@pytest.mark.parametrize(('family', 'folder'), [
    ('linear', None), ('loop', 'loop'), ('nested_loops', 'nested_loop'),
])
def test_conditions_switch_to_legacy_maps_and_back(family, folder):
    if folder is None:
        legacy_demo = CONDITIONS_DEMO.parents[1] / 'map1_win.py'
    else:
        legacy_demo = CONDITIONS_DEMO.parents[1] / folder / 'map1.py'
    _check(f"""
import runpy
from types import SimpleNamespace
import codomir
import codomir.quest as quest
import pygamejr.base as base

base.clock = SimpleNamespace(tick=lambda fps: 16)
codomir.wait_quit = lambda: None
completions = []
player.on_complete = completions.append
for cycle in range(2):
    set_map(maps.conditions.map9)
    old_scene = quest.quest_scene
    old_boxes = list(old_scene.box_sprites.values())
    player.push()  # Deliberate loss: the initial neighboring cell is empty.
    assert player.is_game_over and completions == [False, True] * cycle + [False]
    set_map(getattr(maps, {family!r}).map1)
    runpy.run_path({str(legacy_demo)!r})
    assert player.is_win and not player.is_game_over
    assert completions == [False, True] * (cycle + 1)
    assert not quest.quest_scene.box_positions
    assert not quest.quest_scene.get_sprite_list('boxes')
    assert not old_scene.box_positions
    assert not old_scene.get_sprite_list('boxes')
    assert all(not sprite.groups() for sprite in old_boxes)
    assert player not in old_scene.get_sprite_list('default')
    assert player in quest.quest_scene.get_sprite_list('default')
    legacy_scene = quest.quest_scene
    set_map(maps.conditions.map9)
    assert player not in legacy_scene.get_sprite_list('default')
    assert not player.is_finished and player._direction == quest.Direction.RIGHT
    assert quest.quest_scene.box_positions == {{(2, 0), (6, 4), (3, 6), (1, 4), (2, 3)}}
    assert len(quest.quest_scene.get_sprite_list('boxes')) == 5
    assert completions == [False, True] * (cycle + 1)
""")


@pytest.mark.parametrize('number', [1, 9], ids=lambda number: f'map{number}')
def test_conditions_push_frames_and_reset(number, tmp_path):
    entry = next(entry for entry in MANIFEST if entry['number'] == number)
    _check(f"""
from pathlib import Path
from types import SimpleNamespace
import pygame
import pygamejr
import pygamejr.base as base
import codomir.quest as quest

base.clock = SimpleNamespace(tick=lambda fps: 16)
set_map(getattr(maps.conditions, 'map{number}'))
assert pygamejr.screen.get_size() == (512, 512)
scene = quest.quest_scene
output = Path({str(tmp_path)!r})

def snapshot(name):
    pygamejr.next_frame()
    pygame.image.save(pygamejr.screen, str(output / name))
    return pygamejr.screen.copy()

def pixels(surface):
    return pygame.image.tobytes(surface, 'RGB')

initial = snapshot('initial.png')
if {number} == 9:
    player.move_forward()
before = snapshot('before-push.png')
source = (player._tile_x, player._tile_y)
old_cell = pygame.Rect(source[0] * 64, source[1] * 64, 64, 64)
box_source = (source[0] + 1, source[1])
box = scene.box_sprites[box_source]
player.visible = box.visible = False
background = snapshot('background.png')
player.visible = box.visible = True
player.push()
last_frame = pygamejr.screen.copy()
after = snapshot('after-push.png')
assert pixels(last_frame) == pixels(after)
assert pixels(before) != pixels(after)
assert pixels(after.subsurface(old_cell)) == pixels(background.subsurface(old_cell)), 'Ghost sprite'
destination = pygame.Rect((box_source[0] + 1) * 64, box_source[1] * 64, 64, 64)
expected = background.subsurface(destination).copy()
expected.blit(box.image, (0, 0))
assert pixels(after.subsurface(destination)) == pixels(expected)
win = {entry['win']!r}
win_cell = pygame.Rect(win[0] * 64, win[1] * 64, 64, 64)
# Compare the finish with a clean render without movable sprites.
player.visible = False
for sprite in scene.box_sprites.values():
    sprite.visible = False
clean = snapshot('finish-visible.png')
if not win_cell.colliderect(player.rect) and not any(
        win_cell.colliderect(sprite.rect) for sprite in scene.box_sprites.values()):
    assert pixels(after.subsurface(win_cell)) == pixels(clean.subsurface(win_cell))
player.visible = True
for sprite in scene.box_sprites.values():
    sprite.visible = True
assert len(scene.get_sprite_list('boxes')) == len({entry['boxes']!r})
player.reset()
reset = snapshot('reset.png')
assert pixels(reset) == pixels(initial)
""")


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


DIRECTION_STEPS = [
    ('TOP', 0, -1), ('RIGHT', 1, 0), ('BOTTOM', 0, 1), ('LEFT', -1, 0),
]


def _ahead_scenario(tmp_path, dx, dy, obstacle):
    start = (3, 3)
    if obstacle == 'edge':
        start = (7 if dx > 0 else 0 if dx < 0 else 3,
                 7 if dy > 0 else 0 if dy < 0 else 3)
    target = (start[0] + dx, start[1] + dy)

    def change(root):
        layers = {name: [0] * 64 for name in ('walls', 'boxes', 'objects')}
        layers['objects'][start[1] * 8 + start[0]] = 40
        win = target if obstacle == 'win' else (6, 6)
        layers['objects'][win[1] * 8 + win[0]] = 75
        if obstacle == 'wall':
            layers['walls'][target[1] * 8 + target[0]] = 2
        elif obstacle in ('box', 'distant_box'):
            distance = 1 if obstacle == 'box' else 2
            x, y = start[0] + distance * dx, start[1] + distance * dy
            layers['boxes'][y * 8 + x] = 15
        elif obstacle == 'edge':
            # An open opposite edge must not be reached through negative indices.
            x, y = target[0] % 8, target[1] % 8
            layers['boxes'][y * 8 + x] = 15
        for name, values in layers.items():
            root.find(f"layer[@name='{name}']/data").text = ','.join(map(str, values))

    return _variant(tmp_path, change), start, target


@pytest.mark.parametrize(('direction', 'dx', 'dy'), DIRECTION_STEPS)
@pytest.mark.parametrize('obstacle', ['box', 'empty', 'wall', 'edge', 'distant_box'])
def test_box_sensor_is_pure_in_each_direction(tmp_path, direction, dx, dy, obstacle):
    path, start, target = _ahead_scenario(tmp_path, dx, dy, obstacle)
    _check(f"""
import copy
from unittest.mock import Mock
import pygamejr
import codomir.quest as quest
set_map({str(path)!r})
player._direction = quest.Direction.{direction}
scene = quest.quest_scene
template = copy.deepcopy(quest.tilemap.tmxdata.layernames['boxes'].data)
boxes = dict(scene.box_sprites)
rects = {{pos: sprite.rect.copy() for pos, sprite in boxes.items()}}
rect = player.rect.copy()
image = player.image
player.on_complete = Mock()
pygamejr.next_frame = Mock(side_effect=AssertionError('Sensor rendered a frame'))
pygamejr.every_frame = Mock(side_effect=AssertionError('Sensor started animation'))
player._animate_win = Mock(side_effect=AssertionError('Sensor animated a win'))
player._animate_game_over = Mock(side_effect=AssertionError('Sensor animated a loss'))
for finished, win, lost in [(False, False, False), (True, True, False), (True, False, True)]:
    player._is_end, player._is_win_state, player._is_game_over_state = finished, win, lost
    for _ in range(2):
        assert player.is_box_ahead() is {obstacle == 'box'!r}
    assert (player.is_finished, player.is_win, player.is_game_over) == (finished, win, lost)
    assert (player._tile_x, player._tile_y) == {start!r}
    assert player.rect == rect and player.image is image
    assert player._direction == quest.Direction.{direction}
    assert scene.box_sprites == boxes
    assert all(sprite.rect == rects[pos] for pos, sprite in boxes.items())
    assert quest.tilemap.tmxdata.layernames['boxes'].data == template
player.on_complete.assert_not_called()
pygamejr.next_frame.assert_not_called()
pygamejr.every_frame.assert_not_called()
player._animate_win.assert_not_called()
player._animate_game_over.assert_not_called()
""")


def test_box_sensor_reads_current_positions_instead_of_tmx():
    _check("""
import codomir.quest as quest
set_map(BOX_MAP)
assert player.is_box_ahead() is True
quest.quest_scene._move_box((2, 3), (3, 3))
assert player.is_box_ahead() is False
player.set_position_by_tile(2, 3)
assert player.is_box_ahead() is True
player.reset()
assert player.is_box_ahead() is True
set_map(maps.linear.map1)
assert player.is_box_ahead() is False
""")


@pytest.mark.parametrize(('direction', 'dx', 'dy'), DIRECTION_STEPS)
@pytest.mark.parametrize('obstacle', ['box', 'wall', 'edge'])
def test_blocked_move_loses_once_without_moving_world(tmp_path, direction, dx, dy, obstacle):
    path, start, target = _ahead_scenario(tmp_path, dx, dy, obstacle)
    _check(f"""
import copy
from unittest.mock import Mock
import pygamejr
import codomir.quest as quest
set_map({str(path)!r})
player._direction = quest.Direction.{direction}
scene = quest.quest_scene
boxes = dict(scene.box_sprites)
rects = {{pos: sprite.rect.copy() for pos, sprite in boxes.items()}}
template = copy.deepcopy(quest.tilemap.tmxdata.layernames['boxes'].data)
rect = player.rect.copy()
player.on_complete = Mock()
player._animate_game_over = Mock()
pygamejr.every_frame = Mock(side_effect=AssertionError('Blocked move animated walking'))
pygamejr.next_frame = Mock(side_effect=AssertionError('Blocked move rendered a frame'))
for _ in range(3):
    assert player.move_forward() is None
    assert player.is_finished and player.is_game_over and not player.is_win
    assert (player._tile_x, player._tile_y) == {start!r}
    assert player.rect == rect
    assert scene.box_sprites == boxes
    assert all(sprite.rect == rects[pos] for pos, sprite in boxes.items())
    assert quest.tilemap.tmxdata.layernames['boxes'].data == template
player._animate_game_over.assert_called_once_with({dx}, {dy})
player.on_complete.assert_called_once_with(False)
assert player.is_box_ahead() is {obstacle == 'box'!r}
pygamejr.every_frame.assert_not_called()
pygamejr.next_frame.assert_not_called()
""")


@pytest.mark.parametrize(('direction', 'dx', 'dy'), DIRECTION_STEPS)
@pytest.mark.parametrize('obstacle', ['empty', 'win'])
def test_free_move_and_win_keep_existing_behavior(tmp_path, direction, dx, dy, obstacle):
    path, start, target = _ahead_scenario(tmp_path, dx, dy, obstacle)
    _check(f"""
from unittest.mock import Mock
import pygamejr
import codomir.quest as quest
set_map({str(path)!r})
player._direction = quest.Direction.{direction}
player.on_complete = Mock()
player._animate_win = Mock()
pygamejr.every_frame = lambda count: iter([0] * count)
assert player.move_forward() is None
assert (player._tile_x, player._tile_y) == {target!r}
assert player.rect.topleft == ({target[0] * 64}, {target[1] * 64})
assert player.is_game_over is False
assert player.is_finished is {obstacle == 'win'!r}
assert player.is_win is {obstacle == 'win'!r}
if {obstacle == 'win'!r}:
    for _ in range(2):
        assert player.move_forward() is None
    assert (player._tile_x, player._tile_y) == {target!r}
    assert player.rect.topleft == ({target[0] * 64}, {target[1] * 64})
    player.on_complete.assert_called_once_with(True)
    player._animate_win.assert_called_once_with()
else:
    player.on_complete.assert_not_called()
    player._animate_win.assert_not_called()
""")


def _push_scenario(tmp_path, dx=1, dy=0, obstacle='empty', win='elsewhere'):
    start = (3, 3)
    if obstacle in ('edge', 'front_edge'):
        distance = 1 if obstacle == 'edge' else 0
        start = (7 - distance if dx > 0 else distance, 3) if dx else (
            3, 7 - distance if dy > 0 else distance
        )
    source = (start[0] + dx, start[1] + dy)
    destination = (source[0] + dx, source[1] + dy)

    def change(root):
        layers = {'background': [89] * 64, 'walls': [0] * 64,
                  'objects': [0] * 64, 'boxes': [0] * 64}
        layers['objects'][start[1] * 8 + start[0]] = 40
        finish = {'source': source, 'destination': destination}.get(win, (6, 6))
        layers['objects'][finish[1] * 8 + finish[0]] = 75
        if obstacle not in ('missing', 'front_wall', 'front_edge'):
            layers['boxes'][source[1] * 8 + source[0]] = 15
        if obstacle == 'front_wall':
            layers['walls'][source[1] * 8 + source[0]] = 2
        elif obstacle == 'wall':
            layers['walls'][destination[1] * 8 + destination[0]] = 2
        elif obstacle == 'box':
            layers['boxes'][destination[1] * 8 + destination[0]] = 15
        elif obstacle in ('edge', 'front_edge'):
            # Catch negative indexing and wrapping to the opposite map edge.
            outside = destination if obstacle == 'edge' else source
            layers['boxes'][(outside[1] % 8) * 8 + outside[0] % 8] = 15
        if win == 'source':
            # The box may end in a dead-end pocket beyond the finish.
            for x, y in [(destination[0] + dx, destination[1] + dy),
                         (destination[0] + dy, destination[1] + dx),
                         (destination[0] - dy, destination[1] - dx)]:
                layers['walls'][y * 8 + x] = 2
        for name, values in layers.items():
            root.find(f"layer[@name='{name}']/data").text = ','.join(map(str, values))

    return _variant(tmp_path, change), start, source, destination


@pytest.mark.parametrize(('direction', 'dx', 'dy'), DIRECTION_STEPS)
@pytest.mark.parametrize('frame_count', [0, 7, 64, 65])
def test_push_moves_both_sprites_and_snaps_to_cells(tmp_path, direction, dx, dy, frame_count):
    path, start, source, destination = _push_scenario(tmp_path, dx, dy)
    _check(f"""
import copy
import pygamejr
import codomir.quest as quest
set_map({str(path)!r})
player._direction = quest.Direction.{direction}
player._update_image()
scene = quest.quest_scene
box = scene.box_sprites[{source!r}]
template = copy.deepcopy(quest.tilemap.tmxdata.layernames['boxes'].data)
results = []
player.on_complete = results.append
def frames(count):
    for i in range({frame_count}):
        yield 0
        progress = min(i + 1, 64)
        assert player.rect.topleft == ({start[0] * 64} + progress * {dx}, {start[1] * 64} + progress * {dy})
        assert box.rect.topleft == ({source[0] * 64} + progress * {dx}, {source[1] * 64} + progress * {dy})
pygamejr.every_frame = frames
assert player.push() is None
assert (player._tile_x, player._tile_y) == {source!r}
assert player.rect.topleft == ({source[0] * 64}, {source[1] * 64})
assert scene.box_positions == {{{destination!r}}}
assert scene.box_sprites[{destination!r}] is box
assert box.rect.topleft == ({destination[0] * 64}, {destination[1] * 64})
assert set(scene.get_sprite_list('boxes')) == {{box}}
assert player._direction == quest.Direction.{direction}
assert player.is_box_ahead() is True
assert not any((player.is_finished, player.is_win, player.is_game_over))
assert results == []
assert quest.tilemap.tmxdata.layernames['boxes'].data == template
""")


@pytest.mark.parametrize(('direction', 'dx', 'dy'), DIRECTION_STEPS)
@pytest.mark.parametrize('obstacle', ['missing', 'front_wall', 'front_edge', 'wall', 'box', 'edge'])
def test_invalid_push_loses_once_without_partial_movement(tmp_path, direction, dx, dy, obstacle):
    path, start, source, destination = _push_scenario(tmp_path, dx, dy, obstacle)
    _check(f"""
import copy
import pygamejr
import codomir.quest as quest
set_map({str(path)!r})
player._direction = quest.Direction.{direction}
scene = quest.quest_scene
boxes = dict(scene.box_sprites)
rects = {{pos: sprite.rect.copy() for pos, sprite in boxes.items()}}
template = copy.deepcopy(quest.tilemap.tmxdata.layernames['boxes'].data)
rect = player.rect.copy()
results = []
player.on_complete = results.append
def unexpected_frames(count):
    raise AssertionError('Invalid push started movement')
pygamejr.every_frame = unexpected_frames
for _ in range(3):
    assert player.push() is None
    assert player.is_finished and player.is_game_over and not player.is_win
    assert (player._tile_x, player._tile_y) == {start!r}
    assert player.rect == rect
    assert scene.box_sprites == boxes
    assert all(sprite.rect == rects[pos] for pos, sprite in boxes.items())
assert results == [False]
assert quest.tilemap.tmxdata.layernames['boxes'].data == template
player.reset()
assert scene.box_positions == set(boxes)
assert (player._tile_x, player._tile_y) == {start!r}
assert player._direction == quest.Direction.RIGHT
assert not any((player.is_finished, player.is_win, player.is_game_over))
assert results == [False]
""")


@pytest.mark.parametrize(('direction', 'dx', 'dy'), DIRECTION_STEPS)
@pytest.mark.parametrize('win', ['source', 'destination'])
def test_push_only_wins_when_player_enters_finish(tmp_path, direction, dx, dy, win):
    path, start, source, destination = _push_scenario(tmp_path, dx, dy, win=win)
    _check(f"""
import pygamejr
import codomir.quest as quest
set_map({str(path)!r})
player._direction = quest.Direction.{direction}
pygamejr.every_frame = lambda count: iter([0] * count)
results = []
def complete(success):
    results.append(success)
    assert (player._tile_x, player._tile_y) == {source!r}
    assert player.rect.topleft == ({source[0] * 64}, {source[1] * 64})
    assert quest.quest_scene.box_positions == {{{destination!r}}}
    assert player.is_win and player.is_finished
    player.push()
player.on_complete = complete
player.push()
assert player.is_win is {win == 'source'!r}
assert player.is_finished is {win == 'source'!r}
assert player.is_game_over is False
assert results == {[True] if win == 'source' else []!r}
if player.is_finished:
    box = quest.quest_scene.box_sprites[{destination!r}]
    rect = box.rect.copy()
    player.push()
    player.move_forward()
    assert quest.quest_scene.box_positions == {{{destination!r}}}
    assert box.rect == rect
    assert results == [True]
player.reset()
assert quest.quest_scene.box_positions == {{{source!r}}}
assert (player._tile_x, player._tile_y) == {start!r}
assert not player.is_finished
""")


def test_push_mixed_commands_and_repeated_reset(tmp_path):
    path, start, source, destination = _push_scenario(tmp_path)
    _check(f"""
import pygamejr
import codomir.quest as quest
set_map({str(path)!r})
pygamejr.every_frame = lambda count: iter([0] * count)
for _ in range(3):
    assert player.is_box_ahead()
    player.push()
    player.push()
    assert quest.quest_scene.box_positions == {{(6, 3)}}
    player.turn_left()
    assert not player.is_box_ahead()
    player.move_forward()
    player.turn_right()
    player.move_forward()
    player.turn_right()
    assert player.is_box_ahead()
    player.push()
    assert quest.quest_scene.box_positions == {{(6, 4)}}
    assert (player._tile_x, player._tile_y) == (6, 3)
    assert player.is_box_ahead()
    player.move_forward()
    assert player.is_game_over
    player.reset()
    assert quest.quest_scene.box_positions == {{(4, 3)}}
    assert len(quest.quest_scene.get_sprite_list('boxes')) == 1
    assert (player._tile_x, player._tile_y) == (3, 3)
    assert player._direction == quest.Direction.RIGHT
    assert not any((player.is_finished, player.is_win, player.is_game_over))
""")


def test_push_rendering_has_no_ghosts_and_reset_restores_frame(tmp_path):
    path, start, source, destination = _push_scenario(tmp_path)
    _check(f"""
from pathlib import Path
from types import SimpleNamespace
import pygame
import pygamejr
import pygamejr.base as base
import codomir.quest as quest
set_map({str(path)!r})
# Keep the real frame loop and drawing, replacing only its clock delay.
base.clock = SimpleNamespace(tick=lambda fps: 16)
scene = quest.quest_scene
box = scene.box_sprites[(4, 3)]
output = Path({str(tmp_path)!r})
def snapshot(name):
    pygamejr.next_frame()
    pygame.image.save(pygamejr.screen, str(output / name))
    return pygamejr.screen.copy()
def pixels(surface):
    return pygame.image.tobytes(surface, 'RGB')
before = snapshot('push-before.png')
player.visible = box.visible = False
background = snapshot('push-background.png')
player.visible = box.visible = True
player.push()
# The real frame loop must already have rendered the final aligned sprites.
last_frame = pygamejr.screen.copy()
after = snapshot('push-after.png')
assert pixels(last_frame) == pixels(after), 'Last animation frame differs from final scene'
old_cell = pygame.Rect(192, 192, 64, 64)
assert pixels(after.subsurface(old_cell)) == pixels(background.subsurface(old_cell)), 'Ghost in vacated cell'
box_cell = pygame.Rect(320, 192, 64, 64)
expected_box = background.subsurface(box_cell).copy()
expected_box.blit(box.image, (0, 0))
assert pixels(after.subsurface(box_cell)) == pixels(expected_box), 'Box destination pixels differ'
assert pixels(after) != pixels(before)
assert box.groups() == [scene.get_sprite_list('boxes')]
assert len(scene.get_sprite_list('boxes')) == 1
player.reset()
reset = snapshot('push-reset.png')
assert pixels(reset) == pixels(before), 'Reset does not restore the frame'
""")


def test_first_conditions_map_geometry_and_public_demo():
    _check(f"""
import runpy
import pygamejr
import codomir
import codomir.quest as quest
set_map(maps.conditions.map1)
data = quest.tilemap.tmxdata
assert (data.width, data.height, data.tilewidth, data.tileheight) == (8, 8, 64, 64)
assert pygamejr.screen.get_size() == (512, 512)
assert set(data.layernames) == {{'background', 'walls', 'objects', 'boxes'}}
assert quest._get_spawn_position() == (0, 3)
assert quest.win_position == (2, 3)
assert quest.quest_scene.box_positions == {{(1, 3)}}
assert {{(x, y) for y, row in enumerate(data.layernames['walls'].data)
        for x, gid in enumerate(row) if not gid}} == {{(0, 3), (1, 3), (2, 3), (3, 3)}}
for kind, expected in [('Spawn', (0, 3)), ('Win', (2, 3))]:
    assert [(x, y) for x, y, gid in data.layernames['objects']
            if data.tile_properties.get(gid, {{}}).get('type') == kind] == [expected]
pygamejr.every_frame = lambda count: iter([0] * count)
pygamejr.next_frame = lambda: None
codomir.wait_quit = lambda: None
runpy.run_path({str(CONDITIONS_DEMO)!r})
assert player.is_win and not player.is_game_over
assert (player._tile_x, player._tile_y) == (2, 3)
assert quest.quest_scene.box_positions == {{(3, 3)}}
player.reset()
assert quest.quest_scene.box_positions == {{(1, 3)}}
assert (player._tile_x, player._tile_y) == (0, 3)
assert not player.is_finished
""")


@pytest.mark.parametrize(('box', 'expected_actions', 'expected_sensor'), [
    ((1, 3), ['push', 'push'], [True, True]),
    (None, ['move_forward', 'move_forward'], [False, False]),
    ((2, 3), ['move_forward', 'push'], [False, True]),
])
def test_first_conditions_solution_handles_box_variants(tmp_path, box, expected_actions, expected_sensor):
    root = ET.parse(CONDITIONS_MAP).getroot()
    root.find('tileset').set('source', str(
        CONDITIONS_MAP.with_name('sokoban_tilesheet.tsx').resolve()
    ))
    values = [0] * 64
    if box is not None:
        values[box[1] * 8 + box[0]] = 15
    root.find("layer[@name='boxes']/data").text = ','.join(map(str, values))
    variant = tmp_path / 'conditions1.tmx'
    ET.ElementTree(root).write(variant, encoding='UTF-8', xml_declaration=True)
    _check(f"""
import ast
import runpy
from pathlib import Path
import pygamejr
import codomir
import codomir.quest as quest
source = Path({str(CONDITIONS_DEMO)!r}).read_text(encoding='utf-8')
tree = ast.parse(source)
assert all(isinstance(node, (ast.ImportFrom, ast.Expr, ast.If)) for node in tree.body)
conditions = [node for node in tree.body if isinstance(node, ast.If)]
assert len(conditions) == 2
assert sum(len(ast.get_source_segment(source, node).splitlines()) for node in conditions) == 8
for node in conditions:
    assert isinstance(node.test, ast.Call) and not node.test.args and not node.test.keywords
    assert isinstance(node.test.func, ast.Attribute)
    assert isinstance(node.test.func.value, ast.Name) and node.test.func.value.id == 'player'
    assert node.test.func.attr == 'is_box_ahead'
    for branch, command in [(node.body, 'push'), (node.orelse, 'move_forward')]:
        assert len(branch) == 1 and isinstance(branch[0], ast.Expr)
        call = branch[0].value
        assert isinstance(call, ast.Call) and not call.args and not call.keywords
        assert isinstance(call.func, ast.Attribute) and call.func.attr == command
        assert isinstance(call.func.value, ast.Name) and call.func.value.id == 'player'

def select_variant(selected):
    assert selected == maps.conditions.map1
    set_map({str(variant)!r})
codomir.set_map = select_variant
codomir.wait_quit = lambda: None
pygamejr.every_frame = lambda count: iter([0] * count)
pygamejr.next_frame = lambda: None
actions, sensors, completions = [], [], []
sensor = player.is_box_ahead
def checked_sensor():
    assert not player.is_finished
    result = sensor()
    sensors.append(result)
    return result
player.is_box_ahead = checked_sensor
def checked_command(name, command):
    def run():
        assert not player.is_finished, 'Command after reaching Win'
        actions.append(name)
        command()
    return run
player.push = checked_command('push', player.push)
player.move_forward = checked_command('move_forward', player.move_forward)
player.on_complete = completions.append
runpy.run_path({str(CONDITIONS_DEMO)!r})
assert player.is_win and not player.is_game_over
assert (player._tile_x, player._tile_y) == (2, 3)
assert quest.quest_scene.box_positions == {({(3, 3)} if box else set())!r}
assert actions == {expected_actions!r}
assert sensors == {expected_sensor!r}
assert completions == [True]
player.reset()
assert quest.quest_scene.box_positions == {({box} if box else set())!r}
assert (player._tile_x, player._tile_y) == (0, 3)
assert player._direction == quest.Direction.RIGHT
assert not player.is_finished
""")
