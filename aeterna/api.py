"""The bridge between the game window and the Python game.

pywebview exposes every public method of `Api` to the page as
`window.pywebview.api.<method>(...)`. Each call runs the action, saves, and
returns a response dict:

    {'view': <everything the UI draws>, 'notices': [...], 'result': <combat report or None>}

Methods may be called from several threads at once, so all game access goes
through a lock. Attributes are private (underscore) so pywebview doesn't expose them.
"""

import json
import sys
import threading
import traceback

from .storage import read_json_file, write_json_atomic
from .view import build_view

EXPORT_FILE_NAME = 'aeterna_roma_save.json'


class Api:
    def __init__(self, game, store=None, window=None):
        self._game = game
        self._store = store
        self._window = window
        self._lock = threading.RLock()
        self._startup_notices = []
        self._seq = 0

    # --- plumbing -----------------------------------------------------------------------

    def _respond(self, result=None, save=True):
        game = self._game
        from . import bag
        bag.settle(game.player)  # items added directly (old saves, tests) get a place in the bag
        if save:
            self._save()
        notices = self._startup_notices + game.take_notices()
        self._startup_notices = []
        # `seq` lets the UI ignore a response that arrives after a newer one.
        self._seq += 1
        return {'view': build_view(game, str(self._store.path) if self._store else '', self._seq), 'notices': notices,
                'result': result}

    def _save(self):
        if not self._store:
            return
        try:
            self._store.save(self._game.state)
        except OSError as exc:
            self._game.notify('⚠️ The game could not be saved: %s' % exc)

    def _run(self, action, *args):
        """Runs one game action under the lock and returns the UI response."""
        with self._lock:
            try:
                result = action(*args)
                self._game.check_achievements()
                return self._respond(result if isinstance(result, dict) else None)
            except Exception as exc:  # never let one bad call break the window
                traceback.print_exc(file=sys.stderr)
                self._game.notify('⚠️ Something went wrong: %s' % exc)
                return self._respond(save=False)

    def _on_closed(self):
        with self._lock:
            self._save()

    # --- reading --------------------------------------------------------------------------

    def get_view(self):
        with self._lock:
            return self._respond(save=False)

    def tick(self):
        """Called by the UI every second. Only sends the full view back when something changed."""
        with self._lock:
            change = self._game.tick()
            if change != 'none' and self._game.check_achievements():
                change = 'all'
            if change == 'none':
                return {'change': 'none'}
            response = self._respond(save=change == 'all')
            response['change'] = change
            return response

    # --- fights ---------------------------------------------------------------------------

    def start_expedition(self, location_index, monster_index):
        return self._run(self._game.start_expedition, location_index, monster_index)

    def challenge_arena(self, ladder_index):
        return self._run(self._game.challenge_arena, ladder_index)

    def start_series(self, location_index, monster_index, count):
        return self._run(self._game.start_series, location_index, monster_index, count)

    def attempt_labor(self, labor_index):
        return self._run(self._game.attempt_labor, labor_index)

    def enter_dungeon(self, dungeon_index):
        return self._run(self._game.enter_dungeon, dungeon_index)

    def restart_dungeon(self, dungeon_index):
        return self._run(self._game.restart_dungeon, dungeon_index)

    # --- character, items, merchants --------------------------------------------------------

    def train(self, attribute_index):
        return self._run(self._game.train, attribute_index)

    def equip(self, inventory_index):
        return self._run(self._game.equip, inventory_index)

    def use_potion(self, inventory_index):
        return self._run(self._game.use_potion, inventory_index)

    def unequip(self, slot, x=None, y=None):
        return self._run(self._game.unequip, slot, x, y)

    def move_item(self, inventory_index, x, y):
        return self._run(self._game.move_item, inventory_index, x, y)

    def sell(self, inventory_index):
        return self._run(self._game.sell, inventory_index)

    def sell_junk_preview(self):
        """How many common items "Sell Common Gear" would sell, and for how much (for the confirm dialog)."""
        from .items import sell_price
        with self._lock:
            junk = self._game.junk_items()
            return {'count': len(junk), 'total': sum(sell_price(it) for it in junk)}

    def sell_junk(self):
        return self._run(self._game.sell_junk)

    def toggle_lock(self, inventory_index):
        return self._run(self._game.toggle_lock, inventory_index)

    def sort_inventory(self):
        return self._run(self._game.sort_inventory)

    def reforge(self, location, key):
        return self._run(self._game.reforge, location, key)

    def smelt(self, inventory_index):
        return self._run(self._game.smelt, inventory_index)

    def craft(self, recipe_index):
        return self._run(self._game.craft, recipe_index)

    def enhance(self, location, key):
        return self._run(self._game.enhance, location, key)

    def buy(self, vendor_key, item_index, x=None, y=None):
        return self._run(self._game.buy, vendor_key, item_index, x, y)

    # --- work, guild, quests, rubies ----------------------------------------------------------

    def start_work(self, hours):
        return self._run(self._game.start_work, hours)

    def cancel_work(self):
        return self._run(self._game.cancel_work)

    def create_guild(self, name, tag):
        return self._run(self._game.create_guild, name, tag)

    def donate(self, option_index):
        return self._run(self._game.donate, option_index)

    def upgrade_building(self, key):
        return self._run(self._game.upgrade_building, key)

    def claim_quest(self, slot_index):
        return self._run(self._game.claim_quest, slot_index)

    def abandon_quest(self, slot_index):
        return self._run(self._game.abandon_quest, slot_index)

    def buy_blessing(self, key):
        return self._run(self._game.buy_blessing, key)

    def buy_honor(self, key):
        return self._run(self._game.buy_honor, key)

    def claim_daily(self):
        return self._run(self._game.claim_daily)

    def ruby_refill_energy(self):
        return self._run(self._game.ruby_refill_energy)

    def ruby_skip_arena(self):
        return self._run(self._game.ruby_skip_arena)

    def ruby_restock(self, vendor_key):
        return self._run(self._game.ruby_restock, vendor_key)

    # --- settings & save files ----------------------------------------------------------------

    def rename(self, name):
        return self._run(self._game.rename, name)

    def set_theme(self, key):
        return self._run(self._game.set_theme, key)

    def set_combat_speed(self, key):
        return self._run(self._game.set_combat_speed, key)

    def set_audio_muted(self, muted):
        return self._run(self._game.set_audio_muted, muted)

    def reset_game(self, name=None):
        def reset():
            self._game.reset(name)
            self._game.notify('Gladiator progress reset.')
        return self._run(reset)

    def save_now(self):
        def save():
            self._game.notify('💾 Game saved.')
        return self._run(save)

    def export_save(self):
        """Asks where to save a copy of the game, then writes it there."""
        path = self._ask_path(save=True)
        if not path:
            return self.get_view()
        return self._run(self._export_to, path)

    def import_save(self):
        """Asks for a save file, then loads it (the UI confirms with the player before calling this)."""
        path = self._ask_path(save=False)
        if not path:
            return self.get_view()
        return self._run(self._import_from, path)

    def _export_to(self, path):
        try:
            write_json_atomic(path, self._game.state)
            self._game.notify('📥 Save exported to %s' % path)
        except OSError as exc:
            self._game.notify('⚠️ Could not write the save file: %s' % exc)

    def _import_from(self, path):
        try:
            raw = read_json_file(path)
        except (OSError, ValueError, UnicodeDecodeError):
            raw = None
        if not isinstance(raw, dict) or not isinstance(raw.get('Player'), dict):
            self._game.notify('That file is not an Aeterna Roma save.')
            return
        self._game.load_save(raw)
        self._game.catch_up()
        self._game.notify('📤 Save file loaded.')

    def _ask_path(self, save):
        """Shows the system file dialog. Returns a path or None. Never holds the game lock while waiting."""
        if not self._window:
            return None
        import webview
        dialog = webview.FileDialog.SAVE if save else webview.FileDialog.OPEN
        kwargs = {'file_types': ('Save files (*.json)', 'All files (*.*)')}
        if save:
            kwargs['save_filename'] = EXPORT_FILE_NAME
        chosen = self._window.create_file_dialog(dialog, **kwargs)
        if not chosen:
            return None
        return chosen if isinstance(chosen, str) else chosen[0]


def dumps(response):
    """JSON-encodes a response (used by the test bridge; pywebview does its own encoding)."""
    return json.dumps(response, ensure_ascii=False)
