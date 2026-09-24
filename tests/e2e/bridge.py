"""Test-only stand-in for pywebview's JS bridge.

Reads one JSON request per line from stdin ({"id", "method", "args"}), calls the
matching public method of aeterna.api.Api, and writes {"id", "result"} (or
{"id", "error"}) back on stdout. The UI test (ui_test.js) uses this so the page
talks to the real Python game exactly as it does inside the pywebview window.

A few `test_*` commands let the test set up situations directly (they are not
part of the game's API).
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from aeterna import util  # noqa: E402
from aeterna.api import Api  # noqa: E402
from aeterna.engine import Game  # noqa: E402
from aeterna.storage import SaveStore  # noqa: E402

util.rng.seed(int(os.environ.get('SEED', '7')))
clock_offset = {'ms': 0}
game = Game(clock=lambda: util.now_ms() + clock_offset['ms'])
store = SaveStore(tempfile.mkdtemp(prefix='aeterna-e2e-'))
api = Api(game, store)


def test_set(path, value):
    """Sets a value inside the game state, e.g. test_set(['Player', 'Gold'], 5000)."""
    target = api._game.state
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    from aeterna.rules import recalc_stats
    recalc_stats(api._game.player)


def test_get(path):
    target = api._game.state
    for key in path:
        target = target[key]
    return target


def test_add_item(level, item_type, rarity):
    from aeterna.items import generate_item
    api._game.player['Inventory'].append(generate_item(level, item_type, rarity))


def test_add_unique(boss_name, level):
    from aeterna.items import make_unique
    api._game.player['Inventory'].append(make_unique(boss_name, level))


def test_advance_clock(ms):
    clock_offset['ms'] += ms


def test_export_import(path):
    """Runs the export/import code paths without a native file dialog."""
    api._run(api._export_to, path)
    return api._run(api._import_from, path)


TEST_COMMANDS = {f.__name__: f for f in (test_set, test_get, test_add_item, test_add_unique, test_advance_clock, test_export_import)}

for line in sys.stdin:
    request = json.loads(line)
    try:
        method = request['method']
        if method in TEST_COMMANDS:
            result = TEST_COMMANDS[method](*request['args'])
        elif method.startswith('_') or not callable(getattr(api, method, None)):
            raise AttributeError('No such API method: %s' % method)
        else:
            result = getattr(api, method)(*request['args'])
        reply = {'id': request['id'], 'result': result}
    except Exception as exc:  # report to the test instead of dying
        reply = {'id': request['id'], 'error': '%s: %s' % (exc.__class__.__name__, exc)}
    sys.stdout.write(json.dumps(reply, ensure_ascii=False) + '\n')
    sys.stdout.flush()
