"""The inventory bag: a grid where each item takes up space by its type.

Items in the bag keep their top-left cell in item['Pos'] = [x, y]. An item without a
valid, free position (for example from an imported save) is placed in the first free
spot by `settle`; if there is no room it stays in the list with Pos None ("overflow")
and can still be sold or moved once space frees up.
"""

from .data import BAG_COLS, ITEM_SIZES, bag_rows


def size(item):
    return ITEM_SIZES.get(item.get('Type'), (1, 1))


def dims(player):
    return BAG_COLS, bag_rows(player['InventoryCapacity'])


def _valid_pos(pos):
    return (isinstance(pos, list) and len(pos) == 2 and all(isinstance(v, int) and not isinstance(v, bool) for v in pos))


def _cells(item, x, y):
    w, h = size(item)
    return {(cx, cy) for cx in range(x, x + w) for cy in range(y, y + h)}


def _occupied(player, ignore=None):
    taken = set()
    for item in player['Inventory']:
        if item is ignore or not _valid_pos(item.get('Pos')):
            continue
        taken |= _cells(item, *item['Pos'])
    return taken


def fits_at(player, item, x, y, ignore=None, taken=None):
    cols, rows = dims(player)
    w, h = size(item)
    if x < 0 or y < 0 or x + w > cols or y + h > rows:
        return False
    taken = _occupied(player, ignore) if taken is None else taken
    return not (_cells(item, x, y) & taken)


def free_spot(player, item, ignore=None):
    """The first free top-left cell for `item`, scanning row by row, or None."""
    cols, rows = dims(player)
    taken = _occupied(player, ignore)
    for y in range(rows):
        for x in range(cols):
            if fits_at(player, item, x, y, taken=taken):
                return [x, y]
    return None


def settle(player):
    """Gives every bag item a valid, non-overlapping position (or None when there is no room)."""
    cols, rows = dims(player)
    taken = set()
    unplaced = []
    for item in player['Inventory']:
        pos = item.get('Pos')
        if _valid_pos(pos) and fits_at(player, item, pos[0], pos[1], taken=taken):
            taken |= _cells(item, *pos)
        else:
            item['Pos'] = None
            unplaced.append(item)
    for item in unplaced:
        spot = free_spot(player, item)
        if spot:
            item['Pos'] = spot


def can_add(player, item):
    settle(player)
    return free_spot(player, item) is not None


def add(player, item, pos=None):
    """Puts `item` in the bag, at `pos` if it fits there, else in the first free spot. Returns False if full."""
    settle(player)
    if pos is not None and _valid_pos(pos) and fits_at(player, item, pos[0], pos[1]):
        spot = list(pos)
    else:
        spot = free_spot(player, item)
    if spot is None:
        return False
    item['Pos'] = spot
    player['Inventory'].append(item)
    return True


def repack(player):
    """Re-places every item in list order (used after sorting)."""
    for item in player['Inventory']:
        item['Pos'] = None
    settle(player)


def overflow(player):
    """Indices of items that have no room in the bag."""
    return [i for i, item in enumerate(player['Inventory']) if not _valid_pos(item.get('Pos'))]
