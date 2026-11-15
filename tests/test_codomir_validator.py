"""Adversarial checks for the conditions-map acceptance tool."""
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest


ROOT = Path(__file__).resolve().parents[1]


def first_entry():
    return json.loads((ROOT / 'tests/fixtures/codomir_conditions.json').read_text(
        encoding='utf-8'))['maps'][0]


def first_source():
    """Conditional teacher solution; the public demo uses direct commands."""
    return ('from codomir import player, set_map, wait_quit, maps\n'
            'set_map(maps.conditions.map1)\n'
            + '\n'.join(first_entry()['conditional_solution']) + '\nwait_quit()\n')


def test_bfs_counts_actions_not_sensor_queries():
    from tests.codomir_validator import shortest_solution
    entry = first_entry()
    assert shortest_solution(entry) == ['push', 'push']
    entry['boxes'] = []
    assert shortest_solution(entry) == ['move_forward'] * 2
    entry['boxes'] = [[2, 3]]  # A box on Win does not count as the hero reaching it.
    assert shortest_solution(entry) == ['move_forward', 'push']


def test_box_on_win_schema_requires_both_box_and_finish():
    from tests.codomir_validator import validate_geometry
    entry = first_entry()
    entry['schema'][3] = '>.*.####'
    entry['boxes'] = [[2, 3]]
    validate_geometry(entry)
    assert entry['schema'][3][2] == '*'
    assert entry['win'] == entry['boxes'][0] == [2, 3]
    entry['boxes'] = []
    with pytest.raises(AssertionError, match='boxes mismatch'):
        validate_geometry(entry)
    entry['boxes'] = [[2, 3]]
    entry['win'] = [1, 3]
    with pytest.raises(AssertionError, match='win mismatch'):
        validate_geometry(entry)


@pytest.mark.parametrize('bad_source', [
    'player.move_forward()\nplayer.move_forward()',
    'for i in range(2):\n    player.push()',
    'while player.is_box_ahead():\n    player.push()',
    'if i == 1:\n    player.push()\nelse:\n    player.move_forward()',
    'actions = [player.push, player.push]\nfor action in actions:\n    action()',
    'exec("player.push()")',
    'def solve():\n    player.push()\nsolve()',
    'player.push(); player.push()',
    'player.push() if player.is_box_ahead() else player.move_forward()',
    'if player.is_box_ahead(): player.push()\nelse: player.move_forward()',
])
def test_rejects_noneducational_python(bad_source):
    from tests.codomir_validator import validate_source
    with pytest.raises(AssertionError):
        validate_source(bad_source, 'standalone_conditions')


def test_source_length_excludes_only_demo_boilerplate_and_comments():
    from tests.codomir_validator import validate_source
    assert validate_source(first_source(), 'standalone_conditions', number=1)[1] == 8


def test_demo_requires_imports_map_selection_and_window_loop():
    from tests.codomir_validator import validate_entry
    source = first_source()
    for changed in (
        source.replace('from codomir import player, set_map, wait_quit, maps', ''),
        source.replace('set_map(maps.conditions.map1)', ''),
        source.replace('wait_quit()', ''),
        source.replace('player, set_map, wait_quit, maps', 'set_map, wait_quit, maps'),
    ):
        with pytest.raises(AssertionError):
            validate_entry(first_entry(), changed)


def test_rejects_nested_loop_in_simple_stage():
    from tests.codomir_validator import validate_source
    source = ('for i in range(2):\n    for j in range(3):\n'
              '        if player.is_box_ahead():\n            player.push()\n'
              '        else:\n            player.move_forward()\n')
    with pytest.raises(AssertionError, match='nested'):
        validate_source(source, 'conditions_in_simple_loops')
    assert validate_source(source, 'conditions_in_complex_routes')[1] == 6


def test_rejects_corrupt_wall(tmp_path):
    from tests.codomir_validator import validate_tmx
    entry = first_entry()
    root = ET.parse(ROOT / 'src/codomir/resources/kenney_sokoban/map_conditions1.tmx').getroot()
    root.find('tileset').set('source', str(
        ROOT / 'src/codomir/resources/kenney_sokoban/sokoban_tilesheet.tsx'))
    data = root.find("layer[@name='walls']/data")
    values = data.text.split(',')
    values[24] = '2'
    data.text = ','.join(values)
    path = tmp_path / 'broken.tmx'
    ET.ElementTree(root).write(path)
    with pytest.raises(AssertionError, match='walls'):
        validate_tmx(entry, path)


def test_rejects_wrong_target_length():
    from tests.codomir_validator import validate_entry
    entry = first_entry()
    entry['linear_length'] = 4
    with pytest.raises(AssertionError, match='length'):
        validate_entry(entry, first_source())


def test_detects_command_after_win():
    from tests.codomir_validator import simulate, validate_source
    tree, _ = validate_source(first_source(), 'standalone_conditions', number=1)
    tree.body.append(__import__('ast').parse('player.turn_left()').body[0])
    with pytest.raises(AssertionError, match='after Win'):
        simulate(first_entry(), tree)


def test_real_engine_rejects_command_after_win(tmp_path):
    from tests.codomir_validator import run_engine
    source = first_source().replace('wait_quit()', 'player.turn_left()\nwait_quit()')
    map_path = ROOT / 'src/codomir/resources/kenney_sokoban/map_conditions1.tmx'
    with pytest.raises(AssertionError, match='Command after Win'):
        run_engine(first_entry(), source, map_path, tmp_path)


def test_loop_coverage_requires_different_iterations_of_same_loop():
    from tests.codomir_validator import check_loop_coverage
    # Two separate loops, each with an invariant result, do not teach a choice.
    with pytest.raises(AssertionError, match='different iterations'):
        check_loop_coverage([
            {'loops': [[1, 0]], 'bool': True, 'action': 'push'},
            {'loops': [[6, 0]], 'bool': False, 'action': 'move_forward'},
        ])
    check_loop_coverage([
        {'loops': [[1, 0]], 'bool': False, 'action': 'move_forward'},
        {'loops': [[1, 1]], 'bool': True, 'action': 'push'},
    ])


def loop_entry():
    """Current COD-159 geometry, including the initial left turn."""
    return json.loads((ROOT / 'tests/fixtures/codomir_conditions.json').read_text(
        encoding='utf-8'))['maps'][3]


def loop_source():
    return ('for i in range(2):\n    player.turn_left()\n'
            '    for j in range(6):\n        if player.is_box_ahead():\n'
            '            player.push()\n        else:\n            player.move_forward()\n')


def test_loop_contract_bfs_variants_and_engine(tmp_path):
    from tests.codomir_validator import validate_entry, run_engine, write_variant
    entry = loop_entry()
    validate_entry(entry, loop_source(), require_demo=False)
    # Reuse only artwork/properties, replacing geometry with the independent schema.
    template = ROOT / 'src/codomir/resources/kenney_sokoban/map_conditions1.tmx'
    path = write_variant(entry, template, tmp_path / 'map4.tmx', replace_geometry=True)
    traces = run_engine(entry, loop_source(), path, tmp_path, verify_export=False)
    assert {row['bool'] for row in traces[0] if row['bool'] is not None} == {False, True}


def test_rejects_invariant_condition_on_main_loop_map():
    from tests.codomir_validator import validate_entry
    entry = loop_entry()
    entry['boxes'] = [[7, 6], [6, 1]]
    entry['schema'][5] = '#######.'
    entry['schema'][6] = '#######B'
    entry['schema'][1] = '.F....B.'
    entry['variants'] = [
        {'name': 'near', 'boxes': [[7, 6], [6, 1]], 'final_boxes': [[7, 0], [0, 1]]},
        {'name': 'far', 'boxes': [[7, 2], [6, 1]], 'final_boxes': [[7, 0], [0, 1]]},
    ]
    entry['linear_solution'] = ['player.turn_left()'] + ['player.push()'] * 6 + ['player.turn_left()'] + ['player.push()'] * 6
    entry['loop_solution'] = ['for i in range(2):', '    player.turn_left()',
                              '    for j in range(6):', '        player.push()']
    entry['loop_length'] = 4
    with pytest.raises(AssertionError, match='different iterations'):
        validate_entry(entry, loop_source(), require_demo=False)


def test_rejects_missing_required_variants():
    from tests.codomir_validator import validate_entry
    entry = copy.deepcopy(first_entry())
    entry['variants'] = []
    with pytest.raises(AssertionError, match='variants'):
        validate_entry(entry, first_source())


def test_box_at_turn_belongs_to_incoming_passage():
    from tests.codomir_validator import final_boxes
    entry = {'passages': [
        {'start': [5, 1], 'end': [5, 4], 'pocket': [5, 5]},
        {'start': [5, 4], 'end': [2, 4], 'pocket': [1, 4]},
    ]}
    assert final_boxes(entry, [[5, 4], [4, 4]]) == {(5, 5), (1, 4)}


def test_bfs_rejects_blocked_push_and_unreachable_finish():
    from tests.codomir_validator import shortest_solution
    entry = first_entry()
    # No space behind the box on Win: even reaching the box cannot count as Win.
    entry['schema'][3] = '>BF#####'
    entry['boxes'] = [[2, 3]]
    with pytest.raises(AssertionError, match='No linear solution'):
        shortest_solution(entry)
