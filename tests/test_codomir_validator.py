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
    return (ROOT / 'demo/codomir/conditions/map1.py').read_text(encoding='utf-8')


def test_bfs_counts_actions_not_sensor_queries():
    from tests.codomir_validator import shortest_solution
    entry = first_entry()
    assert shortest_solution(entry) == ['push', 'push']
    entry['boxes'] = []
    assert shortest_solution(entry) == ['move_forward', 'move_forward']
    entry['boxes'] = [[2, 3]]  # Box on Win is legal; pushing it is not yet a win.
    assert shortest_solution(entry) == ['move_forward', 'push']


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
    entry['linear_length'] = 3
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
    """The exact COD-159 geometry exercises the next learning stage early."""
    entry = {
        'number': 4, 'name': 'Left turn',
        'schema': ['######.#', '######F#', '######.#', '######B#',
                   '######.#', '######.#', '######.#', '>.B.....'],
        'spawn': [0, 7], 'win': [6, 1], 'boxes': [[2, 7], [6, 3]],
        'final_boxes': [[7, 7], [6, 0]],
        'passages': [
            {'start': [0, 7], 'end': [6, 7], 'length': 6, 'turn': 'left', 'pocket': [7, 7]},
            {'start': [6, 7], 'end': [6, 1], 'length': 6, 'turn': None, 'pocket': [6, 0]},
        ],
        'linear_solution': ['player.move_forward()'] + ['player.push()'] * 5
            + ['player.turn_left()'] + ['player.move_forward()'] * 3 + ['player.push()'] * 3,
        'linear_length': 13, 'conditional_length': 11,
        'learning_stage': 'conditions_in_simple_loops', 'require_shorter': True,
        'variants': [
            {'name': 'near', 'boxes': [[1, 7], [6, 3]], 'final_boxes': [[7, 7], [6, 0]]},
            {'name': 'far', 'boxes': [[5, 7], [6, 3]], 'final_boxes': [[7, 7], [6, 0]]},
        ],
        'loop_solution': ['player.move_forward()', 'for i in range(5):',
                          '    player.push()', 'player.turn_left()',
                          'for i in range(3):', '    player.move_forward()',
                          'for i in range(3):', '    player.push()'],
        'loop_length': 8,
    }
    return entry


def loop_source():
    block = ('for i in range(6):\n    if player.is_box_ahead():\n'
             '        player.push()\n    else:\n        player.move_forward()\n')
    return block + 'player.turn_left()\n' + block


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
    entry['boxes'][0] = [1, 7]
    entry['boxes'][1] = [6, 6]
    entry['schema'][7] = '>B......'
    entry['schema'][3] = '######.#'
    entry['schema'][6] = '######B#'
    entry['variants'] = [
        {'name': 'near', 'boxes': [[1, 7], [6, 6]], 'final_boxes': [[7, 7], [6, 0]]},
        {'name': 'far', 'boxes': [[5, 7], [6, 6]], 'final_boxes': [[7, 7], [6, 0]]},
    ]
    entry['linear_solution'] = ['player.push()'] * 6 + ['player.turn_left()'] + ['player.push()'] * 6
    entry['loop_solution'] = ['for i in range(6):', '    player.push()',
                              'player.turn_left()', 'for i in range(6):', '    player.push()']
    entry['loop_length'] = 5
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
        {'start': [1, 1], 'end': [3, 1], 'pocket': [4, 1]},
        {'start': [3, 1], 'end': [3, 3], 'pocket': [3, 4]},
    ]}
    assert final_boxes(entry, [[3, 1], [3, 2]]) == {(4, 1), (3, 4)}


def test_bfs_rejects_blocked_push_and_unreachable_finish():
    from tests.codomir_validator import shortest_solution
    entry = first_entry()
    # No space behind the box on Win: even reaching the box cannot count as Win.
    entry['schema'][3] = '>BF#####'
    entry['boxes'] = [[2, 3]]
    with pytest.raises(AssertionError, match='No linear solution'):
        shortest_solution(entry)
