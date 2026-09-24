"""Save files: where they live, how they are written, and the single-instance lock."""

import json
import os
import sys
import time
from pathlib import Path

APP_DIR_NAME = 'AeternaRoma'
SAVE_FILE_NAME = 'save.json'


def default_data_dir():
    """Per-user folder for the save file (e.g. %APPDATA%\\AeternaRoma on Windows)."""
    override = os.environ.get('AETERNA_ROMA_DATA_DIR')
    if override:
        return Path(override)
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA') or Path.home() / 'AppData' / 'Roaming'
        return Path(base) / APP_DIR_NAME
    if sys.platform == 'darwin':
        return Path.home() / 'Library' / 'Application Support' / APP_DIR_NAME
    base = os.environ.get('XDG_DATA_HOME') or Path.home() / '.local' / 'share'
    return Path(base) / 'aeterna-roma'


def read_json_file(path):
    """Reads a JSON file, ignoring a UTF-8 byte-order mark (some editors add one)."""
    with open(path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def write_json_atomic(path, data):
    """Writes JSON to a temporary file and swaps it in, so a crash can't leave a half-written save."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


class SaveStore:
    def __init__(self, directory=None):
        self.directory = Path(directory) if directory else default_data_dir()
        self.path = self.directory / SAVE_FILE_NAME
        self._lock_file = None

    def load(self):
        """Returns (raw_save_or_None, warning_or_None). An unreadable save is kept as a backup."""
        if not self.path.exists():
            return None, None
        try:
            return read_json_file(self.path), None
        except (OSError, ValueError) as exc:
            backup = self.path.with_name('save.corrupt-%d.json' % int(time.time()))
            try:
                os.replace(self.path, backup)
            except OSError:
                backup = None
            where = ' A copy was kept as %s.' % backup.name if backup else ''
            return None, '⚠️ Your save could not be read (%s).%s A new game was started.' % (exc.__class__.__name__, where)

    def save(self, state):
        write_json_atomic(self.path, state)

    # --- single instance ---------------------------------------------------------------

    def acquire_lock(self):
        """Takes an exclusive lock so two game windows can't overwrite each other's save.

        Returns False if another copy of the game already holds it. The lock is
        released automatically when the process exits.
        """
        self.directory.mkdir(parents=True, exist_ok=True)
        handle = open(self.directory / 'game.lock', 'a+')
        try:
            if sys.platform == 'win32':
                import msvcrt
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            handle.close()
            return False
        self._lock_file = handle
        return True
