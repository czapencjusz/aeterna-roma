"""Aeterna Roma launcher.

Run with:  python aeterna_roma.py

Opens the game in a native window (via pywebview). All game logic runs in this
Python process; the window only draws the interface. No web server is started
and no network ports are opened.
"""

import sys

from aeterna import UI_FILE
from aeterna.api import Api
from aeterna.engine import Game
from aeterna.storage import SaveStore


def self_check():
    """Loads the interface and a game without opening a window (useful to test a build)."""
    from aeterna.view import build_view
    html = UI_FILE.read_text(encoding='utf-8')
    game = Game()
    game.start_expedition(0, 0)
    build_view(game)
    assert 'window.pywebview.api' in html
    print('Aeterna Roma OK: interface %d KB, save folder %s' % (len(html) // 1024, SaveStore().directory))


def main():
    if '--check' in sys.argv[1:]:
        self_check()
        return
    try:
        import webview
    except ImportError:
        sys.exit('Aeterna Roma needs the "pywebview" package. Install it with:\n    python -m pip install pywebview')

    store = SaveStore()
    if not store.acquire_lock():
        webview.create_window('Aeterna Roma', html='<body style="font-family:sans-serif;background:#1c1414;color:#e6dac3;'
                              'padding:24px">Aeterna Roma is already running in another window.</body>',
                              width=420, height=160)
        webview.start()
        return

    raw, warning = store.load()
    game = Game.from_save(raw) if raw is not None else Game()
    game.catch_up()

    api = Api(game, store)
    if warning:
        api._startup_notices.append(warning)

    window = webview.create_window(
        'Aeterna Roma - Hero of Rome',
        html=UI_FILE.read_text(encoding='utf-8'),  # loaded straight into the window: no web server
        js_api=api,
        width=1400, height=900, min_size=(900, 600),
        background_color='#0f0a0a',
    )
    api._window = window
    window.events.closed += api._on_closed
    webview.start()


if __name__ == '__main__':
    main()
