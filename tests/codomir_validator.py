"""Manifest-driven acceptance checks; importing this module never starts SDL.

Coordinates are zero based. Directions are clockwise, starting with RIGHT.
The pure search is independent of the real engine used by ``run_engine``.
"""
import ast
from collections import deque
import copy
import io
import json
from pathlib import Path
import tokenize
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
TARGET_LENGTHS = [(2, 8), (3, 12), (5, 17), (13, 11), (18, 17),
                  (19, 17), (19, 12), (23, 18), (26, 24), (26, 24)]
STAGES = ['standalone_conditions', 'conditions_in_simple_loops',
          'conditions_in_complex_routes']
STEPS = [(1, 0), (0, 1), (-1, 0), (0, -1)]
ACTIONS = ('move_forward', 'push', 'turn_left', 'turn_right')


def cells(values):
    return frozenset(map(tuple, values))


def floor(entry):
    return {(x, y) for y, row in enumerate(entry['schema'])
            for x, char in enumerate(row) if char != '#'}


def transition(entry, state, action):
    position, direction, boxes = state
    if position == tuple(entry['win']):
        return None
    if action in ('turn_left', 'turn_right'):
        return position, (direction + (1 if action == 'turn_right' else -1)) % 4, boxes
    dx, dy = STEPS[direction]
    ahead = position[0] + dx, position[1] + dy
    if ahead not in floor(entry):
        return None
    if action == 'move_forward':
        return None if ahead in boxes else (ahead, direction, boxes)
    beyond = ahead[0] + dx, ahead[1] + dy
    if ahead not in boxes or beyond not in floor(entry) or beyond in boxes:
        return None
    return ahead, direction, (boxes - {ahead}) | {beyond}


def shortest_solution(entry):
    """BFS with unit-cost commands, no sensor edges or illegal transitions."""
    start = (tuple(entry['spawn']), 0, cells(entry['boxes']))
    parents = {start: None}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        if state[0] == tuple(entry['win']):
            actions = []
            while parents[state] is not None:
                state, action = parents[state]
                actions.append(action)
            return actions[::-1]
        for action in ACTIONS:
            next_state = transition(entry, state, action)
            if next_state is not None and next_state not in parents:
                parents[next_state] = state, action
                queue.append(next_state)
    raise AssertionError('No linear solution')


def call_name(node):
    if (isinstance(node, ast.Call) and not node.args and not node.keywords
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name) and node.func.value.id == 'player'):
        return node.func.attr
    return None


def range_values(node):
    assert isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    assert node.func.id == 'range' and not node.keywords and 1 <= len(node.args) <= 3
    assert all(isinstance(arg, ast.Constant) and type(arg.value) is int for arg in node.args), \
        'range requires integer constants'
    try:
        values = range(*(arg.value for arg in node.args))
        assert 0 < len(values) <= 100, 'range must have 1..100 iterations'
    except ValueError as error:
        raise AssertionError('Invalid range') from error
    return values


def validate_source(source, stage, number=None, mode='conditional', require_demo=False):
    """Whitelist the small teaching language instead of blacklisting Python."""
    assert stage in STAGES
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise AssertionError('Invalid Python') from error
    assert not any(token.string == ';' for token in tokenize.generate_tokens(
        io.StringIO(source).readline)), 'One instruction per line'
    body = list(tree.body)
    if require_demo:
        assert body and isinstance(body[0], ast.ImportFrom), 'Demo must import codomir'
    # Standalone snippets are useful for negative checks and the for-only control.
    if body and isinstance(body[0], ast.ImportFrom):
        imports = body.pop(0)
        assert imports.module == 'codomir' and imports.level == 0
        assert all(alias.name in ('player', 'set_map', 'maps', 'wait_quit')
                   and alias.asname is None for alias in imports.names)
        assert {alias.name for alias in imports.names} == {'player', 'set_map', 'maps', 'wait_quit'}, 'Missing demo imports'
        assert body and isinstance(body[0], ast.Expr)
        setup = body.pop(0).value
        assert isinstance(setup, ast.Call) and isinstance(setup.func, ast.Name)
        assert setup.func.id == 'set_map' and len(setup.args) == 1 and not setup.keywords
        assert ast.dump(setup.args[0]) == ast.dump(ast.parse(
            f'maps.conditions.map{number}', mode='eval').body), 'Wrong public map export'
        assert body and isinstance(body[-1], ast.Expr)
        finish = body.pop().value
        assert isinstance(finish, ast.Call) and isinstance(finish.func, ast.Name)
        assert finish.func.id == 'wait_quit' and not finish.args and not finish.keywords
    seen_lines, ifs, loops = set(), [], []

    def visit(statements, depth=0):
        count = 0
        for node in statements:
            assert node.lineno not in seen_lines, 'One instruction per line'
            seen_lines.add(node.lineno)
            if isinstance(node, ast.Expr):
                assert call_name(node.value) in ACTIONS, 'Only direct player commands allowed'
                assert node.end_lineno == node.lineno, 'One instruction per line'
                count += 1
            elif isinstance(node, ast.If):
                assert mode == 'conditional', 'Control solution must not contain if'
                assert call_name(node.test) == 'is_box_ahead', 'Condition must use the sensor'
                assert node.test.end_lineno == node.lineno
                assert node.orelse and node.body[0].lineno > node.lineno
                assert node.orelse[0].lineno > node.body[-1].end_lineno + 1, 'Separate else line required'
                assert len(node.body) == len(node.orelse) == 1
                assert isinstance(node.body[0], ast.Expr) and call_name(node.body[0].value) == 'push'
                assert isinstance(node.orelse[0], ast.Expr) and call_name(node.orelse[0].value) == 'move_forward'
                if stage != STAGES[0]:
                    assert depth, 'Condition must be inside a loop'
                ifs.append(node)
                count += 2 + visit(node.body, depth) + visit(node.orelse, depth)
            elif isinstance(node, ast.For):
                assert mode != 'linear', 'Linear solution must not contain loops'
                assert stage != STAGES[0], 'No loops in introductory maps'
                assert stage != STAGES[1] or depth == 0, 'No nested loops in simple stage'
                assert depth < 3, 'Excessive loop nesting'
                assert isinstance(node.target, ast.Name) and node.target.id not in (
                    'player', 'range', 'maps', 'set_map', 'wait_quit')
                range_values(node.iter)
                assert not node.orelse and node.body[0].lineno > node.lineno
                assert node.iter.end_lineno == node.lineno
                loops.append(node)
                count += 1 + visit(node.body, depth + 1)
            else:
                raise AssertionError(f'Forbidden teaching statement: {type(node).__name__}')
        return count

    count = visit(body)
    assert count > 0
    if mode == 'conditional':
        assert ifs, 'Solution must use the sensor'
    if mode == 'loop':
        assert loops, 'Control solution must use for'
    # Count physical nonempty, noncomment lines, including for/if/else.
    first, last = body[0].lineno, body[-1].end_lineno
    physical = sum(bool(line.strip()) and not line.lstrip().startswith('#')
                   for line in source.splitlines()[first - 1:last])
    assert physical == count, 'One instruction per line'
    return ast.Module(body=body, type_ignores=[]), count


def simulate(entry, tree):
    state = (tuple(entry['spawn']), 0, cells(entry['boxes']))
    trace, context = [], []
    decision = None

    def walk(body):
        nonlocal state, decision
        for node in body:
            assert state[0] != tuple(entry['win']), 'Command after Win'
            if isinstance(node, ast.For):
                for iteration, _ in enumerate(range_values(node.iter)):
                    context.append([node.lineno, iteration])
                    walk(node.body)
                    context.pop()
            elif isinstance(node, ast.If):
                dx, dy = STEPS[state[1]]
                decision = (state[0][0] + dx, state[0][1] + dy) in state[2]
                walk(node.body if decision else node.orelse)
            else:
                action = call_name(node.value)
                next_state = transition(entry, state, action)
                assert next_state is not None, f'Forbidden move: {action}'
                trace.append({'loops': copy.deepcopy(context), 'bool': decision, 'action': action})
                decision = None
                assert len(trace) <= 1000, 'Solution too long'
                state = next_state

    walk(tree.body)
    assert state[0] == tuple(entry['win']), 'Solution does not reach Win'
    return state, trace


def check_loop_coverage(trace):
    results = {}
    for row in trace:
        if row['bool'] is None:
            continue
        for depth, (line, iteration) in enumerate(row['loops']):
            # Parent iteration identifies a particular invocation of a nested loop.
            key = tuple(tuple(pair) for pair in row['loops'][:depth]), line
            results.setdefault(key, {}).setdefault(row['bool'], set()).add(iteration)
    assert any(True in values and False in values
               and any(a != b for a in values[True] for b in values[False])
               for values in results.values()), 'Sensor must vary in different iterations of the same loop'


def validate_geometry(entry):
    schema = entry['schema']
    assert len(schema) == 8 and all(len(row) == 8 for row in schema), 'Schema must be 8x8'
    assert set(''.join(schema)) <= set('#.>FB'), 'Unknown schema symbol'
    for char, key in [('>', 'spawn'), ('F', 'win'), ('B', 'boxes')]:
        expected = cells(entry[key]) if key == 'boxes' else {tuple(entry[key])}
        actual = {(x, y) for y, row in enumerate(schema) for x, value in enumerate(row) if value == char}
        assert actual == expected, f'Schema {key} mismatch'
    assert len(entry['boxes']) == len(cells(entry['boxes'])), 'Duplicate boxes'
    passages = entry['passages']
    assert passages and tuple(passages[0]['start']) == tuple(entry['spawn'])
    direction, walked = 0, set()
    for index, passage in enumerate(passages):
        start, end = tuple(passage['start']), tuple(passage['end'])
        dx, dy = STEPS[direction]
        length = passage['length']
        assert type(length) is int and length > 0
        assert end == (start[0] + length * dx, start[1] + length * dy), 'Passage length/direction'
        route = {(start[0] + i * dx, start[1] + i * dy) for i in range(length + 1)}
        pocket = end[0] + dx, end[1] + dy
        assert tuple(passage['pocket']) == pocket and pocket in floor(entry), 'Invalid pocket'
        assert route <= floor(entry), 'Wall in passage'
        walked.update(route | {pocket})
        if index < len(passages) - 1:
            assert tuple(passages[index + 1]['start']) == end
            assert passage['turn'] in ('left', 'right')
            direction = (direction + (1 if passage['turn'] == 'right' else -1)) % 4
        else:
            assert passage['turn'] is None and end == tuple(entry['win'])
    assert walked == floor(entry), 'Unexpected floor outside passages/pockets'


def required_variants(entry):
    number = entry['number']
    boxes = list(map(tuple, entry['boxes']))
    if number == 1:
        return {frozenset(), frozenset({(2, 3)})}
    if number == 2:
        return {frozenset(), frozenset({(1, 3)}), frozenset({(3, 3)})}
    if number == 3:
        return {frozenset({(3, 2)}), frozenset({(2, 1)}), frozenset(),
                frozenset({(3, 1), (3, 2)})}
    start = entry['passages'][0]['start']
    first = min(boxes, key=lambda pos: abs(pos[0] - start[0]) + abs(pos[1] - start[1]))
    return {(cells(boxes) - {first}) | {(start[0] + distance, start[1])}
            for distance in (1, 5)}


def validate_entry(entry, source, require_demo=True):
    number = entry['number']
    assert type(number) is int and 1 <= number <= 10
    stage = STAGES[0 if number <= 3 else 1 if number <= 6 else 2]
    assert entry['learning_stage'] == stage
    assert entry['require_shorter'] is (number >= 4)
    assert (entry['linear_length'], entry['conditional_length']) == TARGET_LENGTHS[number - 1], 'Target length mismatch'
    assert isinstance(entry['name'], str) and entry['name']
    validate_geometry(entry)
    variants = entry['variants']
    assert required_variants(entry) == {cells(variant['boxes']) for variant in variants}, 'Incorrect variants'
    assert len({variant['name'] for variant in variants}) == len(variants), 'Duplicate variant names'
    tree, length = validate_source(source, stage, number=number, require_demo=require_demo)
    assert length == entry['conditional_length'], 'Conditional length mismatch'
    linear, linear_length = validate_source('\n'.join(entry['linear_solution']), stage, mode='linear')
    assert linear_length == entry['linear_length'] == len(shortest_solution(entry)), 'Linear length is not shortest'
    simulate(entry, linear)
    if entry['require_shorter']:
        assert length < linear_length, 'Conditional solution must be shorter'
        control, control_length = validate_source('\n'.join(entry['loop_solution']), stage, mode='loop')
        assert control_length == entry['loop_length'], 'Control length mismatch'
        simulate(entry, control)
    all_results = set()
    for index, boxes in enumerate([entry['boxes']] + [variant['boxes'] for variant in variants]):
        assert len(boxes) == len(cells(boxes)), 'Duplicate variant boxes'
        assert cells(boxes) <= floor(entry) - {tuple(entry['spawn'])}, 'Invalid variant box'
        state, trace = simulate(dict(entry, boxes=boxes), tree)
        expected_boxes = final_boxes(entry, boxes)
        declared_final = entry['final_boxes'] if index == 0 else variants[index - 1]['final_boxes']
        assert cells(declared_final) == expected_boxes, 'Declared final boxes mismatch'
        assert state[2] == expected_boxes, 'Final box positions mismatch'
        all_results.update(row['bool'] for row in trace if row['bool'] is not None)
        if index == 0 and number >= 4:
            check_loop_coverage(trace)
    assert all_results == {True, False}, 'Both sensor outcomes must be covered'
    return tree


def final_boxes(entry, boxes):
    """Every initial box must finish in the pocket of its original passage."""
    result = set()
    for box in map(tuple, boxes):
        matches = []
        for passage in entry['passages']:
            start, end = passage['start'], passage['end']
            if (box != tuple(start)
                    and min(start[0], end[0]) <= box[0] <= max(start[0], end[0])
                    and min(start[1], end[1]) <= box[1] <= max(start[1], end[1])):
                matches.append(tuple(passage['pocket']))
        assert len(matches) == 1, 'Box must belong to one passage'
        result.add(matches[0])
    assert len(result) == len(boxes), 'Multiple boxes in one passage'
    return frozenset(result)


def read_tmx(path):
    path = Path(path)
    root = ET.parse(path).getroot()
    assert [int(root.get(key, '0')) for key in ('width', 'height', 'tilewidth', 'tileheight')] == [8, 8, 64, 64], 'TMX dimensions'
    types = {}
    for tileset in root.findall('tileset'):
        first = int(tileset.get('firstgid'))
        definition = ET.parse(path.parent / tileset.get('source')).getroot() if tileset.get('source') else tileset
        for tile in definition.findall('tile'):
            types[first + int(tile.get('id'))] = tile.get('type', tile.get('class'))
    layers = {}
    assert not root.findall('group') and not root.findall('objectgroup'), 'Only tile layers allowed'
    for layer in root.findall('layer'):
        name = layer.get('name')
        assert name not in layers, 'Duplicate layer'
        assert (layer.get('width'), layer.get('height')) == ('8', '8'), 'Layer dimensions'
        assert all(float(layer.get(key, '0')) == 0 for key in ('x', 'y', 'offsetx', 'offsety')), 'Layer offset'
        data = layer.find('data')
        assert data is not None and data.get('encoding') == 'csv' and not data.get('compression')
        values = list(map(int, data.text.strip().split(',')))
        assert len(values) == 64, 'Layer must contain 64 cells'
        layers[name] = values
    assert set(layers) == {'background', 'walls', 'objects', 'boxes'}, 'Required layers missing'
    return root, types, layers


def validate_tmx(entry, path):
    _, types, layers = read_tmx(path)
    assert {(i % 8, i // 8) for i, gid in enumerate(layers['walls']) if not gid} == floor(entry), 'TMX walls mismatch'
    for name, values in layers.items():
        for i, gid in enumerate(values):
            kind = types.get(gid)
            assert kind not in ('Spawn', 'Win', 'Box') or name == ('boxes' if kind == 'Box' else 'objects'), 'Misplaced semantic tile'
    for kind, key in [('Spawn', 'spawn'), ('Win', 'win')]:
        actual = [(i % 8, i // 8) for i, gid in enumerate(layers['objects']) if types.get(gid) == kind]
        assert actual == [tuple(entry[key])], f'TMX requires exactly one {kind}'
    assert all(not gid or types.get(gid) in ('Spawn', 'Win') for gid in layers['objects']), 'Invalid object'
    assert all(not gid or types.get(gid) == 'Box' for gid in layers['boxes']), 'Invalid Box'
    assert {(i % 8, i // 8) for i, gid in enumerate(layers['boxes']) if gid} == cells(entry['boxes']), 'TMX boxes mismatch'


def write_variant(entry, template, path, replace_geometry=False):
    root, types, layers = read_tmx(template)
    for tileset in root.findall('tileset'):
        if tileset.get('source'):
            tileset.set('source', str((Path(template).parent / tileset.get('source')).resolve()))
    ids = {kind: next(gid for gid, value in types.items() if value == kind) for kind in ('Spawn', 'Win', 'Box')}
    wall = next(gid for gid in layers['walls'] if gid)
    background = next(gid for gid in layers['background'] if gid)
    for name in layers:
        if not replace_geometry and name != 'boxes':
            continue
        values = [0] * 64
        if name in ('background', 'walls'):
            values = [(wall if char == '#' else 0) if name == 'walls' else
                      (background if char != '#' else 0) for row in entry['schema'] for char in row]
        else:
            objects = [(tuple(entry['spawn']), ids['Spawn']), (tuple(entry['win']), ids['Win'])] if name == 'objects' else [(tuple(box), ids['Box']) for box in entry['boxes']]
            for (x, y), gid in objects:
                values[y * 8 + x] = gid
        root.find(f"layer[@name='{name}']/data").text = ','.join(map(str, values))
    ET.ElementTree(root).write(path, encoding='UTF-8', xml_declaration=True)
    return Path(path)


class TraceLoops(ast.NodeTransformer):
    def visit_For(self, node):
        self.generic_visit(node)
        # Keep Python's actual for semantics; record the current iteration index.
        node.iter = ast.Call(func=ast.Name(id='_iterations', ctx=ast.Load()),
                             args=[ast.Constant(node.lineno), node.iter], keywords=[])
        return node


def engine_scenario(entry, source, map_path, trace_path, verify_export=False):
    """Invoked in a fresh subprocess, with SDL configured by tests.test_codomir._run."""
    import pygamejr
    import codomir
    import codomir.quest as quest
    from codomir import player, set_map

    if verify_export:
        public = getattr(codomir.maps.conditions, f"map{entry['number']}")
        assert Path(public).resolve() == (ROOT / f"src/codomir/resources/kenney_sokoban/map_conditions{entry['number']}.tmx").resolve()
    set_map(map_path)
    codomir.set_map = lambda selected: set_map(map_path)
    codomir.wait_quit = lambda: None
    # Remove timing only; every_frame still updates sprites and draws the scene.
    from types import SimpleNamespace
    import pygamejr.base as base
    base.clock = SimpleNamespace(tick=lambda fps: 16)
    player._animate_win = lambda: None
    player._animate_game_over = lambda dx, dy: None
    validate_source(source, entry['learning_stage'], number=entry['number'], require_demo=verify_export)
    trace, context, completions = [], [], []
    pending = None
    player.on_complete = completions.append

    def iterations(line, values):
        for iteration, value in enumerate(values):
            context.append([line, iteration])
            yield value
            context.pop()

    sensor = player.is_box_ahead

    def checked_sensor():
        nonlocal pending
        assert not player.is_finished, 'Sensor after Win'
        pending = sensor()
        return pending

    def checked(action, command):
        def run():
            nonlocal pending
            assert not player.is_finished, 'Command after Win'
            trace.append({'loops': copy.deepcopy(context), 'bool': pending, 'action': action})
            pending = None
            command()
            assert not player.is_game_over, f'Engine rejected {action}'
        return run

    player.is_box_ahead = checked_sensor
    for action in ACTIONS:
        setattr(player, action, checked(action, getattr(player, action)))
    instrumented = ast.fix_missing_locations(TraceLoops().visit(ast.parse(source)))
    exec(compile(instrumented, '<conditions-demo>', 'exec'),
         {'player': player, '_iterations': iterations})
    assert player.is_win and not player.is_game_over and completions == [True]
    assert (player._tile_x, player._tile_y) == tuple(entry['win'])
    assert player.rect.topleft == tuple(value * 64 for value in entry['win'])
    assert quest.quest_scene.box_positions == cells(entry['final_boxes'])
    for (x, y), sprite in quest.quest_scene.box_sprites.items():
        assert sprite.rect.topleft == (x * 64, y * 64)
    Path(trace_path).write_text(json.dumps(trace, indent=2), encoding='utf-8')
    player.reset()
    assert quest.quest_scene.box_positions == cells(entry['boxes'])
    assert (player._tile_x, player._tile_y) == tuple(entry['spawn'])
    assert player._direction == quest.Direction.RIGHT and not player.is_finished


def run_engine(entry, source, map_path, tmp_path, verify_export=True):
    from tests.test_codomir import _run
    tree, _ = validate_source(source, entry['learning_stage'], number=entry['number'], require_demo=verify_export)
    traces = []
    for index, boxes in enumerate([entry['boxes']] + [variant['boxes'] for variant in entry['variants']]):
        expected_boxes = entry['final_boxes'] if index == 0 else entry['variants'][index - 1]['final_boxes']
        variant = dict(entry, boxes=boxes, final_boxes=expected_boxes)
        path = write_variant(variant, map_path, tmp_path / f'variant-{index}.tmx')
        trace_path = tmp_path / f'trace-{index}.json'
        result = _run(f'from tests.codomir_validator import engine_scenario\n'
                      f'engine_scenario({variant!r}, {source!r}, {str(path)!r}, {str(trace_path)!r}, {verify_export!r})')
        assert result.returncode == 0, result.stdout + result.stderr
        trace = json.loads(trace_path.read_text(encoding='utf-8'))
        _, model_trace = simulate(variant, tree)
        assert trace == model_trace
        if index == 0 and entry['number'] >= 4:
            check_loop_coverage(trace)
        traces.append(trace)
    return traces
