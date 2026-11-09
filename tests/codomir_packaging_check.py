"""Run one public demo against a wheel installed into the supplied directory.

Usage: python tests/codomir_packaging_check.py <install-target> <map-number>
Run this in a fresh process for each map after installing the wheel with --target.
"""
import json
import os
from pathlib import Path
import runpy
import sys
from types import SimpleNamespace


os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
target = Path(sys.argv[1]).resolve()
number = int(sys.argv[2])
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(target))

import codomir
import codomir.quest as quest
from codomir import maps, player
import pygamejr
import pygamejr.base as base


assert target in Path(codomir.__file__).resolve().parents, 'Loaded editable codomir'
assert target in Path(pygamejr.__file__).resolve().parents, 'Loaded editable pygamejr'
base.clock = SimpleNamespace(tick=lambda fps: 16)
player._animate_win = lambda: None
player._animate_game_over = lambda dx, dy: None
codomir.wait_quit = lambda: None
entry = json.loads((root / 'tests/fixtures/codomir_conditions.json').read_text(
    encoding='utf-8'))['maps'][number - 1]
path = getattr(maps.conditions, f'map{number}')
assert path.is_file() and target in path.resolve().parents
completions = []
player.on_complete = completions.append
runpy.run_path(str(root / f'demo/codomir/conditions/map{number}.py'))
assert pygamejr.screen.get_size() == (512, 512)
assert player.is_win and not player.is_game_over and completions == [True]
assert quest.quest_scene.box_positions == set(map(tuple, entry['final_boxes']))
player.reset()
assert not player.is_finished
assert quest.quest_scene.box_positions == set(map(tuple, entry['boxes']))
print(f'map{number}: installed modules, TMX, tileset and images loaded; demo wins; reset OK.')
